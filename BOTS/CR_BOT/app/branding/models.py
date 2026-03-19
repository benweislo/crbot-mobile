from dataclasses import dataclass, field


@dataclass
class BrandProfile:
    company_name: str = "Company"
    primary_color: str = "#6e3ea8"
    secondary_color: str = "#E93F7F"
    background_color: str = "#050505"
    text_color: str = "#E5E5E5"
    font_family: str = "CeraPro"
    footer_text: str = "Compte rendu généré automatiquement"
    language: str = "fr"
    context: str = ""
    logo_b64: str = ""
    font_regular_b64: str = ""
    font_bold_b64: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "BrandProfile":
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)
