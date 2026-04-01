/**
 * A.R.C.A.N.E. — Service Worker (Legacy & Edge)
 * Handles offline persistence, background asset caching,
 * and instant-loading performance for the Progressive Web App.
 * Strategy: Network-First for HTML, Stale-While-Revalidate for Assets.
 */
const CACHE_NAME = 'arcane-cache-v5';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/chat_pc.html',
  '/chat_mobile.html',
  '/intro.html',
  '/icon-512.png'
];

// Installs and forces update skip waiting
self.addEventListener('install', event => {
  self.skipWaiting(); 
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.allSettled(
        urlsToCache.map(url =>
          cache.add(url).catch(err => console.warn(`[SW] Failed to cache: ${url}`, err))
        )
      )
    )
  );
});

// Purge old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim()) // 🚀 Take control of all pages instantly
    .then(() => {
      return self.clients.matchAll({ type: 'window' }).then(clients => {
        clients.forEach(client => client.postMessage({ type: 'SW_UPDATED' }));
      });
    })
  );
});

self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const requestUrl = new URL(event.request.url);

  // 🚀 Bypass Service Worker completely for Localhost (Instant Development)
  if (requestUrl.hostname === 'localhost' || requestUrl.hostname === '127.0.0.1') {
    return; 
  }

  // Strategy 1: Network-First for HTML/Navigation request
  // (Makes updates instant on internet connection, fallbacks to cache offline)
  if (event.request.mode === 'navigate' || requestUrl.pathname.endsWith('.html') || requestUrl.pathname === '/') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, response.clone());
            return response;
          });
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Network-Only for API endpoints (Never cache dynamic endpoints)
  if (requestUrl.pathname.startsWith('/characters') ||
      requestUrl.pathname.startsWith('/history') ||
      requestUrl.pathname.startsWith('/models') ||
      requestUrl.pathname.startsWith('/health')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Strategy 2: Stale-While-Revalidate for other static assets (Images, Fonts, etc.)
  // (Loads instantly from cache while updating it in background for next visit)
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse.status === 200 || networkResponse.type === 'opaque') {
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, networkResponse.clone());
          });
        }
        return networkResponse;
      });
      return cachedResponse || fetchPromise;
    })
  );
});
