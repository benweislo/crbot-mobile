import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, field_validator

from proxy.config import ANTHROPIC_API_KEY

router = APIRouter()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant expert en rédaction de comptes rendus professionnels.
On te fournit la transcription d'une réunion. Tu dois générer un Compte Rendu (CR) structuré en respectant **exactement** le format suivant.

{context_block}

Rédige en {language}.

============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : {{date}}
  Durée    : {{durée}}

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • [Thème 1]
  • [Thème 2]
  (Liste courte, à puces, des grands sujets abordés)

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------

  Pour chaque personne identifiée, liste ses actions spécifiques :

  **[Nom/Speaker]:**
  1. [Action claire et précise]
  2. [Action]

  **[Nom/Speaker 2]:**
  1. [Action]

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → [Résumé global de la fin de la réunion et du sentiment général]

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
[Détaille rigoureusement chaque thème abordé :
 - Ce qui a été discuté exactement (idées, débats, propositions).
 - Le détail des actions à mener (qui fait quoi, comment, pourquoi).
 - Fais des paragraphes numérotés et organisés par thème.
 - Cite ce qu'ont dit les speakers de façon lisible et digeste.
 - Sois exhaustif mais concis. N'invente rien.]

============================================================
FIN DU COMPTE RENDU
============================================================"""


def build_system_prompt(context: str = "", language: str = "français") -> str:
    context_block = ""
    if context:
        context_block = f"Contexte de l'entreprise : {context}\nUtilise ce contexte pour mieux comprendre les termes techniques et les rôles des participants."
    return SYSTEM_PROMPT_TEMPLATE.format(context_block=context_block, language=language)


async def call_anthropic(transcript: str, context: str = "", language: str = "fr") -> str:
    """Call Anthropic API to summarize transcript."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    lang_map = {"fr": "français", "en": "English", "es": "español"}
    lang_name = lang_map.get(language, "français")

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0.3,
        system=build_system_prompt(context, lang_name),
        messages=[
            {"role": "user", "content": f"Voici la transcription complète de la réunion :\n\n{transcript}"}
        ],
    )
    return message.content[0].text


class SummarizeRequest(BaseModel):
    license_key: str
    transcript: str
    context: str = ""
    language: str = "fr"

    @field_validator("transcript")
    @classmethod
    def transcript_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Transcript cannot be empty")
        return v


@router.post("/summarize")
async def summarize(req: SummarizeRequest, request: Request):
    mgr = request.app.state.license_mgr
    auth = mgr.validate(req.license_key)
    if not auth["valid"]:
        raise HTTPException(403, auth.get("reason", "Invalid license"))

    if not request.app.state.rate_limiter.check(req.license_key):
        raise HTTPException(429, "Rate limit exceeded")

    logger.info(f"Summarize request from {auth['client_id']}: {len(req.transcript)} chars")

    summary = await call_anthropic(req.transcript, req.context, req.language)

    logger.info(f"Summary complete for {auth['client_id']}: {len(summary)} chars output")
    return {"summary": summary}
