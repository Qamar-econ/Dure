/* Dure offline support. Once a phone or tablet has opened the site, the story page and the demo keep working
   when the Wi-Fi drops (an event hall, a village): pages come from the network when it answers within a few
   seconds and from this device otherwise; pictures, scripts, the Small AI model and the web fonts are kept here.
   Large AI models (Qwen, the photo grader) keep their own cache and are not touched.
   Lives in /assets/ and controls the whole site (_headers sends Service-Worker-Allowed: /). */
const V = 'dure-v1';
const CORE = ['/', '/m.html', '/demo.html', '/assets/intent.json', '/assets/grader_v2.js', '/assets/worldbank.png', '/assets/founder.jpg',
  '/assets/samples/sample_A.jpg', '/assets/samples/sample_B.jpg', '/assets/samples/sample_C.jpg', '/assets/letefoho_sat.jpg'];
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => Promise.all(CORE.map(u => c.add(new Request(u, { cache: 'reload' })).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('dure-v') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

const put = (req, res) => { if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(V).then(c => c.put(req, copy)).catch(() => {}) } return res };
const timeout = (p, ms) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(new Error('slow')), ms))]);

self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const u = new URL(req.url);
  /* pages: the newest version when the network answers in time, this device's copy otherwise */
  if (req.mode === 'navigate' && u.origin === location.origin) {
    const key = new Request(u.origin + u.pathname);   // ?seed=… and the like share one copy
    e.respondWith(timeout(fetch(req), 4000).then(r => put(key, r)).catch(() => caches.match(key).then(r => r || caches.match('/m.html')).then(r => r || Response.error())));
    return;
  }
  /* our own files: answer from this device at once, refresh in the background */
  if (u.origin === location.origin) {
    if (u.pathname.endsWith('/sw.js')) return;
    e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => {
      const net = fetch(req).then(r => put(req, r)).catch(() => hit);
      return hit || net;
    }));
    return;
  }
  /* web fonts: kept once fetched (the stylesheet is fetched with CORS so it may be stored and served to any page) */
  if (FONT_HOSTS.includes(u.hostname)) {
    e.respondWith(caches.match(req.url).then(hit => hit || fetch(req.url, { mode: 'cors', credentials: 'omit' }).then(r => put(req.url, r)).catch(() => fetch(req))));
    return;
  }
  /* everything else (AI models on Hugging Face, script CDNs): untouched */
});
