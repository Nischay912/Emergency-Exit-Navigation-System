// Basic Service Worker for PWA installability
self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
});

self.addEventListener('fetch', (e) => {
  // Pass through all requests - we just need the SW for the "Add to Homescreen" prompt
  e.respondWith(fetch(e.request).catch(() => new Response("Offline")));
});
