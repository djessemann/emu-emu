// Pocket 6502 service worker: precaches the app so it opens offline.
// Bump CACHE whenever any cached file changes, or installed users keep the old version.
const CACHE = 'pocket6502-v4';
const ASSETS = [
  './',
  'index.html',
  'manifest.json',
  'vendor/jsnes.min.js',
  'vendor/jszip.min.js',
  'favicon.png',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).catch(() => {
      if (e.request.mode === 'navigate') return caches.match('index.html');
    }))
  );
});
