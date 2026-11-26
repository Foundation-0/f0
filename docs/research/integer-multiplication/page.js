/* Integer multiplication below n log n (research/integer-multiplication). Vanilla JS on window.F0.
   Five figures: the live reviewed κ (hero), every digit meets every digit (00), how much κ is worth (02),
   the κ staircase (03) and the budget that must stay under one (04). Every figure is SVG or HTML, styled by
   tokens in page.css, so a theme change restyles it without a redraw. */
(function () {
  'use strict';
  var F0 = window.F0;
  var NS = 'http://www.w3.org/2000/svg';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function el(n, a, txt) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (txt != null) e.textContent = txt; return e; }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  var esc = F0.esc;
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function utc(iso, dateOnly) {
    var d = new Date(iso); if (isNaN(d)) return String(iso || '');
    var s = d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear();
    if (dateOnly) return s;
    return s + ', ' + String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0') + ' UTC';
  }
  function minus(s) { return String(s).replace(/-/g, '−'); }
  function pow2html(e, dp) { return '2<sup>' + minus((+e).toFixed(dp == null ? 2 : dp)) + '</sup>'; }
  /* a×10^b in HTML from a positive number */
  function sci(x, sig) {
    if (!(x > 0)) return '0';
    var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e);
    var ms = m.toFixed(sig == null ? 1 : sig - 1);
    if (+ms >= 10) { e += 1; ms = (m / 10).toFixed(sig == null ? 1 : sig - 1); }
    ms = ms.replace(/\.0+$/, '');
    return ms + ' &times; 10<sup>' + minus(e) + '</sup>';
  }
  function sciTxt(x) { var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e); return m.toFixed(1).replace(/\.0$/, '') + ' times 10 to the ' + e; }
  function grp(s) { return String(s).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function supSvg(t, base, exp, opts) { /* base<sup>exp</sup> inside an SVG <text> */
    opts = opts || {};
    t.appendChild(document.createTextNode(base));
    var s = el('tspan', { dy: -5, 'font-size': opts.small || 9 }, exp); t.appendChild(s);
    if (opts.after) { var a = el('tspan', { dy: 5 }, opts.after); t.appendChild(a); }
    return t;
  }

  /* ======================================================================
     The live reviewed κ. F0.kappa(): the race's selected-result.json fetched now, else this site's
     feed.json. We keep this page's own snapshot (selected-result.json @ 0a31ad884) whenever the
     fallback is older than it, and always say which one is shown and when.
     ====================================================================== */
  var SNAP = { decimal: '0.001672660197076918', kappa: '836330098538459/500000000000000000', pr: 1094, at: '2026-10-13T18:45:23Z', source: 'snapshot' };
  var PR_AUTHOR = { 1094: 'Rohan Arun' };
  var MEMBERS = {};
  var liveFns = [], LIVE = null;
  function onLive(fn) { if (LIVE) fn(LIVE); else liveFns.push(fn); }

  function initLive() {
    drawRuler(Math.log2(+SNAP.decimal));
    F0.json(F0.root + 'data/members.json').then(function (m) {
      (m.members || []).forEach(function (x) { MEMBERS[x.login.toLowerCase()] = x.name; });
    }).catch(function () {}).then(function () {
      return F0.kappa ? F0.kappa() : Promise.reject(new Error('no F0.kappa'));
    }).then(function (k) {
      var use = k, why = '';
      if (k.source !== 'live' && !(Date.parse(k.at) > Date.parse(SNAP.at))) { use = SNAP; why = k.source === 'feed' ? ' (live file unreachable; this site’s feed is older)' : ' (live file unreachable)'; }
      if (!use || !/^0\.\d+$/.test(String(use.decimal))) use = SNAP;
      renderLive(use, why);
    }).catch(function (e) { console.warn('κ:', e); renderLive(SNAP, ' (live file unreachable)'); });
  }

  function renderLive(use, why) {
    var v = parseFloat(use.decimal), lg = Math.log2(v);
    var live = use.source === 'live';
    $('#lk-v').textContent = use.decimal;
    if (/^\d+\/\d+$/.test(String(use.kappa || ''))) $('#lk-frac').textContent = String(use.kappa).replace('/', ' / ');
    $('#lk-log').innerHTML = '&kappa; &asymp; ' + pow2html(lg);
    var l10 = Math.log10(v) + 182 * Math.LOG10E * Math.LN2;
    var e = Math.floor(l10), m = Math.pow(10, l10 - e);
    $('#lk-x').innerHTML = m.toFixed(2) + ' &times; 10<sup>' + e + '</sup> times larger';
    var when = $('#lk-when'), chip = $('#lk-chip'), dot = $('.dot', chip);
    if (live) { when.textContent = 'live · fetched ' + utc(use.at); dot.className = 'dot live'; chip.href = 'https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json'; }
    else if (use.source === 'feed') { when.textContent = 'this site’s feed.json · ' + utc(use.at); dot.className = 'dot stale'; chip.href = F0.root + 'feed.json'; }
    else { when.textContent = 'snapshot · ' + utc(use.at) + (why || ''); dot.className = 'dot stale'; }
    var pr = use.pr;
    function who(login) { if (!login) return ''; var n = MEMBERS[login.toLowerCase()]; return n ? ' by founding member ' + esc(n) : ' by @' + esc(login); }
    function setPr(login) {
      $('#lk-pr').innerHTML = pr ? '<a href="https://github.com/CrocSwap/integer-mult-bounds/pull/' + (+pr) + '">PR #' + (+pr) + '</a>' + who(login) : 'see the record file';
    }
    setPr(PR_AUTHOR[pr]);
    if (pr && !PR_AUTHOR[pr]) {
      fetch('https://api.github.com/repos/CrocSwap/integer-mult-bounds/pulls/' + (+pr)).then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d && d.user && d.user.login) { PR_AUTHOR[pr] = d.user.login; setPr(d.user.login); } }).catch(function () {});
    }
    drawRuler(lg);
    /* the credit lines date the record; a live read can confirm it or say it has moved on */
    var cr = $('#credit-rec'), rr = $('#rohan-rec');
    if (live && cr && rr) {
      if (+pr === 1094) { cr.textContent = 'holds the reviewed record (PR #1094, read live ' + utc(use.at, true) + ')'; rr.textContent = '; it is still the record (read live ' + utc(use.at, true) + ')'; }
      else if (pr) { cr.textContent = 'held the reviewed record from 13 Oct 2026 (PR #1094); the live record is now PR #' + (+pr); rr.textContent = '; the live record has since moved to PR #' + (+pr); }
    }
    LIVE = { decimal: String(use.decimal), kappa: use.kappa, v: v, log2: lg, pr: pr, at: use.at, source: use.source || 'snapshot' };
    liveFns.splice(0).forEach(function (f) { try { f(LIVE); } catch (err) { console.error(err); } });
  }

  var rulerLg = null;
  function drawRuler(lgNow, prog) {
    var svg = $('#lk-ruler'); if (!svg) return; clear(svg);
    if (lgNow != null) rulerLg = lgNow; lgNow = rulerLg;
    /* prog < 1 only during the one-shot entrance: the saving slides from the paper's 2^-182 to the record */
    var pr = prog == null ? 1 : 1 - Math.pow(1 - prog, 3), lgShow = -182 + (lgNow + 182) * pr;
    /* sized to its box, so its text is drawn at true size; a narrow box gets fewer, shorter labels */
    var W = Math.max(260, Math.min(640, Math.round(svg.getBoundingClientRect().width) || 520)), narrow = W < 460, H = 92;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    var x0 = 14, x1 = W - 14, lo = -190, hi = 0, y = 54;
    function X(l) { return x0 + (l - lo) / (hi - lo) * (x1 - x0); }
    svg.appendChild(el('line', { x1: x0, y1: y, x2: x1, y2: y, class: 'axis' }));
    for (var t = -180; t <= 0; t += 30) {
      svg.appendChild(el('line', { x1: X(t), y1: y, x2: X(t), y2: y + 5, class: 'tick' }));
      if (narrow && t % 60 !== 0) continue;
      var tx = el('text', { x: X(t), y: y + 19, 'text-anchor': 'middle' });
      if (t === 0) tx.textContent = '1'; else supSvg(tx, '2', minus(t));
      svg.appendChild(tx);
    }
    var recs = [-182, -107.09, -78, -59, -33.49, -31, -30, -14.65, -14.26, -11.08, -10.56, -10.43, -9.36, -9.29, -9.26, -9.23];
    svg.appendChild(el('line', { x1: X(-182), y1: y, x2: X(lgShow), y2: y, class: 'span' }));
    recs.forEach(function (l) { if (l <= lgShow + 1e-9) svg.appendChild(el('line', { x1: X(l), y1: y - 6, x2: X(l), y2: y + 6, class: 'rec' })); });
    svg.appendChild(el('circle', { cx: X(-182), cy: y, r: 5, class: 'paper' }));
    svg.appendChild(el('circle', { cx: X(lgShow), cy: y, r: 6.5, class: 'now' }));
    svg.appendChild(el('text', { x: X(-182) - 4, y: y - 16, class: 'lbl' }, narrow ? 'paper' : 'the paper \u00b7 dated 23 Sep'));
    svg.appendChild(el('text', { x: X(-107.09) - (narrow ? 0 : 4), y: y - 16, class: 'lbl', 'text-anchor': narrow ? 'middle' : 'start' }, narrow ? '7 Oct' : 'day one \u00b7 7 Oct'));
    if (pr >= 1) { var c = el('text', { x: X(lgNow) + 6, y: y - 16, class: 'lbl-now', 'text-anchor': 'end' }); supSvg(c, 'now \u00b7 2', minus(lgNow.toFixed(2))); svg.appendChild(c); }
    svg.appendChild(el('text', { x: x0, y: y + 36 }, narrow ? 'halvings below 1 (log\u2082 \u03ba)' : 'halvings below 1 (log\u2082 \u03ba); every tick is 30 halvings'));
    svg.setAttribute('aria-label', 'A ruler of halvings from 2 to the minus 190 on the left to 1 on the right. The paper\u2019s saving sits at 2 to the minus 182; the race\u2019s first day reached 2 to the minus 107; the reviewed record now sits at about 2 to the minus ' + Math.abs(lgNow).toFixed(2) + ', near the right end.');
  }
  (function () {
    var svg = $('#lk-ruler');
    if (svg && F0.enter) F0.enter(svg, function (t) { if (rulerLg != null) drawRuler(null, t); }, { duration: 1200, threshold: 0.5 });
  })();
  (function () {
    var svg = $('#lk-ruler'), w0 = 0;
    if (svg && 'ResizeObserver' in window) new ResizeObserver(function () { var w = Math.round(svg.getBoundingClientRect().width); if (w !== w0 && rulerLg != null) { w0 = w; drawRuler(); } }).observe(svg);
  })();

  /* ======================================================================
     00 Every digit meets every digit: the school grid and Karatsuba's 3-of-4 pattern.
     ====================================================================== */
  var PI = '3141592653589793238462643383279502884197169399375105820974944592';
  var EE = '2718281828459045235360287471352662497757247093699959574966967627';
  function initGrid() {
    var svg = $('#g-svg'); if (!svg) return;
    var rng = $('#g-n'), out = $('#g-n-out'), play = $('#g-play'), ro = $('#g-out'), desc = $('#g-desc'), prodV = $('#g-prod-v');
    var NS_ = [2, 4, 8, 16, 32, 64];
    var st = { n: 4, method: 'school', k: Infinity, playing: false, t0: 0 };
    function lit(i, j) { return st.method === 'school' || (i & ~j) === 0; }
    function order() { var o = []; for (var i = 0; i < st.n; i++) for (var j = 0; j < st.n; j++) if (lit(i, j)) o.push(i * st.n + j); return o; }
    function total() { return st.method === 'school' ? st.n * st.n : Math.pow(3, Math.log2(st.n)); }
    function draw() {
      clear(svg);
      var n = st.n, lab = n <= 16, pad = lab ? 30 : 4, size = 400 - pad, s = size / n, gap = n <= 16 ? 2 : n <= 32 ? 1.2 : .8;
      var a = PI.slice(0, n), b = EE.slice(0, n), ord = order(), shown = Math.min(st.k, ord.length);
      var on = {}; for (var q = 0; q < shown; q++) on[ord[q]] = 1;
      var dOn = '', dOff = '', dSkip = '';
      for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) {
        var x = pad + j * s + gap / 2, y = pad + i * s + gap / 2, w = s - gap;
        var r = 'M' + x.toFixed(2) + ' ' + y.toFixed(2) + 'h' + w.toFixed(2) + 'v' + w.toFixed(2) + 'h' + (-w).toFixed(2) + 'z';
        if (on[i * n + j]) dOn += r; else if (lit(i, j)) dOff += r; else dSkip += r;
      }
      svg.appendChild(el('path', { d: dSkip, class: 'cell-off' }));
      svg.appendChild(el('path', { d: dOff, class: 'cell' }));
      svg.appendChild(el('path', { d: dOn, class: st.method === 'school' ? 'cell-on' : 'cell-k' }));
      if (lab) {
        var fs = n <= 4 ? 18 : n <= 8 ? 15 : 11;
        for (var c = 0; c < n; c++) {
          svg.appendChild(el('text', { x: pad + c * s + s / 2, y: pad - 9, 'text-anchor': 'middle', 'font-size': fs, class: 'dig-top' }, a[c]));
          svg.appendChild(el('text', { x: pad - 10, y: pad + c * s + s / 2 + fs * .36, 'text-anchor': 'middle', 'font-size': fs, class: 'dig-side' }, b[c]));
        }
      }
      if (st.method === 'school' && n <= 8) {
        var pf = n <= 2 ? 30 : n <= 4 ? 22 : 14;
        for (var i2 = 0; i2 < n; i2++) for (var j2 = 0; j2 < n; j2++) if (on[i2 * n + j2]) {
          svg.appendChild(el('text', { x: pad + j2 * s + s / 2, y: pad + i2 * s + s / 2 + pf * .36, 'text-anchor': 'middle', 'font-size': pf, class: 'prod' }, String(+a[j2] * +b[i2])));
        }
      }
      if (st.method === 'karatsuba' && n >= 4) {
        var h = size / 2;
        [[0, 0], [0, 1], [1, 0], [1, 1]].forEach(function (p) { svg.appendChild(el('rect', { x: pad + p[1] * h + 1, y: pad + p[0] * h + 1, width: h - 2, height: h - 2, class: 'blk' })); });
      }
      if (st.playing && shown > 0 && shown <= ord.length) {
        var cur = ord[shown - 1], ci = Math.floor(cur / n), cj = cur % n;
        svg.appendChild(el('rect', { x: pad + cj * s, y: pad + ci * s, width: s, height: s, class: 'cur' }));
      }
      var tot = total();
      ro.textContent = (shown < ord.length ? grp(shown) + ' of ' : '') + grp(tot) + ' products' + (st.method === 'karatsuba' ? ' (school: ' + grp(n * n) + ')' : '');
      var lv = Math.log2(n);
      desc.innerHTML = st.method === 'school'
        ? 'School method, ' + n + ' digits: ' + n + ' &times; ' + n + ' = ' + grp(n * n) + ' digit products. Karatsuba needs 3<sup>' + lv + '</sup> = ' + grp(tot === n * n ? Math.pow(3, lv) : tot) + '.'
        : 'Karatsuba, ' + n + ' digits: ' + grp(tot) + ' of the ' + grp(n * n) + ' products (3 of every 4, at each of ' + lv + ' level' + (lv > 1 ? 's' : '') + '). Dashed blocks: the four half-size products. Bottom left is never computed; top right stands for the one combined product (A+B)(C+D).';
      svg.setAttribute('aria-label', desc.textContent);
    }
    function product() {
      var n = st.n, a = PI.slice(0, n), b = EE.slice(0, n), p = '';
      try { p = (BigInt(a) * BigInt(b)).toString(); } catch (e) { p = ''; }
      prodV.textContent = grp(a) + ' × ' + grp(b) + ' = ' + grp(p);
    }
    var loop = F0.loop(function (now) {
      var ord = order(), dur = Math.min(6000, ord.length * 280);
      var k = Math.floor((now - st.t0) / dur * ord.length) + 1;
      if (k >= ord.length) { st.k = Infinity; stop(); draw(); return; }
      if (k !== st.k) { st.k = k; draw(); }
    });
    var visible = true;
    F0.whenVisible(svg, function () { visible = true; if (st.playing) loop.start(); }, function () { visible = false; loop.stop(); });
    function stop() { st.playing = false; loop.stop(); play.setAttribute('aria-pressed', 'false'); play.setAttribute('aria-label', 'Play: light the products one at a time'); }
    function start() {
      if (!F0.motion()) { /* motion off: step one row per press */
        var ord = order(); var k = st.k === Infinity || st.k >= ord.length ? 0 : st.k;
        var row = Math.floor((ord[k] || 0) / st.n); while (k < ord.length && Math.floor(ord[k] / st.n) === row) k++;
        st.k = k >= ord.length ? Infinity : k; draw(); return;
      }
      st.playing = true; st.k = 0; st.t0 = performance.now(); play.setAttribute('aria-pressed', 'true'); play.setAttribute('aria-label', 'Pause');
      if (visible) loop.start();
    }
    play.addEventListener('click', function () { if (st.playing) { stop(); st.k = Infinity; draw(); } else start(); });
    F0.onMotion(function (on) { if (!on && st.playing) { stop(); st.k = Infinity; draw(); } });
    rng.addEventListener('input', function () {
      st.n = NS_[+rng.value]; out.textContent = st.n; rng.setAttribute('aria-valuetext', st.n + ' digits');
      if (st.playing) { st.k = 0; st.t0 = performance.now(); } else st.k = Infinity;
      draw(); product();
    });
    $$('[data-g-method]').forEach(function (b) {
      b.addEventListener('click', function () {
        st.method = b.getAttribute('data-g-method');
        $$('[data-g-method]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        if (st.playing) { st.k = 0; st.t0 = performance.now(); } else st.k = Infinity;
        draw();
      });
    });
    draw(); product();
  }

  /* ======================================================================
     01 Multiply by sliding: the convolution behind every fast method, then the cost of doing it the slow way
     against the FFT route, which does all the sliding at once.
     ====================================================================== */
  function initSlide() {
    var svg = $('#sl-svg'); if (!svg) return;
    var rng = $('#sl-s'), rout = $('#sl-s-out'), read = $('#sl-read'), desc = $('#sl-desc'), play = $('#sl-play'), carryB = $('#sl-carry');
    var st = { n: 4, s: 3, carried: false, carryK: 0, playing: false, t0: 0, cs: 40, x0: 0 };
    function digs() { return { a: PI.slice(0, st.n).split('').map(Number), b: EE.slice(0, st.n).split('').map(Number) }; }
    function sums() { var d = digs(), c = []; for (var k = 0; k <= 2 * st.n - 2; k++) { var t = 0; for (var i = 0; i < st.n; i++) { var j = k - i; if (j >= 0 && j < st.n) t += d.a[i] * d.b[j]; } c.push(t); } return c; }
    function pairs(k) { var d = digs(), o = []; for (var i = 0; i < st.n; i++) { var j = k - i; if (j >= 0 && j < st.n) o.push({ i: i, j: j, p: d.a[i] * d.b[j], a: d.a[i], b: d.b[j] }); } return o; }
    function carries() { /* right to left: value, digit, carry out */
      var c = sums(), out = [], cy = 0;
      for (var k = c.length - 1; k >= 0; k--) { var v = c[k] + cy; out.unshift({ k: k, v: v, d: v % 10, cin: cy, cout: Math.floor(v / 10) }); cy = Math.floor(v / 10); }
      return { cols: out, lead: cy };
    }
    function product() { return (BigInt(PI.slice(0, st.n)) * BigInt(EE.slice(0, st.n))).toString(); }
    function pairTxt(k) { return pairs(k).map(function (q) { return q.a + '×' + q.b; }).join(' + '); }
    function draw() {
      clear(svg);
      var W = Math.max(280, Math.min(640, Math.round(svg.parentNode.getBoundingClientRect().width - 16) || 440));
      var narrow = W < 420, labW = narrow ? 0 : 74;
      /* six digits need 16 cells: on a phone that is too small to read, so the choice stops at four */
      var six = $('[data-sl-n="6"]'); if (six) six.hidden = narrow;
      if (narrow && st.n > 4) { st.n = 4; st.s = Math.min(st.s, 6); $$('[data-sl-n]').forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-sl-n') === '4' ? 'true' : 'false'); }); }
      var n = st.n, C = 3 * n - 2;
      var cs = Math.max(18, Math.min(44, Math.floor((W - labW - 6) / C))); st.cs = cs;
      var x0 = labW + Math.max(0, Math.floor((W - labW - C * cs) / 2)); st.x0 = x0;
      var fs = Math.max(12, Math.min(20, Math.round(cs * .5))), pfs = Math.max(11, Math.min(14, Math.round(cs * .34)));
      var top = narrow ? 18 : 8, yA = top, yB = yA + cs + 46, yS = yB + cs + (narrow ? 34 : 30), yR = yS + cs + (narrow ? 34 : 30), H = yR + cs + 8;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      function X(c) { return x0 + (c + n - 1) * cs; }
      function lab(y, t, sub) {
        if (narrow) svg.appendChild(el('text', { x: X(-(n - 1)) + 2, y: y - 5, class: 'sl-lab' }, t));
        else { svg.appendChild(el('text', { x: 4, y: y + cs / 2 + (sub ? -2 : 4), class: 'sl-lab' }, t)); if (sub) svg.appendChild(el('text', { x: 4, y: y + cs / 2 + 12, class: 'sl-lab' }, sub)); }
      }
      var d = digs(), c = sums(), s = st.s, ov = pairs(s);
      var lit = {}; ov.forEach(function (q) { lit[q.i] = q; });
      /* rows */
      lab(yA, 'π', narrow ? '' : 'digits'); lab(yB, narrow ? 'e, backwards' : 'e,', narrow ? '' : 'backwards');
      lab(yS, narrow ? 'column sums' : 'column', narrow ? '' : 'sums');
      for (var i = 0; i < n; i++) {
        var on = !!lit[i];
        svg.appendChild(el('rect', { x: X(i) + 1, y: yA, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-a' + (on ? ' on' : ''), 'data-tip': 'π digit ' + (i + 1) + ': ' + d.a[i] }));
        svg.appendChild(el('text', { x: X(i) + cs / 2, y: yA + cs / 2 + fs * .36, 'font-size': fs, class: 'sl-dig' }, String(d.a[i])));
      }
      for (var j = 0; j < n; j++) {
        var cx = s - j, onb = cx >= 0 && cx < n;
        svg.appendChild(el('rect', { x: X(cx) + 1, y: yB, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-b' + (onb ? ' on' : ''), 'data-tip': 'e digit ' + (j + 1) + ': ' + d.b[j] }));
        svg.appendChild(el('text', { x: X(cx) + cs / 2, y: yB + cs / 2 + fs * .36, 'font-size': fs, class: 'sl-dig' }, String(d.b[j])));
      }
      /* the drag handle hint under the sliding row */
      svg.appendChild(el('rect', { x: X(s - n + 1), y: yB - 4, width: n * cs, height: cs + 8, class: 'sl-grab' }));
      /* products of the overlapping pairs, each falling into this position's column */
      var sx = X(s) + cs / 2;
      ov.forEach(function (q) {
        var x = X(q.i) + cs / 2, my = yA + cs + 23;
        svg.appendChild(el('line', { x1: x, y1: yA + cs, x2: x, y2: my - pfs * .8, class: 'sl-link' }));
        svg.appendChild(el('line', { x1: x, y1: my + 5, x2: x, y2: yB, class: 'sl-link' }));
        svg.appendChild(el('text', { x: x, y: my + pfs * .36, 'font-size': pfs, class: 'sl-prod', 'data-tip': q.a + ' × ' + q.b + ' = ' + q.p }, String(q.p)));
      });
      svg.appendChild(el('path', { d: 'M' + sx + ' ' + (yB + cs + 2) + 'V' + (yS - 4), class: 'sl-drop' }));
      svg.appendChild(el('path', { d: 'M' + (sx - 4) + ' ' + (yS - 9) + 'L' + sx + ' ' + (yS - 3) + 'L' + (sx + 4) + ' ' + (yS - 9), class: 'sl-drop' }));
      /* column sums: done, this one, and the ones still to come */
      for (var k = 0; k <= 2 * n - 2; k++) {
        var done = k < s || st.carried, cur = k === s && !st.carried;
        svg.appendChild(el('rect', { x: X(k) + 1, y: yS, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-s' + (cur ? ' cur' : done ? ' done' : ' todo'), 'data-tip': done || cur ? 'Column ' + (k + 1) + ': ' + pairTxt(k) + ' = ' + c[k] : 'Column ' + (k + 1) + ': not reached yet' }));
        if (done || cur) svg.appendChild(el('text', { x: X(k) + cs / 2, y: yS + cs / 2 + Math.min(fs, cs * .42) * .36, 'font-size': Math.max(11, c[k] >= 100 ? Math.min(fs, Math.round(cs * .36)) : Math.min(fs, Math.round(cs * .44))), class: 'sl-dig' + (cur ? ' cur' : '') }, String(c[k])));
      }
      /* after "Carry": the product's digits, right to left (before it, the row waits, dashed) */
      if (!st.carried) {
        lab(yR, narrow ? 'product: press Carry' : 'product:', narrow ? '' : 'press Carry');
        for (var k2 = 0; k2 <= 2 * n - 2; k2++) svg.appendChild(el('rect', { x: X(k2) + 1, y: yR, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-r' }));
      }
      if (st.carried) {
        lab(yR, 'product', '');
        var cr = carries(), shown = st.carryK;
        cr.cols.forEach(function (q) {
          var vis = q.k >= (2 * n - 1) - shown;
          svg.appendChild(el('rect', { x: X(q.k) + 1, y: yR, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-r' + (vis ? ' on' : ''), 'data-tip': vis ? 'Column ' + (q.k + 1) + ': ' + c[q.k] + (q.cin ? ' + carried ' + q.cin : '') + ' = ' + q.v + ', write ' + q.d + (q.cout ? ', carry ' + q.cout : '') : '' }));
          if (vis) svg.appendChild(el('text', { x: X(q.k) + cs / 2, y: yR + cs / 2 + fs * .36, 'font-size': fs, class: 'sl-dig' }, String(q.d)));
          if (vis && q.cout) svg.appendChild(el('text', { x: X(q.k) - 1, y: yR - 5, 'font-size': 11, class: 'sl-carry' }, '+' + q.cout));
        });
        if (shown >= 2 * n - 1 && cr.lead) String(cr.lead).split('').reverse().forEach(function (ch, m) {
          svg.appendChild(el('rect', { x: X(-1 - m) + 1, y: yR, width: cs - 2, height: cs, rx: 2, class: 'sl-cell sl-r on' }));
          svg.appendChild(el('text', { x: X(-1 - m) + cs / 2, y: yR + cs / 2 + fs * .36, 'font-size': fs, class: 'sl-dig' }, ch));
        });
      }
      /* readouts */
      rng.max = 2 * n - 2; rng.value = s;
      rout.textContent = (s + 1) + ' of ' + (2 * n - 1);
      rng.setAttribute('aria-valuetext', 'position ' + (s + 1) + ' of ' + (2 * n - 1));
      var A = PI.slice(0, n), B = EE.slice(0, n), P = product();
      if (st.carried) {
        var cr2 = carries();
        read.textContent = st.carryK >= 2 * n - 1
          ? 'Carried from the right: ' + cr2.cols.slice().reverse().map(function (q) { return (q.cin ? c[q.k] + '+' + q.cin : String(c[q.k])) + ' → ' + q.d; }).join(', ') + (cr2.lead ? ', and ' + cr2.lead + ' left over' : '') + '. ' + grp(A) + ' × ' + grp(B) + ' = ' + grp(P) + '.'
          : 'Carrying from the right…';
      } else read.textContent = 'Position ' + (s + 1) + ' of ' + (2 * n - 1) + ': ' + pairTxt(s).replace(/×/g, '×') + ' = ' + c[s] + ', written in column ' + (s + 1) + '.';
      desc.textContent = A + ' × ' + B + ' by sliding: the column sums are ' + c.join(', ') + '; carrying turns them into ' + grp(P) + '.';
      svg.setAttribute('aria-label', (st.carried ? 'After carrying: ' : 'Sliding, ') + read.textContent);
      carryB.textContent = st.carried ? 'Undo carry' : 'Carry';
    }
    function setS(v) { st.s = Math.max(0, Math.min(2 * st.n - 2, v)); st.carried = false; draw(); }
    var loop = F0.loop(function (now) {
      if (st.carried && st.carryK < 2 * st.n - 1) { var kk = Math.floor((now - st.t0) / 260) + 1; if (kk !== st.carryK) { st.carryK = Math.min(2 * st.n - 1, kk); draw(); } if (st.carryK >= 2 * st.n - 1 && !st.playing) loop.stop(); return; }
      if (!st.playing) { loop.stop(); return; }
      var k = Math.floor((now - st.t0) / 750);
      if (k > 2 * st.n - 2) { stopPlay(); st.s = 2 * st.n - 2; startCarry(); return; }
      if (k !== st.s) { st.s = k; draw(); }
    });
    var visible = true;
    F0.whenVisible(svg, function () { visible = true; if (st.playing || (st.carried && st.carryK < 2 * st.n - 1)) loop.start(); }, function () { visible = false; loop.stop(); });
    function startCarry() {
      st.carried = true;
      if (F0.motion()) { st.carryK = 0; st.t0 = performance.now(); if (visible) loop.start(); } else st.carryK = 2 * st.n - 1;
      draw();
    }
    function finishAll() { if (st.carried) st.carryK = 2 * st.n - 1; }
    function stopPlay() { st.playing = false; play.setAttribute('aria-pressed', 'false'); }
    play.addEventListener('click', function () {
      if (st.playing) { stopPlay(); loop.stop(); draw(); return; }
      if (!F0.motion()) { /* motion off: one position per press */ if (st.carried || st.s >= 2 * st.n - 2) { if (!st.carried) startCarry(); else setS(0); } else setS(st.s + 1); return; }
      st.carried = false; st.playing = true; st.s = 0; st.t0 = performance.now(); play.setAttribute('aria-pressed', 'true'); draw(); if (visible) loop.start();
    });
    F0.onMotion(function (on) { if (!on) { if (st.playing) { stopPlay(); } finishAll(); loop.stop(); draw(); } });
    $('#sl-back').addEventListener('click', function () { stopPlay(); setS(st.s - 1); });
    $('#sl-next').addEventListener('click', function () { stopPlay(); setS(st.s + 1); });
    rng.addEventListener('input', function () { stopPlay(); setS(+rng.value); });
    carryB.addEventListener('click', function () { stopPlay(); if (st.carried) { st.carried = false; loop.stop(); draw(); } else startCarry(); });
    $$('[data-sl-n]').forEach(function (b) {
      b.addEventListener('click', function () {
        stopPlay(); st.n = +b.getAttribute('data-sl-n'); st.s = st.n - 1; st.carried = false;
        $$('[data-sl-n]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        draw();
      });
    });
    /* drag the lower row: one cell of movement is one position */
    var drag = null;
    svg.addEventListener('pointerdown', function (ev) {
      if (!ev.target.classList || !(ev.target.classList.contains('sl-grab') || ev.target.classList.contains('sl-b'))) return;
      drag = { x: ev.clientX, s: st.s, k: svg.getBoundingClientRect().width / (+svg.getAttribute('viewBox').split(' ')[2]) };
      stopPlay(); try { svg.setPointerCapture(ev.pointerId); } catch (e) {} ev.preventDefault();
    });
    svg.addEventListener('pointermove', function (ev) {
      if (drag) { var v = drag.s + Math.round((ev.clientX - drag.x) / (st.cs * drag.k)); if (v !== st.s) setS(v); return; }
      var t = ev.target.closest ? ev.target.closest('[data-tip]') : null, tip = t && t.getAttribute('data-tip');
      if (tip) F0.tip.show('<p class="tip-t">' + esc(tip) + '</p>', ev.clientX, ev.clientY); else F0.tip.hide();
    });
    function endDrag() { drag = null; }
    svg.addEventListener('pointerup', endDrag); svg.addEventListener('pointercancel', endDrag);
    svg.addEventListener('pointerleave', function () { F0.tip.hide(); });
    var w0 = 0;
    if ('ResizeObserver' in window) new ResizeObserver(function () { var w = Math.round(svg.parentNode.getBoundingClientRect().width); if (w !== w0) { w0 = w; draw(); if (!$('#sl-p-count').hidden) drawCost(); } }).observe(svg.parentNode.parentNode.parentNode);

    /* ---- Count the work ---- */
    var cost = $('#sl-cost'), nr = $('#sl-n');
    function human(sec) {
      if (sec < 1e-3) return 'under a millisecond';
      if (sec < 1) return (sec * 1000).toPrecision(2).replace(/\.0+$/, '') + ' ms';
      if (sec < 120) return (+sec.toPrecision(2)) + ' seconds';
      if (sec < 7200) return Math.round(sec / 60) + ' minutes';
      if (sec < 172800) return Math.round(sec / 3600) + ' hours';
      if (sec < 63072000) return Math.round(sec / 86400) + ' days';
      return grp(Math.round(sec / 31557600)) + ' years';
    }
    function sciP(x) { if (x < 1e4) return grp(Math.round(x)); var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e); return (m < 1.05 ? '' : m.toFixed(1) + ' × ') + '10^' + e; }
    function sciH(x) { if (x < 1e4) return grp(Math.round(x)); var e = Math.floor(Math.log10(x)), m = x / Math.pow(10, e); return (m < 1.05 ? '' : m.toFixed(1) + ' &times; ') + '10<sup>' + e + '</sup>'; }
    function drawCost() {
      clear(cost);
      var L = +nr.value, n = Math.pow(10, L), school = n * n, fft = 3 * n * Math.log2(n);
      var W = Math.max(280, Math.min(640, Math.round(cost.parentNode.getBoundingClientRect().width - 16) || 440)), narrow = W < 420;
      var rows = [{ k: 'Every digit meets every digit', f: 'n²', v: school, c: 'sl-bar' }, { k: 'FFT route', f: '≈ 3 n log₂ n', v: fft, c: 'sl-bar hi' }, { k: 'Read the digits once', f: 'n', v: n, c: 'sl-bar lo' }];
      var x0 = 4, x1 = W - 8, rowH = 50, top = 8, H = top + rows.length * rowH + 34, maxE = 19;
      cost.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      function X(v) { return x0 + Math.max(0, Math.log10(Math.max(1, v))) / maxE * (x1 - x0); }
      for (var e = 0; e <= maxE; e += (narrow ? 6 : 3)) {
        cost.appendChild(el('line', { x1: X(Math.pow(10, e)), y1: top, x2: X(Math.pow(10, e)), y2: top + rows.length * rowH, class: 'grid' }));
        var t = el('text', { x: X(Math.pow(10, e)), y: top + rows.length * rowH + 16, 'text-anchor': e === 0 ? 'start' : 'middle', class: 'sl-ax' }); if (e === 0) t.textContent = '1'; else supSvg(t, '10', String(e)); cost.appendChild(t);
      }
      cost.appendChild(el('text', { x: x1, y: top + rows.length * rowH + 31, 'text-anchor': 'end', class: 'sl-ax' }, 'steps, each gridline ' + (narrow ? 'a million' : 'a thousand') + ' times more'));
      rows.forEach(function (r, i) {
        var y = top + i * rowH;
        cost.appendChild(el('text', { x: x0, y: y + 13, class: 'sl-lab' }, r.k + ', ' + r.f));
        cost.appendChild(el('rect', { x: x0, y: y + 19, width: Math.max(2, X(r.v) - x0), height: 16, rx: 2, class: r.c, 'data-tip': r.k + ' (' + r.f + '): about ' + sciP(r.v) + ' steps' }));
        var vt = el('text', { x: Math.min(X(r.v) + 6, x1 - 70), y: y + 32, class: 'sl-val' });
        if (r.v < 1e4) vt.textContent = grp(Math.round(r.v));
        else { var ee = Math.floor(Math.log10(r.v)), mm = r.v / Math.pow(10, ee); supSvg(vt, (mm < 1.05 ? '' : mm.toFixed(1) + ' × ') + '10', String(ee)); }
        cost.appendChild(vt);
      });
      var nTxt = grp(n);
      $('#sl-n-out').textContent = nTxt; nr.setAttribute('aria-valuetext', nTxt + ' digits');
      $('#sl-c-school').innerHTML = sciH(school) + ' products';
      $('#sl-c-fft').innerHTML = '~' + sciH(fft) + ' steps';
      $('#sl-c-time').textContent = human(school / 1e9) + ' vs ' + human(fft / 1e9);
      $('#sl-cost-desc').textContent = 'For ' + nTxt + '-digit numbers, every digit meeting every digit takes about ' + sciTxt(school) + ' products; the FFT route takes about ' + sciTxt(fft) + ' steps, constants ignored. At a billion steps a second that is ' + human(school / 1e9) + ' against ' + human(fft / 1e9) + '.';
      cost.setAttribute('aria-label', $('#sl-cost-desc').textContent);
    }
    nr.addEventListener('input', drawCost);
    cost.addEventListener('pointermove', function (ev) { var t = ev.target.getAttribute && ev.target.getAttribute('data-tip'); if (t) F0.tip.show('<p class="tip-t">' + esc(t) + '</p>', ev.clientX, ev.clientY); else F0.tip.hide(); });
    cost.addEventListener('pointerleave', function () { F0.tip.hide(); });
    $$('[data-sl-tab]').forEach(function (b) {
      b.addEventListener('click', function () {
        var tab = b.getAttribute('data-sl-tab');
        $$('[data-sl-tab]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        $('#sl-p-slide').hidden = tab !== 'slide'; $('#sl-p-count').hidden = tab !== 'count';
        if (tab === 'count') { stopPlay(); loop.stop(); drawCost(); } else draw();
      });
    });
    draw();
  }

  /* ======================================================================
     02 How much is κ worth? Steps per method (halvings scale) and the share saved over n log n.
     ====================================================================== */
  var KAPPAS = [
    { v: Math.pow(2, -182), name: 'the paper’s 2⁻¹⁸²', html: '2<sup>&minus;182</sup>' },
    { v: 5.8e-33, name: 'day one’s 5.8 × 10⁻³³', html: '5.8 &times; 10<sup>&minus;33</sup>' },
    { v: 0.0004609169, name: '9 October’s 0.0004609169', html: '0.0004609169' },
    { v: +SNAP.decimal, name: 'today’s ' + SNAP.decimal, html: SNAP.decimal }
  ];
  function savedFrac(k, L) { return -Math.expm1(-k * Math.log(L)); } /* 1 - L^-k, exact for tiny k */
  function initWorth() {
    var bars = $('#w-bars'), curve = $('#w-curve'); if (!bars) return;
    var rng = $('#w-n'), out = $('#w-n-out');
    var st = { L: 20, ki: 3 }, CURVE_X = [52, 506, 520];
    function boxW(svg) { return Math.max(260, Math.min(720, Math.round(svg.parentNode.getBoundingClientRect().width - 24) || 520)); }
    onLive(function (lv) { KAPPAS[3].v = lv.v; KAPPAS[3].html = esc(lv.decimal); KAPPAS[3].name = (lv.source === 'live' ? 'the live record’s ' : 'the record’s ') + lv.decimal; render(); });
    var METHODS = [
      { name: 'School method', f: 'n²', fs: ['n', '2', ' · ancient'], s: function (L) { return 2 * L; } },
      { name: 'Karatsuba', f: 'n to the 1.585, 1962', fs: ['n', '1.585', ' · 1962'], s: function (L) { return L * Math.log2(3); } },
      { name: 'Schönhage–Strassen', f: 'n log n log log n, 1971', fs: ['n log n log log n · 1971'], s: function (L) { return L + Math.log2(L) + Math.log2(Math.log2(L)); } },
      { name: 'Harvey–van der Hoeven', f: 'n log n, 2019', fs: ['n log n · 2019'], s: function (L) { return L + Math.log2(L); } },
      { name: 'The race', f: 'n (log n) to the 1−κ, 2026, conditional', fs: ['n (log n)', '1−κ', ' · conditional'], s: function (L, k) { return L + (1 - k) * Math.log2(L); }, hi: 1 }
    ];
    function pctHTML(p) { /* p as a fraction */
      if (p >= 1e-4) return (p * 100).toFixed(2) + '%';
      return sci(p * 100, 1) + '%';
    }
    function render() {
      var L = st.L, k = KAPPAS[st.ki].v;
      out.innerHTML = '2<sup>' + L + '</sup> bits';
      var dec = L * Math.LOG10E * Math.LN2;
      rng.setAttribute('aria-valuetext', '2 to the ' + L + ' bits, about 10 to the ' + Math.round(dec) + ' bits');
      $('#w-n-txt').innerHTML = '2<sup>' + L + '</sup>-bit';
      /* bars */
      clear(bars);
      /* drawn at the panel's true pixel width; below 470px each label sits above its bar */
      var BW_ = boxW(bars), stack = BW_ < 470;
      var x0 = stack ? 4 : 196, x1 = BW_ - (stack ? 70 : 50), top = stack ? 6 : 14, rowH = stack ? 58 : 40, maxE = 128, by = stack ? 26 : 7;
      var BH_ = top + rowH * 5 + 44;
      bars.setAttribute('viewBox', '0 0 ' + BW_ + ' ' + BH_);
      function X(e) { return x0 + e / maxE * (x1 - x0); }
      for (var g = 0; g <= maxE; g += 32) {
        bars.appendChild(el('line', { x1: X(g), y1: top - 4, x2: X(g), y2: top + rowH * 5 + 2, class: 'grid' }));
        var gt = el('text', { x: X(g), y: top + rowH * 5 + 20, 'text-anchor': g === 0 && stack ? 'start' : 'middle', 'font-size': 12 }); supSvg(gt, '2', String(g)); bars.appendChild(gt);
      }
      bars.appendChild(el('text', { x: x0, y: top + rowH * 5 + 38, 'font-size': 12 }, 'steps, each gridline 32 doublings'));
      var descBits = [];
      METHODS.forEach(function (m, i) {
        var e = m.s(L, k), y = top + i * rowH, dp = i >= 3 ? 3 : 1;
        bars.appendChild(el('text', { x: 0, y: y + 15, 'font-size': 12.5, class: m.hi ? 'lbl-strong' : 'lbl' }, m.name));
        var ft = el('text', { x: stack ? x0 + 0 : 0, y: stack ? y + 15 : y + 31, 'font-size': 11.5 });
        if (stack) { ft.setAttribute('x', BW_); ft.setAttribute('text-anchor', 'end'); }
        if (m.fs.length > 1) supSvg(ft, m.fs[0], m.fs[1], { after: stack ? '' : m.fs[2] }); else ft.textContent = stack ? m.fs[0].replace(/ \u00b7 .*$/, '') : m.fs[0]; bars.appendChild(ft);
        bars.appendChild(el('rect', { x: x0, y: y + by, width: Math.max(1, X(e) - x0), height: 18, rx: 2, class: m.hi ? 'bar bar-hi' : 'bar' }));
        var vt = el('text', { x: X(e) + 6, y: y + by + 14, 'font-size': 12.5, class: m.hi ? 'lbl-strong' : 'lbl' }); supSvg(vt, '2', e.toFixed(dp), { small: 10 }); bars.appendChild(vt);
        var hit = el('rect', { x: 0, y: y, width: BW_, height: rowH, class: 'bar-hit' });
        hit.addEventListener('pointermove', function (ev) {
          F0.tip.show('<p class="tip-k">' + esc(m.name) + '</p><p class="tip-t">2<sup>' + e.toFixed(dp) + '</sup> steps</p><p class="tip-note">' + esc(m.f) + ' for 2<sup>' + L + '</sup>-bit numbers, constants ignored' + (m.hi ? '; κ = ' + esc(KAPPAS[st.ki].name) : '') + '.</p>', ev.clientX, ev.clientY);
        });
        hit.addEventListener('pointerleave', function () { F0.tip.hide(); });
        bars.appendChild(hit);
        descBits.push(m.name + ' 2^' + e.toFixed(dp));
      });
      $('#w-bars-desc').innerHTML = 'For 2<sup>' + L + '</sup>-bit numbers, constants ignored: ' + METHODS.map(function (m, i) { return esc(m.name) + ' 2<sup>' + m.s(L, k).toFixed(i >= 3 ? 3 : 1) + '</sup>'; }).join(', ') + '. &kappa; = ' + KAPPAS[st.ki].html + '.';
      /* curve */
      clear(curve);
      var CW_ = boxW(curve), cx0 = 52, cx1 = CW_ - 14, cy0 = 16, cy1 = 206, yMax = 0.01;
      curve.setAttribute('viewBox', '0 0 ' + CW_ + ' 250'); CURVE_X = [cx0, cx1, CW_];
      function CX(l) { return cx0 + (l - 10) / 54 * (cx1 - cx0); }
      function CY(p) { return cy1 - Math.min(p, yMax) / yMax * (cy1 - cy0); }
      [0, .0025, .005, .0075, .01].forEach(function (p) {
        curve.appendChild(el('line', { x1: cx0, y1: CY(p), x2: cx1, y2: CY(p), class: p ? 'grid' : 'axis' }));
        curve.appendChild(el('text', { x: cx0 - 8, y: CY(p) + 4, 'text-anchor': 'end', 'font-size': 12 }, (p ? (p * 100).toFixed(2) : '0') + '%'));
      });
      [10, 20, 30, 40, 50, 64].forEach(function (l) {
        var t = el('text', { x: CX(l), y: cy1 + 20, 'text-anchor': 'middle', 'font-size': 12 }); supSvg(t, '2', String(l)); curve.appendChild(t);
      });
      curve.appendChild(el('text', { x: cx1, y: cy1 + 38, 'text-anchor': 'end', 'font-size': 12 }, 'size of the numbers, in bits'));
      var d = '', area = '';
      for (var l = 10; l <= 64; l += .5) { var px = CX(l).toFixed(1), py = CY(savedFrac(k, l)).toFixed(1); d += (d ? 'L' : 'M') + px + ' ' + py; }
      area = d + 'L' + CX(64).toFixed(1) + ' ' + cy1 + 'L' + CX(10).toFixed(1) + ' ' + cy1 + 'Z';
      curve.appendChild(el('path', { d: area, class: 'curve-area' }));
      curve.appendChild(el('path', { d: d, class: 'curve' }));
      var p = savedFrac(k, L);
      curve.appendChild(el('line', { x1: CX(L), y1: cy0, x2: CX(L), y2: cy1, class: 'xhair' }));
      curve.appendChild(el('circle', { cx: CX(L), cy: CY(p), r: 5, class: 'pt' }));
      var flip = CX(L) > cx1 - 130, lbX = flip ? CX(L) - 10 : CX(L) + 10, anchor = flip ? 'end' : 'start';
      if (p >= 1e-4) curve.appendChild(el('text', { x: lbX, y: CY(p) - 18, 'text-anchor': anchor, 'font-size': 13, class: 'lbl-strong' }, (p * 100).toFixed(2) + '% fewer'));
      else {
        var tt = el('text', { x: (cx0 + cx1) / 2, y: cy0 + 40, 'text-anchor': 'middle', 'font-size': 13, class: 'lbl-strong' });
        var mx = savedFrac(k, 64) * 100, ee = Math.floor(Math.log10(mx));
        tt.appendChild(document.createTextNode((CW_ < 420 ? 'flat: at most ' : 'flat on this scale: at most ') + (mx / Math.pow(10, ee)).toFixed(0) + ' × 10'));
        tt.appendChild(el('tspan', { dy: -5, 'font-size': 10 }, minus(ee))); tt.appendChild(el('tspan', { dy: 5 }, ' %'));
        curve.appendChild(tt);
      }
      $('#w-curve-desc').textContent = 'The share of steps saved over n log n, for kappa = ' + KAPPAS[st.ki].name + ', rises from ' + pctTxt(savedFrac(k, 10)) + ' at 2 to the 10 bits to ' + pctTxt(savedFrac(k, 64)) + ' at 2 to the 64 bits. At the chosen size it is ' + pctTxt(p) + '.';
      /* readouts */
      var f = Math.exp(k * Math.log(L));
      $('#w-f').innerHTML = k > 1e-6 ? f.toFixed(5) : '1 + ' + sci(Math.expm1(k * Math.log(L)), 2);
      $('#w-pct').innerHTML = pctHTML(p);
      var E = Math.LOG10E * Math.LN2 / k; /* n = 2^(10^E) bits halves the work */
      $('#w-half').innerHTML = E < 1e6 ? '2<sup>10<sup>' + Math.round(E) + '</sup></sup> bits' : '2<sup>10<sup>' + sci(E, 2) + '</sup></sup> bits';
    }
    function pctTxt(p) { return p >= 1e-4 ? (p * 100).toFixed(2) + ' percent' : 'about ' + sciTxt(p * 100) + ' percent'; }
    rng.addEventListener('input', function () { st.L = +rng.value; render(); });
    $$('[data-w-k]').forEach(function (b) {
      b.addEventListener('click', function () {
        st.ki = +b.getAttribute('data-w-k');
        $$('[data-w-k]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        render();
      });
    });
    /* the curve: point to read any size; click or arrow keys to choose it */
    function lAt(ev) { var r = curve.getBoundingClientRect(), sx = (ev.clientX - r.left) / r.width * CURVE_X[2]; return Math.max(10, Math.min(64, Math.round(10 + (sx - CURVE_X[0]) / (CURVE_X[1] - CURVE_X[0]) * 54))); }
    var rw0 = 0;
    if ('ResizeObserver' in window) new ResizeObserver(function () { var w = boxW(curve) + boxW(bars); if (w !== rw0) { rw0 = w; render(); } }).observe(bars.parentNode);
    curve.addEventListener('pointermove', function (ev) {
      var l = lAt(ev), k = KAPPAS[st.ki].v;
      F0.tip.show('<p class="tip-k">2<sup>' + l + '</sup>-bit numbers</p><p class="tip-t">' + pctHTML(savedFrac(k, l)) + ' fewer steps</p><p class="tip-note">than n log n, with &kappa; = ' + KAPPAS[st.ki].html + '. Click to choose this size; the Size slider does the same from the keyboard.</p>', ev.clientX, ev.clientY);
    });
    curve.addEventListener('pointerleave', function () { F0.tip.hide(); });
    curve.addEventListener('click', function (ev) { st.L = lAt(ev); rng.value = st.L; render(); });
    render();
  }

  /* ======================================================================
     03 The κ staircase. Records from kappa-history.json; Aska's two claims; optional open claims from
     this site's chart-data.json (11 Oct snapshot); a "now" step when the live record is newer.
     ====================================================================== */
  /* the table twin under the staircase: every reviewed record, then Aska's two claims. The HTML carries a
     pre-rendered copy (scripts/prerender.mjs) for readers without JavaScript. */
  function stairTable(d) {
    var tb = $('#s-table tbody'); if (!tb) return;
    function when(t) { return utc(t).replace(/ UTC$/, ''); }
    function kap(r) {
      if (/^2\^/.test(r.kappa)) return '2<sup>' + minus(r.kappa.slice(2)) + '</sup>';
      return String(r.decimal).indexOf('0.0000000') === 0 ? sci(parseFloat(r.decimal), 2) : esc(r.decimal);
    }
    var rows = d.records.map(function (r, i) {
      var src = i === 0 ? '<a href="' + esc(r.link) + '">preprint</a>' : r.commit_url ? '<a href="' + esc(r.commit_url) + '">' + esc(r.commit) + '</a>' : '';
      return '<tr><td>' + esc(i === 0 ? 'dated ' + utc(r.t, true) : when(r.t)) + '</td><td class="n">' + kap(r) + '</td><td class="n">' + minus(r.log2.toFixed(2)) + '</td>' +
        '<td>' + esc(r.what) + (r.who ? ' <span class="im-who-t">' + esc(r.who) + '</span>' : '') + '</td><td>' + src + '</td></tr>';
    });
    (d.aska_claims || []).forEach(function (a) {
      rows.push('<tr class="im-row-aska"><td>' + esc(when(a.t)) + '</td><td class="n">' + esc(a.decimal) + '</td><td class="n">' + minus(Math.log2(parseFloat(a.decimal)).toFixed(2)) + '</td>' +
        '<td>Aska #' + (+a.pr) + ': ' + esc(a.what) + ' <span class="im-who-t">' + esc(a.status) + '</span></td><td><a href="https://github.com/CrocSwap/integer-mult-bounds/pull/' + (+a.pr) + '">PR #' + (+a.pr) + '</a></td></tr>');
    });
    tb.innerHTML = rows.join('');
  }
  function initStair() {
    var svg = $('#s-svg'); if (!svg) return;
    var detail = $('#s-detail'), out = $('#s-out');
    var st = { scale: 'log', aska: true, claims: false, sel: -1, data: null, claimsData: null, live: null, until: null, rp: -1 };
    var Wv = 960, Hv = 440, M = { l: 78, r: 26, t: 34, b: 52 }, NARROW = false;
    /* drawn at the stage's true pixel width, so text stays readable from 320px phones to wide screens */
    function size() {
      var w = Math.round(svg.parentNode.getBoundingClientRect().width - 16) || 960;
      Wv = Math.max(290, Math.min(1400, w)); NARROW = Wv < 600;
      Hv = NARROW ? 400 : Math.max(420, Math.min(520, Math.round(Wv * 0.42)));
      M = NARROW ? { l: 56, r: 14, t: 52, b: 50 } : { l: 78, r: 26, t: 34, b: 52 };
      svg.setAttribute('viewBox', '0 0 ' + Wv + ' ' + Hv);
    }
    var T0 = Date.parse('2026-09-23T00:00:00Z'), TG = Date.parse('2026-10-07T00:00:00Z'), TE = Date.parse('2026-10-14T00:00:00Z');
    var items = [];
    function decOf(r) { return r.decimal ? parseFloat(r.decimal) : Math.pow(2, r.log2); }
    function build() {
      var d = st.data; items = [];
      d.records.forEach(function (r, i) { items.push({ kind: i === 0 ? 'paper' : 'rec', t: Date.parse(r.t), v: decOf(r), lg: r.log2, r: r }); });
      if (st.aska) d.aska_claims.forEach(function (a) { var v = parseFloat(a.decimal); items.push({ kind: 'aska', t: Date.parse(a.t), v: v, lg: Math.log2(v), r: a }); });
      var last = d.records[d.records.length - 1];
      if (st.live && st.live.v > decOf(last) * (1 + 1e-15) && Date.parse(st.live.at) > Date.parse(last.t)) items.push({ kind: 'live', t: Date.parse(st.live.at), v: st.live.v, lg: st.live.log2, r: st.live });
      items.sort(function (a, b) { return a.t - b.t; });
    }
    function hasNow() { return items.some(function (i) { return i.kind === 'live'; }); }
    function geom() {
      var nowW = hasNow() ? (NARROW ? 54 : 74) : 0, px0 = M.l, px1 = Wv - M.r - nowW, gapW = (px1 - px0) * (NARROW ? .16 : .12);
      return { px0: px0, px1: px1, gapW: gapW, nowX: Wv - M.r - 22, nowW: nowW };
    }
    function X(t, g) {
      if (t >= TE + 3600e3 * 30) return g.nowX; /* live points well after the end sit in the "now" column */
      if (t < TG) return g.px0 + (t - T0) / (TG - T0) * g.gapW;
      return g.px0 + g.gapW + Math.min(1, (t - TG) / (TE - TG)) * (g.px1 - g.px0 - g.gapW);
    }
    function yDom() {
      if (st.scale === 'log') return { lo: -190, hi: 0 };
      var mx = 0; items.forEach(function (i) { mx = Math.max(mx, i.v); });
      return { lo: 0, hi: Math.max(0.0018, Math.ceil(mx / 0.0005) * 0.0005 * 1.02) };
    }
    function Y(it, dom) {
      var v = st.scale === 'log' ? it.lg : it.v;
      return Hv - M.b - (v - dom.lo) / (dom.hi - dom.lo) * (Hv - M.t - M.b);
    }
    function draw() {
      clear(svg); size();
      var g = geom(), dom = yDom();
      /* gap band + break marks */
      svg.appendChild(el('rect', { x: g.px0, y: M.t, width: g.gapW, height: Hv - M.t - M.b, class: 'gapband' }));
      var roomy = g.gapW >= 90;
      svg.appendChild(el('text', { x: g.px0 + g.gapW / 2, y: M.t + 18, 'text-anchor': 'middle', 'font-size': 11 }, roomy ? '2 weeks,' : '2 wk'));
      if (roomy) svg.appendChild(el('text', { x: g.px0 + g.gapW / 2, y: M.t + 32, 'text-anchor': 'middle', 'font-size': 11 }, 'compressed'));
      /* y grid */
      if (st.scale === 'log') {
        for (var e = -180; e <= 0; e += 30) {
          var yy = Y({ lg: e }, dom);
          svg.appendChild(el('line', { x1: M.l, y1: yy, x2: Wv - M.r, y2: yy, class: 'grid' }));
          var t = el('text', { x: M.l - 10, y: yy + 4, 'text-anchor': 'end' }); if (e === 0) t.textContent = '1'; else supSvg(t, '2', minus(e), { small: 10 }); svg.appendChild(t);
        }
        svg.appendChild(el('text', { x: NARROW ? 0 : M.l, y: NARROW ? 14 : M.t - 14, class: 'lbl' }, 'κ on a halvings scale'));
      } else {
        for (var v = 0; v <= dom.hi + 1e-12; v += 0.0005) {
          var y2 = Y({ v: v }, dom);
          svg.appendChild(el('line', { x1: M.l, y1: y2, x2: Wv - M.r, y2: y2, class: 'grid' }));
          svg.appendChild(el('text', { x: M.l - 10, y: y2 + 4, 'text-anchor': 'end' }, v === 0 ? '0' : v.toFixed(4)));
        }
        svg.appendChild(el('text', { x: NARROW ? 0 : M.l, y: NARROW ? 14 : M.t - 14, class: 'lbl' }, 'κ, plain'));
      }
      /* x axis */
      var yb = Hv - M.b;
      svg.appendChild(el('line', { x1: M.l, y1: yb, x2: Wv - M.r, y2: yb, class: 'axis' }));
      svg.appendChild(el('text', { x: g.px0, y: yb + 20, 'text-anchor': 'start' }, '23 Sep'));
      var narrow = NARROW;
      for (var dd = 7; dd <= 14; dd++) {
        var tx = X(Date.UTC(2026, 9, dd), g);
        svg.appendChild(el('line', { x1: tx, y1: yb, x2: tx, y2: yb + 5, class: 'axis' }));
        if (!narrow || (dd % 2 === 1 && dd !== 7)) svg.appendChild(el('text', { x: tx, y: yb + 20, 'text-anchor': 'middle' }, dd + (dd === 9 || !narrow ? ' Oct' : '')));
      }
      var bx = g.px0 + g.gapW - 12;
      svg.appendChild(el('path', { d: 'M' + (bx - 7) + ' ' + (yb + 7) + 'L' + (bx - 1) + ' ' + (yb - 7) + 'M' + (bx + 1) + ' ' + (yb + 7) + 'L' + (bx + 7) + ' ' + (yb - 7), class: 'brk' }));
      if (g.nowW) {
        var nb = g.px1 + 14;
        svg.appendChild(el('path', { d: 'M' + (nb - 7) + ' ' + (yb + 7) + 'L' + (nb - 1) + ' ' + (yb - 7) + 'M' + (nb + 1) + ' ' + (yb + 7) + 'L' + (nb + 7) + ' ' + (yb - 7), class: 'brk' }));
        svg.appendChild(el('text', { x: g.nowX, y: yb + 20, 'text-anchor': 'middle' }, 'now'));
      }
      svg.appendChild(el('text', { x: Wv - M.r, y: yb + 40, 'text-anchor': 'end' }, 'time, UTC'));
      /* claims overlay */
      if (st.claims && st.claimsData) {
        var cd = '';
        st.claimsData.forEach(function (c) {
          var cx = X(c.t, g), cy = Y(c, dom); if (cy < M.t || cy > yb) return;
          cd += 'M' + (cx - 2.4).toFixed(1) + ' ' + cy.toFixed(1) + 'a2.4 2.4 0 1 0 4.8 0a2.4 2.4 0 1 0 -4.8 0';
        });
        svg.appendChild(el('path', { d: cd, class: 'claim' }));
      }
      /* staircase: records (and live) only; during a replay, only what had happened by the cursor time */
      var U = st.until, seen = function (it) { return U == null || it.t <= U; };
      var recs = items.filter(function (i) { return i.kind !== 'aska' && seen(i); });
      var ghost = '', path = '';
      for (var k = 0; k < recs.length; k++) {
        var a = recs[k], x = X(a.t, g), y = Y(a, dom);
        var nx = k + 1 < recs.length ? X(recs[k + 1].t, g) : (a.kind === 'live' ? x : U != null ? Math.max(x, X(U, g)) : g.px1);
        var ny = k + 1 < recs.length ? Y(recs[k + 1], dom) : y;
        var seg = 'M' + x.toFixed(1) + ' ' + y.toFixed(1) + 'H' + nx.toFixed(1) + (k + 1 < recs.length ? 'V' + ny.toFixed(1) : '');
        if (a.kind === 'paper' || (k + 1 < recs.length && recs[k + 1].kind === 'live')) ghost += seg; else path += seg;
      }
      svg.appendChild(el('path', { d: ghost, class: 'step-ghost' }));
      svg.appendChild(el('path', { d: path, class: 'step' }));
      items.forEach(function (it) {
        if (!seen(it)) return;
        var x = X(it.t, g), y = Y(it, dom);
        if (it.kind === 'paper') svg.appendChild(el('circle', { cx: x, cy: y, r: 5.5, class: 'rec-paper' }));
        else if (it.kind === 'rec') svg.appendChild(el('circle', { cx: x, cy: y, r: 4.5, class: 'rec' }));
        else if (it.kind === 'aska') svg.appendChild(el('path', { d: 'M' + x + ' ' + (y - 6) + 'l6 6-6 6-6-6z', class: 'aska' }));
        else { svg.appendChild(el('circle', { cx: x, cy: y, r: 9, class: 'ring-live' })); svg.appendChild(el('circle', { cx: x, cy: y, r: 5.5, class: 'rec-live' })); }
      });
      /* selective direct labels: the paper, the newest record, Aska's claims */
      var paper = items[0], lastRec = recs[recs.length - 1];
      var px_ = X(TG, g) + 10, py_ = Y(paper, dom);
      svg.appendChild(el('text', { x: px_, y: py_ - 38, class: 'lbl' }, NARROW ? 'preprint, dated 23 Sep' : 'the preprint, dated 23 Sep'));
      var pl = el('text', { x: px_, y: py_ - 12, class: 'lbl' });
      if (st.scale === 'log') supSvg(pl, '2', '−182', { small: 10 }); else pl.textContent = '≈ 0';
      svg.appendChild(pl);
      var lx = X(lastRec.t, g), ly = Y(lastRec, dom);
      if (lastRec.kind !== 'paper') {
        var ll = el('text', { x: lx - (NARROW ? 14 : 8), y: NARROW ? ly - 16 : ly + 28, 'text-anchor': 'end', class: 'lbl-strong' });
        ll.textContent = (lastRec.kind === 'live' ? 'live ' : '') + (lastRec.v >= 1e-6 ? lastRec.v.toFixed(6) + ' ≈ ' : '') + '2';
        ll.appendChild(el('tspan', { dy: -5, 'font-size': 10 }, minus(lastRec.lg.toFixed(2))));
        svg.appendChild(ll);
      }
      if (st.aska) {
        var ak = items.filter(function (i) { return i.kind === 'aska'; });
        if (ak.length && seen(ak[1])) {
          /* below the line, clear of the end label (above it at narrow widths, far right of it otherwise) */
          var ax = X(ak[1].t, g), ay = Y(ak[1], dom);
          if (NARROW) {
            var nx_ = Math.min(Wv - M.r, ax + 44);
            svg.appendChild(el('line', { x1: ax, y1: ay + 8, x2: ax, y2: ay + 30, class: 'lead' }));
            svg.appendChild(el('text', { x: nx_, y: ay + 46, 'text-anchor': 'end', class: 'lbl' }, 'Aska\u2019s 2 claims'));
          } else {
            svg.appendChild(el('line', { x1: ax - 3, y1: ay + 7, x2: ax - 12, y2: ay + 30, class: 'lead' }));
            svg.appendChild(el('text', { x: ax - 16, y: ay + 44, 'text-anchor': 'end', class: 'lbl' }, 'Aska #464, #469'));
            svg.appendChild(el('text', { x: ax - 16, y: ay + 59, 'text-anchor': 'end', class: 'lbl' }, 'claims, never reviewed'));
          }
        }
      }
      /* the replay cursor, and its counter in the corner */
      if (U != null) {
        var ux = X(U, g);
        svg.appendChild(el('line', { x1: ux, y1: M.t, x2: ux, y2: yb, class: 'cursor' }));
        var ud = new Date(U);
        svg.appendChild(el('text', { x: ux + 90 > Wv - M.r ? ux - 6 : ux + 6, y: (M.t + yb) / 2, 'text-anchor': ux + 90 > Wv - M.r ? 'end' : 'start', class: 'lbl' }, ud.getUTCDate() + ' ' + MON[ud.getUTCMonth()] + (U >= TG ? ', ' + String(ud.getUTCHours()).padStart(2, '0') + ':' + String(ud.getUTCMinutes()).padStart(2, '0') : '')));
        var pm = /#(\d+)/.exec(lastRec.r.what || ''), who = lastRec.r.who ? lastRec.r.who.split(/[;,(]/)[0].trim() : '';
        out.textContent = (lastRec.kind === 'paper' ? 'the preprint' : (pm ? '#' + pm[1] : utc(new Date(lastRec.t).toISOString(), true))) + (who && lastRec.kind !== 'paper' ? ' · ' + who : '') + ' · 2^' + minus(lastRec.lg.toFixed(2));
        return;
      }
      /* selection */
      if (st.sel >= 0 && items[st.sel]) {
        var s = items[st.sel];
        svg.appendChild(el('line', { x1: X(s.t, g), y1: M.t, x2: X(s.t, g), y2: yb, class: 'xhair' }));
        svg.appendChild(el('circle', { cx: X(s.t, g), cy: Y(s, dom), r: 10, class: 'sel' }));
      }
      out.textContent = st.data.records.length + ' records' + (st.live ? (hasNow() ? ' · + a newer live record' : st.live.source === 'live' ? ' · live file agrees' : '') : '');
    }
    function statusBadge(it) {
      var L = F0.ladderHTML;
      if (it.kind === 'paper') return '<span class="badge p">' + L(2) + 'Machine-written preprint</span><span class="badge n">Not peer reviewed</span>';
      if (it.kind === 'aska') return '<span class="badge c">' + L(1) + 'Claimed &middot; never reviewed</span><span class="badge n">Closed 13 Oct</span>';
      if (it.kind === 'claim') return '<span class="badge c">' + L(1) + 'Claimed &middot; open PR on 11 Oct</span>';
      if (it.kind === 'live') return '<span class="badge p">' + L(2) + 'Maintainer-reviewed &middot; conditional</span><span class="badge n">Live record</span>';
      return '<span class="badge p">' + L(2) + (it.r.file ? 'Maintainer-reviewed &middot; conditional' : 'Maintainer&rsquo;s conditional result') + '</span>';
    }
    function kappaHTML(it) {
      var r = it.r;
      if (it.kind === 'paper') return '2<sup>&minus;182</sup> <small>&asymp; 1.63 &times; 10<sup>&minus;55</sup></small>';
      if (it.kind === 'live') return esc(r.decimal) + (r.kappa ? ' <small>= ' + esc(String(r.kappa)) + '</small>' : '');
      if (it.kind === 'claim') return esc(r.dec);
      if (/^2\^/.test(r.kappa)) return '2<sup>' + minus(r.kappa.slice(2)) + '</sup> <small>&asymp; ' + sci(it.v, 3) + '</small>';
      var small = r.decimal && r.decimal.indexOf('0.0000000') === 0;
      return (small ? sci(it.v, 3) : esc(r.decimal)) + ' <small>= ' + esc(r.kappa) + '</small>';
    }
    function whatHTML(it) {
      var r = it.r;
      if (it.kind === 'live') return '<b>The record right now</b>, read from the race&rsquo;s selected-result.json' + (r.pr ? ': PR #' + (+r.pr) : '') + '. Newer than the last step compiled for this page.';
      if (it.kind === 'aska') return '<b>Aska PR #' + r.pr + '</b>: ' + esc(r.what) + '. ' + esc(r.status) + '.';
      if (it.kind === 'claim') return '<b>PR #' + r.pr + '</b>' + (r.draft ? ' (draft)' : '') + ': a claim on our tracker&rsquo;s 11 Oct snapshot, placed at the PR&rsquo;s last update. Never a record unless the maintainer selects it.';
      return '<b>' + esc(r.what) + '</b>' + (r.who ? '. ' + esc(r.who) + '.' : '.');
    }
    function linkHTML(it) {
      var r = it.r;
      if (it.kind === 'paper') return '<a href="' + esc(r.link) + '">The preprint (openai/math)</a>';
      if (it.kind === 'aska' || it.kind === 'claim') return '<a href="https://github.com/CrocSwap/integer-mult-bounds/pull/' + (+r.pr) + '">PR #' + (+r.pr) + '</a>';
      if (it.kind === 'live') return '<a href="https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json">selected-result.json</a>';
      return r.commit_url ? '<a href="' + esc(r.commit_url) + '">commit ' + esc(r.commit) + '</a>' : '';
    }
    function whenTxt(it) { return it.kind === 'paper' ? 'dated 23 Sep 2026 · public 6 Oct' : it.kind === 'live' ? 'fetched ' + utc(it.r.at) : utc(new Date(it.t).toISOString()); }
    function showDetail(it) {
      detail.className = 'im-detail' + (it.kind === 'aska' ? ' aska' : '');
      detail.innerHTML = '<p class="d-k">' + esc(whenTxt(it)) + ' &middot; log&#8322;&#8201;&kappa; = ' + minus(it.lg.toFixed(3)) + '</p><p class="d-v">' + kappaHTML(it) + '</p><p class="d-t">' + whatHTML(it) + '</p><div class="d-row"><span class="badges">' + statusBadge(it) + '</span>' + linkHTML(it) + '</div>';
    }
    function tipFor(it, cx, cy) {
      F0.tip.show('<p class="tip-k">' + esc(whenTxt(it)) + '</p><p class="tip-t">' + kappaHTML(it).replace(/<small>.*<\/small>/, '') + '</p><p class="tip-note">' + whatHTML(it) + '</p><p class="tip-foot">log&#8322; &kappa; = ' + minus(it.lg.toFixed(2)) + ' &middot; click for details</p>', cx, cy);
    }
    function svgPt(ev) { var r = svg.getBoundingClientRect(); return { x: (ev.clientX - r.left) / r.width * Wv, y: (ev.clientY - r.top) / r.height * Hv, s: r.width / Wv }; }
    function nearest(p) {
      var g = geom(), dom = yDom(), best = null, bd = Infinity;
      items.forEach(function (it, i) { var dx = X(it.t, g) - p.x, dy = Y(it, dom) - p.y, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = { it: it, i: i }; } });
      if (st.claims && st.claimsData) {
        st.claimsData.forEach(function (c) { var dx = X(c.t, g) - p.x, dy = Y(c, dom) - p.y, d = dx * dx + dy * dy; if (d < bd - 40) { bd = d; best = { it: c, i: -1 }; } });
      }
      var lim = 28 / Math.max(.35, p.s); return bd <= lim * lim ? best : null;
    }
    svg.addEventListener('pointermove', function (ev) {
      var n = nearest(svgPt(ev)); if (n) tipFor(n.it, ev.clientX, ev.clientY); else F0.tip.hide();
    });
    svg.addEventListener('pointerleave', function () { F0.tip.hide(); });
    svg.addEventListener('click', function (ev) {
      var n = nearest(svgPt(ev)); if (!n) return;
      if (n.i >= 0) { st.sel = n.i; draw(); } showDetail(n.it);
    });
    svg.addEventListener('keydown', function (ev) {
      var d = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1 }[ev.key], i = st.sel < 0 ? items.length - 1 : st.sel;
      if (ev.key === 'Home') { i = 0; d = 0; } else if (ev.key === 'End') { i = items.length - 1; d = 0; } else if (d == null) return;
      ev.preventDefault();
      st.sel = Math.max(0, Math.min(items.length - 1, i + d)); draw(); showDetail(items[st.sel]);
      var g = geom(), dom = yDom(), r = svg.getBoundingClientRect(), it = items[st.sel];
      tipFor(it, r.left + X(it.t, g) / Wv * r.width, r.top + Y(it, dom) / Hv * r.height);
    });
    svg.addEventListener('blur', function () { F0.tip.hide(); });
    $$('[data-s-scale]').forEach(function (b) {
      b.addEventListener('click', function () {
        st.scale = b.getAttribute('data-s-scale');
        $$('[data-s-scale]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        draw();
      });
    });
    function selIdx(pred) { for (var i = items.length - 1; i >= 0; i--) if (pred(items[i])) return i; return items.length - 1; }
    $('#s-aska').addEventListener('click', function () {
      var cur = items[st.sel];
      st.aska = !st.aska; this.setAttribute('aria-pressed', st.aska ? 'true' : 'false');
      $('.im-leg-aska').hidden = !st.aska;
      build(); st.sel = cur ? selIdx(function (x) { return x === cur || (x.t === cur.t && x.kind === cur.kind); }) : -1;
      if (cur && cur.kind === 'aska' && !st.aska) { st.sel = items.length - 1; showDetail(items[st.sel]); }
      draw();
    });
    $('#s-claims').addEventListener('click', function () {
      var btn = this;
      st.claims = !st.claims; btn.setAttribute('aria-pressed', st.claims ? 'true' : 'false');
      $('.im-leg-claims').hidden = !st.claims;
      if (st.claims && !st.claimsData) {
        F0.json(F0.root + 'chart-data.json').then(function (c) {
          st.claimsData = (c.claimed || []).map(function (r) { var v = parseFloat(r.kappa_decimal); return { kind: 'claim', t: Date.parse(r.pr_updated_at), v: v, lg: Math.log2(v), r: { pr: r.pr, draft: r.draft, dec: r.kappa_decimal } }; })
            .filter(function (c) { return c.v > 0 && isFinite(c.t); });
          draw();
        }).catch(function (e) { console.warn('chart-data.json:', e); });
      }
      draw();
    });
    /* Replay the race: a cursor sweeps from the preprint to the last record in about 8 s, drawing each step as it
       happened. Motion off: each press jumps to the next of the five largest steps, then back to the full record. */
    var rpBtn = $('#s-replay'), RP_MS = 8000, rpT0 = 0, rpVisible = true;
    function xInv(x) {
      var g = geom();
      if (x <= g.px0 + g.gapW) return T0 + Math.max(0, x - g.px0) / g.gapW * (TG - T0);
      return TG + Math.min(1, (x - g.px0 - g.gapW) / (g.px1 - g.px0 - g.gapW)) * (TE - TG);
    }
    function rpEnd() {
      st.until = null; st.rp = -1; rpLoop.stop(); rpBtn.setAttribute('aria-pressed', 'false');
      st.sel = items.length - 1; draw(); showDetail(items[st.sel]);
    }
    var rpLoop = F0.loop(function (now) {
      if (st.until == null) { rpLoop.stop(); return; }
      var p = Math.min(1, (now - rpT0) / RP_MS), g = geom();
      if (p >= 1) { rpEnd(); return; }
      st.until = xInv(g.px0 + p * (g.px1 - g.px0)); draw();
    });
    F0.whenVisible(svg, function () { rpVisible = true; if (st.until != null && st.rp < 0) rpLoop.start(); }, function () { rpVisible = false; rpLoop.stop(); });
    function bigSteps() {
      var rs = st.data.records, jumps = [];
      for (var i = 1; i < rs.length; i++) jumps.push({ t: Date.parse(rs[i].t), d: rs[i].log2 - rs[i - 1].log2 });
      return jumps.sort(function (a, b) { return b.d - a.d; }).slice(0, 5).sort(function (a, b) { return a.t - b.t; });
    }
    if (rpBtn) rpBtn.addEventListener('click', function () {
      if (!st.data) return;
      if (F0.motion()) {
        if (st.until != null) { rpEnd(); return; }
        st.until = T0; st.rp = -1; rpT0 = performance.now(); rpBtn.setAttribute('aria-pressed', 'true'); draw(); if (rpVisible) rpLoop.start();
        return;
      }
      var steps = bigSteps(); st.rp += 1;
      if (st.rp >= steps.length) { rpEnd(); return; }
      st.until = steps[st.rp].t; rpBtn.setAttribute('aria-pressed', 'true'); draw();
      var idx = -1; items.forEach(function (it, i) { if (it.t === steps[st.rp].t && it.kind !== 'aska') idx = i; });
      if (idx >= 0) showDetail(items[idx]);
    });
    F0.onMotion(function (on) { if (!on && st.until != null && st.rp < 0) rpEnd(); });
    svg.addEventListener('keydown', function () { if (st.until != null) { st.until = null; st.rp = -1; rpLoop.stop(); rpBtn.setAttribute('aria-pressed', 'false'); } }, true);
    var rw = 0, ro = 'ResizeObserver' in window ? new ResizeObserver(function () { var w = Math.round(svg.parentNode.getBoundingClientRect().width); if (st.data && w !== rw) { rw = w; draw(); } }) : null;
    if (ro) ro.observe(svg.parentNode);
    F0.json('kappa-history.json').then(function (d) {
      stairTable(d);
      st.data = d; build(); st.sel = selIdx(function (x) { return x.kind === 'rec'; }); draw(); showDetail(items[st.sel]);
      onLive(function (lv) {
        st.live = lv; var cur = items[st.sel]; build();
        var li = selIdx(function (x) { return x.kind === 'live'; });
        st.sel = items[li] && items[li].kind === 'live' ? li : selIdx(function (x) { return x === cur || (x.t === cur.t && x.kind === cur.kind); });
        draw(); showDetail(items[st.sel]);
      });
    }).catch(function (e) {
      console.warn('kappa-history.json:', e);
      detail.textContent = 'The record history could not be loaded; the table below lists every step.';
    });
  }

  /* ======================================================================
     04 The budget that must stay under one. bill(a) = Σ n_r (r/m)^(1−a) / W + charge·E·m^(a−1) / W.
     Exact child counts from PR #450 / #469 PROOF.md; break-even a by bisection; κ = a/(1+a).
     ====================================================================== */
  var BM = 78, BW = 1200, RANKS = [1, 2, 3, 4, 5, 6, 7, 8, 14, 56];
  var H450 = { 1: 27060, 2: 11132, 3: 3036, 4: 3465, 5: 1188, 6: 462, 7: 154, 8: 99, 14: 1, 56: 184 };
  var H469 = { 1: 26411, 2: 11209, 3: 3201, 4: 3465, 5: 1089, 6: 660, 7: 55, 8: 99, 14: 1, 56: 184 };
  var CH_INH = 1e-16 * 32 * BM * BM;                                    /* inherited: 10^-16 · 32 m² */
  var CH_SHARP = (2 * BM * BM * BM / Math.pow(2, 80)) * 146478;         /* sharp: (2m³/2^80) · (6N(N−1)+3N+6(N−1)), N = 2m */
  var PRESETS = {
    pr450: { h: H450, ch: CH_INH, pub: '0.001347744547714835', frac: '269548909542967/200000000000000000',
      note: '<b>PR #450 by DreamingOfClouds</b>: the parent block both of Aska&rsquo;s claims started from, with the inherited insurance charge.' },
    pr464: { h: H450, ch: CH_SHARP, pub: '0.001347744550711765', frac: '269548910142353/200000000000000000',
      note: '<b>Aska&rsquo;s PR #464</b>: the same children as #450, with the sharper insurance charge first found by Srikrishnabalaji (PR #461). The charge is about 10<sup>&minus;11</sup> of the budget, so &kappa; moves only in its 12th digit.' },
    pr469: { h: H469, ch: CH_INH, pub: '0.001350580884553120', frac: '8441130528457/6250000000000000',
      note: '<b>Aska&rsquo;s PR #469</b>: 113 data moves re-timed. 649 fewer jobs of size 1, 99 fewer of size 7, 198 more of size 6; the same total size. The bill at <i>a</i> = 0 is unchanged, but it grows more slowly, so &kappa; rises 0.21%.' }
  };
  function E_(h) { var e = 0; RANKS.forEach(function (r) { e += h[r]; }); return e; }
  function share(h, r, a) { return h[r] * Math.pow(r / BM, 1 - a) / BW; }
  /* bill − 1, kept exact to ~1e-19: the plain shares sum to the rational 93,192/93,600, and each child's extra
     billing is share × expm1(a·ln(m/r)), so nothing near 1 is ever subtracted in floating point. */
  function billM1(p, a) {
    var mass = 0, terms = [], s = 0;
    RANKS.forEach(function (r) { mass += r * p.h[r]; terms.push((p.h[r] * r / (BM * BW)) * Math.expm1(a * Math.log(BM / r))); });
    terms.sort(function (x, y) { return x - y; }).forEach(function (t) { s += t; });
    return (mass - BM * BW) / (BM * BW) + s + p.ch * E_(p.h) * Math.pow(BM, a - 1) / BW;
  }
  function bill(p, a) { return 1 + billM1(p, a); }
  function breakEven(p) { var lo = 0, hi = 0.01; for (var i = 0; i < 80; i++) { var mid = (lo + hi) / 2; if (billM1(p, mid) < 0) lo = mid; else hi = mid; } return lo; }
  function floor18(k) { return '0.' + String(Math.floor(k * 1e18)).padStart(18, '0'); }
  function agreeDigits(a, b) { var x = a.replace(/^0\.0*/, ''), y = b.replace(/^0\.0*/, ''), n = 0; while (n < x.length && n < y.length && x[n] === y[n]) n++; return n; }

  function initBudget() {
    var host = $('#b-bars'); if (!host) return;
    var rng = $('#b-a'), out = $('#b-a-out'), find = $('#b-find');
    var st = { p: 'pr450', a: 0, exact: false, timer: 0 };
    var cols = {};
    host.setAttribute('role', 'list'); host.setAttribute('aria-label', 'Share of the bill by child size');
    RANKS.forEach(function (r) {
      var c = document.createElement('div'); c.className = 'im-bar'; c.setAttribute('role', 'listitem'); c.tabIndex = 0;
      c.innerHTML = '<span class="pct"></span><span class="col"><span class="fill"></span></span><span class="r">' + r + '</span><span class="nr"></span><span class="int"></span>';
      function tip(ev) {
        var p = PRESETS[st.p], s = share(p.h, r, st.a), it = Math.pow(BM / r, st.a);
        var bx = c.getBoundingClientRect();
        F0.tip.show('<p class="tip-k">Child jobs of size ' + r + '</p><p class="tip-t">' + (s * 100).toFixed(3) + '% of the budget</p><p class="tip-note">' + grp(p.h[r]) + ' jobs &times; (' + r + '/78)<sup>1&minus;a</sup> &divide; 1,200. Billed &times;' + it.toFixed(5) + ' for the saving a.' + (p.h === H469 && H469[r] !== H450[r] ? ' #469 changed this count by ' + minus((H469[r] > H450[r] ? '+' : '') + (H469[r] - H450[r])) + '.' : '') + '</p>', ev && ev.clientX != null ? ev.clientX : bx.right, ev && ev.clientY != null ? ev.clientY : bx.top);
      }
      c.addEventListener('pointermove', tip); c.addEventListener('focus', function () { tip(null); });
      c.addEventListener('pointerleave', function () { F0.tip.hide(); }); c.addEventListener('blur', function () { F0.tip.hide(); });
      host.appendChild(c); cols[r] = c;
    });
    var key = document.createElement('div'); key.className = 'im-bars-k'; key.setAttribute('aria-hidden', 'true');
    key.innerHTML = '<span>&uarr; share of bill &middot; size <i>r</i> &middot; jobs <i>n<sub>r</sub></i> &middot; billed &times;(<i>m</i>/<i>r</i>)<sup><i>a</i></sup></span>';
    host.parentNode.insertBefore(key, host.nextSibling);

    function compact(n) { return n >= 10000 ? (n / 1000).toFixed(1) + 'k' : n >= 1000 ? (n / 1000).toFixed(1) + 'k' : String(n); }
    function render() {
      var p = PRESETS[st.p], a = st.a, bm = billM1(p, a), b = 1 + bm, k = a / (1 + a);
      var w = Math.max(0, Math.min(1, (b - 0.995) / 0.006));
      var fill = $('#b-fill'), state = $('#b-state');
      fill.style.width = (w * 100).toFixed(3) + '%';
      var even = st.exact || Math.abs(bm) < 1e-15;
      fill.classList.toggle('over', bm > 0 && !even);
      state.className = 'im-gauge-state' + (even ? ' even' : bm > 0 ? ' over' : '');
      state.textContent = even ? 'At break-even' : bm > 0 ? 'Over budget by ' + (bm * 100).toFixed(4) + '%' : 'Under budget by ' + (-bm * 100).toFixed(4) + '%';
      RANKS.forEach(function (r) {
        var c = cols[r], s = share(p.h, r, a);
        c.querySelector('.pct').textContent = (s * 100).toFixed(s < 0.001 ? 2 : 1) + '%';
        c.querySelector('.fill').style.setProperty('--h', Math.max(0.6, s / 0.30 * 100).toFixed(2) + '%');
        c.querySelector('.fill').classList.toggle('up', p.h === H469 && H469[r] > H450[r]);
        c.querySelector('.nr').textContent = compact(p.h[r]);
        c.querySelector('.int').textContent = '×' + Math.pow(BM / r, a).toFixed(4);
        c.setAttribute('aria-label', 'Size ' + r + ': ' + grp(p.h[r]) + ' jobs, ' + (s * 100).toFixed(3) + ' percent of the budget, billed times ' + Math.pow(BM / r, a).toFixed(5));
      });
      out.textContent = st.exact ? a.toPrecision(17) : a.toFixed(6);
      rng.setAttribute('aria-valuetext', 'a = ' + out.textContent);
      $('#b-bill').innerHTML = st.exact ? '1 ' + (bm < 0 ? '&minus; ' : '+ ') + (bm ? sci(Math.abs(bm), 2) : '0') : b.toFixed(9);
      if (st.exact) {
        var ks = floor18(k), n = agreeDigits(ks, p.pub);
        $('#b-kappa').innerHTML = esc(ks) + '<br><small class="im-agree">' + (n >= 16 ? 'matches every published digit (18 decimals, rounded down)' : 'matches the published value to ' + n + ' significant digits') + '</small>';
      } else $('#b-kappa').textContent = a ? k.toFixed(9) : '0';
      $('#b-pub').innerHTML = esc(p.pub) + '<br><small class="im-agree">= ' + esc(p.frac) + '</small>';
      var chg = p.ch * E_(p.h) * Math.pow(BM, a - 1) / BW;
      $('#b-note').innerHTML = p.note + ' Insurance charge at this <i>a</i>: ' + sci(chg, 3) + ' of the budget, too thin to draw.';
    }
    function setPreset(id) {
      st.p = id; st.exact = false; cancel();
      $$('[data-b-preset]').forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-b-preset') === id ? 'true' : 'false'); });
      render();
    }
    function cancel() { if (st.timer) { clearTimeout(st.timer); st.timer = 0; st.finish = null; find.textContent = 'Find the break-even'; } }
    $$('[data-b-preset]').forEach(function (b) { b.addEventListener('click', function () { setPreset(b.getAttribute('data-b-preset')); }); });
    rng.addEventListener('input', function () { cancel(); st.exact = false; st.a = +rng.value * 1e-6; render(); });
    find.addEventListener('click', function () {
      if (st.timer) { cancel(); return; }
      var p = PRESETS[st.p], root = breakEven(p);
      function finish() { st.timer = 0; st.finish = null; find.textContent = 'Find the break-even'; st.a = root; st.exact = true; rng.value = Math.round(root * 1e6); render(); }
      if (!F0.motion()) { finish(); return; }
      st.finish = finish;
      var lo = 0, hi = 0.003, i = 0; st.exact = false; find.textContent = 'Stop';
      (function step() {
        var mid = (lo + hi) / 2; st.a = mid; rng.value = Math.round(mid * 1e6); render();
        if (billM1(p, mid) < 0) lo = mid; else hi = mid;
        if (++i >= 22) { st.timer = setTimeout(finish, 160); return; }
        st.timer = setTimeout(step, 150);
      })();
    });
    /* motion turned off mid-search: jump straight to the answer */
    F0.onMotion(function (on) { if (!on && st.timer) { clearTimeout(st.timer); if (st.finish) st.finish(); } });
    /* twin table */
    var a450 = breakEven(PRESETS.pr450);
    var rows = RANKS.map(function (r) {
      return '<tr><td class="n">' + r + '</td><td class="n">' + grp(H450[r]) + '</td><td class="n">' + grp(H469[r]) + '</td><td class="n">' + minus((H469[r] - H450[r] > 0 ? '+' : '') + (H469[r] - H450[r])) + '</td><td class="n">' + (share(H450, r, 0) * 100).toFixed(3) + '%</td><td class="n">&times;' + Math.pow(BM / r, a450).toFixed(5) + '</td></tr>';
    }).join('');
    $('#b-table').innerHTML = '<table class="tbl"><caption>Child jobs by size r, block width m = 78, W = 1,200 roles</caption><thead><tr><th class="n">Size r</th><th class="n">Jobs, #450</th><th class="n">Jobs, #469</th><th class="n">Change</th><th class="n">Share of bill at a = 0</th><th class="n">Billed &times;(m/r)<sup>a</sup> at #450&rsquo;s break-even</th></tr></thead><tbody>' + rows +
      '<tr><td>Total</td><td class="n">' + grp(E_(H450)) + '</td><td class="n">' + grp(E_(H469)) + '</td><td class="n">&minus;407</td><td class="n">99.564%</td><td></td></tr></tbody></table>' +
      '<table class="tbl"><caption>Break-even saving and &kappa; for each block</caption><thead><tr><th>Block</th><th class="n">Break-even a (your browser)</th><th class="n">&kappa; (your browser, rounded down to 18 decimals)</th><th class="n">&kappa; published</th></tr></thead><tbody>' +
      ['pr450', 'pr464', 'pr469'].map(function (id) { var p = PRESETS[id], a = breakEven(p); return '<tr><td>' + { pr450: '#450', pr464: 'Aska #464', pr469: 'Aska #469' }[id] + '</td><td class="n">' + a.toPrecision(17) + '</td><td class="n">' + floor18(a / (1 + a)) + '</td><td class="n">' + p.pub + '</td></tr>'; }).join('') + '</tbody></table>';
    render();
  }

  function boot() {
    [initLive, initGrid, initSlide, initWorth, initStair, initBudget].forEach(function (f) { try { f(); } catch (e) { console.error(e); } });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
