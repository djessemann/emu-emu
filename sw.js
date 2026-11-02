// emu service worker: makes the app open offline.
// The app shell (and the NES core) is stored on install. Every other file the app fetches (the other systems'
// emulator cores, fetched when you have games for them) is stored the first time it loads.
// Bump CACHE whenever any file changes, or installed users keep the old version.
const CACHE = 'emuemu-v8';
const ASSETS = [
  './',
  'index.html',
  'manifest.json',
  'vendor/fceumm/fceumm_libretro.js',
  'vendor/fceumm/fceumm_libretro.wasm',
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
  const req = e.request;
  if(req.method !== 'GET') return;
  const sameOrigin = new URL(req.url).origin === self.location.origin;
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if(sameOrigin && res.ok && res.status === 200 && !req.headers.has('range')){
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
      }
      return res;
    }).catch(() => {
      if(req.mode === 'navigate') return caches.match('index.html');
    }))
  );
});
