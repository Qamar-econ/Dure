/* Dure photo grader in the browser: MobileNetV3-Small + trained head, exported to ONNX (3.7 MB).
   Runs on the device with onnxruntime-web (WebAssembly). No photo leaves the browser.
   Preprocessing matches training: shorter side to 232 px, centre crop 224, ImageNet mean/std. */
const Grader = (() => {
  const MODEL = 'grader.onnx', THR = 0.60, NOVEL = 0.2988,   // novelty: share of the photo's features the training photos can't explain (98th percentile of validation photos; ai/photo/ood_export.py)
        CDN = 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/';
  let sess = null, loading = null;
  const loadOrt = () => new Promise((res, rej) => {
    if (window.ort) return res();
    const s = document.createElement('script'); s.src = CDN + 'ort.min.js'; s.onload = res; s.onerror = () => rej(new Error('runtime')); document.head.appendChild(s);
  });
  function load() {
    if (sess) return Promise.resolve(sess);
    if (!loading) loading = (async () => {
      await loadOrt(); ort.env.wasm.wasmPaths = CDN; ort.env.wasm.numThreads = 1;
      sess = await ort.InferenceSession.create(MODEL, { executionProviders: ['wasm'] }); return sess;
    })().catch(e => { loading = null; throw e; });
    return loading;
  }
  const imgOf = src => new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
  function tensor(img) {
    const c = document.createElement('canvas'); c.width = c.height = 224; const x = c.getContext('2d');
    const w = img.naturalWidth || img.width, h = img.naturalHeight || img.height, k = 232 / Math.min(w, h), side = 224 / k;
    x.drawImage(img, (w - side) / 2, (h - side) / 2, side, side, 0, 0, 224, 224);
    const d = x.getImageData(0, 0, 224, 224).data, f = new Float32Array(3 * 224 * 224), M = [.485, .456, .406], S = [.229, .224, .225];
    for (let i = 0; i < 224 * 224; i++) for (let ch = 0; ch < 3; ch++) f[ch * 50176 + i] = (d[i * 4 + ch] / 255 - M[ch]) / S[ch];
    return new ort.Tensor('float32', f, [1, 3, 224, 224]);
  }
  const pack = (p, ms, engine, nov) => { const i = p.indexOf(Math.max(...p)), novel = nov != null && nov > NOVEL;
    const pc = v => Math.min(99, Math.max(1, Math.round(v * 100)));   // never show 0% or 100%: the model is never that certain
    return { probs: p.map(pc), grade: 'ABC'[i], conf: pc(p[i]), novel, novelty: nov == null ? null : Math.round(nov * 100), sure: !novel && p[i] >= THR, ms: ms == null ? null : Math.round(ms), engine }; };
  async function grade(src, cached) {
    const t0 = performance.now();
    try { const s = await load(), im = await imgOf(src), t1 = performance.now(), out = await s.run({ image: tensor(im) });
      return { ...pack([...out.probs.data], performance.now() - t1, 'model', out.novelty.data[0]), loadMs: Math.round(t1 - t0) }; }
    catch (e) { if (cached) return pack(cached.probs, null, 'cached', cached.novelty); return { probs: null, grade: null, conf: 0, sure: false, engine: 'unavailable' }; }
  }
  return { load, grade, THR, NOVEL };
})();
