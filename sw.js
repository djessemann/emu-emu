// emu service worker: makes the app open offline.
// The app shell is stored on install. The emulator cores live in their own cache (CORES) that survives app
// updates, so an update doesn't make every core download again (4–7 MB each). The NES core is stored on
// install; every other file the app fetches (the other systems' cores) is stored the first time it loads.
// Bump CACHE whenever any file changes, or installed users keep the old version.
// Bump CORES only if a file under vendor/<core>/ changes (a core update keeps the same file names).
const CACHE = 'emuemu-v14';
const CORES = 'emu-cores-v1';
const ASSETS = [
  './',
  'index.html',
  'manifest.json',
  'vendor/jszip.min.js',
  'favicon.png',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png'
];
const NES_CORE = ['vendor/fceumm/fceumm_libretro.js', 'vendor/fceumm/fceumm_libretro.wasm'];
const isCore = url => /\/vendor\/[a-z0-9_]+\/[a-z0-9_]+_libretro\.(js|wasm)$/.test(new URL(url).pathname);

self.addEventListener('install', e => {
  e.waitUntil(Promise.all([
    caches.open(CACHE).then(c => c.addAll(ASSETS)),
    caches.open(CORES).then(async c => {
      for(const u of NES_CORE) if(!(await c.match(u))) await c.add(u);
    })
  ]).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const old = (await caches.keys()).filter(k => k !== CACHE && k !== CORES);
    const cores = await caches.open(CORES);
    for(const k of old){
      // move cores out of the old app cache (from before CORES existed) instead of downloading them again
      try{
        const c = await caches.open(k);
        for(const req of await c.keys()) if(isCore(req.url) && !(await cores.match(req))) await cores.put(req, await c.match(req));
      }catch(err){}
      await caches.delete(k);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const sameOrigin = new URL(req.url).origin === self.location.origin;
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if(sameOrigin && res.ok && res.status === 200 && !req.headers.has('range')){
        const copy = res.clone();
        caches.open(isCore(req.url) ? CORES : CACHE).then(c => c.put(req, copy)).catch(() => {});
      }
      return res;
    }).catch(() => {
      if(req.mode === 'navigate') return caches.match('index.html');
    }))
  );
});
