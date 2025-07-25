// Substitua por sua VAPID public key real (base64 url safe)
const VAPID_PUBLIC_KEY = "SUA_PUBLICA_VAPID_KEY_AQUI";

export async function subscribeUserToPush(token) {
  if (!('serviceWorker' in navigator)) return false;
  const registration = await navigator.serviceWorker.ready;
  let permission = Notification.permission;
  if (permission !== "granted") {
    permission = await Notification.requestPermission();
    if (permission !== "granted") return false;
  }
  try {
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
    });
    // Envie subscription para o backend via fetch/AJAX com Authorization
    await fetch("/api/v1/push-subscription/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(subscription)
    });
    return true;
  } catch (e) {
    return false;
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
} 