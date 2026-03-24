import * as TaskManager from 'expo-task-manager';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

export const BACKGROUND_AUDIO_TASK = 'CRBOT_BACKGROUND_AUDIO';

/**
 * Background audio task definition.
 * On Android: paired with a foreground service notification.
 * On iOS: the "audio" UIBackgroundMode in app.json keeps the session alive.
 * expo-av manages the actual audio — this task keeps the process alive.
 */
TaskManager.defineTask(BACKGROUND_AUDIO_TASK, async () => {
  // No-op: expo-av handles audio recording.
  // Task exists to maintain the foreground service on Android.
});

/**
 * Start background recording support.
 * On Android: shows a persistent notification.
 * On iOS: audio background mode is automatic via app.json config.
 */
export async function startBackgroundTask(): Promise<void> {
  if (Platform.OS === 'android') {
    // Android foreground service notification
    await Notifications.setNotificationChannelAsync('recording', {
      name: 'Enregistrement',
      importance: Notifications.AndroidImportance.LOW,
    });
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'CR_BOT',
        body: 'Enregistrement en cours...',
        sticky: true,
      },
      trigger: null, // Immediate
    });
  }
}

export async function stopBackgroundTask(): Promise<void> {
  if (Platform.OS === 'android') {
    await Notifications.dismissAllNotificationsAsync();
  }
  const isRegistered = await TaskManager.isTaskRegisteredAsync(BACKGROUND_AUDIO_TASK);
  if (isRegistered) {
    await TaskManager.unregisterTaskAsync(BACKGROUND_AUDIO_TASK);
  }
}
