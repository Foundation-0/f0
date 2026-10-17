/* Witness Map page: renders the map, the readout and the number twin from physics.js (window.WM). */
(function () {
  'use strict';
  const W = window.WM; if (!W) return;
  const { C, ENVS, OBJECTS, rates, BH_M, RS } = W;
  const $ = id => document.getElementById(id);
  const esc = s => (window.F0 && F0.esc) ? F0.esc(s) : String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // ---------- formatting ----------
  const minus = s => String(s).replace('-', '−');
  function pow10(x) {
    if (!isFinite(x)) return '∞';
    if (x === 0) return '0';
    const e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e);
    if (e >= -2 && e <= 3) return x >= 100 ? Math.round(x).toLocaleString('en-US') : String(Number(x.toPrecision(2)));
    const ms = m.toFixed(1).replace(/\.0$/, '');
    return (ms === '1' ? '' : ms + '×') + '10<sup>' + minus(e) + '</sup>';
  }
  function order(x) {
    if (x === 0) return '0';
    const e = Math.round(Math.log10(x));
    return e === 0 ? '1' : e === 1 ? '10' : '10<sup>' + minus(e) + '</sup>';
  }
  const p2 = v => Number(v.toPrecision(2)).toLocaleString('en-US', { maximumSignificantDigits: 2 });
  function fmtLen(m) {
    const n = (v, u) => (v >= 100 ? Math.round(v).toLocaleString('en-US') : p2(v)) + ' ' + u;
    if (m < 1e-6) return n(m * 1e9, 'nm');
    if (m < 1e-3) return n(m * 1e6, 'µm');
    if (m < 1) return n(m * 1e3, 'mm');
    if (m < 1e3) return n(m, 'm');
    if (m < 1e10) return n(m / 1e3, 'km');
    if (m < 9.46e14) return n(m / C.au, 'AU');
    if (m < C.kpc) return n(m / C.ly, 'light-years');
    return n(m / C.kpc, 'kpc');
  }
  const YEAR = 3.156e7, AGE = 4.35e17;
  function fmtTime(s) {
    if (!isFinite(s)) return 'never';
    if (s < 1e-12) return pow10(s) + ' s';
    if (s < 1e-9) return p2(s * 1e12) + ' ps';
    if (s < 1e-6) return p2(s * 1e9) + ' ns';
    if (s < 1e-3) return p2(s * 1e6) + ' µs';
    if (s < 1) return p2(s * 1e3) + ' ms';
    if (s < 120) return p2(s) + ' s';
    if (s < 7200) return p2(s / 60) + ' min';
    if (s < 2 * 86400) return p2(s / 3600) + ' hours';
    if (s < YEAR) return p2(s / 86400) + ' days';
    if (s < 1e4 * YEAR) return Math.round(s / YEAR).toLocaleString('en-US') + ' years';
    return pow10(s / YEAR) + ' years';
  }
  const fmtMass = kg => pow10(kg) + ' kg';
  const verdict = Wn => { if (Wn === 0) return ['none', 'Nothing watches it'];
    const l = Math.log10(Wn); return l < -1 ? ['wave', 'Wave wins'] : l > 1 ? ['watch', 'Witnesses win'] : ['edge', 'At the line']; };

  // ---------- state ----------
  const state = { lgap: W.DEFAULT_LOG_GAP, env: 'natural', bh: false, bhR: 10, sel: 'bigmol' };
  const PRESETS = [
    { lg: -9, t: '1 nm' }, { lg: W.DEFAULT_LOG_GAP, t: '250 nm' }, { lg: -3, t: '1 mm' },
    { lg: 0, t: '1 m' }, { lg: Math.log10(1.274e7), t: 'Earth’s width' }, { lg: Math.log10(C.kpc), t: '1 kpc' },
  ];
  const BH_OPTS = [3, 10, 100, 1e4, 1e6, 1e8];
  const sup = n => String(n).split('').map(c => ({ '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹' }[c] || c)).join('');

  const gap = $('wm-gap'), gapOut = $('wm-gap-out'), seg = $('wm-presets'), envSel = $('wm-env'), bhBox = $('wm-bh'), bhSel = $('wm-bh-dist');
  PRESETS.forEach(p => { const b = document.createElement('button'); b.type = 'button'; b.textContent = p.t; b.dataset.lg = p.lg; b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', () => { state.lgap = p.lg; gap.value = p.lg; update(); }); seg.appendChild(b); });
  envSel.innerHTML = '<option value="natural">Each in its natural home</option>' + Object.keys(ENVS).map(k => '<option value="' + k + '">Everything in: ' + esc(ENVS[k].name) + '</option>').join('');
  bhSel.innerHTML = BH_OPTS.map(r => { const d = r * RS, far = d / C.ly;
    const where = far >= 0.1 ? p2(far) + ' light-years' : p2(d / C.au) + ' AU';
    return '<option value="' + r + '">' + (r >= 1e4 ? '10' + sup(Math.round(Math.log10(r))) : r) + ' horizon radii (' + where + ')</option>'; }).join('');
  bhSel.value = '10';
  gap.addEventListener('input', () => { state.lgap = parseFloat(gap.value); update(); });
  envSel.addEventListener('change', () => { state.env = envSel.value; update(); });
  bhBox.addEventListener('change', () => { state.bh = bhBox.checked; bhSel.disabled = !state.bh; update(); });
  bhSel.addEventListener('change', () => { state.bhR = parseFloat(bhSel.value); update(); });

  // ---------- rows ----------
  const rowsEl = $('wm-rows'), rowEls = {};
  let last = [];
  OBJECTS.forEach(o => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'wm-row'; b.setAttribute('aria-pressed', 'false');
    b.innerHTML = '<span class="wm-name"><span class="wm-n">' + esc(o.name) + (o.seen ? ' <span class="wm-seen">seen as a wave</span>' : '') +
      '</span><span class="wm-m">' + fmtMass(o.m) + '</span></span><span class="wm-track" aria-hidden="true"><span class="wm-zero"></span><span class="wm-dot"></span></span><span class="wm-val"></span>';
    b.addEventListener('click', () => { state.sel = o.id; update(); });
    const tip = (x, y) => { if (!window.F0 || !F0.tip) return; const r = last.find(z => z.o.id === o.id); if (r) F0.tip.show(tipHTML(r), x, y); };
    b.addEventListener('mousemove', e => tip(e.clientX, e.clientY));
    b.addEventListener('mouseleave', () => window.F0 && F0.tip && F0.tip.hide());
    b.addEventListener('focus', () => { const rc = b.getBoundingClientRect(); tip(rc.left + rc.width * 0.6, rc.top); });
    b.addEventListener('blur', () => window.F0 && F0.tip && F0.tip.hide(true));
    rowsEl.appendChild(b); rowEls[o.id] = b;
  });
  function topWitness(r) { return r.parts.slice().sort((a, b) => b.rate - a.rate)[0]; }
  function tipHTML({ o, env, r }) {
    const t = topWitness(r), v = verdict(r.W)[1];
    return '<p class="tip-k">' + esc(o.name) + '</p><p class="tip-t">' + v + (r.W > 0 ? ' · W ≈ ' + order(r.W) : '') + '</p>' +
      '<div class="tip-rows"><div class="tip-row"><span>Wave clock</span><span class="tip-v">' + fmtTime(r.tWave) + '</span></div>' +
      '<div class="tip-row"><span>Witness clock</span><span class="tip-v">' + fmtTime(r.tau) + '</span></div></div>' +
      '<p class="tip-note">' + esc(env.name) + (t ? ' · main witness: ' + esc(t.label.toLowerCase()) : ' · no witnesses') + '</p>';
  }

  function compute() {
    const dx = Math.pow(10, state.lgap), bh = state.bh ? { M: BH_M, b: state.bhR * RS } : null;
    return OBJECTS.map(o => { const env = ENVS[state.env === 'natural' ? o.home : state.env]; return { o, env, r: rates(o, env, dx, bh), dx }; });
  }

  function update() {
    const dx = Math.pow(10, state.lgap);
    gapOut.textContent = fmtLen(dx).replace(/ /g, ' ');
    gap.setAttribute('aria-valuetext', fmtLen(dx).replace(/ /g, ' '));
    seg.querySelectorAll('button').forEach(c => c.setAttribute('aria-pressed', Math.abs(parseFloat(c.dataset.lg) - state.lgap) < 0.02 ? 'true' : 'false'));
    const res = last = compute();
    const logs = res.filter(x => x.r.W > 0).map(x => Math.log10(x.r.W));
    let lo = Math.max(-60, Math.min(-20, ...logs)), hi = Math.min(200, Math.max(20, ...logs));
    const step = (hi - lo) > 120 ? 40 : 20;
    lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step;
    const pct = v => ((Math.min(hi, Math.max(lo, v)) - lo) / (hi - lo)) * 100, z = pct(0);
    rowsEl.style.setProperty('--z', z + '%');
    let ax = '<span class="wm-reg wave">◀ wave</span><span class="wm-reg watch" style="left:' + z + '%">witnessed ▶</span><span class="wm-zero"></span>';
    for (let t = lo; t <= hi; t += step) ax += '<span class="wm-tick" style="left:' + pct(t) + '%">' + order(Math.pow(10, t)) + '</span>';
    $('wm-axis').innerHTML = ax; $('wm-axis').style.setProperty('--z', z + '%');
    res.forEach(({ o, r }) => {
      const el = rowEls[o.id], dot = el.querySelector('.wm-dot'), val = el.querySelector('.wm-val');
      el.setAttribute('aria-pressed', state.sel === o.id ? 'true' : 'false');
      const [cls, txt] = verdict(r.W);
      el.dataset.v = cls;
      if (r.W === 0) { dot.style.left = '0%'; val.textContent = 'no witnesses'; el.setAttribute('aria-label', o.name + ': no witnesses. Show details'); return; }
      const lw = Math.log10(r.W);
      dot.dataset.clip = lw < lo ? 'l' : lw > hi ? 'r' : '';
      dot.style.left = pct(lw) + '%';
      val.innerHTML = order(r.W);
      el.setAttribute('aria-label', o.name + ': W about 10 to the ' + Math.round(lw) + ', ' + txt.toLowerCase() + '. Show details');
    });
    renderDetail(res.find(x => x.o.id === state.sel) || res[0]);
    renderTwin(res);
    $('wm-cap').textContent = 'Gap ' + fmtLen(dx).replace(/ /g, ' ') + ', ' + (state.env === 'natural' ? 'each object in its natural home' : 'everything in: ' + ENVS[state.env].name.toLowerCase()) +
      (state.bh ? ', with the black hole at ' + state.bhR.toLocaleString('en-US') + ' horizon radii' : '') + '. ' +
      res.filter(x => x.r.W > 0 && x.r.W < 1 || x.r.W === 0).length + ' of ' + res.length + ' objects are on the wave side.';
  }

  function renderDetail({ o, env, r, dx }) {
    const [cls, txt] = verdict(r.W), parts = r.parts.slice().sort((a, b) => b.rate - a.rate);
    const max = parts.length ? parts[0].rate / r.gamma : 1;
    let explain;
    if (r.W === 0) explain = o.dark ? 'No light bounces off it and it does not collide with gas. Only gravity touches it, and with the black hole off nothing in this model records where it is. Its wave can spread as long as it likes.' : 'Nothing in these surroundings interacts with it.';
    else if (r.W < 0.1) explain = 'Its wave crosses the gap about ' + order(1 / r.W) + ' times faster than the surroundings can record which side it is on.';
    else if (r.W > 10) explain = 'The surroundings record which side it is on about ' + order(r.W) + ' times before its wave could spread across the gap.';
    else explain = 'The two clocks run at about the same speed. A small change to the gap or the surroundings tips it either way.';
    const bhPart = r.parts.find(p => p.label === 'Black hole horizon (gravity)');
    let bh = '';
    if (state.bh) bh = r.bhNote ? '<p class="wm-note">' + r.bhNote + '</p>' : '<p class="wm-note">The black hole horizon alone records it once every ' + fmtTime(1 / bhPart.rate) + (1 / bhPart.rate > AGE ? ', far longer than the age of the universe' : '') + '.</p>';
    $('wm-detail').innerHTML =
      '<div class="wm-dh"><h3 class="wm-dt">' + esc(o.name) + '</h3><span class="wm-verdict" data-v="' + cls + '">' + txt + (r.W > 0 ? ' · W ≈ ' + order(r.W) : '') + '</span></div>' +
      '<p class="wm-ex">' + explain + '</p>' +
      '<dl class="kv wm-kv"><div><dt>Wave clock</dt><dd>' + fmtTime(r.tWave) + '<small>to spread across ' + fmtLen(dx) + '</small></dd></div>' +
      '<div><dt>Witness clock</dt><dd>' + fmtTime(r.tau) + '<small>until a record of its place exists</small></dd></div>' +
      '<div><dt>Surroundings</dt><dd class="wm-env">' + esc(env.name) + '<small>' + fmtMass(o.m) + (o.a ? ' · ' + fmtLen(2 * o.a) + ' across' : '') + '</small></dd></div></dl>' +
      (parts.length ? '<div class="wm-who"><p class="ctrl-label">Who is watching // share of records</p>' + parts.map(p => { const s = p.rate / r.gamma;
        return '<div class="wm-wr"><span>' + esc(p.label) + '</span><span class="wm-bar"><i style="width:' + Math.max(0.6, s / max * 100) + '%"></i></span><span class="wm-pc">' + (s >= 0.001 ? p2(s * 100) + '%' : '&lt;0.1%') + '</span></div>'; }).join('') + '</div>' : '') +
      bh + (o.seen ? '<p class="wm-note">Seen behaving as a wave in experiments (' + esc(o.seen) + '), at gaps of a few hundred nanometres or less.</p>' : '');
  }

  function renderTwin(res) {
    $('wm-twin-cap').textContent = 'At the settings above: gap ' + fmtLen(Math.pow(10, state.lgap)).replace(/ /g, ' ');
    $('wm-twin-body').innerHTML = res.map(({ o, env, r }) => { const t = topWitness(r);
      return '<tr><th scope="row">' + esc(o.name) + '</th><td>' + esc(env.name) + '</td><td class="n">' + fmtTime(r.tWave) + '</td><td class="n">' + fmtTime(r.tau) + '</td><td class="n">' + (r.W === 0 ? '0' : order(r.W)) + '</td><td>' + (t ? esc(t.label) : 'none') + '</td></tr>'; }).join('');
  }

  gap.value = state.lgap; envSel.value = state.env; bhBox.checked = false; bhSel.disabled = true;
  update();
})();
