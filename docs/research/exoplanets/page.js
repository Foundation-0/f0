/* Exoplanets page: seven figures, vanilla JS, no dependencies.
   0 make a transit (canvas; a limb-darkened star, the light curve from the exact covered light)
   1 sky map of the counted candidates (canvas; Hammer projection, or period against radius)
   2 find the heartbeat (canvas; real TESS light curve of TIC 4206066, live box search)
   3 why stacking works (canvas + SVG; signal-to-noise against transits stacked)
   4 turn the sky upside down (canvas; L 98-59 flipped, a false alarm, measured rates)
   5 funnel tooltips
   6 the next transits (canvas + list; from transits.json, computed in the browser so they never go stale)
   Data: candidates.json and lightcurves.json in this folder, derived from github.com/eumemic/exoplanets
   (results and data CC BY 4.0, eumemic): candidates.json is rebuilt by scripts/exoplanets_data.py and names
   its commit and date (58c6318, 14 Oct 2026); lightcurves.json is from da72261 (its source is unchanged since).
   The sky map's counts (title, tiers, table) are rendered from candidates.json; the HTML keeps a copy for readers
   without JavaScript (scripts/prerender.mjs). Colours come from tokens via F0.css; every canvas redraws
   on F0.onTheme. Nothing moves until a visitor presses a button, and nothing moves with motion off. */
