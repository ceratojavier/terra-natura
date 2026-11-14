const APP_CACHE = "terra-natura-app-shell-v1";
const APP_HOME = "/app/";

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(APP_CACHE).then((cache) => cache.add(APP_HOME)).catch(() => undefined));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith("terra-natura-app-shell-") && key !== APP_CACHE).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(async () => (await caches.match(APP_HOME)) || Response.error()));
  }
});

self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch { data = { body: event.data?.text() || "Te llegó un mensaje nuevo." }; }
  const title = data.title || "Nuevo mensaje · Terra Natura";
  const count = Number(data.unreadCount || 0);
  event.waitUntil((async () => {
    if (count > 0 && self.navigator?.setAppBadge) await self.navigator.setAppBadge(count).catch(() => undefined);
    else if (self.navigator?.clearAppBadge) await self.navigator.clearAppBadge().catch(() => undefined);
    await self.registration.showNotification(title, {
      body: data.body || "Te llegó un mensaje por WhatsApp.",
      icon: "/app/logo-terra-natura.png",
      badge: "/app/logo-terra-natura.png",
      tag: data.tag || "terra-natura-chat",
      renotify: true,
      silent: false,
      vibrate: [250, 120, 250, 120, 450],
      data: { url: data.url || "/app/admin/pms/bandeja" },
    });
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL(event.notification.data?.url || "/app/admin/pms/bandeja", self.location.origin).href;
  event.waitUntil((async () => {
    const clients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of clients) {
      if (client.url.startsWith(self.location.origin + "/app/")) {
        await client.focus();
        if ("navigate" in client) await client.navigate(target);
        return;
      }
    }
    await self.clients.openWindow(target);
  })());
});
