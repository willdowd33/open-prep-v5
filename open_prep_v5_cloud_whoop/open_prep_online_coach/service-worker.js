// V5.0: no offline HTML caching; always fetch the latest UI.
const VERSION = "open-prep-5.0";
self.addEventListener("install", event => { self.skipWaiting(); });
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) await caches.delete(key);
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  // Network-only avoids serving an obsolete version or stale nutrition data.
});
