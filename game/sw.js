const CACHE = 'gore-zone-v24';
const FILES = ['./', './index.html', './three.min.js', './manifest.json', './icon-192.png', './icon-512.png', './fonts/Oswald-cyrillic-db2216.woff2', './fonts/Oswald-cyrillic-ext-6b10e1.woff2', './fonts/Oswald-latin-ed56cb.woff2', './fonts/RubikWetPaint-cyrillic-ext-94dafe.woff2', './fonts/RubikWetPaint-cyrillic-feed60.woff2', './fonts/RubikWetPaint-latin-77da82.woff2', './fonts/RussoOne-cyrillic-54efa9.woff2', './fonts/RussoOne-latin-b8b6da.woff2', './fonts/fonts.css'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== CACHE).map(n => caches.delete(n))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {}); return r; })
    .catch(() => caches.match(e.request)));
});