(function () {
  'use strict';
  var F0 = window.F0;
  if (!F0) return;
  var $ = function (id) { return document.getElementById(id); };
  var SVGNS = 'http://www.w3.org/2000/svg';
  var DAY = 86400;
  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function hexRGB(h) {
    h = String(h || '#888888').trim();
    if (h.charAt(0) === '#' && h.length === 4) h = '#' + h[1] + h[1] + h[2] + h[2] + h[3] + h[3];
    var n = parseInt(h.slice(1, 7), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function rgba(hex, a) { var c = hexRGB(hex); return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + a + ')'; }
  function fmt(x, d) { return Number(x).toFixed(d); }
  function grp(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function pressed(b, on) { b.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  function mono(px, w) { return (w || 500) + ' ' + px + 'px ' + (F0.css('--f-mono') || 'monospace'); }
  function sans(px, w) { return (w || 500) + ' ' + px + 'px ' + (F0.css('--f-sans') || 'sans-serif'); }
  function colors() {
    return { acc: F0.css('--acc-exoplanets'), ink: F0.css('--ink'), ink2: F0.css('--ink-2'), ink3: F0.css('--ink-3'),
      bg: F0.css('--bg'), bg1: F0.css('--bg-1'), bg2: F0.css('--bg-2'), bg3: F0.css('--bg-3'), grid: F0.css('--grid'),
      line: F0.css('--line'), lineui: F0.css('--line-ui'), dig: F0.css('--dig'), bio: F0.css('--bio'), focus: F0.css('--focus'),
      dark: F0.theme() === 'dark' };
  }
  function decode(o) {
    var n = o.dt.length, t = new Float64Array(n), f = new Float32Array(n), acc = 0;
    for (var i = 0; i < n; i++) { acc += o.dt[i]; t[i] = o.t0 + acc * 1e-4; f[i] = o.f[i]; }
    return { t: t, f: f };
  }
  function shape(ctx, tier, x, y, r) {
    ctx.beginPath();
    if (tier === 0) ctx.arc(x, y, r, 0, Math.PI * 2);
    else if (tier === 1) { var s = r * .88; ctx.rect(x - s, y - s, 2 * s, 2 * s); }
    else if (tier === 2) { ctx.moveTo(x, y - r * 1.15); ctx.lineTo(x + r * 1.08, y + r * .78); ctx.lineTo(x - r * 1.08, y + r * .78); ctx.closePath(); }
    else { ctx.moveTo(x, y - r * 1.18); ctx.lineTo(x + r * 1.18, y); ctx.lineTo(x, y + r * 1.18); ctx.lineTo(x - r * 1.18, y); ctx.closePath(); }
  }
  var TIERS = ['A', 'B', 'N', 'L1'];
  var TIER_TXT = ['more than one signal on the star', 'one signal, clean field', 'a neighbour within 15″, cleared statistically', 'weaker signal picked by a classifier'];
  function tipAt(el, html) { var r = el.getBoundingClientRect(); F0.tip.show(html, r.left + r.width / 2, r.top + r.height / 2); }

  /* =========================================================================
     0. Make a transit: a limb-darkened star, a planet disc, and the light curve from the exact covered light
     ========================================================================= */
  (function makeTransit() {
    var cv = $('mt-canvas'); if (!cv) return;
    var C = F0.canvas(cv), U1 = .5, U2 = .2, RE = 0.0091577; // Earth's radius in Sun radii
    var F0T = Math.PI * (1 - U1 / 3 - U2 / 6); // the whole star's light
    function I(r) { var mu = Math.sqrt(Math.max(0, 1 - r * r)); return 1 - U1 * (1 - mu) - U2 * (1 - mu) * (1 - mu); }
    /* the light hidden by a disc of radius k whose centre is d from the star's centre (star radius 1):
       the sum over rings of the star of (ring brightness) x (length of the ring inside the disc) */
    function blocked(k, d) {
      var r0 = Math.max(0, d - k), r1 = Math.min(1, d + k); if (r1 <= r0) return 0;
      var n = 160, h = (r1 - r0) / n, sum = 0;
      for (var i = 0; i <= n; i++) {
        var r = r0 + i * h, L;
        if (r <= 0) L = 0;
        else if (r <= k - d) L = 2 * Math.PI * r; // the whole ring is covered
        else { var c = (r * r + d * d - k * k) / (2 * r * Math.max(d, 1e-12)); L = c >= 1 ? 0 : c <= -1 ? 2 * Math.PI * r : 2 * r * Math.acos(c); }
        sum += (i === 0 || i === n ? 1 : i % 2 ? 4 : 2) * I(Math.min(r, 1)) * L;
      }
      return sum * h / 3 / F0T;
    }
    var SUN = { name: 'sun', Rs: 1, P: 365.25, aR: 215.03, label: 'A Sun-like star · orbit like Earth’s' };
    var TIC = { name: 'tic', P: 3.18277, label: 'TIC 4206066 · 3.18-day orbit' };
    var st = { rp: 3.88, b: .3, x: 0, star: SUN, curve: null };
    function k() { return st.star === TIC ? st.kTic : st.rp * RE / st.star.Rs; }
    function speed() { return 2 * Math.PI * st.star.aR / st.star.P / 24; } // star radii per hour
    function chord() { var kk = k(); return Math.sqrt(Math.max(0, (1 + kk) * (1 + kk) - st.b * st.b)); }
    function T14() { return 2 * chord() / speed(); } // hours, first to last contact
    function half() { var kk = k(); return Math.max(chord(), Math.sqrt((1 + kk) * (1 + kk) - Math.min(st.b * st.b, .81))) * 1.45; } // half-width of the shown path, star radii
    function build() { // the curve along the whole shown path
      var kk = k(), H = half(), N = 240, c = [];
      for (var i = 0; i <= N; i++) { var x = -H + 2 * H * i / N; c.push([x, blocked(kk, Math.hypot(x, st.b))]); }
      st.curve = c; st.deep = c.reduce(function (m, p) { return Math.max(m, p[1]); }, 0);
    }
    function shapeTxt() {
      var kk = k();
      if (st.b >= 1 + kk) return ['none', 'No transit: the planet passes above the star and blocks nothing.'];
      if (st.b > 1 - kk) return ['weak', 'V-shaped and shallow: a grazing transit, where the planet never fully enters the disc. Two stars eclipsing each other edge-on often look like this, which is one way they fool a search.'];
      return ['good', 'U-shaped: steep sides as the planet enters and leaves, then a rounded floor, deepest in the middle because the star is brightest there.'];
    }
    function ppm(v) { return Math.round(v * 1e6).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
    function draw() {
      if (!st.curve || !C.w) return;
      var ctx = C.ctx, c = colors(), W0 = C.w, H0 = C.h, kk = k(), Hw = half();
      ctx.clearRect(0, 0, W0, H0);
      var narrow = W0 < 520, top = 34, splitY = Math.round(H0 * (narrow ? .5 : .54)), Rpx = Math.min((splitY - top - 10) / 2, W0 * .2), cx = W0 / 2, cy = top + (splitY - top) / 2;
      // the star: brightness from the limb-darkening rule, as a radial gradient
      var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Rpx), ac = hexRGB(c.acc), sc = c.dark ? c.acc : '#' + ac.map(function (v) { return ('0' + Math.round(v + (255 - v) * .45).toString(16)).slice(-2); }).join(''); // a lighter star on paper
      for (var i = 0; i <= 10; i++) { var r = i / 10; g.addColorStop(r, rgba(sc, Math.max(0, I(Math.min(r, .999))))); }
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, Rpx, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = rgba(c.ink3, .5); ctx.lineWidth = 1; ctx.stroke();
      // the path and the planet
      var px = cx + st.x * Hw * Rpx, py = cy - st.b * Rpx;
      ctx.setLineDash([3, 4]); ctx.strokeStyle = rgba(c.ink3, .7); ctx.beginPath(); ctx.moveTo(cx - Hw * Rpx, py); ctx.lineTo(cx + Hw * Rpx, py); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = c.ink; ctx.beginPath(); ctx.arc(px, py, Math.max(1.5, kk * Rpx), 0, Math.PI * 2); ctx.fill();
      if (kk * Rpx < 4) { ctx.strokeStyle = c.ink; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(px, py, 7, 0, Math.PI * 2); ctx.stroke(); } // a ring, so a planet smaller than a few pixels can still be found
      // the light curve
      var L = narrow ? 46 : 58, R0 = W0 - 14, T = splitY + 22, B = H0 - 26;
      var depthMax = Math.max(st.deep, 100e-6) * 1.18;
      var X = function (x) { return L + (x + Hw) / (2 * Hw) * (R0 - L); }, Y = function (v) { return T + v / depthMax * (B - T); };
      ctx.font = mono(11); ctx.fillStyle = c.ink2; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(narrow ? 'BRIGHTNESS · PPM' : 'THE STAR’S BRIGHTNESS · PPM BELOW NORMAL', L, splitY + 12);
      var step = niceStep(depthMax * 1e6);
      ctx.strokeStyle = c.grid; ctx.fillStyle = c.ink3; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      for (var v = 0; v <= depthMax * 1e6; v += step) { ctx.beginPath(); ctx.moveTo(L, Y(v / 1e6)); ctx.lineTo(R0, Y(v / 1e6)); ctx.stroke(); ctx.fillText(v === 0 ? '0' : '−' + ppm(v / 1e6), L - 6, Y(v / 1e6)); }
      // hours along the bottom
      var vh = speed(), hrs = Hw / vh, hs = niceStep(hrs * 2 / 4);
      ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      for (var t = -Math.floor(hrs / hs) * hs; t <= hrs + 1e-9; t += hs) ctx.fillText((t > 0 ? '+' : t < 0 ? '−' : '') + fmt(Math.abs(t), hs < 1 ? 1 : 0) + (Math.abs(t - Math.floor(hrs / hs) * hs) < 1e-9 ? ' h' : ''), X(t * vh), H0 - 8);
      // whole curve faint, the part up to the planet solid
      ctx.lineJoin = 'round';
      ctx.strokeStyle = rgba(c.acc, .3); ctx.lineWidth = 2; ctx.beginPath();
      st.curve.forEach(function (p, j) { var xx = X(p[0]), yy = Y(p[1]); if (j) ctx.lineTo(xx, yy); else ctx.moveTo(xx, yy); }); ctx.stroke();
      ctx.strokeStyle = c.acc; ctx.lineWidth = 2.2; ctx.beginPath();
      var xNow = st.x * Hw, last = null;
      st.curve.forEach(function (p, j) { if (p[0] > xNow) return; var xx = X(p[0]), yy = Y(p[1]); if (j) ctx.lineTo(xx, yy); else ctx.moveTo(xx, yy); last = p; });
      var dNow = blocked(kk, Math.hypot(xNow, st.b));
      ctx.lineTo(X(xNow), Y(dNow)); ctx.stroke();
      ctx.fillStyle = c.bg1; ctx.beginPath(); ctx.arc(X(xNow), Y(dNow), 5.5, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = c.acc; ctx.beginPath(); ctx.arc(X(xNow), Y(dNow), 4, 0, Math.PI * 2); ctx.fill();
      // the simple rule, for comparison
      if (kk < 1) { ctx.setLineDash([4, 4]); ctx.strokeStyle = c.ink2; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(L, Y(kk * kk)); ctx.lineTo(R0, Y(kk * kk)); ctx.stroke(); ctx.setLineDash([]);
        ctx.font = mono(11); ctx.textAlign = 'right'; ctx.textBaseline = 'alphabetic'; ctx.lineWidth = 4; ctx.strokeStyle = c.bg1; var lt = narrow ? 'simple rule' : 'the simple rule, planet area ÷ star area'; ctx.strokeText(lt, R0 - 2, Y(kk * kk) - 5); ctx.fillStyle = c.ink2; ctx.fillText(lt, R0 - 2, Y(kk * kk) - 5); }
    }
    function niceStep(span) { var p = Math.pow(10, Math.floor(Math.log10(span))), m = span / p; return (m < 1.5 ? .5 : m < 3.5 ? 1 : m < 7.5 ? 2 : 5) * p; }
    function read() {
      var kk = k(), sh = shapeTxt();
      $('mt-r-p').innerHTML = st.star === TIC ? 'R<sub>p</sub> &divide; R<sub>&lowast;</sub> = ' + fmt(kk, 4) : fmt(st.rp, 2) + ' &times; Earth <small>R<sub>p</sub> &divide; R<sub>&lowast;</sub> = ' + fmt(kk, 4) + '</small>';
      $('mt-r-d').textContent = ppm(kk * kk) + ' ppm';
      $('mt-r-dd').textContent = st.b >= 1 + kk ? '0 ppm' : ppm(st.deep) + ' ppm';
      $('mt-r-t').textContent = st.b >= 1 + kk ? 'none' : fmt(T14(), 1) + ' h';
      var sd = $('mt-r-s'); sd.textContent = sh[1]; sd.className = sh[0];
      $('mt-rp-out').textContent = st.star === TIC ? '—' : fmt(st.rp, 2) + ' × Earth';
      $('mt-b-out').textContent = 'b = ' + fmt(st.b, 2);
      $('mt-corner').textContent = st.star.label;
      document.querySelectorAll('[data-rp]').forEach(function (b) { pressed(b, st.star === SUN && Math.abs(+b.dataset.rp - st.rp) < .005); });
    }
    function setX(x) { st.x = Math.max(-1, Math.min(1, x)); $('mt-x').value = String(st.x); var h = st.x * half() / speed(); $('mt-x-out').textContent = Math.abs(h) < .05 ? 'mid-transit' : (h < 0 ? '−' : '+') + fmt(Math.abs(h), 1) + ' h'; $('mt-x').setAttribute('aria-valuetext', $('mt-x-out').textContent + ' from mid-transit'); draw(); }
    function all(say) { build(); read(); setX(st.x); if (say) $('mt-say').textContent = $('mt-r-s').textContent + ' Deepest point ' + $('mt-r-dd').textContent + ', lasting ' + $('mt-r-t').textContent + '.'; }
    $('mt-rp').addEventListener('input', function () { stop(); if (st.star === TIC) st.star = SUN; st.rp = +this.value; all(); });
    $('mt-b').addEventListener('input', function () { stop(); st.b = +this.value; all(); });
    $('mt-x').addEventListener('input', function () { stop(); setX(+this.value); });
    document.querySelectorAll('[data-rp]').forEach(function (b) { b.addEventListener('click', function () { stop(); st.star = SUN; st.rp = +b.dataset.rp; $('mt-rp').value = st.rp; all(true); }); });
    $('mt-graze').addEventListener('click', function () { stop(); st.b = Math.min(1.1, Math.round((1 - k() * .2) * 200) / 200); $('mt-b').value = st.b; all(true); });
    $('mt-tic').addEventListener('click', function () {
      stop();
      // the published signal: 398 ppm deep, 1.7 h long, a 3.18-day orbit; through the middle of the star
      st.star = TIC; st.b = 0; st.kTic = Math.sqrt(398e-6);
      TIC.Rs = 1; TIC.aR = (1 + st.kTic) / Math.sin(Math.PI * 1.7 / 24 / TIC.P);
      $('mt-b').value = 0; all(true);
    });
    // drag the planet, or move it with the arrow keys
    var drag = false;
    function xFromEvent(ev) { var r = cv.getBoundingClientRect(), W0 = C.w, Rpx = Math.min((Math.round(C.h * (W0 < 520 ? .5 : .54)) - 44) / 2, W0 * .2); return (ev.clientX - r.left - W0 / 2) / (half() * Rpx); }
    cv.addEventListener('pointerdown', function (ev) { drag = true; stop(); try { cv.setPointerCapture(ev.pointerId); } catch (e) {} setX(xFromEvent(ev)); });
    cv.addEventListener('pointermove', function (ev) { if (drag) setX(xFromEvent(ev)); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) { cv.addEventListener(t, function () { drag = false; }); });
    cv.addEventListener('keydown', function (ev) {
      var d = ev.shiftKey ? .1 : .02;
      if (ev.key === 'ArrowLeft') { ev.preventDefault(); stop(); setX(st.x - d); } else if (ev.key === 'ArrowRight') { ev.preventDefault(); stop(); setX(st.x + d); }
    });
    // play: the planet crosses in about 5 seconds; with motion off, each press moves it a quarter of the way
    var playBtn = $('mt-play'), playTxt = $('mt-play-txt'), playing = false, lastT = 0;
    var loop = F0.loop(function (now) {
      if (!lastT) lastT = now;
      var dt = Math.min(.1, (now - lastT) / 1000); lastT = now;
      setX(st.x + dt * .4);
      if (st.x >= 1) stop();
    });
    function stop() { if (!playing) return; playing = false; loop.stop(); pressed(playBtn, false); sync(); $('mt-say').textContent = 'Stopped at ' + $('mt-x-out').textContent + '.'; }
    function sync() { playTxt.textContent = playing ? 'Pause' : F0.motion() ? 'Play' : 'Step'; playBtn.setAttribute('aria-label', playing ? 'Pause' : F0.motion() ? 'Play the transit' : 'Move the planet a quarter of the way'); }
    playBtn.addEventListener('click', function () {
      if (!F0.motion()) { setX(st.x >= 1 ? -1 : Math.min(1, Math.round((st.x + .5) * 4) / 4)); return; }
      if (playing) { stop(); return; }
      if (st.x >= .99) setX(-1);
      playing = true; lastT = 0; pressed(playBtn, true); sync(); loop.start();
    });
    F0.onMotion(function () { if (!F0.motion()) stop(); sync(); }); sync();
    F0.whenVisible(cv, null, stop);
    C.resize(draw); F0.onTheme(draw);
    // the numbers twin: three planets across a Sun-sized star
    var tb = $('mt-tbody');
    [['Earth', 1], ['Neptune', 3.88], ['Jupiter', 11.2]].forEach(function (pl) {
      var kk = pl[1] * RE, deep = blocked(kk, 0), dur = 2 * (1 + kk) / (2 * Math.PI * SUN.aR / SUN.P / 24), tr = document.createElement('tr');
      [pl[0], fmt(pl[1], 2), ppm(kk * kk), ppm(deep), fmt(dur, 1)].forEach(function (x, j) { var td = document.createElement('td'); td.textContent = x; if (j) td.className = 'n'; tr.appendChild(td); });
      tb.appendChild(tr);
    });
    all();
  })();

  var SKY = {}; // the sky map's hook for other figures: SKY.show(tic, period)
  /* =========================================================================
     1. Sky map of the counted candidates
     ========================================================================= */
  (function sky() {
    var cv = $('sky-canvas'); if (!cv) return;
    var C = F0.canvas(cv), D = null, view = 'sky', show = [true, true, true, true], sel = -1, hov = -1, order = [];
    var EPS = 23.4392911 * Math.PI / 180, R2 = Math.SQRT2;
    function hammer(raDeg, decDeg) {
      var ra = raDeg > 180 ? raDeg - 360 : raDeg, lam = -ra * Math.PI / 180, phi = decDeg * Math.PI / 180;
      var z = Math.sqrt(1 + Math.cos(phi) * Math.cos(lam / 2));
      return [2 * R2 * Math.cos(phi) * Math.sin(lam / 2) / z, R2 * Math.sin(phi) / z];
    }
    function eclToEq(l) { // ecliptic longitude (rad), latitude 0
      return [((Math.atan2(Math.sin(l) * Math.cos(EPS), Math.cos(l)) * 180 / Math.PI) + 360) % 360, Math.asin(Math.sin(EPS) * Math.sin(l)) * 180 / Math.PI];
    }
    function galToEq(l, b) { // degrees
      var aN = 192.85948 * Math.PI / 180, dN = 27.12825 * Math.PI / 180, lN = 122.93192 * Math.PI / 180;
      l *= Math.PI / 180; b *= Math.PI / 180;
      var sd = Math.sin(dN) * Math.sin(b) + Math.cos(dN) * Math.cos(b) * Math.cos(lN - l);
      var y = Math.cos(b) * Math.sin(lN - l), x = Math.cos(dN) * Math.sin(b) - Math.sin(dN) * Math.cos(b) * Math.cos(lN - l);
      return [((aN + Math.atan2(y, x)) * 180 / Math.PI + 360) % 360, Math.asin(sd) * 180 / Math.PI];
    }
    function eclLat(ra, dec) {
      ra *= Math.PI / 180; dec *= Math.PI / 180;
      return Math.asin(Math.sin(dec) * Math.cos(EPS) - Math.cos(dec) * Math.sin(EPS) * Math.sin(ra)) * 180 / Math.PI;
    }
    var geo = null; // cached curves in unit coords
    function buildGeo() {
      function curve(fn, n) { var a = []; for (var i = 0; i <= n; i++) a.push(fn(i / n)); return a; }
      geo = { mer: [], par: [] };
      for (var h = 0; h < 24; h += 2) geo.mer.push(curve(function (u) { return hammer(h * 15 + (h === 12 ? -1e-6 : 0), -90 + 180 * u); }, 60));
      geo.mer.push(curve(function (u) { return hammer(180 + 1e-6, -90 + 180 * u); }, 60));
      [-60, -30, 0, 30, 60].forEach(function (d) { geo.par.push(curve(function (u) { return hammer(180.0001 + 359.9998 * u, d); }, 120)); });
      geo.outline = curve(function (u) { var a = u * Math.PI * 2; return [2 * R2 * Math.cos(a), R2 * Math.sin(a)]; }, 160);
      geo.ecl = curve(function (u) { var q = eclToEq(u * Math.PI * 2); return hammer(q[0], q[1]); }, 240);
      geo.gal = curve(function (u) { var q = galToEq(u * 360, 0); return hammer(q[0], q[1]); }, 240);
      geo.galU = curve(function (u) { var q = galToEq(u * 360, 10); return hammer(q[0], q[1]); }, 240);
      geo.galL = curve(function (u) { var q = galToEq(u * 360, -10); return hammer(q[0], q[1]); }, 240);
    }
    var M = {};
    function layout() {
      var W = C.w, H = C.h;
      if (view === 'sky') {
        var s = Math.min((W - 28) / (4 * R2), (H - 70) / (2 * R2));
        M = { s: s, cx: W / 2, cy: H / 2 + 8 };
      } else {
        M = { l: 46, r: 16, t: 56, b: 34 };
        M.pw = W - M.l - M.r; M.ph = H - M.t - M.b;
      }
    }
    function P2(u) { return [M.cx + u[0] * M.s, M.cy - u[1] * M.s]; }
    var PMIN = Math.log(.4), PMAX = Math.log(60), RMIN = Math.log(.7), RMAX = Math.log(25);
    function orbXY(i) {
      return [M.l + (Math.log(D.P[i]) - PMIN) / (PMAX - PMIN) * M.pw, M.t + (1 - (Math.log(D.rp[i]) - RMIN) / (RMAX - RMIN)) * M.ph];
    }
    function pos(i) { return view === 'sky' ? P2(D.u[i]) : orbXY(i); }
    function rad(i) { var k = Math.max(.62, Math.min(1, C.w / 600)); return (view === 'sky' ? 2.9 + Math.max(0, Math.min(1, (13.5 - D.tmag[i]) / 5.5)) * 2.3 : 3.6) * k; }
    function polyline(ctx, pts, breakJump) {
      ctx.beginPath();
      for (var i = 0; i < pts.length; i++) {
        var p = P2(pts[i]);
        if (i === 0 || (breakJump && Math.abs(pts[i][0] - pts[i - 1][0]) > 1)) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
      }
    }
    function draw() {
      if (!D) return;
      var ctx = C.ctx, W = C.w, H = C.h, c = colors();
      ctx.clearRect(0, 0, W, H);
      layout();
      ctx.lineWidth = 1;
      if (view === 'sky') {
        if (!geo) buildGeo();
        // ellipse fill
        polyline(ctx, geo.outline); ctx.closePath(); ctx.fillStyle = rgba(c.bg2, c.dark ? .55 : .7); ctx.fill();
        // Milky Way band
        ctx.save(); polyline(ctx, geo.outline); ctx.closePath(); ctx.clip();
        ctx.strokeStyle = rgba(c.dig, c.dark ? .10 : .09); ctx.lineWidth = Math.max(10, M.s * .32); ctx.lineCap = 'butt';
        polyline(ctx, geo.gal, true); ctx.stroke();
        ctx.restore();
        ctx.lineWidth = 1; ctx.strokeStyle = c.grid;
        geo.mer.forEach(function (m) { polyline(ctx, m); ctx.stroke(); });
        geo.par.forEach(function (m) { polyline(ctx, m); ctx.stroke(); });
        ctx.strokeStyle = c.lineui; polyline(ctx, geo.outline); ctx.closePath(); ctx.stroke();
        // galactic plane centre line and ecliptic
        ctx.strokeStyle = rgba(c.dig, .55); ctx.lineWidth = 1; polyline(ctx, geo.gal, true); ctx.stroke();
        ctx.setLineDash([5, 4]); ctx.strokeStyle = c.ink3; polyline(ctx, geo.ecl, true); ctx.stroke(); ctx.setLineDash([]);
      } else {
        // axes for period against radius
        ctx.font = mono(11); ctx.textBaseline = 'middle';
        [.5, 1, 2, 5, 10, 20, 50].forEach(function (p) {
          var x = M.l + (Math.log(p) - PMIN) / (PMAX - PMIN) * M.pw;
          ctx.strokeStyle = c.grid; ctx.beginPath(); ctx.moveTo(x, M.t); ctx.lineTo(x, M.t + M.ph); ctx.stroke();
          ctx.fillStyle = c.ink3; ctx.textAlign = 'center'; ctx.fillText(p + '', x, M.t + M.ph + 12);
        });
        [[1, 'Earth'], [3.88, 'Neptune'], [11.2, 'Jupiter']].forEach(function (r) {
          var y = M.t + (1 - (Math.log(r[0]) - RMIN) / (RMAX - RMIN)) * M.ph;
          ctx.strokeStyle = c.grid; ctx.beginPath(); ctx.moveTo(M.l, y); ctx.lineTo(M.l + M.pw, y); ctx.stroke();
          ctx.fillStyle = c.ink2; ctx.textAlign = 'right'; ctx.font = sans(11, 500); ctx.fillText(r[1], M.l + M.pw - 2, y - 8);
        });
        ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right';
        [1, 2, 4, 10, 20].forEach(function (r) { var y = M.t + (1 - (Math.log(r) - RMIN) / (RMAX - RMIN)) * M.ph; ctx.fillText(r + '', M.l - 6, y); });
        ctx.strokeStyle = c.lineui; ctx.beginPath(); ctx.moveTo(M.l, M.t + M.ph); ctx.lineTo(M.l + M.pw, M.t + M.ph); ctx.stroke();
        ctx.textAlign = 'left'; ctx.fillText('radius (Earth = 1)', 8, M.t - 12);
        ctx.textAlign = 'right'; ctx.fillText('orbital period, days', M.l + M.pw, H - 6);
      }
      // marks
      var ring = c.bg1, n = 0;
      for (var k = 0; k < D.n; k++) {
        var i = D.draw[k]; if (!show[D.tier[i]]) continue; n++;
        var p = pos(i), r = rad(i);
        shape(ctx, D.tier[i], p[0], p[1], r + 1.4); ctx.fillStyle = ring; ctx.fill();
        shape(ctx, D.tier[i], p[0], p[1], r); ctx.fillStyle = rgba(c.acc, .92); ctx.fill();
      }
      if (view === 'sky') skyLabels(ctx, c);
      [sel, hov].forEach(function (i, j) {
        if (i < 0 || !show[D.tier[i]]) return;
        var p = pos(i), r = rad(i);
        ctx.lineWidth = 2; ctx.strokeStyle = j === 0 ? c.focus : c.ink;
        ctx.beginPath(); ctx.arc(p[0], p[1], r + 6, 0, Math.PI * 2); ctx.stroke();
      });
      $('sky-count').textContent = n + ' shown';
      $('sky-corner').textContent = view === 'sky' ? (W < 460 ? 'Whole sky' : 'Whole sky · Hammer projection') : (W < 460 ? 'Period vs radius' : 'Period against radius · log scales');
    }
    /* the map's own labels go on top of the marks, each with a halo, and the line labels sit where their line
       passes through the emptiest sky (fewest candidate marks under the label) */
    var labKey = '', labPos = null;
    function halo(ctx, c, txt, x, y) { ctx.lineJoin = 'round'; ctx.lineWidth = 4; ctx.strokeStyle = c.bg1; ctx.strokeText(txt, x, y); ctx.fillText(txt, x, y); }
    function skyLabels(ctx, c) {
      var key = C.w + 'x' + C.h + show.join('');
      if (key !== labKey) {
        labKey = key;
        var marks = []; for (var i = 0; i < D.n; i++) if (show[D.tier[i]]) marks.push(P2(D.u[i]));
        var busy = function (x, y, w) { var n = 0; marks.forEach(function (m) { if (m[0] > x - 8 && m[0] < x + w + 8 && m[1] > y - 12 && m[1] < y + 12) n++; }); return n; };
        var inside = function (x, y, w) { var u = (x - M.cx) / M.s, v = (M.cy - y) / M.s, u2 = (x + w - M.cx) / M.s; return u * u / 8 + v * v / 2 < .8 && u2 * u2 / 8 + v * v / 2 < .8; };
        // boxes [x, y, w] the line labels must keep clear of: the hour labels on the equator, then each other
        var avoid = [[0, '0h'], [90, '6h'], [270, '18h']].map(function (a) { var p = P2(hammer(a[0], 0)); return [p[0] - 12, p[1] + 10, 24]; });
        var pick = function (pts, w) {
          var best = null, bs = 1e9;
          pts.forEach(function (p) {
            var x = p[0] + 6, y = p[1] - 9; if (!inside(x, y, w)) return;
            if (avoid.some(function (a) { return Math.abs(a[1] - y) < 18 && x < a[0] + a[2] + 10 && x + w > a[0] - 10; })) return;
            var sc = busy(x, y, w); if (sc < bs) { bs = sc; best = [x, y, w]; }
          });
          if (best) avoid.push(best);
          return best;
        };
        var gal = [], ecl = [];
        for (var l = 0; l < 360; l += 4) { var q = galToEq(l, 0); gal.push(P2(hammer(q[0], q[1]))); var e = eclToEq(l * Math.PI / 180); ecl.push(P2(hammer(e[0], e[1]))); }
        var mw = pick(gal, 64), ec = pick(ecl, 50);
        labPos = { mw: mw, ec: ec };
      }
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      [[0, '0h'], [90, '6h'], [270, '18h']].forEach(function (a) { var p = P2(hammer(a[0], 0)); halo(ctx, c, a[1], p[0], p[1] + 10); });
      ctx.textAlign = 'right';
      [[60, '+60°'], [30, '+30°'], [-30, '−30°'], [-60, '−60°']].forEach(function (a) { var p = P2(hammer(179.9, a[0])); halo(ctx, c, a[1], p[0] - 4, p[1]); });
      ctx.textAlign = 'left'; ctx.fillStyle = c.ink2; ctx.font = sans(11, 500);
      if (labPos.mw) halo(ctx, c, 'Milky Way', labPos.mw[0], labPos.mw[1]);
      if (labPos.ec) halo(ctx, c, 'ecliptic', labPos.ec[0], labPos.ec[1]);
    }
    function details(i, long) {
      var t = D.tier[i];
      var s = '<b>TIC ' + D.tic[i] + '</b> · tier ' + TIERS[t] + ' (' + TIER_TXT[t] + ')<br><span class="mono">P = ' + fmt(D.P[i], 4) + ' d · ' + fmt(D.rp[i], 2) + ' Earth radii · depth ' + grp(D.depth[i]) + ' ppm · T = ' + fmt(D.tmag[i], 2) + ' · RA ' + fmt(D.ra[i], 2) + '°, Dec ' + (D.dec[i] >= 0 ? '+' : '−') + fmt(Math.abs(D.dec[i]), 2) + '°</span>';
      if (long) s += '<br><a href="https://exofop.ipac.caltech.edu/tess/target.php?id=' + D.tic[i] + '">ExoFOP page</a><a href="https://eumemic.github.io/exoplanets/candidates.html?q=' + D.tic[i] + '">In the project&rsquo;s explorer</a>';
      return s;
    }
    var readDefault = $('sky-read').innerHTML, readOrb = '';
    function select(i) {
      sel = i; draw();
      $('sky-read').innerHTML = i < 0 ? (view === 'sky' ? readDefault : readOrb) : details(i, true);
    }
    function nearest(x, y) {
      var best = -1, bd = 16 * 16;
      for (var i = 0; i < D.n; i++) {
        if (!show[D.tier[i]]) continue;
        var p = pos(i), d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y);
        if (d < bd) { bd = d; best = i; }
      }
      return best;
    }
    cv.addEventListener('pointermove', function (ev) {
      if (!D) return;
      var r = cv.getBoundingClientRect(), i = nearest(ev.clientX - r.left, ev.clientY - r.top);
      if (i !== hov) { hov = i; draw(); }
      if (i >= 0) F0.tip.show('<div class="tip-k">TIC ' + D.tic[i] + ' · tier ' + TIERS[i >= 0 ? D.tier[i] : 0] + '</div><div class="tip-t">' + fmt(D.P[i], 3) + ' d · ' + fmt(D.rp[i], 2) + ' × Earth</div><div class="tip-note">Depth ' + grp(D.depth[i]) + ' ppm · star T = ' + fmt(D.tmag[i], 1) + '. Click to keep it below the map.</div>', ev.clientX, ev.clientY);
      else F0.tip.hide();
    });
    cv.addEventListener('pointerleave', function () { hov = -1; F0.tip.hide(); draw(); });
    cv.addEventListener('click', function (ev) {
      if (!D) return;
      var r = cv.getBoundingClientRect(), i = nearest(ev.clientX - r.left, ev.clientY - r.top);
      select(i);
    });
    function rebuildOrder() {
      order = [];
      for (var i = 0; i < D.n; i++) if (show[D.tier[i]]) order.push(i);
      if (view === 'sky') order.sort(function (a, b) { return D.ra[a] - D.ra[b]; });
      else order.sort(function (a, b) { return D.P[a] - D.P[b]; });
    }
    cv.addEventListener('keydown', function (ev) {
      if (!D) return;
      var k = ev.key, j = order.indexOf(sel);
      if (k === 'ArrowRight' || k === 'ArrowDown') j = j < 0 ? 0 : (j + 1) % order.length;
      else if (k === 'ArrowLeft' || k === 'ArrowUp') j = j < 0 ? order.length - 1 : (j - 1 + order.length) % order.length;
      else if (k === 'Home') j = 0; else if (k === 'End') j = order.length - 1;
      else if (k === 'Escape') { select(-1); F0.tip.hide(); return; }
      else return;
      ev.preventDefault();
      if (!order.length) return;
      select(order[j]);
      var p = pos(sel), r = cv.getBoundingClientRect();
      F0.tip.show('<div class="tip-k">' + (j + 1) + ' of ' + order.length + (view === 'sky' ? ', by right ascension' : ', by period') + '</div><div class="tip-t">TIC ' + D.tic[sel] + ' · tier ' + TIERS[D.tier[sel]] + '</div>', r.left + p[0], r.top + p[1]);
    });
    cv.addEventListener('blur', function () { F0.tip.hide(); });
    var bSky = $('sky-v-sky'), bOrb = $('sky-v-orb');
    function setView(v) {
      view = v; pressed(bSky, v === 'sky'); pressed(bOrb, v === 'orb');
      cv.setAttribute('aria-label', v === 'sky' ? 'Sky map of the counted candidates in a Hammer equal-area projection, with the ecliptic and the plane of the Milky Way. Use the left and right arrow keys to step through the candidates by right ascension; details appear below the map.' : 'Scatter plot of the counted candidates: orbital period against radius, both on logarithmic scales, with Earth, Neptune and Jupiter sizes marked. Use the arrow keys to step through the candidates by period.');
      if (D) { rebuildOrder(); draw(); if (sel < 0) $('sky-read').innerHTML = v === 'sky' ? readDefault : readOrb; }
    }
    bSky.addEventListener('click', function () { setView('sky'); });
    bOrb.addEventListener('click', function () { setView('orb'); });
    document.querySelectorAll('.sky-legend button').forEach(function (b) {
      b.addEventListener('click', function () {
        var t = +b.dataset.tier; show[t] = !show[t]; pressed(b, show[t]);
        if (sel >= 0 && !show[D.tier[sel]]) select(-1);
        rebuildOrder(); draw();
      });
    });
    C.resize(draw); F0.onTheme(draw);
    SKY.show = function (tic, P) {
      if (!D) return;
      var best = -1, bd = 1e9;
      for (var i = 0; i < D.n; i++) if (D.tic[i] === tic) { var dd = Math.abs(Math.log(D.P[i] / P)); if (dd < bd) { bd = dd; best = i; } }
      if (best < 0) return;
      if (view !== 'sky') setView('sky');
      if (!show[D.tier[best]]) { show[D.tier[best]] = true; document.querySelectorAll('.sky-legend button').forEach(function (b) { pressed(b, show[+b.dataset.tier]); }); rebuildOrder(); }
      select(best);
      cv.scrollIntoView({ block: 'center', behavior: F0.motion() ? 'smooth' : 'auto' });
      cv.focus({ preventScroll: true });
    };
    F0.json('candidates.json').then(function (d) {
      D = d; D.u = []; D.draw = [];
      // counts in the figure's title, tier buttons and table summary, from the data
      document.querySelectorAll('[data-sky-n]').forEach(function (e) { e.textContent = D.n; });
      document.querySelectorAll('[data-sky-tier]').forEach(function (e) { var t = +e.getAttribute('data-sky-tier'); e.textContent = D.tier.filter(function (x) { return x === t; }).length; });
      for (var i = 0; i < D.n; i++) { D.u.push(hammer(D.ra[i], D.dec[i])); D.draw.push(i); }
      // draw faint stars first so bright ones sit on top
      D.draw.sort(function (a, b) { return D.tmag[b] - D.tmag[a]; });
      var pole = 0; for (i = 0; i < D.n; i++) if (Math.abs(eclLat(D.ra[i], D.dec[i])) >= 60) pole++;
      readDefault = pole + ' of the ' + D.n + ' (' + Math.round(pole / D.n * 100) + '%) sit within 30° of an ecliptic pole, where TESS watches longest and so collects the most transits. Point at a mark for its numbers; click to keep them here.';
      var rs = D.rp.slice().sort(function (a, b) { return a - b; }), ps = D.P.slice().sort(function (a, b) { return a - b; });
      var small = D.rp.filter(function (r) { return r < 4; }).length, med = function (a) { return a.length % 2 ? a[(a.length - 1) / 2] : (a[a.length / 2 - 1] + a[a.length / 2]) / 2; };
      readOrb = small + ' of the ' + D.n + ' (' + Math.round(small / D.n * 100) + '%) are smaller than 4 Earth radii, about Neptune&rsquo;s size or less; the median is ' + fmt(med(rs), 2) + '. The median orbit is ' + fmt(med(ps), 1) + ' days: short orbits are favoured, because the full-sky search needed at least three transits.';
      $('sky-read').innerHTML = view === 'sky' ? readDefault : readOrb;
      rebuildOrder(); draw();
      // the table twin, built when first opened
      var tw = $('sky-twin'), done = false;
      tw.addEventListener('toggle', function () {
        if (!tw.open || done) return; done = true;
        var idx = []; for (var i = 0; i < D.n; i++) idx.push(i);
        idx.sort(function (a, b) { return D.tier[a] - D.tier[b] || D.P[a] - D.P[b]; });
        var h = '<table class="tbl"><caption>The ' + D.n + ' counted candidates, by tier and period' + (D.commit ? ' (eumemic/exoplanets at ' + D.commit + ', ' + F0.fmtDate(D.date) + ')' : '') + '</caption><thead><tr><th>TIC</th><th>Tier</th><th class="n">Period (d)</th><th class="n">Radius (Earths)</th><th class="n">Depth (ppm)</th><th class="n">T mag</th><th class="n">RA (°)</th><th class="n">Dec (°)</th></tr></thead><tbody>';
        idx.forEach(function (i) {
          h += '<tr><td><a href="https://exofop.ipac.caltech.edu/tess/target.php?id=' + D.tic[i] + '">' + D.tic[i] + '</a></td><td>' + TIERS[D.tier[i]] + '</td><td class="n">' + fmt(D.P[i], 4) + '</td><td class="n">' + fmt(D.rp[i], 2) + '</td><td class="n">' + grp(D.depth[i]) + '</td><td class="n">' + fmt(D.tmag[i], 2) + '</td><td class="n">' + fmt(D.ra[i], 3) + '</td><td class="n">' + fmt(D.dec[i], 3) + '</td></tr>';
        });
        $('sky-table').innerHTML = h + '</tbody></table>';
      });
    }).catch(function () { $('sky-read').textContent = 'The candidate data could not be loaded. The full table is in the repository: results_public/candidates_allsky.csv.'; });
  })();

  /* =========================================================================
     Shared light-curve data
     ========================================================================= */
  var LC = F0.json('lightcurves.json');
  var P1 = 3.182773250965767, T01 = 1468.4290909684505, P2 = 11.132735789579636, T02 = 1473.7333619682367;
  var W = 1.6978 / 24, W2 = 1.2874 / 24;

  /* =========================================================================
     2. Find the heartbeat
     ========================================================================= */
  (function heartbeat() {
    var cv = $('hb-canvas'); if (!cv) return;
    var C = F0.canvas(cv), S = null, st = { P: P1, orbit: false, fine: false, res: null, fineCurve: null }, peaks = [];
    var LN1 = Math.log(1), LN13 = Math.log(13), SMAX = 20000;
    function pToV(P) { return Math.round((Math.log(P) - LN1) / (LN13 - LN1) * SMAX); }
    function vToP(v) { return Math.exp(LN1 + v / SMAX * (LN13 - LN1)); }
    // box search at one period: the same rule as Foundation0's offline search in lightcurves.json
    var NBMAX = Math.ceil(13 / W) + 3, cnt = new Float64Array(NBMAX), sum = new Float64Array(NBMAX);
    function search(P) {
      var t = S.t, f = S.f, n = t.length, best = { snr: -1e9, c: 0, dep: 0, n: 0 }, nb = Math.ceil(P / W) + 2, k, i, off;
      for (off = 0; off < 1; off += .25) {
        for (k = 0; k < nb; k++) { cnt[k] = 0; sum[k] = 0; }
        for (i = 0; i < n; i++) {
          var x = (t[i] - T01) / P + .5; x = (x - Math.floor(x)) * P;
          k = Math.floor(x / W + off); cnt[k]++; sum[k] += f[i];
        }
        for (k = 0; k < nb; k++) {
          if (cnt[k] < 3) continue;
          var dep = S.mu - sum[k] / cnt[k], snr = dep / (S.sig / Math.sqrt(cnt[k]));
          if (snr > best.snr) best = { snr: snr, c: (k - off + .5) * W, dep: dep, n: cnt[k] };
        }
      }
      return best;
    }
    function hms(P) {
      var s = P * DAY, d = Math.floor(s / DAY); s -= d * DAY;
      var h = Math.floor(s / 3600); s -= h * 3600; var m = Math.floor(s / 60); s -= m * 60;
      return d + ' d ' + h + ' h ' + m + ' min ' + fmt(s, 1) + ' s';
    }
    function offTxt(P) {
      var d1 = (P - P1) * DAY, d2 = (P - P2) * DAY;
      function s(x) { var a = Math.abs(x); return (x >= 0 ? '+' : '−') + (a < 99.95 ? fmt(a, 1) + ' s' : a < 3600 ? fmt(a / 60, 1) + ' min' : fmt(a / 3600, 1) + ' h'); }
      if (Math.abs(d1) <= Math.abs(d2)) return Math.abs(d1) < 86400 * .02 ? s(d1) + ' <small>from 3.182773 d</small>' : 'far from either fitted period';
      return Math.abs(d2) < 86400 * .05 ? s(d2) + ' <small>from 11.132736 d (second signal)</small>' : 'far from either fitted period';
    }
    function verdict(snr) {
      if (snr >= 12) return ['good', 'A dip stands far above the noise. This is a heartbeat.'];
      if (snr >= 10) return ['weak', 'Strong-ish, but across 373,825 trial periods noise alone reaches about 10 somewhere.'];
      if (snr >= 7.5) return ['weak', 'Weak: chance lines up this well often when you try many periods.'];
      return ['none', 'Nothing stands out. This is what noise looks like.'];
    }
    /* ---- drawing ---- */
    function layout() {
      var W0 = C.w, H = C.h, narrow = W0 < 560, padL = narrow ? 40 : 52, padR = narrow ? 10 : 16;
      var lab = 22, gap = narrow ? 18 : 22, bottom = 30;
      var avail = H - 3 * lab - 2 * gap - bottom - 6;
      var hA = avail * .26, hB = avail * .44, hC = avail * .30, y = 6;
      var A = { x: padL, w: W0 - padL - padR, y: y + lab, h: hA }; y = A.y + hA + gap;
      var B = { x: padL, w: W0 - padL - padR, y: y + lab, h: hB }; y = B.y + hB + gap;
      var Cc = { x: padL, w: W0 - padL - padR, y: y + lab, h: hC };
      return { A: A, B: B, C: Cc, narrow: narrow };
    }
    var L = null, segs = null;
    function label(ctx, c, x, y, txt, right) {
      ctx.font = mono(11); ctx.fillStyle = c.ink2; ctx.textAlign = right ? 'right' : 'left'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(txt, x, y);
    }
    function draw() {
      if (!S) return;
      var ctx = C.ctx, c = colors(), r = st.res, P = st.P;
      L = layout();
      ctx.clearRect(0, 0, C.w, C.h);
      var inBox = function (h) { return Math.abs(h) <= W * 12; };
      /* ---- panel A: the record ---- */
      var A = L.A, gapPx = L.narrow ? 12 : 18, tot = 0;
      S.sec.forEach(function (s) { tot += s.t1 - s.t0; });
      var scale = (A.w - gapPx * (S.sec.length - 1)) / tot, xo = A.x;
      segs = S.sec.map(function (s) { var g = { s: s, x: xo, w: (s.t1 - s.t0) * scale }; xo += g.w + gapPx; return g; });
      var yA = function (v) { return A.y + A.h / 2 - Math.max(-1, Math.min(1, v / 1600)) * A.h / 2; };
      label(ctx, c, A.x, A.y - 8, L.narrow ? 'THE RECORD · PPM' : 'THE RECORD · BRIGHTNESS, PPM FROM NORMAL');
      ctx.strokeStyle = c.grid; ctx.lineWidth = 1;
      segs.forEach(function (g) {
        ctx.beginPath(); ctx.moveTo(g.x, yA(0)); ctx.lineTo(g.x + g.w, yA(0)); ctx.stroke();
        ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'left';
        ctx.fillText((L.narrow ? 'S' : 'Sector ') + g.s.s + ' · ' + g.s.y, g.x + 2, A.y + A.h + 13);
      });
      // predicted transit ticks
      var phase0 = T01 + r.c - P / 2;
      ctx.strokeStyle = c.acc; ctx.lineWidth = 1.5;
      segs.forEach(function (g) {
        var n0 = Math.ceil((g.s.t0 - phase0) / P), n1 = Math.floor((g.s.t1 - phase0) / P);
        if (n1 - n0 > 400) return;
        for (var n = n0; n <= n1; n++) {
          var x = g.x + (phase0 + n * P - g.s.t0) * scale;
          ctx.beginPath(); ctx.moveTo(x, A.y - 2); ctx.lineTo(x, A.y + 5); ctx.stroke();
        }
      });
      var pts = S.t.length, i, hrs = S.hrs;
      ctx.fillStyle = rgba(c.ink3, c.dark ? .55 : .5);
      for (i = 0; i < pts; i++) {
        if (inBox(hrs[i])) continue;
        var g = segs[S.si[i]]; ctx.fillRect(g.x + (S.t[i] - g.s.t0) * scale - .75, yA(S.f[i]) - .75, 1.5, 1.5);
      }
      ctx.fillStyle = c.acc;
      for (i = 0; i < pts; i++) {
        if (!inBox(hrs[i])) continue;
        g = segs[S.si[i]]; ctx.beginPath(); ctx.arc(g.x + (S.t[i] - g.s.t0) * scale, yA(S.f[i]), 1.9, 0, Math.PI * 2); ctx.fill();
      }
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right';
      ctx.fillText('+1600', A.x - 6, A.y + 4); ctx.fillText('−1600', A.x - 6, A.y + A.h);
      /* ---- panel B: the stack ---- */
      var B = L.B, span = st.orbit ? P * 12 : 6;
      var xB = function (h) { return B.x + (h + span) / (2 * span) * B.w; };
      var yB = function (v) { return B.y + (1 - (Math.max(-1600, Math.min(1100, v)) + 1600) / 2700) * B.h; };
      label(ctx, c, B.x, B.y - 8, (L.narrow ? 'STACKED AT ' : 'STACKED AT THE TRIAL PERIOD · ') + fmt(P, 6) + ' D');
      ctx.strokeStyle = c.grid; ctx.lineWidth = 1;
      [-1000, -500, 0, 500].forEach(function (v) { ctx.beginPath(); ctx.moveTo(B.x, yB(v)); ctx.lineTo(B.x + B.w, yB(v)); ctx.stroke(); });
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      [-1000, -500, 0, 500].forEach(function (v) { ctx.fillText(v === 0 ? '0' : (v > 0 ? '+' : '−') + Math.abs(v), B.x - 6, yB(v)); });
      // the box
      ctx.fillStyle = rgba(c.acc, c.dark ? .13 : .14);
      ctx.fillRect(xB(-W * 12), B.y, xB(W * 12) - xB(-W * 12), B.h);
      // points
      ctx.fillStyle = rgba(c.ink3, c.dark ? .5 : .45);
      for (i = 0; i < pts; i++) { var h = hrs[i]; if (h < -span || h > span || inBox(h)) continue; ctx.fillRect(xB(h) - .8, yB(S.f[i]) - .8, 1.6, 1.6); }
      ctx.fillStyle = c.acc;
      for (i = 0; i < pts; i++) { h = hrs[i]; if (!inBox(h) || h < -span || h > span) continue; ctx.beginPath(); ctx.arc(xB(h), yB(S.f[i]), 1.9, 0, Math.PI * 2); ctx.fill(); }
      // binned mean
      var nb = st.orbit ? Math.max(40, Math.min(220, Math.round(P * 24 / .8))) : 40, bw = 2 * span / nb;
      var bc = new Float64Array(nb), bs = new Float64Array(nb);
      for (i = 0; i < pts; i++) { h = hrs[i]; if (h < -span || h >= span) continue; var k = Math.floor((h + span) / bw); bc[k]++; bs[k] += S.f[i]; }
      ctx.strokeStyle = c.ink; ctx.lineWidth = 2; ctx.lineJoin = 'round'; ctx.beginPath();
      var started = false; st.bins = [];
      for (k = 0; k < nb; k++) {
        if (bc[k] < 1) continue;
        var m = bs[k] / bc[k], xx = xB(-span + (k + .5) * bw); st.bins.push([-span + (k + .5) * bw, m, bc[k]]);
        if (!started) { ctx.moveTo(xx, yB(m)); started = true; } else ctx.lineTo(xx, yB(m));
      }
      ctx.stroke();
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textBaseline = 'alphabetic';
      ctx.textAlign = 'left'; ctx.fillText((st.orbit ? '−' + fmt(span, 0) : '−6') + ' h', B.x, B.y + B.h + 13);
      ctx.textAlign = 'right'; ctx.fillText('+' + (st.orbit ? fmt(span, 0) : '6') + ' h', B.x + B.w, B.y + B.h + 13);
      ctx.textAlign = 'center'; ctx.fillText(L.narrow ? 'hours from the deepest dip' : 'hours from the deepest dip (shaded box, ' + fmt(W * 24, 2) + ' h wide)', B.x + B.w / 2, B.y + B.h + 13);
      ctx.textAlign = 'right'; ctx.font = mono(11); ctx.fillStyle = c.ink2;
      ctx.fillText('average', B.x + B.w - 4, B.y + 12);
      ctx.strokeStyle = c.ink; ctx.lineWidth = 2; ctx.beginPath(); var lw = ctx.measureText('average').width; ctx.moveTo(B.x + B.w - 12 - lw - 16, B.y + 8); ctx.lineTo(B.x + B.w - 12 - lw, B.y + 8); ctx.stroke();
      /* ---- panel C: the search ---- */
      var Cc = L.C;
      var yC = function (v) { return Cc.y + (1 - Math.max(0, Math.min(16, v)) / 16) * Cc.h; };
      label(ctx, c, Cc.x, Cc.y - 8, st.fine ? (L.narrow ? 'SEARCH · ±90 S' : 'SEARCH NEARBY · ±90 SECONDS, COMPUTED LIVE') : (L.narrow ? 'SEARCH · 1–13 DAYS' : 'SEARCH · DEEPEST DIP AT EVERY PERIOD, 1–13 DAYS'));
      ctx.strokeStyle = c.grid; ctx.lineWidth = 1; ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      [0, 5, 10, 15].forEach(function (v) { ctx.beginPath(); ctx.moveTo(Cc.x, yC(v)); ctx.lineTo(Cc.x + Cc.w, yC(v)); ctx.stroke(); ctx.fillText(v + '', Cc.x - 6, yC(v)); });
      ctx.textBaseline = 'alphabetic';
      var xC;
      if (!st.fine) {
        xC = function (p) { return Cc.x + (Math.log(p) - LN1) / (LN13 - LN1) * Cc.w; };
        var sp = S.search;
        ctx.beginPath(); ctx.moveTo(xC(sp.P[0]), yC(0));
        for (i = 0; i < sp.P.length; i++) ctx.lineTo(xC(sp.P[i]), yC(sp.snr[i]));
        ctx.lineTo(xC(sp.P[sp.P.length - 1]), yC(0)); ctx.closePath();
        ctx.fillStyle = rgba(c.acc, .12); ctx.fill();
        ctx.beginPath();
        for (i = 0; i < sp.P.length; i++) { var X = xC(sp.P[i]), Y = yC(sp.snr[i]); if (i) ctx.lineTo(X, Y); else ctx.moveTo(X, Y); }
        ctx.strokeStyle = c.acc; ctx.lineWidth = 1.25; ctx.stroke();
        ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'center';
        [1, 2, 3, 5, 8, 13].forEach(function (p) { ctx.textAlign = p === 1 ? 'left' : p === 13 ? 'right' : 'center'; ctx.fillText(p + (p === 13 ? ' d' : ''), xC(p), Cc.y + Cc.h + 13); });
        ctx.fillStyle = c.ink2; ctx.font = mono(11);
        peaks.forEach(function (pk) { ctx.textAlign = pk.P > 8 ? 'right' : 'left'; ctx.fillText(fmt(pk.P, 4) + ' d', xC(pk.P) + (pk.P > 8 ? -6 : 6), yC(pk.snr) + 4); });
      } else {
        xC = function (p) { return Cc.x + ((p - P) * DAY + 90) / 180 * Cc.w; };
        var fc = st.fineCurve;
        if (fc) {
          ctx.beginPath(); ctx.moveTo(Cc.x, yC(0));
          for (i = 0; i < fc.length; i++) ctx.lineTo(Cc.x + i / (fc.length - 1) * Cc.w, yC(fc[i]));
          ctx.lineTo(Cc.x + Cc.w, yC(0)); ctx.closePath(); ctx.fillStyle = rgba(c.acc, .12); ctx.fill();
          ctx.beginPath();
          for (i = 0; i < fc.length; i++) { X = Cc.x + i / (fc.length - 1) * Cc.w; Y = yC(fc[i]); if (i) ctx.lineTo(X, Y); else ctx.moveTo(X, Y); }
          ctx.strokeStyle = c.acc; ctx.lineWidth = 2; ctx.stroke();
        }
        ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'center';
        [-90, -60, -30, 0, 30, 60, 90].forEach(function (s) { ctx.textAlign = s === -90 ? 'left' : s === 90 ? 'right' : 'center'; ctx.fillText((s > 0 ? '+' : s < 0 ? '−' : '') + Math.abs(s) + (s === 90 ? ' s' : ''), Cc.x + (s + 90) / 180 * Cc.w, Cc.y + Cc.h + 13); });
        [[P1, 'fit'], [P2, 'fit 2']].forEach(function (q) {
          var dx = (q[0] - P) * DAY; if (Math.abs(dx) > 90) return;
          var x = Cc.x + (dx + 90) / 180 * Cc.w;
          ctx.fillStyle = c.ink2; ctx.beginPath(); ctx.moveTo(x, Cc.y + Cc.h); ctx.lineTo(x - 4, Cc.y + Cc.h + 5); ctx.lineTo(x + 4, Cc.y + Cc.h + 5); ctx.closePath(); ctx.fill();
          ctx.font = mono(11); ctx.textAlign = 'center'; ctx.fillText(q[1], x, Cc.y + Cc.h - 6);
        });
      }
      // marker at the trial period
      var mx = st.fine ? Cc.x + Cc.w / 2 : xC(P);
      ctx.strokeStyle = c.ink; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(mx, Cc.y); ctx.lineTo(mx, Cc.y + Cc.h); ctx.stroke();
      ctx.fillStyle = c.ink; ctx.strokeStyle = c.bg1; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(mx, yC(r.snr), 4.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    }
    /* ---- state updates ---- */
    var slider = $('hb-p'), out = $('hb-p-out'), pend = 0, lastRead = 0;
    function compute() {
      var P = st.P;
      st.res = search(P);
      var c = st.res.c - P / 2, hrs = S.hrs;
      for (var i = 0; i < S.t.length; i++) {
        var x = (S.t[i] - T01) / P + .5; x = (x - Math.floor(x)) * P - P / 2 - c; // days from the deepest dip
        x = x - Math.round(x / P) * P; hrs[i] = x * 24;
      }
      if (st.fine) {
        var fc = new Array(181);
        for (var s = -90; s <= 90; s++) fc[s + 90] = Math.max(0, search(P + s / DAY).snr);
        st.fineCurve = fc;
      }
    }
    function update() {
      if (!S) return;
      compute();
      var P = st.P, r = st.res, v = verdict(r.snr);
      draw();
      var tnow = performance.now();
      if (scanning && tnow - lastRead < 250) return; // while the computer searches, the numbers change a few times a second at most
      lastRead = tnow;
      slider.value = String(pToV(P));
      out.textContent = fmt(P, 6) + ' d';
      slider.setAttribute('aria-valuetext', fmt(P, 6) + ' days');
      $('hb-r-p').innerHTML = fmt(P, 6) + ' d <small>' + hms(P) + '</small>';
      $('hb-r-off').innerHTML = offTxt(P);
      $('hb-r-dep').innerHTML = grp(r.dep) + ' ppm <small>' + r.n + ' measurements in the box</small>';
      $('hb-r-snr').textContent = fmt(r.snr, 1);
      var vd = $('hb-r-v'); vd.textContent = v[1]; vd.className = v[0];
      if (sayNext && sayEl) { sayNext = false; sayEl.textContent = 'Trial period ' + fmt(P, 6) + ' days: signal-to-noise ' + fmt(r.snr, 1) + '. ' + v[1]; }
    }
    function schedule() { if (pend) return; pend = requestAnimationFrame(function () { pend = 0; update(); }); }
    function setP(P) { st.P = Math.max(1, Math.min(13, P)); schedule(); }
    slider.addEventListener('input', function () { stopScan(); setP(vToP(+slider.value)); });
    document.querySelectorAll('.hb-nudge button').forEach(function (b) { b.addEventListener('click', function () { stopScan(); sayLater(); setP(st.P + (+b.dataset.nudge) / DAY); }); });
    var PRE = { best: P1, s8: P1 + 8 / DAY, m1: P1 + 60 / DAY, three: 3.1, p2: P2 };
    document.querySelectorAll('[data-preset]').forEach(function (b) { b.addEventListener('click', function () { stopScan(); sayLater(); setP(PRE[b.dataset.preset]); }); });
    var vO = $('hb-v-orbit'), vZ = $('hb-v-zoom'), sA = $('hb-s-all'), sF = $('hb-s-fine');
    vO.addEventListener('click', function () { st.orbit = true; pressed(vO, true); pressed(vZ, false); schedule(); });
    vZ.addEventListener('click', function () { st.orbit = false; pressed(vO, false); pressed(vZ, true); schedule(); });
    sA.addEventListener('click', function () { st.fine = false; pressed(sA, true); pressed(sF, false); schedule(); });
    sF.addEventListener('click', function () { st.fine = true; pressed(sA, false); pressed(sF, true); schedule(); });
    /* ---- "let the computer search": sweep the trial period across 1-13 d, then settle on the tallest peak ---- */
    var scanBtn = $('hb-scan'), scanTxt = $('hb-scan-txt'), scanning = false, scanT = 0, lastNow = 0;
    var loop = F0.loop(function (now) {
      if (!lastNow) lastNow = now;
      scanT += Math.min(.1, (now - lastNow) / 1000) / 3.2; lastNow = now;
      if (scanT >= 1) { stopScan(); sayLater(); setP(peaks[0].P); return; }
      st.P = vToP(scanT * SMAX); update();
    });
    function stopScan() { if (!scanning) return; scanning = false; loop.stop(); pressed(scanBtn, false); scanTxt.textContent = 'Let the computer search'; }
    var sayEl = $('hb-say'), sayNext = false;
    function sayLater() { sayNext = true; } // the next update speaks once (a preset, a nudge, the end of a search)
    scanBtn.addEventListener('click', function () {
      if (scanning) { stopScan(); return; }
      if (!S) return;
      if (!F0.motion()) { sayLater(); setP(peaks[0].P); return; }
      scanning = true; scanT = 0; lastNow = 0; pressed(scanBtn, true); scanTxt.textContent = 'Stop the search'; loop.start();
    });
    F0.onMotion(function () { if (!F0.motion()) stopScan(); });
    F0.whenVisible(cv, null, stopScan);
    /* ---- pointer: hover the search panel for values, click to jump there ---- */
    function panelAt(ev) {
      if (!L) return null;
      var r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, Cc = L.C, B = L.B;
      if (x >= Cc.x && x <= Cc.x + Cc.w && y >= Cc.y - 6 && y <= Cc.y + Cc.h + 6) return { p: 'C', u: (x - Cc.x) / Cc.w };
      if (x >= B.x && x <= B.x + B.w && y >= B.y && y <= B.y + B.h) return { p: 'B', u: (x - B.x) / B.w };
      return null;
    }
    function periodAt(u) {
      if (st.fine) return st.P + (u * 180 - 90) / DAY;
      var sp = S.search, lp = LN1 + u * (LN13 - LN1), best = 0, bd = 1e9;
      for (var i = 0; i < sp.P.length; i++) { var d = Math.abs(Math.log(sp.P[i]) - lp); if (d < bd) { bd = d; best = i; } }
      // snap to the tallest bin within a few pixels
      var lo = Math.max(0, best - 3), hi = Math.min(sp.P.length - 1, best + 3), top = best;
      for (i = lo; i <= hi; i++) if (sp.snr[i] > sp.snr[top]) top = i;
      return { P: sp.P[top], snr: sp.snr[top] };
    }
    cv.addEventListener('pointermove', function (ev) {
      if (!S) return;
      var a = panelAt(ev);
      if (!a) { F0.tip.hide(); return; }
      if (a.p === 'C') {
        if (st.fine) { var s = Math.round(a.u * 180 - 90); F0.tip.show('<div class="tip-k">' + (s >= 0 ? '+' : '−') + Math.abs(s) + ' s from the trial period</div><div class="tip-t">Signal-to-noise ' + fmt(st.fineCurve ? st.fineCurve[s + 90] : 0, 1) + '</div><div class="tip-note">Click to try this period.</div>', ev.clientX, ev.clientY); }
        else { var q = periodAt(a.u); F0.tip.show('<div class="tip-k">Near ' + fmt(q.P, 4) + ' days</div><div class="tip-t">Signal-to-noise ' + fmt(q.snr, 1) + '</div><div class="tip-note">Click to try this period.</div>', ev.clientX, ev.clientY); }
      } else {
        var span = st.orbit ? st.P * 12 : 6, h = -span + a.u * 2 * span, near = null, bd = 1e9;
        (st.bins || []).forEach(function (b) { var d = Math.abs(b[0] - h); if (d < bd) { bd = d; near = b; } });
        if (near) F0.tip.show('<div class="tip-k">' + (near[0] >= 0 ? '+' : '−') + fmt(Math.abs(near[0]), 1) + ' h from the deepest dip</div><div class="tip-t">Average ' + (near[1] >= 0 ? '+' : '−') + grp(Math.abs(near[1])) + ' ppm</div><div class="tip-note">' + near[2] + ' measurements in this bin.</div>', ev.clientX, ev.clientY);
      }
    });
    cv.addEventListener('pointerleave', function () { F0.tip.hide(); });
    cv.addEventListener('click', function (ev) {
      if (!S) return;
      var a = panelAt(ev); if (!a || a.p !== 'C') return;
      stopScan();
      if (st.fine) setP(st.P + (Math.round(a.u * 180 - 90)) / DAY); else setP(periodAt(a.u).P);
    });
    C.resize(draw); F0.onTheme(draw);
    LC.then(function (d) {
      var o = d.tic4206066, t = [], f = [], si = [], sec = [];
      o.sectors.forEach(function (s, j) {
        var q = decode(s); sec.push({ s: s.s, y: s.y, t0: q.t[0] - .2, t1: q.t[q.t.length - 1] + .2 });
        for (var i = 0; i < q.t.length; i++) { t.push(q.t[i]); f.push(q.f[i]); si.push(j); }
      });
      var n = t.length, mu = 0, v = 0, i;
      for (i = 0; i < n; i++) mu += f[i]; mu /= n;
      for (i = 0; i < n; i++) v += (f[i] - mu) * (f[i] - mu);
      S = { t: Float64Array.from(t), f: Float32Array.from(f), si: si, sec: sec, mu: mu, sig: Math.sqrt(v / n), hrs: new Float64Array(n), search: d.search };
      // the two tallest separate peaks of the offline search
      var idx = d.search.snr.map(function (s, i) { return i; }).sort(function (a, b) { return d.search.snr[b] - d.search.snr[a]; });
      idx.forEach(function (i) { if (peaks.length < 2 && peaks.every(function (p) { return Math.abs(Math.log(p.P / d.search.P[i])) > .05; })) peaks.push({ P: d.search.P[i], snr: d.search.snr[i] }); });
      // numbers twin
      var rows = [['Best fit (the project’s)', P1], ['8 seconds longer', P1 + 8 / DAY], ['1 minute longer', P1 + 60 / DAY], ['A guess: 3.1 days', 3.1], ['Tallest peak of the search', peaks[0].P], ['Second signal (the project’s fit)', P2]];
      var tb = $('hb-tbody');
      rows.forEach(function (rw) {
        var r = search(rw[1]), tr = document.createElement('tr'), off = (rw[1] - (Math.abs(rw[1] - P1) < Math.abs(rw[1] - P2) ? P1 : P2)) * DAY;
        [rw[0], fmt(rw[1], 6), Math.abs(off) > 3600 ? '—' : (off >= 0 ? '+' : '−') + fmt(Math.abs(off), 1) + ' s', grp(r.dep), fmt(r.snr, 1)].forEach(function (x, j) { var td = document.createElement('td'); td.textContent = x; if (j) td.className = 'n'; tr.appendChild(td); });
        tb.appendChild(tr);
      });
      update();
    });
  })();

  /* =========================================================================
     3. Why stacking works: signal-to-noise against transits stacked
     ========================================================================= */
  (function stacking() {
    var cv = $('st-canvas'), svg = $('st-svg'); if (!cv || !svg) return;
    var C = F0.canvas(cv), S = null, N = 6, NT = 28, rows = [];
    function draw() {
      if (!S) return;
      var ctx = C.ctx, c = colors(), Wd = C.w, H = C.h, M = { l: 46, r: 12, t: 30, b: 26 };
      var pw = Wd - M.l - M.r, ph = H - M.t - M.b;
      var xs = function (h) { return M.l + (h + 6) / 12 * pw; }, ys = function (v) { return M.t + (1 - (Math.max(-1500, Math.min(1000, v)) + 1500) / 2500) * ph; };
      ctx.clearRect(0, 0, Wd, H);
      ctx.strokeStyle = c.grid; ctx.lineWidth = 1; ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      [-1000, -500, 0, 500].forEach(function (v) { ctx.beginPath(); ctx.moveTo(M.l, ys(v)); ctx.lineTo(M.l + pw, ys(v)); ctx.stroke(); ctx.fillText(v === 0 ? '0' : (v > 0 ? '+' : '−') + Math.abs(v), M.l - 6, ys(v)); });
      ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      [-6, -3, 0, 3, 6].forEach(function (h) { ctx.fillText((h > 0 ? '+' : h < 0 ? '−' : '') + Math.abs(h) + ' h', xs(h), H - 8); });
      ctx.fillStyle = rgba(c.acc, c.dark ? .12 : .13); ctx.fillRect(xs(-W * 12), M.t, xs(W * 12) - xs(-W * 12), ph);
      var use = S.ep.slice(0, N), bins = 24, bc = new Float64Array(bins), bs = new Float64Array(bins), i, k;
      ctx.fillStyle = rgba(c.ink3, c.dark ? .55 : .5);
      use.forEach(function (e) {
        e.h.forEach(function (h, j) {
          ctx.fillRect(xs(h) - 1, ys(e.f[j]) - 1, 2, 2);
          k = Math.floor((h + 6) / .5); if (k >= 0 && k < bins) { bc[k]++; bs[k] += e.f[j]; }
        });
      });
      // binned means with error bars
      ctx.strokeStyle = c.acc; ctx.fillStyle = c.acc; ctx.lineWidth = 1.5;
      for (k = 0; k < bins; k++) {
        if (!bc[k]) continue;
        var m = bs[k] / bc[k], e = S.sig / Math.sqrt(bc[k]), x = xs(-6 + (k + .5) * .5);
        ctx.beginPath(); ctx.moveTo(x, ys(m - e)); ctx.lineTo(x, ys(m + e)); ctx.stroke();
      }
      for (k = 0; k < bins; k++) {
        if (!bc[k]) continue;
        x = xs(-6 + (k + .5) * .5);
        ctx.beginPath(); ctx.arc(x, ys(bs[k] / bc[k]), 3.6, 0, Math.PI * 2); ctx.fillStyle = c.bg1; ctx.fill();
        ctx.beginPath(); ctx.arc(x, ys(bs[k] / bc[k]), 2.8, 0, Math.PI * 2); ctx.fillStyle = c.acc; ctx.fill();
      }
      // the fitted depth for reference
      ctx.setLineDash([4, 4]); ctx.strokeStyle = c.ink2; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(xs(-W * 12), ys(-398)); ctx.lineTo(xs(W * 12), ys(-398)); ctx.stroke(); ctx.setLineDash([]);
      ctx.font = mono(11); ctx.fillStyle = c.ink2; ctx.textAlign = 'left';
      ctx.fillText(Wd < 460 ? '398 ppm' : 'fitted depth 398 ppm', xs(W * 12) + 6, ys(-398) + 4);
    }
    // SVG chart of signal-to-noise against N
    var SW = 480, SH = 236, M = { l: 40, r: 14, t: 46, b: 44 };
    var xs = function (n) { return M.l + (n - 1) / (NT - 1) * (SW - M.l - M.r); }, ys = function (v) { return M.t + (1 - v / 16) * (SH - M.t - M.b); };
    var dots = [], guide, hl;
    function buildChart() {
      // drawn at the container's own width, so the text stays at its true size on phones
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      dots = [];
      SW = Math.max(300, Math.min(600, Math.round(svg.parentNode.clientWidth || 480)));
      svg.setAttribute('viewBox', '0 0 ' + SW + ' ' + SH);
      [0, 5, 10, 15].forEach(function (v) {
        el('line', { x1: M.l, x2: SW - M.r, y1: ys(v), y2: ys(v), stroke: 'var(--grid)', 'stroke-width': 1 }, svg);
        var t = el('text', { x: M.l - 7, y: ys(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = v;
      });
      el('line', { x1: M.l, x2: SW - M.r, y1: ys(7.1), y2: ys(7.1), stroke: 'var(--ink-3)', 'stroke-width': 1 }, svg);
      var t71 = el('text', { x: SW - M.r, y: ys(7.1) + 14, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t71.textContent = SW < 420 ? '7.1 · NASA, one sector' : '7.1 · NASA single-sector threshold';
      // sector separators
      [[6.5, ''], [14.5, '']].forEach(function (s) { el('line', { x1: xs(s[0]), x2: xs(s[0]), y1: M.t - 4, y2: SH - M.b, stroke: 'var(--line-ui)', 'stroke-width': 1, 'stroke-dasharray': '2 3' }, svg); });
      [[3.5, '2018'], [10.5, '2020'], [21.5, '2025']].forEach(function (s) { var t = el('text', { x: xs(s[0]), y: M.t - 8, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-2)' }, svg); t.textContent = s[1]; });
      [1, 6, 14, 28].forEach(function (n) { var t = el('text', { x: xs(n), y: SH - M.b + 16, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = n; });
      var xl = el('text', { x: (M.l + SW - M.r) / 2, y: SH - 4, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); xl.textContent = 'transits stacked';
      var yl = el('text', { x: 4, y: 12, 'font-size': 11, fill: 'var(--ink-3)' }, svg); yl.textContent = 'SIGNAL-TO-NOISE';
      // the square-root rule
      var d = ''; for (var n = 1; n <= NT; n += .25) d += (n === 1 ? 'M' : 'L') + fmt(xs(n), 1) + ' ' + fmt(ys(rows[NT - 1].snr * Math.sqrt(n / NT)), 1);
      el('path', { d: d, fill: 'none', stroke: 'var(--ink-2)', 'stroke-width': 1.5 }, svg);
      guide = el('line', { y1: M.t - 4, y2: SH - M.b, stroke: 'var(--ink)', 'stroke-width': 1, 'stroke-opacity': .5 }, svg);
      rows.forEach(function (r, i) {
        var g = el('g', { 'class': 'st-dot' }, svg);
        el('circle', { cx: xs(i + 1), cy: ys(r.snr), r: 9, fill: 'transparent' }, g);
        var c = el('circle', { cx: xs(i + 1), cy: ys(r.snr), r: 3.6, fill: 'var(--acc-exoplanets)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, g);
        g.addEventListener('click', function () { set(i + 1); });
        g.addEventListener('pointermove', function (ev) { F0.tip.show('<div class="tip-k">' + (i + 1) + ' transit' + (i ? 's' : '') + ' · last in ' + r.year + '</div><div class="tip-t">Signal-to-noise ' + fmt(r.snr, 1) + '</div><div class="tip-note">Depth ' + grp(r.dep) + ' ± ' + grp(r.err) + ' ppm from ' + r.n + ' measurements. √N rule: ' + fmt(r.rule, 1) + '.</div>', ev.clientX, ev.clientY); });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        dots.push(c);
      });
      hl = el('circle', { r: 7, fill: 'none', stroke: 'var(--focus)', 'stroke-width': 2 }, svg);
      // legend
      var lg = el('g', {}, svg);
      el('circle', { cx: M.l + 8, cy: 14, r: 3.6, fill: 'var(--acc-exoplanets)' }, lg);
      var l1 = el('text', { x: M.l + 16, y: 18, 'font-size': 11, fill: 'var(--ink-2)' }, lg); l1.textContent = 'measured';
      el('line', { x1: M.l + 92, x2: M.l + 110, y1: 14, y2: 14, stroke: 'var(--ink-2)', 'stroke-width': 1.5 }, lg);
      var l2 = el('text', { x: M.l + 116, y: 18, 'font-size': 11, fill: 'var(--ink-2)' }, lg); l2.textContent = '√N rule';
      yl.setAttribute('x', SW - M.r); yl.setAttribute('text-anchor', 'end');
    }
    var slider = $('st-n'), out = $('st-n-out');
    function set(n) {
      N = Math.max(1, Math.min(NT, n | 0));
      var r = rows[N - 1];
      slider.value = N; out.textContent = N + ' of ' + NT;
      slider.setAttribute('aria-valuetext', N + ' of ' + NT + ' transits, signal-to-noise ' + fmt(r.snr, 1));
      $('st-corner').textContent = N + ' of ' + NT;
      $('st-r-n').textContent = N + ' (to ' + r.year + ')';
      $('st-r-pts').textContent = r.n;
      $('st-r-dep').textContent = grp(r.dep) + ' ± ' + grp(r.err) + ' ppm';
      $('st-r-snr').textContent = fmt(r.snr, 1);
      document.querySelectorAll('.st-seg button').forEach(function (b) { pressed(b, +b.dataset.n === N); });
      guide.setAttribute('x1', xs(N)); guide.setAttribute('x2', xs(N));
      hl.setAttribute('cx', xs(N)); hl.setAttribute('cy', ys(r.snr));
      draw();
    }
    slider.addEventListener('input', function () { stop(); set(+slider.value); });
    document.querySelectorAll('.st-seg button').forEach(function (b) { b.addEventListener('click', function () { stop(); set(+b.dataset.n); }); });
    var playBtn = $('st-play'), playTxt = $('st-play-txt'), playing = false, acc = 0, last = 0;
    var loop = F0.loop(function (now) {
      if (!last) last = now; acc += now - last; last = now;
      if (acc >= 380) { acc = 0; if (N >= NT) { stop(); return; } set(N + 1); if (N >= NT) stop(); }
    });
    function stop() { if (!playing) return; playing = false; loop.stop(); pressed(playBtn, false); syncTxt(); var r = rows[N - 1], sy = $('st-say'); if (sy && r) sy.textContent = N + ' of ' + NT + ' transits stacked: signal-to-noise ' + fmt(r.snr, 1) + '.'; }
    function syncTxt() { playTxt.textContent = playing ? 'Pause' : (F0.motion() ? 'Play' : 'Add one'); playBtn.setAttribute('aria-label', playing ? 'Pause' : (F0.motion() ? 'Add transits one by one' : 'Add one transit')); }
    playBtn.addEventListener('click', function () {
      if (!S) return;
      if (!F0.motion()) { set(N >= NT ? 1 : N + 1); return; }
      if (playing) { stop(); return; }
      if (N >= NT) set(1);
      playing = true; acc = 0; last = 0; pressed(playBtn, true); syncTxt(); loop.start();
    });
    F0.onMotion(function () { if (!F0.motion()) stop(); syncTxt(); }); syncTxt();
    F0.whenVisible(cv, null, stop);
    C.resize(draw); F0.onTheme(draw);
    LC.then(function (d) {
      var o = d.tic4206066, t = [], f = [], yr = [];
      o.sectors.forEach(function (s) { var q = decode(s); for (var i = 0; i < q.t.length; i++) { t.push(q.t[i]); f.push(q.f[i]); yr.push(s.y); } });
      // baseline: every point outside both signals' transits
      var mu = 0, nn = 0, v = 0, i, inn = [];
      for (i = 0; i < t.length; i++) {
        var e1 = Math.round((t[i] - T01) / P1), x1 = t[i] - T01 - e1 * P1, e2 = Math.round((t[i] - T02) / P2), x2 = t[i] - T02 - e2 * P2;
        inn.push(Math.abs(x1) < W / 2 || Math.abs(x2) < W2 / 2);
        if (!inn[i]) { mu += f[i]; nn++; }
      }
      mu /= nn; for (i = 0; i < t.length; i++) if (!inn[i]) v += (f[i] - mu) * (f[i] - mu);
      var sig = Math.sqrt(v / nn), eps = {}, list = [];
      for (i = 0; i < t.length; i++) {
        var e = Math.round((t[i] - T01) / P1), x = t[i] - T01 - e * P1;
        if (Math.abs(x) > .25) continue;
        if (!eps[e]) eps[e] = { e: e, h: [], f: [], fin: [], year: yr[i] };
        eps[e].h.push(x * 24); eps[e].f.push(f[i] - mu);
        if (Math.abs(x) < W / 2) eps[e].fin.push(f[i]);
      }
      Object.keys(eps).forEach(function (k) { if (eps[k].fin.length) list.push(eps[k]); });
      list.sort(function (a, b) { return a.e - b.e; });
      S = { ep: list, sig: sig };
      NT = list.length;
      var sum = 0, n = 0;
      list.forEach(function (ep, j) {
        ep.fin.forEach(function (x) { sum += x; n++; });
        var dep = mu - sum / n, err = sig / Math.sqrt(n);
        rows.push({ n: n, dep: dep, err: err, snr: dep / err, year: ep.year });
      });
      rows.forEach(function (r, j) { r.rule = rows[NT - 1].snr * Math.sqrt((j + 1) / NT); });
      slider.max = NT;
      buildChart();
      if ('ResizeObserver' in window) new ResizeObserver(function () {
        var w = svg.parentNode.clientWidth;
        if (w && Math.abs(Math.max(300, Math.min(600, w)) - SW) > 6) { buildChart(); set(N); }
      }).observe(svg.parentNode);
      var tb = $('st-tbody');
      rows.forEach(function (r, j) {
        var tr = document.createElement('tr');
        [j + 1, r.year, r.n, grp(r.dep), grp(r.err), fmt(r.snr, 1), fmt(r.rule, 1)].forEach(function (x, k) { var td = document.createElement('td'); td.textContent = x; if (k !== 1) td.className = 'n'; tr.appendChild(td); });
        tb.appendChild(tr);
      });
      set(N);
    });
  })();

  /* =========================================================================
     4. Turn the sky upside down
     ========================================================================= */
  (function flip() {
    var c1 = $('fl-c1'), c2 = $('fl-c2'), c3 = $('fl-c3'); if (!c1) return;
    var C1 = F0.canvas(c1), C2 = F0.canvas(c2), C3 = F0.canvas(c3), D = null, k = 0, target = 0, flipped = false;
    var steps = document.querySelectorAll('.fl-steps button');
    function showStep(n) {
      steps.forEach(function (b) { pressed(b, +b.dataset.step === n); });
      [1, 2, 3].forEach(function (i) { $('fl-p' + i).hidden = i !== n; });
      requestAnimationFrame(function () { C1.fit(); C2.fit(); C3.fit(); drawAll(); });
    }
    steps.forEach(function (b) { b.addEventListener('click', function () { showStep(+b.dataset.step); }); });
    function axes(ctx, c, M, W0, H, yv, ticks, xticks, xs) {
      ctx.strokeStyle = c.grid; ctx.lineWidth = 1; ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      ticks.forEach(function (v) { ctx.beginPath(); ctx.moveTo(M.l, yv(v)); ctx.lineTo(W0 - M.r, yv(v)); ctx.stroke(); ctx.fillText(v === 0 ? '0' : (v > 0 ? '+' : '−') + grp(Math.abs(v)), M.l - 6, yv(v)); });
      ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      xticks.forEach(function (x) { ctx.fillText(x[1], xs(x[0]), H - 6); });
    }
    function draw1() {
      if (!D) return;
      var ctx = C1.ctx, c = colors(), W0 = C1.w, H = C1.h, L9 = D.l9, M = { l: 50, r: 12, t: 54, b: 24 };
      ctx.clearRect(0, 0, W0, H);
      var t0 = L9.t[0], t1 = L9.t[L9.t.length - 1];
      var xs = function (t) { return M.l + (t - t0) / (t1 - t0) * (W0 - M.l - M.r); };
      var s = 1 - 2 * k; // 1 as observed, -1 flipped
      var ys = function (v) { return M.t + (1 - (Math.max(-2000, Math.min(2000, v)) + 2000) / 4000) * (H - M.t - M.b); };
      var xt = []; for (var d = 0; d <= 10; d += 2) xt.push([t0 + d, d === 0 ? '0' : d + '']);
      axes(ctx, c, M, W0, H, ys, [-1500, -1000, -500, 0, 500, 1000, 1500].filter(function (v) { return v % 1000 === 0 || v === 0; }), xt, xs);
      // planet transit markers
      ctx.font = mono(11); ctx.textAlign = 'center';
      var marks = [];
      L9.pl.forEach(function (p) { p.tc.forEach(function (tc) { marks.push([xs(tc), p.name]); }); });
      marks.sort(function (a, b) { return a[0] - b[0]; });
      var lastX = -1e9, lift = 0;
      marks.forEach(function (m) {
        ctx.fillStyle = rgba(c.acc, .1); ctx.fillRect(m[0] - 5, M.t, 10, H - M.t - M.b);
        lift = m[0] - lastX < 12 ? (lift ? 0 : 11) : 0; lastX = m[0];
        ctx.fillStyle = c.ink2; ctx.fillText(m[1], m[0], M.t - 6 - lift);
      });
      for (var i = 0; i < L9.t.length; i++) {
        var y = ys(L9.f[i] * s), x = xs(L9.t[i]);
        if (L9.inT[i]) { ctx.fillStyle = c.acc; ctx.beginPath(); ctx.arc(x, y, 2.6, 0, Math.PI * 2); ctx.fill(); }
        else { ctx.fillStyle = rgba(c.ink3, c.dark ? .7 : .65); ctx.fillRect(x - 1.1, y - 1.1, 2.2, 2.2); }
      }
      $('fl-c1-tl').textContent = k > .5 ? 'L 98-59 · Sector 2 · flipped' : 'L 98-59 · Sector 2 · as observed';
    }
    function draw2() {
      if (!D) return;
      var ctx = C2.ctx, c = colors(), W0 = C2.w, H = C2.h, I = D.inv, M = { l: 50, r: 10, t: 50, b: 24 };
      ctx.clearRect(0, 0, W0, H);
      var t0 = I.t[0], t1 = I.t[I.t.length - 1];
      var xs = function (t) { return M.l + (t - t0) / (t1 - t0) * (W0 - M.l - M.r); };
      var ys = function (v) { return M.t + (1 - (Math.max(-10000, Math.min(3000, v)) + 10000) / 13000) * (H - M.t - M.b); };
      var xt = []; for (var d = 0; d <= 25; d += 5) xt.push([t0 + d, d + (d === 25 ? ' d' : '')]);
      axes(ctx, c, M, W0, H, ys, [-8000, -4000, 0], xt, xs);
      I.ev.forEach(function (e) { if (e < t0 || e > t1) return; var x = xs(e); ctx.fillStyle = rgba(c.acc, .14); ctx.fillRect(x - 6, M.t, 12, H - M.t - M.b); ctx.font = mono(11); ctx.fillStyle = c.ink2; ctx.textAlign = 'center'; ctx.fillText('event', x, M.t - 8); });
      for (var i = 0; i < I.t.length; i++) {
        var near = I.ev.some(function (e) { return Math.abs(I.t[i] - e) < .1; });
        if (near) { ctx.fillStyle = c.acc; ctx.beginPath(); ctx.arc(xs(I.t[i]), ys(I.f[i]), 2.4, 0, Math.PI * 2); ctx.fill(); }
        else { ctx.fillStyle = rgba(c.ink3, c.dark ? .6 : .55); ctx.fillRect(xs(I.t[i]) - 1, ys(I.f[i]) - 1, 2, 2); }
      }
    }
    function draw3() {
      if (!D) return;
      var ctx = C3.ctx, c = colors(), W0 = C3.w, H = C3.h, I = D.inv, M = { l: 50, r: 10, t: 50, b: 24 };
      ctx.clearRect(0, 0, W0, H);
      var xs = function (h) { return M.l + (h + 5) / 10 * (W0 - M.l - M.r); };
      var ys = function (v) { return M.t + (1 - (Math.max(-9500, Math.min(2000, v)) + 9500) / 11500) * (H - M.t - M.b); };
      axes(ctx, c, M, W0, H, ys, [-8000, -4000, 0], [[-4, '−4 h'], [0, '0'], [4, '+4 h']], xs);
      ctx.setLineDash([4, 4]); ctx.strokeStyle = c.ink2; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(xs(-I.dur / 2), ys(-I.depth)); ctx.lineTo(xs(I.dur / 2), ys(-I.depth)); ctx.stroke(); ctx.setLineDash([]);
      ctx.font = mono(11); ctx.fillStyle = c.ink2; ctx.textAlign = 'left'; ctx.fillText('fitted depth', xs(I.dur / 2) + 6, ys(-I.depth) + 4);
      ctx.strokeStyle = c.acc; ctx.lineWidth = 2; ctx.lineJoin = 'round'; ctx.beginPath();
      I.fx.forEach(function (h, i) { var X = xs(h), Y = ys(I.fy[i]); if (i) ctx.lineTo(X, Y); else ctx.moveTo(X, Y); });
      ctx.stroke();
      I.fx.forEach(function (h, i) { ctx.beginPath(); ctx.arc(xs(h), ys(I.fy[i]), 3.4, 0, Math.PI * 2); ctx.fillStyle = c.bg1; ctx.fill(); ctx.beginPath(); ctx.arc(xs(h), ys(I.fy[i]), 2.6, 0, Math.PI * 2); ctx.fillStyle = c.acc; ctx.fill(); });
    }
    function drawAll() { draw1(); draw2(); draw3(); }
    var btn = $('fl-flip'), cap = $('fl-cap1'), last = 0;
    var CAP = ['L 98-59 has three known planets. As observed, their transits are dips (marked). Press Flip.',
      'Flipped: the planets’ dips are now bumps, and a search for dips ignores them. The noise still wiggles both ways, so there are still “dips”; any the search finds here must be false alarms.'];
    var anim = F0.loop(function (now) {
      if (!last) last = now;
      var dt = (now - last) / 600; last = now;
      k += (target > k ? 1 : -1) * dt;
      if ((target === 1 && k >= 1) || (target === 0 && k <= 0)) { k = target; anim.stop(); }
      draw1();
    });
    btn.addEventListener('click', function () {
      flipped = !flipped; target = flipped ? 1 : 0; pressed(btn, flipped);
      btn.textContent = flipped ? 'Turn it back' : 'Flip it';
      cap.textContent = CAP[flipped ? 1 : 0];
      if (!F0.motion()) { k = target; draw1(); return; }
      last = 0; anim.start();
    });
    F0.whenVisible(c1, null, function () { if (k !== target) { k = target; anim.stop(); draw1(); } });
    [C1, C2, C3].forEach(function (C) { C.resize(drawAll); });
    F0.onTheme(drawAll);
    LC.then(function (d) {
      var q = decode(d.l9859), L9 = { t: q.t, f: q.f, inT: [], pl: [] };
      d.l9859.planets.forEach(function (p) {
        var tc = [], n0 = Math.ceil((q.t[0] - p.t0) / p.P), n1 = Math.floor((q.t[q.t.length - 1] - p.t0) / p.P);
        for (var n = n0; n <= n1; n++) tc.push(p.t0 + n * p.P);
        L9.pl.push({ name: p.name, P: p.P, tc: tc });
      });
      for (var i = 0; i < q.t.length; i++) L9.inT.push(L9.pl.some(function (p) { return p.tc.some(function (tc) { return Math.abs(q.t[i] - tc) < .03; }); }));
      var r = decode(d.inverted);
      D = { l9: L9, inv: { t: r.t, f: r.f, ev: d.inverted.events, fx: d.inverted.fold_x_h, fy: d.inverted.fold_ppm, depth: d.inverted.depth, dur: d.inverted.dur_h } };
      var tb = $('fl-tbody');
      L9.pl.forEach(function (p) {
        var s = 0, n = 0;
        for (var i = 0; i < q.t.length; i++) if (p.tc.some(function (tc) { return Math.abs(q.t[i] - tc) < .03; })) { s += q.f[i]; n++; }
        var tr = document.createElement('tr');
        ['L 98-59 ' + p.name, fmt(p.P, 4), p.tc.length, (s / n >= 0 ? '+' : '−') + grp(Math.abs(s / n)), (s / n <= 0 ? '+' : '−') + grp(Math.abs(s / n))].forEach(function (x, j) { var td = document.createElement('td'); td.textContent = x; if (j) td.className = 'n'; tr.appendChild(td); });
        tb.appendChild(tr);
      });
      drawAll();
    });
  })();

  /* =========================================================================
     6. The next transits: every predicted transit of a counted candidate in the next 48 hours, computed here
        from transits.json (period, a reference transit, and the published uncertainty), so it never goes stale
     ========================================================================= */
  (function nextTransits() {
    var cv = $('nt-canvas'), list = $('nt-list'); if (!cv || !list) return;
    var C = F0.canvas(cv), T = null, tz = 'utc', items = [], hov = -1, sel = -1, t0 = 0, timer = 0, visible = false;
    var MS = 864e5, AU_S = 499.00478, TTUTC = 69.184;
    function earthDot(jd, ra, dec) { // Earth's heliocentric position (AU) . the direction to the star; the Almanac's low-precision Sun
      var n = jd - 2451545, R2D = Math.PI / 180;
      var L = ((280.460 + 0.9856474 * n) % 360) * R2D, g = ((357.528 + 0.9856003 * n) % 360) * R2D;
      var lam = L + 1.915 * R2D * Math.sin(g) + 0.020 * R2D * Math.sin(2 * g), Rr = 1.00014 - 0.01671 * Math.cos(g) - 0.00014 * Math.cos(2 * g), eps = (23.439 - 0.0000004 * n) * R2D;
      var sx = Rr * Math.cos(lam), sy = Rr * Math.cos(eps) * Math.sin(lam), sz = Rr * Math.sin(eps) * Math.sin(lam), a = ra * R2D, d = dec * R2D;
      return -(sx * Math.cos(d) * Math.cos(a) + sy * Math.cos(d) * Math.sin(a) + sz * Math.sin(d));
    }
    function bjdToMs(bjd, ra, dec) { // BJD_TDB -> UTC (ms since 1970) at Earth's centre
      var jd = bjd - TTUTC / 86400;
      for (var i = 0; i < 2; i++) jd = bjd - TTUTC / 86400 - AU_S * earthDot(jd, ra, dec) / 86400;
      return (jd - 2440587.5) * MS;
    }
    function msToBjd(ms) { return ms / MS + 2440587.5 + TTUTC / 86400; } // without the light-time term (under 8.4 min)
    function sigma(i, k) { var s = T.s2[i]; return Math.sqrt(Math.max(0, s[0] + s[1] * k + s[2] * k * k)); }
    function compute(now) {
      var from = now - 3 * 3600e3, to = now + 48 * 3600e3, b0 = msToBjd(from) - .01, b1 = msToBjd(to) + .01, out = [];
      for (var i = 0; i < T.n; i++) {
        var P = T.P[i], k = Math.ceil((b0 - T.tc0[i]) / P);
        for (var bjd = T.tc0[i] + k * P; bjd <= b1; k++, bjd += P) {
          var ms = bjdToMs(bjd, T.ra[i], T.dec[i]);
          if (ms < from || ms > to) continue;
          out.push({ i: i, k: k, ms: ms, sig: sigma(i, k), half: T.dur[i] * 1800e3 });
        }
      }
      out.sort(function (a, b) { return a.ms - b.ms; });
      return out;
    }
    function two(n) { return ('0' + n).slice(-2); }
    function clock(ms) {
      var d = new Date(ms);
      if (tz === 'utc') return d.getUTCDate() + ' ' + MONS[d.getUTCMonth()] + ', ' + two(d.getUTCHours()) + ':' + two(d.getUTCMinutes()) + ' UTC';
      return d.getDate() + ' ' + MONS[d.getMonth()] + ', ' + two(d.getHours()) + ':' + two(d.getMinutes());
    }
    var MONS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    function until(ms, now, secs) {
      var d = Math.round((ms - now) / 1000);
      if (Math.abs(d) * 1000 < 1) return 'now';
      var a = Math.abs(d), h = Math.floor(a / 3600), m = Math.floor((a % 3600) / 60), s = a % 60;
      var txt = (h ? h + 'h ' + two(m) + 'm' : m + 'm') + (secs ? ' ' + two(s) + 's' : '');
      return d > 0 ? 'in ' + txt : txt + ' ago';
    }
    function layout() { var W0 = C.w, H0 = C.h, narrow = W0 < 560; return { L: narrow ? 10 : 14, R: W0 - (narrow ? 10 : 14), T: 44, B: H0 - 24, narrow: narrow }; } // T: below the corner captions
    var DMIN = Math.log10(100), DMAX = Math.log10(20000);
    function pos(it, Lo, now) {
      var x = Lo.L + (it.ms - (now - 3 * 3600e3)) / (51 * 3600e3) * (Lo.R - Lo.L);
      var dep = Math.max(DMIN, Math.min(DMAX, Math.log10(Math.max(1, T.depth[it.i]))));
      return [x, Lo.B - 6 - (dep - DMIN) / (DMAX - DMIN) * (Lo.B - Lo.T - 12)];
    }
    function draw() {
      if (!T || !C.w) return;
      var ctx = C.ctx, c = colors(), Lo = layout(), now = t0;
      ctx.clearRect(0, 0, C.w, C.h);
      ctx.strokeStyle = c.lineui; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(Lo.L, Lo.B); ctx.lineTo(Lo.R, Lo.B); ctx.stroke();
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textBaseline = 'alphabetic';
      // hour ticks, every 6 h (every 12 h when narrow)
      var step = Lo.narrow ? 12 : 6;
      for (var h = 0; h <= 48; h += step) {
        var x = Lo.L + (h + 3) / 51 * (Lo.R - Lo.L);
        ctx.strokeStyle = c.grid; ctx.beginPath(); ctx.moveTo(x, Lo.T); ctx.lineTo(x, Lo.B); ctx.stroke();
        ctx.textAlign = h === 48 ? 'right' : 'center'; ctx.fillText(h === 0 ? '' : '+' + h + ' h', x, C.h - 7);
      }
      // depth guides
      ctx.textAlign = 'left';
      [[300, '300 ppm'], [3000, '3,000 ppm']].forEach(function (g) { var y = Lo.B - 6 - (Math.log10(g[0]) - DMIN) / (DMAX - DMIN) * (Lo.B - Lo.T - 12); ctx.strokeStyle = c.grid; ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(Lo.L, y); ctx.lineTo(Lo.R, y); ctx.stroke(); ctx.setLineDash([]); });
      // transits in progress: a band for the time each is under way
      items.forEach(function (it, j) {
        var p = pos(it, Lo, now), live = Math.abs(it.ms - now) <= it.half;
        ctx.strokeStyle = rgba(c.acc, live ? .9 : .45); ctx.lineWidth = live ? 1.6 : 1;
        ctx.beginPath(); ctx.moveTo(p[0], Lo.B); ctx.lineTo(p[0], p[1]); ctx.stroke();
      });
      items.forEach(function (it, j) {
        var p = pos(it, Lo, now), r = Lo.narrow ? 3 : 3.6;
        shape(ctx, T.tier[it.i], p[0], p[1], r + 1.3); ctx.fillStyle = c.bg1; ctx.fill();
        shape(ctx, T.tier[it.i], p[0], p[1], r); ctx.fillStyle = rgba(c.acc, .95); ctx.fill();
      });
      [sel, hov].forEach(function (j, q) {
        if (j < 0 || !items[j]) return;
        var p = pos(items[j], Lo, now); ctx.strokeStyle = q ? c.ink : c.focus; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p[0], p[1], 9, 0, Math.PI * 2); ctx.stroke();
      });
      ctx.font = mono(11); ctx.textAlign = 'right'; ctx.lineJoin = 'round';
      [[300, '300 ppm'], [3000, '3,000 ppm']].forEach(function (g) { var y = Lo.B - 6 - (Math.log10(g[0]) - DMIN) / (DMAX - DMIN) * (Lo.B - Lo.T - 12) - 4; ctx.lineWidth = 4; ctx.strokeStyle = c.bg1; ctx.strokeText(g[1], Lo.R, y); ctx.fillStyle = c.ink2; ctx.fillText(g[1], Lo.R, y); });
      // now
      var xn = Lo.L + 3 / 51 * (Lo.R - Lo.L);
      ctx.strokeStyle = c.ink; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(xn, Lo.T - 8); ctx.lineTo(xn, Lo.B); ctx.stroke();
      ctx.fillStyle = c.ink; ctx.textAlign = 'left'; ctx.font = mono(11, 600); ctx.fillText('NOW', xn + 5, Lo.T - 2);
      ctx.font = mono(11); ctx.fillStyle = c.ink3; ctx.textAlign = 'left';
    }
    function rowHTML(it, now, secs) {
      var i = it.i, t = T.tier[i];
      return '<span class="nt-cd" data-ms="' + it.ms + '">' + until(it.ms, now, secs) + '</span>' +
        '<span class="nt-who"><svg aria-hidden="true"><use href="#sh-' + ['a', 'b', 'n', 'l'][t] + '"/></svg><b>TIC ' + T.tic[i] + '</b> · tier ' + T.tiers[t] + ' · every ' + fmt(T.P[i], 3) + ' d</span>' +
        '<span class="nt-when">' + clock(it.ms) + ' <small>± ' + Math.max(1, Math.round(it.sig)) + ' min</small></span>' +
        '<span class="nt-dep">' + grp(T.depth[i]) + ' ppm · ' + fmt(T.dur[i], 1) + ' h</span>' +
        '<button type="button" class="nt-go" data-j="' + items.indexOf(it) + '" aria-label="Show TIC ' + T.tic[i] + ' on the sky map">On the sky map</button>';
    }
    function renderList(secs) {
      var now = Date.now(), next = items.filter(function (it) { return it.ms >= t0; }).slice(0, 10);
      list.innerHTML = next.map(function (it) { return '<li data-j="' + items.indexOf(it) + '">' + rowHTML(it, now, secs) + '</li>'; }).join('');
      var inNow = items.filter(function (it) { return Math.abs(it.ms - now) <= it.half; }).length;
      $('nt-now').textContent = inNow + ' in transit now';
      $('nt-note').textContent = 'Computed ' + clock(t0) + (now > Date.parse(T.published_until) ? '. Past the published predictions (to ' + T.published_until.slice(0, 10) + '): these use the same periods, extended.' : '');
    }
    function tick() { // countdowns, once a second
      var now = Date.now();
      list.querySelectorAll('.nt-cd').forEach(function (e) { e.textContent = until(+e.getAttribute('data-ms'), now, true); });
      if (now - t0 > 60e3) refresh(); // the strip moves on once a minute
    }
    function startTimer() { if (!timer && visible && F0.motion()) timer = setInterval(tick, 1000); }
    function stopTimer() { if (timer) { clearInterval(timer); timer = 0; } }
    function refresh() {
      t0 = Date.now(); items = compute(t0); hov = -1; if (sel >= items.length) sel = -1;
      draw(); renderList(F0.motion());
    }
    function nearest(ev) {
      var r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, Lo = layout(), best = -1, bd = 14 * 14;
      items.forEach(function (it, j) { var p = pos(it, Lo, t0), d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y); if (d < bd) { bd = d; best = j; } });
      return best;
    }
    function tip(it) {
      var i = it.i;
      return '<div class="tip-k">TIC ' + T.tic[i] + ' · tier ' + T.tiers[T.tier[i]] + '</div><div class="tip-t">' + clock(it.ms) + ' ± ' + Math.max(1, Math.round(it.sig)) + ' min</div><div class="tip-note">' + until(it.ms, Date.now(), false) + ' · depth ' + grp(T.depth[i]) + ' ppm for ' + fmt(T.dur[i], 1) + ' h · predicted, not observed</div>';
    }
    cv.addEventListener('pointermove', function (ev) { if (!T) return; var j = nearest(ev); if (j !== hov) { hov = j; draw(); } if (j >= 0) F0.tip.show(tip(items[j]), ev.clientX, ev.clientY); else F0.tip.hide(); });
    cv.addEventListener('pointerleave', function () { hov = -1; F0.tip.hide(); draw(); });
    cv.addEventListener('click', function (ev) { if (!T) return; var j = nearest(ev); if (j >= 0) { sel = j; draw(); highlight(j); } });
    function highlight(j) { list.querySelectorAll('li').forEach(function (li) { li.classList.toggle('on', +li.getAttribute('data-j') === j); }); }
    list.addEventListener('click', function (e) {
      var b = e.target.closest('.nt-go'); if (!b) return;
      var it = items[+b.getAttribute('data-j')]; if (!it) return;
      sel = +b.getAttribute('data-j'); draw(); highlight(sel);
      if (SKY.show) SKY.show(T.tic[it.i], T.P[it.i]);
    });
    list.addEventListener('focusin', function (e) { var li = e.target.closest('li'); if (li) { sel = +li.getAttribute('data-j'); draw(); } });
    document.querySelectorAll('.nt-ctrl [data-tz]').forEach(function (b) { b.addEventListener('click', function () { tz = b.dataset.tz; document.querySelectorAll('.nt-ctrl [data-tz]').forEach(function (x) { pressed(x, x === b); }); if (T) { renderList(F0.motion()); } }); });
    $('nt-refresh').addEventListener('click', function () { if (T) refresh(); });
    F0.whenVisible(cv, function () { visible = true; if (T) { if (Date.now() - t0 > 60e3) refresh(); startTimer(); } }, function () { visible = false; stopTimer(); });
    F0.onMotion(function (on) { if (!T) return; if (on) startTimer(); else stopTimer(); renderList(on); });
    C.resize(draw); F0.onTheme(draw);
    F0.json('transits.json').then(function (d) {
      T = d; refresh(); startTimer();
      var tw = $('nt-twin');
      tw.addEventListener('toggle', function () {
        if (!tw.open) return;
        var now = Date.now();
        $('nt-table').innerHTML = '<table class="tbl"><caption>' + items.length + ' predicted transits from 3 hours ago to 48 hours ahead, computed ' + clock(t0) + ' (eumemic/exoplanets at ' + T.commit + ')</caption><thead><tr><th>Mid-transit</th><th>From now</th><th class="n">± 1σ (min)</th><th>TIC</th><th>Tier</th><th class="n">Period (d)</th><th class="n">Depth (ppm)</th><th class="n">Duration (h)</th></tr></thead><tbody>' +
          items.map(function (it) { var i = it.i; return '<tr><td>' + clock(it.ms) + '</td><td>' + until(it.ms, now, false) + '</td><td class="n">' + Math.max(1, Math.round(it.sig)) + '</td><td>' + T.tic[i] + '</td><td>' + T.tiers[T.tier[i]] + '</td><td class="n">' + fmt(T.P[i], 4) + '</td><td class="n">' + grp(T.depth[i]) + '</td><td class="n">' + fmt(T.dur[i], 2) + '</td></tr>'; }).join('') + '</tbody></table>';
      });
    }).catch(function () { list.innerHTML = '<li>The predictions could not be loaded. They are in the repository: candidates/predictions.csv.</li>'; });
  })();

  /* =========================================================================
     5. Funnel: exact log widths, an axis, and tooltips on hover and focus
     ========================================================================= */
  (function funnel() {
    var list = $('fn-list'); if (!list) return;
    var MAX = Math.log10(7459491);
    list.querySelectorAll('li').forEach(function (li) {
      var n = +li.querySelector('.fn-v').textContent.replace(/,/g, '');
      li.querySelector('.fn-tr i').style.setProperty('--w', (Math.log10(n) / MAX * 100).toFixed(2) + '%');
      li.setAttribute('aria-label', li.querySelector('.fn-k').textContent + ': ' + li.querySelector('.fn-v').textContent + '. ' + li.dataset.tip);
      var html = function () { return '<div class="tip-k">' + F0.esc(li.querySelector('.fn-k').textContent) + '</div><div class="tip-t">' + F0.esc(li.querySelector('.fn-v').textContent) + '</div><div class="tip-note">' + F0.esc(li.dataset.tip) + '</div>'; };
      li.addEventListener('pointermove', function (ev) { F0.tip.show(html(), ev.clientX, ev.clientY); });
      li.addEventListener('pointerleave', function () { F0.tip.hide(); });
      li.addEventListener('focus', function () { tipAt(li.querySelector('.fn-tr'), html()); });
      li.addEventListener('blur', function () { F0.tip.hide(); });
    });
    var ax = document.createElement('div'); ax.className = 'fn-axis'; ax.setAttribute('aria-hidden', 'true');
    var mid = '';
    [[1, '1'], [100, '100'], [1e4, '10K'], [1e6, '1M']].forEach(function (a) { mid += '<i style="left:' + (Math.log10(a[0]) / MAX * 100).toFixed(2) + '%">' + a[1] + '</i>'; });
    ax.innerHTML = '<span></span><span>' + mid + '</span><span></span>';
    list.parentNode.insertBefore(ax, list.nextSibling);
  })();
})();
