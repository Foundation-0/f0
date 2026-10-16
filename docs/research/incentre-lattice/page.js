/* Incentre lattice page: five figures, vanilla JS, no dependencies.
   1 the doodle stepper (SVG)            2 the mirror room (canvas; adapted from incentre-lattice mirrors.html, MIT)
   3 every dimension (SVG)               4 fold without stretching (canvas + SVG; formula from fold-continuous.js, MIT)
   5 the search ladder (SVG; data verbatim from autoresearch-fold/results.tsv)
   Source project: https://github.com/Foundation-0/incentre-lattices (code MIT; text and figures CC BY 4.0,
   (c) Ahraz Arifuddin, Aska Digital, and contributors). Colours come from tokens via F0.css and redraw on F0.onTheme. */
(function () {
  'use strict';
  var F0 = window.F0;
  if (!F0) return;
  var $ = function (id) { return document.getElementById(id); };
  var SVGNS = 'http://www.w3.org/2000/svg';
  var S2 = Math.SQRT2, R = S2 - 1;
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
  function mix(a, b, t, alpha) {
    var A = hexRGB(a), B = hexRGB(b);
    var c = [0, 1, 2].map(function (i) { return Math.round(A[i] + (B[i] - A[i]) * t); });
    return alpha == null ? 'rgb(' + c.join(',') + ')' : 'rgba(' + c.join(',') + ',' + alpha + ')';
  }
  function fmt(x, d) { return Number(x).toFixed(d); }
  function pressed(btn, on) { btn.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  /* shared 3D bits: a turntable view (yaw about the vertical axis, pitch toward the viewer), painter's order, shaded balls */
  function turn(v, yaw, pitch) {
    var cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
    var x = cy * v[0] + sy * v[2], z = -sy * v[0] + cy * v[2];
    return [x, cp * v[1] - sp * z, sp * v[1] + cp * z]; // screen x, screen y (up), depth (toward the viewer)
  }
  function ball(ctx, x, y, r, base, bg, dark, alpha) {
    var lo = dark ? mix(base, bg, .78) : mix(base, bg, .45), hi = dark ? mix(base, '#ffffff', .55) : mix(base, '#ffffff', .78), mid = dark ? mix(base, bg, .35) : mix(base, '#ffffff', .35);
    var g = ctx.createRadialGradient(x - r * .32, y - r * .38, r * .06, x, y, r);
    g.addColorStop(0, hi); g.addColorStop(.45, mid); g.addColorStop(1, lo);
    ctx.globalAlpha = alpha == null ? .92 : alpha; ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(x, y, Math.max(.5, r), 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = Math.min(1, (alpha == null ? 1 : alpha) + .2); ctx.strokeStyle = mix(base, bg, .25); ctx.lineWidth = .8; ctx.stroke();
    ctx.globalAlpha = 1;
  }
  /* drag and arrow keys turn a view {yaw, pitch}; redraw() after each change */
  function turntable(cv, view, redraw) {
    var ptr = null;
    cv.addEventListener('pointerdown', function (ev) { ptr = [ev.clientX, ev.clientY]; try { cv.setPointerCapture(ev.pointerId); } catch (e) {} });
    cv.addEventListener('pointermove', function (ev) {
      if (!ptr) return;
      view.yaw += (ev.clientX - ptr[0]) * .008;
      view.pitch = Math.max(-1.45, Math.min(1.45, view.pitch + (ev.clientY - ptr[1]) * .008));
      ptr = [ev.clientX, ev.clientY]; redraw();
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) { cv.addEventListener(t, function () { ptr = null; }); });
    cv.addEventListener('keydown', function (ev) {
      var used = true;
      if (ev.key === 'ArrowLeft') view.yaw -= .12; else if (ev.key === 'ArrowRight') view.yaw += .12;
      else if (ev.key === 'ArrowUp') view.pitch = Math.max(-1.45, view.pitch - .1); else if (ev.key === 'ArrowDown') view.pitch = Math.min(1.45, view.pitch + .1);
      else used = false;
      if (used) { ev.preventDefault(); redraw(); }
    });
  }

  /* =========================================================================
     1. The doodle: a square, diagonals, incentres, touching circles, the 4.8.8 tiling
     ========================================================================= */
  (function doodle() {
    var svg = $('dd-svg'); if (!svg) return;
    var cap = $('dd-cap');
    var CAPS = {
      1: 'Step 1 of 7. Start with a square of side 2.',
      2: 'Step 2 of 7. Its two diagonals cut it into four triangles.',
      3: 'Step 3 of 7. In each triangle, mark the incentre: the one point equally far from all three sides. The circle around it is the largest that fits.',
      4: 'Step 4 of 7. Neighbouring circles just touch, along the diagonals and across the edges: every radius is √2 − 1 ≈ 0.4142.',
      5: 'Step 5 of 7. Repeat the square in every direction. Joining the centres of touching balls draws octagons and squares: the 4.8.8 tiling.',
      6: 'Step 6 of 7. Into 3D: cut a cube of side 2 from its centre into six pyramids, one per face. Each pyramid’s incentre sits 2 − √2 from the centre, and balls of radius √2 − 1 there touch their four neighbours and the cube’s faces: together they form an octahedron.',
      7: ''
    };
    var centres = function (i, j) { var x = 2 * i, y = 2 * j; return [[x + 1, y + R], [x + 2 - R, y + 1], [x + 1, y + 2 - R], [x + R, y + 1]]; };
    var L = [];
    for (var k = 1; k <= 5; k++) L[k] = el('g', { 'class': 'dd-layer' }, null);
    // layer 5 (neighbours) goes underneath everything
    svg.appendChild(L[5]);
    for (k = 1; k <= 4; k++) svg.appendChild(L[k]);
    // neighbours: squares, diagonals, circles, the contact network
    var allC = [];
    for (var i = -1; i <= 1; i++) for (var j = -1; j <= 1; j++) {
      var cs = centres(i, j); allC = allC.concat(cs);
      if (i === 0 && j === 0) continue;
      el('rect', { x: 2 * i, y: 2 * j, width: 2, height: 2, 'class': 'dd-sq-n' }, L[5]);
      el('path', { d: 'M' + 2 * i + ' ' + 2 * j + 'l2 2M' + (2 * i + 2) + ' ' + 2 * j + 'l-2 2', 'class': 'dd-diag-n' }, L[5]);
      cs.forEach(function (c) { el('circle', { cx: c[0], cy: c[1], r: R, 'class': 'dd-circ-n' }, L[5]); });
    }
    var net = '';
    for (var a = 0; a < allC.length; a++) for (var b = a + 1; b < allC.length; b++) {
      var d = Math.hypot(allC[a][0] - allC[b][0], allC[a][1] - allC[b][1]);
      if (Math.abs(d - 2 * R) < 1e-6) net += 'M' + fmt(allC[a][0], 4) + ' ' + fmt(allC[a][1], 4) + 'L' + fmt(allC[b][0], 4) + ' ' + fmt(allC[b][1], 4);
    }
    el('path', { d: net, 'class': 'dd-net' }, L[5]);
    allC.forEach(function (c) { if (!(c[0] > 0 && c[0] < 2 && c[1] > 0 && c[1] < 2)) el('circle', { cx: c[0], cy: c[1], r: .035, 'class': 'dd-dot-n' }, L[5]); });
    var t8 = el('text', { x: 0, y: 0.06, 'text-anchor': 'middle', 'class': 'dd-lab k' }, L[5]); t8.textContent = '8';
    var t4 = el('text', { x: 1, y: 1.05, 'text-anchor': 'middle', 'class': 'dd-lab k' }, L[5]); t4.textContent = '4';
    // layer 1: the square
    el('rect', { x: 0, y: 0, width: 2, height: 2, 'class': 'dd-sq' }, L[1]);
    var side = el('text', { x: 1, y: 2.2, 'text-anchor': 'middle', 'class': 'dd-lab' }, L[1]); side.textContent = 'side 2';
    // layer 2: diagonals
    el('path', { d: 'M0 0L2 2M2 0L0 2', 'class': 'dd-diag' }, L[2]);
    // layer 3: incentres and incircles
    centres(0, 0).forEach(function (c) { el('circle', { cx: c[0], cy: c[1], r: R, 'class': 'dd-circ' }, L[3]); });
    centres(0, 0).forEach(function (c) { el('circle', { cx: c[0], cy: c[1], r: .045, 'class': 'dd-dot' }, L[3]); });
    el('path', { d: 'M1 ' + R + 'L1 0', 'class': 'dd-r' }, L[3]);
    var rl = el('text', { x: 1.06, y: -.07, 'class': 'dd-lab' }, L[3]); rl.textContent = 'r = √2−1';
    // layer 4: the touching points
    var touch = [[(1 + R) / 2, (1 + R) / 2], [2 - (1 + R) / 2, (1 + R) / 2], [(1 + R) / 2, 2 - (1 + R) / 2], [2 - (1 + R) / 2, 2 - (1 + R) / 2], [1, 0], [2, 1], [1, 2], [0, 1]];
    touch.forEach(function (p) { el('circle', { cx: p[0], cy: p[1], r: .032, 'class': 'dd-touch' }, L[4]); });
    var tl = el('text', { x: -.07, y: 1.04, 'text-anchor': 'end', 'class': 'dd-lab' }, L[4]); tl.textContent = 'touch';

    /* steps 6 and 7: one cube cut into six pyramids, then N x N x N cubes, drawn in 3D on a canvas */
    var cv = $('dd-canvas'), C3 = cv ? F0.canvas(cv) : null, ctl = $('dd-3d'), cur = 4;
    var v3 = { yaw: .62, pitch: .38, n: 2, balls: true }, D = 2 - S2; // ball centres sit D from the cube centre, radius R
    var AX = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    var VIEWS = { face: [0, 0], edge: [Math.PI / 4, 0], corner: [Math.PI / 4, Math.asin(1 / Math.sqrt(3))] };
    function contacts(n) { return 12 * n * n * n + 3 * n * n * (n - 1); }
    function draw3() {
      if (!C3 || cur < 6 || !C3.w) return;
      var ctx = C3.ctx, W = C3.w, H = C3.h, n = cur === 6 ? 1 : v3.n;
      var col = { acc: F0.css('--acc-incentre'), ink2: F0.css('--ink-2'), ink3: F0.css('--ink-3'), line: F0.css('--line-ui'), bg: F0.css('--bg-1'), dark: F0.theme() === 'dark' };
      ctx.setTransform(C3.dpr, 0, 0, C3.dpr, 0, 0); ctx.clearRect(0, 0, W, H);
      var k = Math.min(W, H - 56) / 2 / (n * Math.sqrt(3) + .15), off = n - 1; // cube centres at 2i - (n - 1)
      function P(v) { var t = turn(v, v3.yaw, v3.pitch); return [W / 2 + t[0] * k, H / 2 + 6 - t[1] * k, t[2]]; }
      var items = [], cells = [];
      for (var i = 0; i < n; i++) for (var j = 0; j < n; j++) for (var l = 0; l < n; l++) {
        var c = [2 * i - off, 2 * j - off, 2 * l - off], bs = AX.map(function (a) { return P([c[0] + a[0] * D, c[1] + a[1] * D, c[2] + a[2] * D]); });
        cells.push({ c: c, b: bs, ijk: [i, j, l] });
        bs.forEach(function (p) { items.push({ z: p[2], ball: p }); });
        for (var a = 0; a < 6; a++) for (var b = a + 1; b < 6; b++) if ((a >> 1) !== (b >> 1)) items.push({ z: (bs[a][2] + bs[b][2]) / 2, a: bs[a], b: bs[b] });
      }
      // rods across shared faces: the +axis ball of one cube to the -axis ball of the next
      cells.forEach(function (cl) {
        cells.forEach(function (o) {
          for (var ax = 0; ax < 3; ax++) {
            var d = [0, 0, 0]; d[ax] = 1;
            if (o.ijk[0] === cl.ijk[0] + d[0] && o.ijk[1] === cl.ijk[1] + d[1] && o.ijk[2] === cl.ijk[2] + d[2]) items.push({ z: (cl.b[2 * ax][2] + o.b[2 * ax + 1][2]) / 2, a: cl.b[2 * ax], b: o.b[2 * ax + 1], bridge: true });
          }
        });
      });
      // the cubes' edges (and, in step 6, the pyramids' edges from the centre to each corner), behind everything
      ctx.lineWidth = 1; ctx.strokeStyle = col.line; ctx.globalAlpha = .6;
      cells.forEach(function (cl) {
        var cr = []; for (var q = 0; q < 8; q++) cr.push(P([cl.c[0] + (q & 1 ? 1 : -1), cl.c[1] + (q & 2 ? 1 : -1), cl.c[2] + (q & 4 ? 1 : -1)]));
        ctx.beginPath();
        for (var q1 = 0; q1 < 8; q1++) for (var q2 = q1 + 1; q2 < 8; q2++) { var x = q1 ^ q2; if (x === 1 || x === 2 || x === 4) { ctx.moveTo(cr[q1][0], cr[q1][1]); ctx.lineTo(cr[q2][0], cr[q2][1]); } }
        ctx.stroke();
        if (cur === 6) { var o = P(cl.c); ctx.setLineDash([3, 4]); ctx.beginPath(); cr.forEach(function (p) { ctx.moveTo(o[0], o[1]); ctx.lineTo(p[0], p[1]); }); ctx.stroke(); ctx.setLineDash([]); }
      });
      ctx.globalAlpha = 1;
      items.sort(function (u, w) { return u.z - w.z; });
      var showBalls = cur === 6 || v3.balls;
      items.forEach(function (it) {
        if (it.ball) {
          if (showBalls) ball(ctx, it.ball[0], it.ball[1], R * k, col.acc, col.bg, col.dark, .9);
          else { ctx.fillStyle = col.ink2; ctx.beginPath(); ctx.arc(it.ball[0], it.ball[1], 3.4, 0, Math.PI * 2); ctx.fill(); }
        } else {
          ctx.strokeStyle = it.bridge ? col.acc : col.ink3; ctx.lineWidth = it.bridge ? 2.4 : (showBalls ? 1 : 1.4);
          ctx.globalAlpha = it.bridge ? 1 : (showBalls ? .7 : .9); ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(it.a[0], it.a[1]); ctx.lineTo(it.b[0], it.b[1]); ctx.stroke(); ctx.globalAlpha = 1;
        }
      });
    }
    function caption7() {
      var n = v3.n, c = contacts(n);
      return 'Step 7 of 7. Stack the cubes: each ball also touches the ball across the shared face (the green rods). ' + n + ' × ' + n + ' × ' + n + (n === 1 ? ' cube holds ' : ' cubes hold ') + 6 * n * n * n + ' balls and 12N<sup>3</sup> + 3N<sup>2</sup>(N − 1) = ' + c + ' touching pairs. These ball centres are where the boron atoms sit in calcium hexaboride.';
    }
    function show(step) {
      cur = step;
      var flat = step <= 5;
      for (var k = 1; k <= 5; k++) L[k].classList.toggle('off', k > step);
      svg.style.display = flat ? '' : 'none'; if (cv) cv.hidden = flat; if (ctl) ctl.hidden = step !== 7;
      svg.setAttribute('viewBox', step >= 5 ? '-1.25 -1.25 4.5 4.5' : '-0.55 -0.55 3.1 3.1');
      side.style.display = step >= 5 ? 'none' : '';
      document.querySelectorAll('.dd-seg button').forEach(function (b) { pressed(b, +b.dataset.step === step); });
      var corner = $('dd-corner'); if (corner) corner.textContent = flat ? 'Square of side 2' : step === 6 ? 'Cube of side 2 · drag to turn' : 'Cubes of side 2 · drag to turn';
      if (step === 7) cap.innerHTML = caption7(); else cap.textContent = CAPS[step];
      if (!flat && C3) { C3.fit(); draw3(); }
    }
    if (cv && C3) {
      turntable(cv, v3, function () { document.querySelectorAll('.dd-3d [data-view]').forEach(function (b) { pressed(b, false); }); draw3(); });
      C3.resize(draw3); F0.onTheme(draw3);
      var nIn = $('dd-n'), nOut = $('dd-n-out');
      nIn.addEventListener('input', function () { v3.n = +nIn.value; nOut.textContent = v3.n; nIn.setAttribute('aria-valuetext', v3.n + ' per side, ' + contacts(v3.n) + ' touching pairs'); cap.innerHTML = caption7(); draw3(); });
      var bB = $('dd-balls'), bR = $('dd-rods');
      bB.addEventListener('click', function () { v3.balls = true; pressed(bB, true); pressed(bR, false); draw3(); });
      bR.addEventListener('click', function () { v3.balls = false; pressed(bB, false); pressed(bR, true); draw3(); });
      document.querySelectorAll('.dd-3d [data-view]').forEach(function (b) {
        b.addEventListener('click', function () {
          var v = VIEWS[b.dataset.view]; v3.yaw = v[0]; v3.pitch = v[1];
          document.querySelectorAll('.dd-3d [data-view]').forEach(function (x) { pressed(x, x === b); });
          draw3();
        });
      });
    }
    var ent = null;
    document.querySelectorAll('.dd-seg button').forEach(function (b) {
      b.addEventListener('click', function () { if (ent && ent.running) ent.finish(); show(+b.dataset.step); });
    });
    show(4);
    /* one-shot entrance (README section 5): with motion on, when the figure first comes into view it builds
       steps 1 to 4 in 1.2 s and stops on step 4, the informative frame; the caption is quiet until it ends */
    if (F0.enter) {
      ent = F0.enter(svg.closest('.fig') || svg, function (t) {
        cap.setAttribute('aria-live', t < 1 ? 'off' : 'polite');
        var s = Math.min(4, 1 + Math.floor(t * 4)); if (s !== cur) show(s);
      }, { duration: 1200, threshold: 0.5 });
    }
  })();

  /* =========================================================================
     2. The mirror room (adapted from incentre-lattice mirrors.html, MIT)
     ========================================================================= */
  (function mirrorRoom() {
    var cv = $('mr-canvas'); if (!cv) return;
    var C = F0.canvas(cv);
    var st = { P: [1, R], lock: true, balls: true };
    var D4 = [[1, 0, 0, 1], [-1, 0, 0, 1], [1, 0, 0, -1], [-1, 0, 0, -1], [0, 1, 1, 0], [0, -1, 1, 0], [0, 1, -1, 0], [0, -1, -1, 0]];
    var gens = [function (p) { return [p[0], -p[1]]; }, function (p) { return [p[1], p[0]]; }, function (p) { return [2 - p[0], p[1]]; }];
    var NAMES = ['floor', 'diagonal', 'centre line'];
    function dists(p) { return [p[1], (p[0] - p[1]) / S2, 1 - p[0]]; }
    var view = { cx: 1, cy: .78, span: 3.1 };
    function k() { return Math.min(C.w, C.h) / view.span; }
    function X(x) { return C.w / 2 + (x - view.cx) * k(); }
    function Y(y) { return C.h / 2 - (y - view.cy) * k(); }
    function draw() {
      var ctx = C.ctx, W = C.w, H = C.h, s = k();
      var col = { bg: F0.css('--bg-1'), grid: F0.css('--grid'), lineui: F0.css('--line-ui'), ink: F0.css('--ink'), ink2: F0.css('--ink-2'), ink3: F0.css('--ink-3'),
        acc: F0.css('--acc-incentre'), w: [F0.css('--w0'), F0.css('--w1'), F0.css('--w2')] };
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = col.bg; ctx.fillRect(0, 0, W, H);
      var xmin = view.cx - W / 2 / s - .2, xmax = view.cx + W / 2 / s + .2, ymin = view.cy - H / 2 / s - .2, ymax = view.cy + H / 2 / s + .2;
      // mirror lines: every integer line, and diagonals with even constants
      ctx.lineWidth = 1;
      for (var x = Math.floor(xmin); x <= xmax; x++) { ctx.strokeStyle = x % 2 === 0 ? col.lineui : col.grid; ctx.globalAlpha = x % 2 === 0 ? .55 : 1; ctx.beginPath(); ctx.moveTo(X(x), 0); ctx.lineTo(X(x), H); ctx.stroke(); }
      for (var y = Math.floor(ymin); y <= ymax; y++) { ctx.strokeStyle = y % 2 === 0 ? col.lineui : col.grid; ctx.globalAlpha = y % 2 === 0 ? .55 : 1; ctx.beginPath(); ctx.moveTo(0, Y(y)); ctx.lineTo(W, Y(y)); ctx.stroke(); }
      ctx.globalAlpha = 1; ctx.strokeStyle = col.grid;
      for (var m = -8; m <= 8; m += 2) {
        ctx.beginPath(); ctx.moveTo(X(xmin), Y(xmin - m)); ctx.lineTo(X(xmax), Y(xmax - m)); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(X(xmin), Y(m - xmin)); ctx.lineTo(X(xmax), Y(m - xmax)); ctx.stroke();
      }
      // the chamber
      ctx.fillStyle = mix(col.acc, col.bg, .82);
      ctx.beginPath(); ctx.moveTo(X(0), Y(0)); ctx.lineTo(X(1), Y(0)); ctx.lineTo(X(1), Y(1)); ctx.closePath(); ctx.fill();
      ctx.lineWidth = 2;
      [[[0, 0], [1, 0], 0], [[0, 0], [1, 1], 1], [[1, 0], [1, 1], 2]].forEach(function (w) {
        ctx.strokeStyle = col.w[w[2]]; ctx.globalAlpha = .9;
        ctx.beginPath(); ctx.moveTo(X(w[0][0]), Y(w[0][1])); ctx.lineTo(X(w[1][0]), Y(w[1][1])); ctx.stroke();
      });
      ctx.globalAlpha = 1;
      var P = st.P, d = dists(P), e = d.map(function (v) { return 2 * v; });
      var nz = e.filter(function (v) { return v > 1e-6; }), emin = Math.min.apply(null, nz);
      // the orbit of P and its links
      var seen = {}, pts = {}, list = [];
      function key(p) { return Math.round(p[0] * 1e4) + ',' + Math.round(p[1] * 1e4); }
      ctx.lineCap = 'round';
      for (var g = 0; g < 8; g++) for (var a = -2; a <= 3; a++) for (var b = -2; b <= 3; b++) {
        var M = D4[g];
        var ap = function (q) { return [M[0] * q[0] + M[1] * q[1] + 2 * a, M[2] * q[0] + M[3] * q[1] + 2 * b]; };
        var A = ap(P);
        if (A[0] < xmin - 1 || A[0] > xmax + 1 || A[1] < ymin - 1 || A[1] > ymax + 1) continue;
        var ka = key(A); if (!pts[ka]) { pts[ka] = A; list.push(A); }
        for (var i = 0; i < 3; i++) {
          if (e[i] < 1e-6) continue;
          var B = ap(gens[i](P)), kb = key(B), ky = (ka < kb ? ka + '|' + kb : kb + '|' + ka) + i;
          if (seen[ky]) continue; seen[ky] = 1;
          ctx.strokeStyle = col.w[i]; ctx.lineWidth = 2.2;
          ctx.beginPath(); ctx.moveTo(X(A[0]), Y(A[1])); ctx.lineTo(X(B[0]), Y(B[1])); ctx.stroke();
        }
      }
      if (st.balls && nz.length) {
        ctx.strokeStyle = col.ink3; ctx.lineWidth = 1; ctx.fillStyle = mix(col.acc, col.bg, .9, .55);
        list.forEach(function (A) { ctx.beginPath(); ctx.arc(X(A[0]), Y(A[1]), emin / 2 * s, 0, Math.PI * 2); ctx.fill(); ctx.stroke(); });
      }
      ctx.fillStyle = col.ink2;
      list.forEach(function (A) { ctx.beginPath(); ctx.arc(X(A[0]), Y(A[1]), 2.6, 0, Math.PI * 2); ctx.fill(); });
      // distances from P to the three walls
      var feet = [[P[0], 0], [(P[0] + P[1]) / 2, (P[0] + P[1]) / 2], [1, P[1]]];
      ctx.lineWidth = 1.4;
      feet.forEach(function (q, i) {
        if (d[i] < 1e-6) return;
        ctx.strokeStyle = col.w[i]; ctx.globalAlpha = .75;
        ctx.beginPath(); ctx.moveTo(X(P[0]), Y(P[1])); ctx.lineTo(X(q[0]), Y(q[1])); ctx.stroke();
      });
      ctx.globalAlpha = 1;
      var eq = nz.length > 0 && Math.max.apply(null, nz) - emin < 2e-3;
      ctx.fillStyle = col.bg; ctx.beginPath(); ctx.arc(X(P[0]), Y(P[1]), 9, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = col.ink; ctx.beginPath(); ctx.arc(X(P[0]), Y(P[1]), 6.5, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = eq ? col.acc : col.ink3; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(X(P[0]), Y(P[1]), 12, 0, Math.PI * 2); ctx.stroke();
      return { P: P, d: d, e: e, eq: eq, nz: nz };
    }
    var bars = document.querySelectorAll('#mr-bars .mr-bar');
    function update() {
      var r = draw();
      var P = r.P, e = r.e;
      var ang = Math.atan2(P[1], P[0]) * 180 / Math.PI;
      $('mr-angle').textContent = (C.w < 440 ? '' : 'Angle at the corner ') + fmt(ang, 2) + '°';
      bars.forEach(function (b, i) {
        var none = e[i] < 1e-6;
        b.querySelector('.tr i').style.width = (none ? 0 : Math.min(100, e[i] / 1.2 * 100)) + '%';
        b.querySelector('.val').textContent = none ? 'none' : fmt(e[i], 4);
      });
      var v = $('mr-verdict'), txt;
      if (st.lock) {
        if (r.eq) txt = '<b>All links equal (' + fmt(e[0], 4) + ').</b> The dot is at height √2 − 1 = 0.4142 on the centre line, exactly 22.5° up from the corner, so balls of radius 0.4142 all touch.';
        else txt = 'Unequal: across the floor ' + fmt(e[0], 4) + ', across the diagonal ' + fmt(e[1], 4) + '. On the centre line they match only at height √2 − 1 ≈ 0.4142 (22.5°). The dot is at height ' + fmt(P[1], 4) + ' (' + fmt(ang, 1) + '°).';
      } else {
        if (r.eq && r.nz.length === 3) txt = '<b>All three links equal (' + fmt(e[0], 4) + ').</b> This is the chamber’s own incentre, (0.7071, 0.2929), which also sits on the 22.5° line.';
        else if (r.eq) txt = '<b>All links equal (' + fmt(r.nz[0], 4) + ').</b> The dot sits on a wall, so one kind of link has vanished.';
        else txt = 'Three kinds of link: ' + e.map(function (x, i) { return NAMES[i] + ' ' + (x < 1e-6 ? 'none' : fmt(x, 4)); }).join(', ') + '. All three match only at the chamber’s incentre.';
      }
      v.innerHTML = txt; v.classList.toggle('eq', r.eq);
      $('mr-tx').textContent = fmt(P[0], 6); $('mr-ty').textContent = fmt(P[1], 6);
      [0, 1, 2].forEach(function (i) { $('mr-t' + i).textContent = e[i] < 1e-6 ? 'none' : fmt(e[i], 6); });
      cv.setAttribute('aria-label', 'The mirror room. The dot is at (' + fmt(P[0], 3) + ', ' + fmt(P[1], 3) + '). Arrow keys move the dot; hold Shift for bigger steps.');
    }
    function setP(p, snap) {
      if (st.lock) p = [1, Math.max(0, Math.min(1, p[1]))];
      else { p[1] = Math.max(0, p[1]); p[0] = Math.min(1, Math.max(0, p[0])); if (p[1] > p[0]) p[1] = p[0]; }
      if (snap) {
        if (Math.abs(p[1] - R) < .012 && p[0] > .985) p = [1, R];
        if (Math.hypot(p[0] - S2 / 2, p[1] - (1 - S2 / 2)) < .015) p = [S2 / 2, 1 - S2 / 2];
      }
      st.P = p; update();
    }
    function fromEvent(ev) {
      var r = cv.getBoundingClientRect(), s = k();
      return [view.cx + (ev.clientX - r.left - C.w / 2) / s, view.cy - (ev.clientY - r.top - C.h / 2) / s];
    }
    var dragging = false;
    cv.addEventListener('pointerdown', function (ev) { dragging = true; try { cv.setPointerCapture(ev.pointerId); } catch (e) {} setP(fromEvent(ev), true); });
    cv.addEventListener('pointermove', function (ev) { if (dragging) setP(fromEvent(ev), true); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) { cv.addEventListener(t, function () { dragging = false; }); });
    cv.addEventListener('keydown', function (ev) {
      var step = ev.shiftKey ? .02 : .005, p = st.P.slice(), used = true;
      if (ev.key === 'ArrowUp') p[1] += step; else if (ev.key === 'ArrowDown') p[1] -= step;
      else if (ev.key === 'ArrowLeft') p[0] -= step; else if (ev.key === 'ArrowRight') p[0] += step;
      else used = false;
      if (used) { ev.preventDefault(); setP(p, false); }
    });
    var lockBtn = $('mr-lock'), ballBtn = $('mr-balls');
    $('mr-snap-dot').addEventListener('click', function () { st.lock = true; pressed(lockBtn, true); setP([1, R]); });
    $('mr-snap-all').addEventListener('click', function () { st.lock = false; pressed(lockBtn, false); setP([S2 / 2, 1 - S2 / 2]); });
    lockBtn.addEventListener('click', function () { st.lock = !st.lock; pressed(lockBtn, st.lock); setP(st.P.slice()); });
    ballBtn.addEventListener('click', function () { st.balls = !st.balls; pressed(ballBtn, st.balls); update(); });
    C.resize(update); F0.onTheme(update);
    update();
  })();

  /* =========================================================================
     3. Every dimension: cross-polytope schematic + Poisson-ratio columns
     ========================================================================= */
  (function dimensions() {
    var poly = $('dm-poly'), chart = $('dm-chart'), range = $('dm-n'); if (!poly || !chart || !range) return;
    var NS = [3, 4, 5, 6, 7, 8];
    function nu(n) { return 1 / (n * n - n - 1); }
    // table twin
    var tb = $('dm-tbody');
    NS.forEach(function (n) {
      var tr = document.createElement('tr');
      [n, 2 * n, 2 * n - 1, 2 * n * n - n, n * (n - 1) / 2, n * (n - 3) / 2, '1/' + (n * n - n - 1) + ' = ' + fmt(nu(n), 4)].forEach(function (v) {
        var td = document.createElement('td'); td.className = 'n'; td.textContent = v; tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    // chart frame (columns, emphasis form: the chosen n in the accent, the rest muted)
    var M = { l: 40, r: 12, t: 26, b: 40 }, W = 300, H = 260, pw = W - M.l - M.r, ph = H - M.t - M.b;
    var yv = function (v) { return M.t + ph - v / .22 * ph; };
    [0, .1, .2].forEach(function (v) {
      el('line', { x1: M.l, x2: W - M.r, y1: yv(v), y2: yv(v), stroke: 'var(--grid)', 'stroke-width': 1 }, chart);
      var t = el('text', { x: M.l - 8, y: yv(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, chart); t.textContent = v === 0 ? '0' : fmt(v, 1);
    });
    var ttl = el('text', { x: M.l, y: 14, 'font-size': 11, fill: 'var(--ink-2)' }, chart); ttl.textContent = 'POISSON RATIO 1/(n';
    var sup = el('tspan', { 'baseline-shift': 'super', 'font-size': '8.5' }, ttl); sup.textContent = '2';
    var rest = el('tspan', {}, ttl); rest.textContent = '−n−1)';
    var band = pw / NS.length, bw = Math.min(24, band * .55), cols = [];
    NS.forEach(function (n, i) {
      var g = el('g', { 'class': 'dm-col', style: 'cursor:pointer' }, chart);
      var x = M.l + band * i + band / 2;
      var h = ph - (yv(nu(n)) - M.t);
      el('rect', { x: M.l + band * i, y: M.t, width: band, height: ph, fill: 'transparent' }, g);
      var top = yv(nu(n)), r = 4;
      var p = el('path', { d: 'M' + (x - bw / 2) + ' ' + yv(0) + 'V' + (top + r) + 'Q' + (x - bw / 2) + ' ' + top + ' ' + (x - bw / 2 + r) + ' ' + top + 'H' + (x + bw / 2 - r) + 'Q' + (x + bw / 2) + ' ' + top + ' ' + (x + bw / 2) + ' ' + (top + r) + 'V' + yv(0) + 'Z' }, g);
      var lab = el('text', { x: x, y: top - 6, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-2)' }, g); lab.textContent = '1/' + (n * n - n - 1);
      var xl = el('text', { x: x, y: H - M.b + 18, 'text-anchor': 'middle', 'font-size': 11.5, fill: 'var(--ink-2)' }, g); xl.textContent = 'n=' + n;
      g.addEventListener('click', function () { set(n); });
      g.addEventListener('pointermove', function (ev) { F0.tip.show('<div class="tip-k">Dimension ' + n + '</div><div class="tip-t">ν = 1/' + (n * n - n - 1) + ' = ' + fmt(nu(n), 4) + '</div><div class="tip-note">Stretch by 1% along a cube axis and it thins by ' + fmt(nu(n), 3) + '% sideways.</div>', ev.clientX, ev.clientY); });
      g.addEventListener('pointerleave', function () { F0.tip.hide(); });
      cols.push({ n: n, p: p, lab: lab });
    });
    el('line', { x1: M.l, x2: W - M.r, y1: yv(0), y2: yv(0), stroke: 'var(--line-ui)', 'stroke-width': 1 }, chart);
    /* the 2n balls around one cube centre in n dimensions (a cross-polytope), turned in n-dimensional space and projected
       onto the page. At angle 0 it is the flat picture: ball i at angle 180°·i/n, its opposite partner across the centre. */
    var ang = 0, polyN = 0, P = null, nodes = null;
    function basis(n) {
      var u = [], v = [], w = [], g = [], i;
      for (i = 0; i < n; i++) { u.push(Math.cos(Math.PI * i / n) * Math.sqrt(2 / n)); v.push(Math.sin(Math.PI * i / n) * Math.sqrt(2 / n)); g.push(i + 1.7); }
      var gu = 0, gv = 0; for (i = 0; i < n; i++) { gu += g[i] * u[i]; gv += g[i] * v[i]; }
      var nn = 0; for (i = 0; i < n; i++) { w.push(g[i] - gu * u[i] - gv * v[i]); nn += w[i] * w[i]; }
      nn = Math.sqrt(nn) || 1; for (i = 0; i < n; i++) w[i] /= nn;
      return [u, v, w];
    }
    function rotated(n, t) { // the n unit axes after turning in the planes (0,1), (1,2), ... at different speeds
      var E = [], i, k;
      for (i = 0; i < n; i++) { var e = []; for (k = 0; k < n; k++) e.push(i === k ? 1 : 0); E.push(e); }
      for (k = 0; k < n - 1; k++) {
        var th = t / (1 + .55 * k), c = Math.cos(th), sn = Math.sin(th);
        E.forEach(function (e) { var a = e[k], b = e[k + 1]; e[k] = c * a - sn * b; e[k + 1] = sn * a + c * b; });
      }
      return E;
    }
    function drawPoly(n) {
      if (n !== polyN) {
        polyN = n; P = basis(n);
        while (poly.firstChild) poly.removeChild(poly.firstChild);
        nodes = { edges: el('path', { stroke: 'var(--ink-3)', 'stroke-width': n > 5 ? .006 : .009, 'stroke-opacity': n > 5 ? .55 : .75, fill: 'none' }, poly),
          stubs: el('path', { stroke: 'var(--acc-incentre)', 'stroke-width': .028, 'stroke-linecap': 'round', fill: 'none' }, poly), balls: [] };
        for (var q = 0; q < 2 * n; q++) nodes.balls.push(el('circle', { fill: 'color-mix(in srgb, var(--acc-incentre) 22%, var(--bg-1))', stroke: 'var(--acc-incentre)', 'stroke-width': .014 }, poly));
        el('circle', { cx: 0, cy: 0, r: .028, fill: 'var(--ink-2)' }, poly);
      }
      var E = rotated(n, ang), pts = [];
      for (var i = 0; i < n; i++) for (var sgn = 1; sgn >= -1; sgn -= 2) {
        var x = 0, y = 0, z = 0;
        for (var k = 0; k < n; k++) { x += sgn * E[i][k] * P[0][k]; y += sgn * E[i][k] * P[1][k]; z += sgn * E[i][k] * P[2][k]; }
        var sc = 1; // a true orthogonal projection: no ball can land farther than 1 from the centre
        pts.push({ ax: i, x: x * sc, y: y * sc, z: z * sc });
      }
      var ed = '', st = '', br = Math.max(.07, .2 - n * .016);
      for (var p = 0; p < pts.length; p++) for (var q2 = p + 1; q2 < pts.length; q2++) if (pts[p].ax !== pts[q2].ax) ed += 'M' + fmt(pts[p].x, 4) + ' ' + fmt(pts[p].y, 4) + 'L' + fmt(pts[q2].x, 4) + ' ' + fmt(pts[q2].y, 4);
      pts.forEach(function (pt) { var m = Math.hypot(pt.x, pt.y); if (m > .05) st += 'M' + fmt(pt.x * (1 + br * .9 / m), 4) + ' ' + fmt(pt.y * (1 + br * .9 / m), 4) + 'L' + fmt(pt.x * (1 + .24 / m), 4) + ' ' + fmt(pt.y * (1 + .24 / m), 4); });
      nodes.edges.setAttribute('d', ed); nodes.stubs.setAttribute('d', st);
      var order = pts.map(function (pt, j) { return j; }).sort(function (a, b) { return pts[a].z - pts[b].z; }), ok = order.join();
      order.forEach(function (j) {
        var c = nodes.balls[j], pt = pts[j], dz = Math.max(-1, Math.min(1, pt.z));
        c.setAttribute('cx', fmt(pt.x, 3)); c.setAttribute('cy', fmt(pt.y, 3)); c.setAttribute('r', fmt(br * (1 + .18 * dz), 3));
        c.setAttribute('fill-opacity', fmt(.75 + .25 * dz, 2));
        if (ok !== nodes.order) poly.appendChild(c); // nearer balls drawn last; reorder only when the order changes
      });
      nodes.order = ok;
    }
    // turning: drag the picture, or press Turn (with motion off, each press turns it by 15°)
    var turnBtn = $('dm-turn'), turning = false, lastT = 0;
    var tl = F0.loop(function (now) { if (!lastT) lastT = now; ang += Math.min(.1, (now - lastT) / 1000) * .55; lastT = now; drawPoly(+range.value); });
    function setTurning(on) { turning = on; lastT = 0; if (turnBtn) { pressed(turnBtn, on); turnBtn.setAttribute('aria-label', on ? 'Stop turning' : (F0.motion() ? 'Turn the picture' : 'Turn the picture by 15 degrees')); } if (on) tl.start(); else tl.stop(); }
    if (turnBtn) turnBtn.addEventListener('click', function () {
      if (!F0.motion()) { ang += Math.PI / 12; drawPoly(+range.value); return; }
      setTurning(!turning);
    });
    F0.onMotion(function (on) { if (!on && turning) setTurning(false); });
    F0.whenVisible(poly, null, function () { if (turning) setTurning(false); });
    var dptr = null;
    poly.addEventListener('pointerdown', function (ev) { dptr = ev.clientX; try { poly.setPointerCapture(ev.pointerId); } catch (e) {} if (turning) setTurning(false); });
    poly.addEventListener('pointermove', function (ev) { if (dptr == null) return; ang += (ev.clientX - dptr) * .01; dptr = ev.clientX; drawPoly(+range.value); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) { poly.addEventListener(t, function () { dptr = null; }); });
    function set(n) {
      n = Math.max(3, Math.min(8, n | 0));
      range.value = n; $('dm-n-out').textContent = n;
      range.setAttribute('aria-valuetext', 'dimension ' + n + ', Poisson ratio 1/' + (n * n - n - 1));
      cols.forEach(function (c) {
        var on = c.n === n;
        c.p.setAttribute('fill', on ? 'var(--acc-incentre)' : 'var(--mark-mid)');
        c.lab.setAttribute('fill', on ? 'var(--ink)' : 'var(--ink-3)');
        c.lab.setAttribute('font-weight', on ? 600 : 400);
      });
      drawPoly(n);
      $('dm-balls').textContent = 2 * n;
      $('dm-touch').textContent = 2 * n - 1;
      $('dm-rods').textContent = 2 * n * n - n;
      $('dm-zero').textContent = n * (n - 1) / 2;
      $('dm-nu').textContent = '1/' + (n * n - n - 1) + ' = ' + fmt(nu(n), 4);
      $('dm-c').textContent = (n - 1) * (n - 1);
    }
    range.addEventListener('input', function () { set(+range.value); });
    set(3);
  })();

  /* =========================================================================
     3b. Two sizes beat one (results/cab6-packing/PROOF.md): the CaB6 pattern with two ball sizes
     ========================================================================= */
  (function twoSizes() {
    var cv = $('ts-canvas'), svg = $('ts-svg'), range = $('ts-gamma'); if (!cv || !svg || !range) return;
    var G0 = S2 - 1, MS = (S2 - 1) / 2, XS = (S2 - 1) / 2, FCC = Math.PI / Math.sqrt(18);
    function radii(g) { return g <= G0 ? { L: .5, S: g / 2, big: true } : { L: MS / g, S: MS, big: false }; }
    function phi(g) { return g <= G0 ? Math.PI / 6 * (1 + 6 * g * g * g) : Math.PI / 6 * Math.pow(S2 - 1, 3) * (6 + 1 / (g * g * g)); }
    var LO = Math.cbrt((S2 - 1) / 6), HI = Math.pow(4 + 7 * S2, -1 / 3); // 0.41023 and 0.41591, where it meets equal balls
    var st = { g: G0, yaw: .55, pitch: .35 };
    // the cube: Ca at the corners (0,0,0)+..., B at (x*, 1/2, 1/2) and permutations, x* = (sqrt2 - 1)/2 (a = 1)
    var CA = [], B6 = [];
    for (var q = 0; q < 8; q++) CA.push([q & 1 ? .5 : -.5, q & 2 ? .5 : -.5, q & 4 ? .5 : -.5]);
    [0, 1, 2].forEach(function (ax) { [-1, 1].forEach(function (sg) { var v = [0, 0, 0]; v[ax] = sg * (.5 - XS); B6.push(v); }); });
    var C = F0.canvas(cv);
    function draw() {
      if (!C.w) return;
      var ctx = C.ctx, W = C.w, H = C.h, r = radii(st.g), k = Math.min(W, H) / 2 / 1.42;
      var col = { acc: F0.css('--acc-incentre'), ink: F0.css('--ink-3'), line: F0.css('--line-ui'), bg: F0.css('--bg-1'), dark: F0.theme() === 'dark' };
      ctx.setTransform(C.dpr, 0, 0, C.dpr, 0, 0); ctx.clearRect(0, 0, W, H);
      function P(v) { var t = turn(v, st.yaw, st.pitch); return [W / 2 + t[0] * k, H / 2 - t[1] * k, t[2]]; }
      var cr = CA.map(P);
      ctx.strokeStyle = col.line; ctx.lineWidth = 1; ctx.beginPath();
      for (var a = 0; a < 8; a++) for (var b = a + 1; b < 8; b++) { var x = a ^ b; if (x === 1 || x === 2 || x === 4) { ctx.moveTo(cr[a][0], cr[a][1]); ctx.lineTo(cr[b][0], cr[b][1]); } }
      ctx.stroke();
      var items = cr.map(function (p) { return { p: p, r: r.L, big: true }; }).concat(B6.map(function (v) { return { p: P(v), r: r.S, big: false }; }));
      items.sort(function (u, w) { return u.p[2] - w.p[2]; });
      items.forEach(function (it) { ball(ctx, it.p[0], it.p[1], it.r * k, it.big ? col.ink : col.acc, col.bg, col.dark, it.big ? .32 : .95); });
    }
    turntable(cv, st, draw);
    C.resize(draw); F0.onTheme(draw);
    // the curve
    var CW = 320, CH = 240, M = { l: 46, r: 12, t: 26, b: 40 }, g0 = .30, g1 = .60, v0 = .38, v1 = .78;
    var xs = function (g) { return M.l + (g - g0) / (g1 - g0) * (CW - M.l - M.r); }, ys = function (v) { return M.t + (1 - (Math.max(v0, Math.min(v1, v)) - v0) / (v1 - v0)) * (CH - M.t - M.b); };
    var sw = Math.max(5, xs(HI) - xs(LO)), sx = (xs(LO) + xs(HI)) / 2 - sw / 2; // the window is 0.0057 wide: drawn at least 5 units so it shows
    el('rect', { x: sx, y: M.t, width: sw, height: CH - M.t - M.b, fill: 'var(--bio)', 'fill-opacity': .35 }, svg);
    var wl = el('text', { x: sx - 5, y: ys(.5), 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-2)', 'class': 'il-halo' }, svg); wl.textContent = 'wins only here';
    var wl2 = el('text', { x: sx - 5, y: ys(.5) + 14, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)', 'class': 'il-halo' }, svg); wl2.textContent = '0.41023–0.41591';
    [.4, .5, .6, .7].forEach(function (v) {
      el('line', { x1: M.l, x2: CW - M.r, y1: ys(v), y2: ys(v), stroke: 'var(--grid)', 'stroke-width': 1 }, svg);
      var t = el('text', { x: M.l - 6, y: ys(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = Math.round(v * 100) + '%';
    });
    el('line', { x1: M.l, x2: CW - M.r, y1: ys(FCC), y2: ys(FCC), stroke: 'var(--ink-2)', 'stroke-width': 1, 'stroke-dasharray': '4 3' }, svg);
    var fl = el('text', { x: CW - M.r, y: ys(FCC) + 14, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-2)', 'class': 'il-halo' }, svg); fl.textContent = 'equal balls 74.05%';
    var ttl = el('text', { x: M.l, y: 14, 'font-size': 11, fill: 'var(--ink-3)', 'letter-spacing': '.08em' }, svg); ttl.textContent = 'SPACE FILLED, AT BEST';
    el('line', { x1: M.l, x2: CW - M.r, y1: CH - M.b, y2: CH - M.b, stroke: 'var(--line-ui)', 'stroke-width': 1 }, svg);
    [.3, .4, .5, .6].forEach(function (g) { var t = el('text', { x: xs(g), y: CH - M.b + 16, 'text-anchor': g === .3 ? 'start' : g === .6 ? 'end' : 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = fmt(g, 1); });
    var xl = el('text', { x: (M.l + CW - M.r) / 2, y: CH - 6, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); xl.textContent = 'size ratio γ (small ÷ big)';
    var d = '';
    for (var i = 0; i <= 240; i++) { var g = g0 + (g1 - g0) * i / 240; d += (i ? 'L' : 'M') + fmt(xs(g), 2) + ' ' + fmt(ys(phi(g)), 2); }
    // make sure the curve passes exactly through its peak
    el('path', { d: d, fill: 'none', stroke: 'var(--acc-incentre)', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
    el('circle', { cx: xs(G0), cy: ys(phi(G0)), r: 3.5, fill: 'var(--ink)' }, svg);
    var pk = el('text', { x: xs(G0) + 8, y: ys(phi(G0)) - 6, 'font-size': 11, fill: 'var(--ink)', 'class': 'il-halo' }, svg); pk.textContent = '74.69% at √2 − 1';
    var mLine = el('line', { y1: M.t, y2: CH - M.b, stroke: 'var(--ink-3)', 'stroke-width': 1, 'stroke-dasharray': '2 3' }, svg);
    var mDot = el('circle', { r: 5, fill: 'var(--acc-incentre)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, svg);
    var hit = el('rect', { x: M.l, y: M.t, width: CW - M.l - M.r, height: CH - M.t - M.b, fill: 'transparent', style: 'cursor:crosshair' }, svg);
    function gAt(ev) { var b = svg.getBoundingClientRect(), x = (ev.clientX - b.left) / b.width * CW; return Math.max(g0, Math.min(g1, g0 + (x - M.l) / (CW - M.l - M.r) * (g1 - g0))); }
    var drag = false;
    hit.addEventListener('pointermove', function (ev) {
      var g = gAt(ev); F0.tip.show('<div class="tip-k">γ = ' + fmt(g, 4) + '</div><div class="tip-t">' + fmt(phi(g) * 100, 3) + '% at best</div><div class="tip-note">' + (phi(g) > FCC ? 'Beats equal balls.' : 'Below equal balls (74.048%).') + ' Click to set.</div>', ev.clientX, ev.clientY);
      if (drag) set(g);
    });
    hit.addEventListener('pointerleave', function () { F0.tip.hide(); });
    hit.addEventListener('pointerdown', function (ev) { drag = true; try { hit.setPointerCapture(ev.pointerId); } catch (e) {} set(gAt(ev)); });
    ['pointerup', 'pointercancel'].forEach(function (t) { hit.addEventListener(t, function () { drag = false; }); });
    function set(g) {
      st.g = Math.max(g0, Math.min(g1, g));
      if (Math.abs(st.g - G0) < .0008) st.g = G0; // snap to the peak
      var f = phi(st.g), r = radii(st.g), diff = (f - FCC) * 100;
      range.value = String(st.g);
      $('ts-g-out').textContent = fmt(st.g, 4);
      range.setAttribute('aria-valuetext', 'size ratio ' + fmt(st.g, 4) + ', ' + fmt(f * 100, 3) + '% filled');
      $('ts-g').textContent = fmt(st.g, 4) + (st.g === G0 ? ' = √2 − 1' : '');
      $('ts-phi').textContent = fmt(f * 100, 4) + '%';
      $('ts-vs').textContent = Math.abs(diff) < .005 ? 'ties 74.05%: the edge of the window' : diff > 0 ? 'beats 74.05% by ' + fmt(diff, 2) + ' points' : 'below 74.05% by ' + fmt(-diff, 2) + ' points';
      $('ts-touch').textContent = st.g === G0 ? 'both: big balls along the edges, small balls with each other' : r.big ? 'the big balls, along the cube edges; the small ones have room' : 'the small balls, with each other; the big ones have room';
      mLine.setAttribute('x1', xs(st.g)); mLine.setAttribute('x2', xs(st.g));
      mDot.setAttribute('cx', xs(st.g)); mDot.setAttribute('cy', ys(f));
      draw();
    }
    range.addEventListener('input', function () { set(+range.value); });
    $('ts-snap').addEventListener('click', function () { set(G0); });
    $('ts-lo').addEventListener('click', function () { set(LO); });
    $('ts-hi').addEventListener('click', function () { set(HI); });
    var tb = $('ts-tbody');
    [.30, .40, LO, G0, HI, .45, .50, .60].forEach(function (g) {
      var r = radii(g), f = phi(g), tr = document.createElement('tr');
      [g === G0 ? fmt(g, 5) + ' (√2 − 1)' : fmt(g, 5), fmt(r.L, 4), fmt(r.S, 4), fmt(f * 100, 4) + '%', (f - FCC >= -1e-9 ? '+' : '−') + fmt(Math.abs(f - FCC) * 100, 3) + ' points'].forEach(function (v) { var td = document.createElement('td'); td.className = 'n'; td.textContent = v; tr.appendChild(td); });
      tb.appendChild(tr);
    });
    set(G0);
  })();

  /* =========================================================================
     4. Fold without stretching (state(s) ported from fold-continuous.js, MIT)
     ========================================================================= */
  (function fold() {
    var cv = $('fd-canvas'); if (!cv) return;
    var CM = [[0, -1, -1], [1, 0, -1], [1, -1, 0]];
    var MOTIF = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
    function state(s) {
      var t = 2 * s / (1 + s * s), a = S2 * (1 - s * s) / (1 + s * s), d = 2 + a;
      var L = CM.map(function (row, i) { return row.map(function (c, j) { return t * c + (i === j ? d : 0); }); });
      var det = d * d * d + d * t * t + 2 * t * t * t;
      return { s: s, t: t, a: a, L: L, det: det, density: 2 * S2 * Math.PI / det };
    }
    // nearby cell offsets with |n|^2 <= 11 (the proof's 171 translations)
    var NB = [];
    for (var a = -3; a <= 3; a++) for (var b = -3; b <= 3; b++) for (var c = -3; c <= 3; c++) if (a * a + b * b + c * c <= 11) NB.push([a, b, c]);
    function axis(p) { return p >> 1; }
    function sgn(p) { return p % 2 === 0 ? 1 : -1; }
    function bonded(n, p, q) {
      if (!n[0] && !n[1] && !n[2]) return axis(p) !== axis(q);
      var nz = [0, 1, 2].filter(function (i) { return n[i] !== 0; });
      if (nz.length !== 1 || Math.abs(n[nz[0]]) !== 1) return false;
      var i = nz[0], x = n[i];
      return axis(p) === i && axis(q) === i && sgn(p) === -x && sgn(q) === x;
    }
    function measures(S) {
      var L = S.L, gap = Infinity, touching = 0, barErr = 0;
      for (var i = 0; i < 3; i++) {
        var v = [0, 1, 2].map(function (j) { return L[i][j] - (i === j ? 2 : 0); });
        // "Break it": one rod stretched by 1% (the rod joining neighbouring cells along the first edge)
        barErr = Math.max(barErr, Math.abs(Math.hypot(v[0], v[1], v[2]) * (view.stretch && i === 0 ? 1.01 : 1) - S2));
      }
      NB.forEach(function (n) {
        var nl = [0, 1, 2].map(function (j) { return n[0] * L[0][j] + n[1] * L[1][j] + n[2] * L[2][j]; });
        var zero = !n[0] && !n[1] && !n[2];
        for (var p = 0; p < 6; p++) for (var q = 0; q < 6; q++) {
          if (zero && p === q) continue;
          var dd = Math.hypot(nl[0] + MOTIF[p][0] - MOTIF[q][0], nl[1] + MOTIF[p][1] - MOTIF[q][1], nl[2] + MOTIF[p][2] - MOTIF[q][2]);
          if (Math.abs(dd - S2) < 1e-9) touching++;
          if (!bonded(n, p, q) && dd < gap) gap = dd;
        }
      });
      return { gap: gap, contacts: touching / 6, barErr: barErr };
    }
    var C = F0.canvas(cv);
    var view = { yaw: .65, pitch: .42, s: 0, balls: true, stretch: false };
    function project(p) {
      var cy = Math.cos(view.yaw), sy = Math.sin(view.yaw), cp = Math.cos(view.pitch), sp = Math.sin(view.pitch);
      var x = cy * p[0] + sy * p[2], z = -sy * p[0] + cy * p[2];
      // scale from the open scaffold's bounding sphere (radius 4.7), so the drawing never runs under the corner captions
      var band = 28, k = Math.min(C.w - 16, C.h - 2 * band) / 2 / 4.7;
      return [C.w * .5 + x * k, C.h * .5 - (cp * p[1] - sp * z) * k, sp * p[1] + cp * z, k];
    }
    function draw() {
      var ctx = C.ctx, W = C.w, H = C.h;
      var col = { acc: F0.css('--acc-incentre'), ink: F0.css('--ink'), ink2: F0.css('--ink-2'), ink3: F0.css('--ink-3'), bg: F0.css('--bg-1'), bg2: F0.css('--bg-2'), dark: F0.theme() === 'dark' };
      ctx.clearRect(0, 0, W, H);
      var S = state(view.s), L = S.L;
      var off = [0, 1, 2].map(function (j) { return -.5 * (L[0][j] + L[1][j] + L[2][j]); });
      var items = [], cells = {};
      for (var i = 0; i < 2; i++) for (var j = 0; j < 2; j++) for (var k = 0; k < 2; k++) {
        var n = [i, j, k];
        var cen = [0, 1, 2].map(function (m) { return off[m] + n[0] * L[0][m] + n[1] * L[1][m] + n[2] * L[2][m]; });
        var pts = MOTIF.map(function (p) { return project([cen[0] + p[0], cen[1] + p[1], cen[2] + p[2]]); });
        var home = i + j + k === 0;
        cells[n.join(',')] = pts;
        pts.forEach(function (p) { items.push({ z: p[2], ball: true, p: p, home: home }); });
        for (var p = 0; p < 6; p++) for (var q = p + 1; q < 6; q++) if (axis(p) !== axis(q)) items.push({ z: (pts[p][2] + pts[q][2]) / 2, a: pts[p], b: pts[q], bridge: false });
      }
      Object.keys(cells).forEach(function (key) {
        var n = key.split(',').map(Number);
        for (var ax = 0; ax < 3; ax++) {
          var m = n.slice(); m[ax]++;
          var nb = cells[m.join(',')];
          if (nb) { var A = cells[key][2 * ax], B = nb[2 * ax + 1]; items.push({ z: (A[2] + B[2]) / 2, a: A, b: B, bridge: true, bad: view.stretch && ax === 0 && key === '0,0,0' }); }
        }
      });
      items.sort(function (u, v) { return u.z - v.z; });
      var lo = col.dark ? mix(col.acc, col.bg, .78) : mix(col.acc, col.bg, .45);
      var hi = col.dark ? mix(col.acc, '#ffffff', .55) : mix(col.acc, '#ffffff', .78);
      var mid = col.dark ? mix(col.acc, col.bg, .35) : mix(col.acc, '#ffffff', .35);
      var hiH = mix(col.ink, col.bg, .05), midH = mix(col.ink, col.bg, .45), loH = mix(col.ink, col.bg, .8);
      items.forEach(function (it) {
        if (it.ball) {
          var p = it.p, r = view.balls ? p[3] / S2 : 3.6;
          if (view.balls) {
            var g = ctx.createRadialGradient(p[0] - r * .32, p[1] - r * .38, r * .06, p[0], p[1], r);
            g.addColorStop(0, it.home ? hiH : hi); g.addColorStop(.45, it.home ? midH : mid); g.addColorStop(1, it.home ? loH : lo);
            ctx.globalAlpha = .9; ctx.fillStyle = g;
            ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill();
            ctx.globalAlpha = 1; ctx.strokeStyle = it.home ? mix(col.ink, col.bg, .4) : mix(col.acc, col.bg, .25); ctx.lineWidth = .8; ctx.stroke();
          } else {
            ctx.fillStyle = it.home ? col.ink : col.ink2;
            ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2); ctx.fill();
          }
        } else {
          ctx.strokeStyle = it.bad ? F0.css('--hair') : it.bridge ? col.acc : col.ink3;
          ctx.lineWidth = it.bad ? 4 : it.bridge ? (view.balls ? 2.6 : 2.4) : (view.balls ? 1 : 1.3);
          ctx.globalAlpha = it.bridge ? 1 : (view.balls ? .7 : .9);
          ctx.lineCap = 'round';
          ctx.beginPath(); ctx.moveTo(it.a[0], it.a[1]); ctx.lineTo(it.b[0], it.b[1]); ctx.stroke();
          ctx.globalAlpha = 1;
        }
      });
    }
    // density curve
    var svg = $('fd-curve');
    var CW = 320, CH = 230, M = { l: 44, r: 14, t: 26, b: 40 };
    var xs = function (s) { return M.l + s * (CW - M.l - M.r); };
    var ys = function (v) { return M.t + (1 - (v - .2) / (.78 - .2)) * (CH - M.t - M.b); };
    [.3, .4, .5, .6].forEach(function (v) {
      el('line', { x1: M.l, x2: CW - M.r, y1: ys(v), y2: ys(v), stroke: 'var(--grid)', 'stroke-width': 1 }, svg);
      var t = el('text', { x: M.l - 7, y: ys(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = Math.round(v * 100) + '%';
    });
    var kep = Math.PI / Math.sqrt(18);
    el('line', { x1: M.l, x2: CW - M.r, y1: ys(kep), y2: ys(kep), stroke: 'var(--ink-2)', 'stroke-width': 1 }, svg);
    var kt = el('text', { x: M.l + 6, y: ys(kep) + 15, 'font-size': 11, fill: 'var(--ink-2)' }, svg); kt.textContent = 'Kepler bound π/√18 ≈ 74.05%';
    var kt2 = el('text', { x: M.l + 6, y: ys(kep) + 29, 'font-size': 11, fill: 'var(--ink-3)' }, svg); kt2.textContent = '(proved by Hales, 2005)';
    var ttl = el('text', { x: M.l, y: 14, 'font-size': 11, fill: 'var(--ink-3)', 'letter-spacing': '.08em' }, svg); ttl.textContent = 'SPACE FILLED';
    el('line', { x1: M.l, x2: CW - M.r, y1: CH - M.b, y2: CH - M.b, stroke: 'var(--line-ui)', 'stroke-width': 1 }, svg);
    [['0', 0, 'start'], ['s = 1', 1, 'end']].forEach(function (a) { var t = el('text', { x: xs(a[1]), y: CH - M.b + 16, 'text-anchor': a[2], 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = a[0]; });
    var xl = el('text', { x: (M.l + CW - M.r) / 2, y: CH - M.b + 16, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); xl.textContent = 'fold parameter s';
    var dpath = '';
    for (var i = 0; i <= 120; i++) { var s = i / 120; dpath += (i ? 'L' : 'M') + fmt(xs(s), 2) + ' ' + fmt(ys(state(s).density), 2); }
    el('path', { d: dpath, fill: 'none', stroke: 'var(--acc-incentre)', 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, svg);
    var mLine = el('line', { y1: M.t, y2: CH - M.b, stroke: 'var(--ink-3)', 'stroke-width': 1 }, svg);
    var mDot = el('circle', { r: 5, fill: 'var(--acc-incentre)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, svg);
    var hit = el('rect', { x: M.l, y: M.t, width: CW - M.l - M.r, height: CH - M.t - M.b, fill: 'transparent', style: 'cursor:crosshair' }, svg);
    function sFromEvent(ev) { var r = svg.getBoundingClientRect(); var x = (ev.clientX - r.left) / r.width * CW; return Math.max(0, Math.min(1, (x - M.l) / (CW - M.l - M.r))); }
    var curveDrag = false;
    hit.addEventListener('pointermove', function (ev) {
      var s = sFromEvent(ev), S = state(s);
      F0.tip.show('<div class="tip-k">s = ' + fmt(s, 3) + '</div><div class="tip-t">' + fmt(S.density * 100, 2) + '% of space filled</div><div class="tip-note">Click to fold to here.</div>', ev.clientX, ev.clientY);
      if (curveDrag) choose(s);
    });
    hit.addEventListener('pointerleave', function () { F0.tip.hide(); });
    hit.addEventListener('pointerdown', function (ev) { curveDrag = true; try { hit.setPointerCapture(ev.pointerId); } catch (e) {} choose(sFromEvent(ev)); });
    ['pointerup', 'pointercancel'].forEach(function (t) { hit.addEventListener(t, function () { curveDrag = false; }); });

    var slider = $('fd-s'), out = $('fd-s-out');
    var lastRead = 0, say = $('fd-say');
    function update() {
      var S = state(view.s);
      slider.value = String(view.s);
      out.textContent = fmt(view.s, 3);
      var pct = fmt(S.density * 100, 4) + '%';
      slider.setAttribute('aria-valuetext', 's = ' + fmt(view.s, 3) + ', ' + pct + ' of space filled');
      $('fd-corner').textContent = 's = ' + fmt(view.s, 3);
      mLine.setAttribute('x1', xs(view.s)); mLine.setAttribute('x2', xs(view.s));
      mDot.setAttribute('cx', xs(view.s)); mDot.setAttribute('cy', ys(S.density));
      draw();
      // the number readouts change a few times a second at most while the fold plays
      var t = performance.now();
      if (playing && t - lastRead < 250) return;
      lastRead = t;
      var m = measures(S);
      $('fd-dens').textContent = pct;
      $('fd-vol').textContent = fmt(S.det, 3);
      var ex = m.barErr === 0 ? null : m.barErr.toExponential(0).split('e');
      $('fd-bar').innerHTML = '√2 · error ' + (ex ? ex[0] + '×10<sup>' + ex[1].replace('-', '−') + '</sup>' : '0') + (view.stretch ? ' · <b class="fd-no">rejected: not the certified motion</b>' : '');
      $('fd-gap').textContent = fmt(m.gap, 4) + ' (touch: 1.4142)';
      var c = Math.round(m.contacts);
      var nar = C.w < 460;
      $('fd-note').textContent = view.s >= 1 ? (nar ? 'Densest packing · 12 touching' : 'Densest packing (face-centred cubic) · 12 touching neighbours per ball') : (view.s === 0 ? 'Open scaffold' : 'Folding') + ' · ' + c + (nar ? ' touching' : ' touching neighbours per ball');
    }
    // play: 10 s from open to closed, only on press; with motion off it steps by a quarter
    var playBtn = $('fd-play'), playTxt = $('fd-play-txt'), playing = false, lastT = 0;
    var loop = F0.loop(function (now) {
      if (!lastT) lastT = now;
      var dt = Math.min(.1, (now - lastT) / 1000); lastT = now;
      view.s = Math.min(1, view.s + dt / 10); update();
      if (view.s >= 1) setPlaying(false);
    });
    function setPlaying(on) {
      var was = playing;
      playing = on; lastT = 0;
      if (was && !on) { update(); if (say) say.textContent = 'Fold paused at s = ' + fmt(view.s, 3) + ': ' + fmt(state(view.s).density * 100, 2) + '% of space filled.'; }
      pressed(playBtn, on);
      playBtn.setAttribute('aria-label', on ? 'Pause the fold' : (F0.motion() ? 'Play the fold' : 'Step the fold forward'));
      if (on) loop.start(); else loop.stop();
    }
    function syncMotion() {
      playTxt.textContent = F0.motion() ? 'Play' : 'Step';
      if (!F0.motion() && playing) setPlaying(false);
      playBtn.setAttribute('aria-label', playing ? 'Pause the fold' : (F0.motion() ? 'Play the fold' : 'Step the fold forward'));
    }
    playBtn.addEventListener('click', function () {
      if (!F0.motion()) { view.s = view.s >= 1 ? 0 : Math.min(1, Math.floor(view.s * 4 + 1e-9) / 4 + .25); update(); return; }
      if (playing) { setPlaying(false); return; }
      if (view.s >= 1) view.s = 0;
      setPlaying(true);
    });
    F0.onMotion(syncMotion); syncMotion();
    F0.whenVisible(cv, null, function () { if (playing) setPlaying(false); });
    function choose(s) { if (playing) setPlaying(false); view.s = Math.max(0, Math.min(1, s)); update(); }
    slider.addEventListener('input', function () { choose(+slider.value); });
    $('fd-open').addEventListener('click', function () { choose(0); });
    $('fd-close').addEventListener('click', function () { choose(1); });
    var bBalls = $('fd-balls'), bRods = $('fd-rods');
    bBalls.addEventListener('click', function () { view.balls = true; pressed(bBalls, true); pressed(bRods, false); draw(); });
    bRods.addEventListener('click', function () { view.balls = false; pressed(bBalls, false); pressed(bRods, true); draw(); });
    $('fd-turn').addEventListener('click', function () { view.yaw += Math.PI / 6; draw(); });
    /* Break it: stretch one rod by 1% and let the same rod check say no */
    var brk = $('fd-break');
    if (brk) brk.addEventListener('click', function () {
      view.stretch = !view.stretch; pressed(brk, view.stretch); lastRead = 0; update();
      if (say) say.textContent = view.stretch ? 'One rod stretched by 1%: its length error is now about 1 in 100, so the check rejects it. That is not the certified motion.' : 'Rod restored: every rod is √2 again, to rounding error.';
    });
    var ptr = null;
    cv.addEventListener('pointerdown', function (ev) { ptr = [ev.clientX, ev.clientY]; try { cv.setPointerCapture(ev.pointerId); } catch (e) {} });
    cv.addEventListener('pointermove', function (ev) {
      if (!ptr) return;
      view.yaw += (ev.clientX - ptr[0]) * .007;
      view.pitch = Math.max(-1.3, Math.min(1.3, view.pitch + (ev.clientY - ptr[1]) * .007));
      ptr = [ev.clientX, ev.clientY]; draw();
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) { cv.addEventListener(t, function () { ptr = null; }); });
    cv.addEventListener('keydown', function (ev) {
      var used = true;
      if (ev.key === 'ArrowLeft') view.yaw -= .12; else if (ev.key === 'ArrowRight') view.yaw += .12;
      else if (ev.key === 'ArrowUp') view.pitch = Math.max(-1.3, view.pitch - .1); else if (ev.key === 'ArrowDown') view.pitch = Math.min(1.3, view.pitch + .1);
      else used = false;
      if (used) { ev.preventDefault(); draw(); }
    });
    C.resize(draw); F0.onTheme(draw);
    update();
  })();

  /* =========================================================================
     5. The search ladder (autoresearch-fold/results.tsv, 12 Oct 2026)
     ========================================================================= */
  (function ladder() {
    var svg = $('sl-svg'); if (!svg) return;
    var RUNS = [
      { time: '07:56:10', hash: 'e270829', valid: true, max: .468585, contacts: '6.00 (6–6)', out: 'kept', label: 'Kept as the baseline',
        desc: 'baseline: analytic cubic [111] checkerboard fold to 60 deg, m=2, no continuation',
        plain: 'A fold the project already knew: the octahedra tilt in a checkerboard about the cube’s long diagonal. It locks at 60° with 46.86% of space filled and each ball touching 6 others.' },
      { time: '07:56:30', hash: 'd8144dc', valid: true, max: .710861, contacts: '11.50 (11–12)', out: 'kept', label: 'Kept: new best',
        desc: 'iter1: baseline fold to 60 deg then LP-guided free-lattice continuation (m=2, tie-break l1, kicks)',
        plain: 'Fold to 60°, then let the box change shape freely, each small step chosen by linear programming to raise the density. It reached 71.09%.' },
      { time: '07:59:03', hash: '876afa7', valid: true, max: .572893, contacts: '6.08 (5–8)', out: 'disc', label: 'Discarded: valid, not better',
        desc: 'iter2: skip fold, free-lattice LP continuation straight from canonical state via kicks (m=2, seed 1)',
        plain: 'Skip the fold and push the open scaffold directly, with random kicks to break its symmetry. It got stuck at 57.29%, so the script went back to the previous best.' },
      { time: '08:03:36', hash: '6e9ead9', valid: false, max: .540015, contacts: '5.03 (5–6)', out: 'rej', label: 'Rejected by the checker',
        desc: 'iter3: iter1 pipeline (fold to 60 deg + free continuation) on m=4 supercell',
        plain: 'Run 2’s recipe on a bigger block of 4 × 4 × 4 cells. The box moved by more than 0.01 in one step, so the locked checker failed the whole path. Under the rules an invalid path is worth nothing.' },
      { time: '08:06:56', hash: 'cae3bdb', valid: true, max: .740480, contacts: '12.00 (12–12)', out: 'kept', label: 'Kept: best, at the ceiling',
        desc: 'iter4: stage-A step scaled by 1/m (fixes iter3 continuity bug); fold only to 30 deg then free continuation, m=2',
        plain: 'Fix the step size for bigger blocks, fold only to 30°, then let the box shear freely. It reached 74.05%, the Kepler ceiling, with every ball touching 12 others: hexagonal close packing.' }
    ];
    var W = 520, H = 300, M = { l: 52, r: 18, t: 30, b: 42 }, marks = [], guide = null;
    function sec(t) { var p = t.split(':').map(Number); return p[0] * 3600 + p[1] * 60 + p[2]; }
    var t0 = sec('07:55:20'), t1 = sec('08:07:50');
    var xs = function (t) { return M.l + (sec(t) - t0) / (t1 - t0) * (W - M.l - M.r); };
    var ys = function (v) { return M.t + (1 - (v - .4) / (.78 - .4)) * (H - M.t - M.b); };
    // drawn at the container's own width so its text keeps its true size on phones
    function build() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      W = Math.max(300, Math.min(600, Math.round(svg.parentNode.clientWidth || 520)));
      var narrow = W < 420;
      M = { l: narrow ? 40 : 52, r: narrow ? 12 : 18, t: 30, b: 42 };
      H = narrow ? 280 : 300;
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
      [.45, .55, .65, .75].forEach(function (v) {
        el('line', { x1: M.l, x2: W - M.r, y1: ys(v), y2: ys(v), stroke: 'var(--grid)', 'stroke-width': 1 }, svg);
        var t = el('text', { x: M.l - 8, y: ys(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); t.textContent = Math.round(v * 100) + '%';
      });
      var hd = el('text', { x: M.l, y: 15, 'font-size': 11, fill: 'var(--ink-3)', 'letter-spacing': '.08em' }, svg); hd.textContent = narrow ? 'HIGHEST DENSITY' : 'HIGHEST DENSITY ON THE PATH';
      var kep = .74048;
      el('line', { x1: M.l, x2: W - M.r, y1: ys(kep), y2: ys(kep), stroke: 'var(--ink-2)', 'stroke-width': 1 }, svg);
      var kt = el('text', { x: M.l + 6, y: ys(kep) - 7, 'font-size': 11, fill: 'var(--ink-2)' }, svg); kt.textContent = narrow ? 'Kepler 74.05%' : 'Kepler ceiling 74.05%';
      el('line', { x1: M.l, x2: W - M.r, y1: H - M.b, y2: H - M.b, stroke: 'var(--line-ui)', 'stroke-width': 1 }, svg);
      (narrow ? ['07:56:00', '08:00:00', '08:04:00'] : ['07:56:00', '07:58:00', '08:00:00', '08:02:00', '08:04:00', '08:06:00']).forEach(function (t) {
        var x = xs(t);
        el('line', { x1: x, x2: x, y1: H - M.b, y2: H - M.b + 4, stroke: 'var(--line-ui)', 'stroke-width': 1 }, svg);
        var tx = el('text', { x: x, y: H - M.b + 18, 'text-anchor': 'middle', 'font-size': 11, fill: 'var(--ink-3)' }, svg); tx.textContent = t.slice(0, 5);
      });
      var xl = el('text', { x: W - M.r, y: H - 6, 'text-anchor': 'end', 'font-size': 11, fill: 'var(--ink-3)' }, svg); xl.textContent = 'clock time, 12 Oct 2026';
      // best valid so far: a step line
      var best = 0, d = '';
      RUNS.forEach(function (r) {
        if (r.valid && r.max > best) { d += (d ? 'H' + fmt(xs(r.time), 1) + 'V' : 'M' + fmt(xs(r.time), 1) + ' ') + fmt(ys(r.max), 1); best = r.max; }
      });
      d += 'H' + (W - M.r);
      el('path', { d: d, fill: 'none', stroke: 'var(--st-verified)', 'stroke-width': 2, 'stroke-opacity': .55, 'stroke-linejoin': 'round' }, svg);
      var bl = el('text', { x: xs('07:56:30') + 10, y: ys(.710861) + 16, 'font-size': 11, fill: 'var(--ink-3)' }, svg); bl.textContent = 'best valid so far';
      guide = el('line', { y1: M.t, y2: H - M.b, stroke: 'var(--ink-3)', 'stroke-width': 1 }, svg);
      marks = RUNS.map(function (r, i) {
        var g = el('g', { 'class': 'sl-run' }, svg), x = xs(r.time), y = ys(r.max);
        el('circle', { cx: x, cy: y, r: 16, fill: 'transparent', 'class': 'sl-hit' }, g);
        var ring = el('circle', { cx: x, cy: y, r: 13, fill: 'none', stroke: 'var(--focus)', 'stroke-width': 2, opacity: 0 }, g);
        if (r.out === 'kept') {
          el('circle', { cx: x, cy: y, r: 8.5, fill: 'var(--st-verified)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, g);
          el('path', { d: 'M' + (x - 3.6) + ' ' + y + 'l2.6 2.8 4.8-5.4', fill: 'none', stroke: 'var(--bg-1)', 'stroke-width': 1.8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
        } else if (r.out === 'disc') {
          el('circle', { cx: x, cy: y, r: 7.5, fill: 'var(--bg-1)', stroke: 'var(--ink-3)', 'stroke-width': 2 }, g);
        } else {
          el('circle', { cx: x, cy: y, r: 8.5, fill: 'var(--st-contested)', stroke: 'var(--bg-1)', 'stroke-width': 2 }, g);
          el('path', { d: 'M' + (x - 3.2) + ' ' + (y - 3.2) + 'l6.4 6.4M' + (x + 3.2) + ' ' + (y - 3.2) + 'l-6.4 6.4', stroke: 'var(--bg-1)', 'stroke-width': 1.8, 'stroke-linecap': 'round' }, g);
        }
        var lab = el('text', { x: i === 4 ? x - 16 : i === 1 ? x + 13 : x, y: y + (i === 1 ? -4 : i === 4 ? -10 : 24), 'text-anchor': i === 4 ? 'end' : i === 1 ? 'start' : 'middle', 'font-size': 11, fill: 'var(--ink-2)', 'class': 'il-halo' }, g);
        lab.textContent = (r.valid ? fmt(r.max * 100, 2) + '%' : 'rejected');
        g.addEventListener('click', function () { select(i); });
        g.addEventListener('pointermove', function (ev) {
          F0.tip.show('<div class="tip-k">Run ' + (i + 1) + ' · ' + r.time + '</div><div class="tip-t">' + (r.valid ? fmt(r.max * 100, 2) + '% reached' : 'Invalid path') + '</div><div class="tip-note">' + F0.esc(r.label) + '</div>', ev.clientX, ev.clientY);
        });
        g.addEventListener('pointerleave', function () { F0.tip.hide(); });
        return { ring: ring, x: x };
      });
    }
    build();
    if ('ResizeObserver' in window) new ResizeObserver(function () {
      var w = Math.max(300, Math.min(600, svg.parentNode.clientWidth || 0));
      if (w && Math.abs(w - W) > 6) { build(); select(cur); }
    }).observe(svg.parentNode);
    var OUT = { kept: ['k-kept', '✓'], disc: ['k-disc', '○'], rej: ['k-rej', '×'] };
    var cur = 4, card = $('sl-card');
    function select(i) {
      cur = (i + RUNS.length) % RUNS.length;
      var r = RUNS[cur];
      marks.forEach(function (m, j) { m.ring.setAttribute('opacity', j === cur ? 1 : 0); });
      guide.setAttribute('x1', marks[cur].x); guide.setAttribute('x2', marks[cur].x);
      document.querySelectorAll('.sl-seg button').forEach(function (b) { pressed(b, +b.dataset.run === cur); });
      card.innerHTML = '<p class="k"><span>Run <b>' + (cur + 1) + '</b> of 5</span><span>' + r.time + '</span><span>' + r.hash + '</span><span>' + (r.valid ? 'valid' : '<b>invalid</b>') + '</span><span>contacts ' + F0.esc(r.contacts) + '</span><span class="out"><span class="sl-key ' + OUT[r.out][0] + '" aria-hidden="true">' + OUT[r.out][1] + '</span><b>' + F0.esc(r.label) + '</b></span></p>' +
        '<q>' + F0.esc(r.desc) + '</q><p>' + F0.esc(r.plain) + '</p>';
    }
    document.querySelectorAll('.sl-seg button').forEach(function (b) { b.addEventListener('click', function () { select(+b.dataset.run); }); });
    $('sl-prev').addEventListener('click', function () { select(cur - 1); });
    $('sl-next').addEventListener('click', function () { select(cur + 1); });
    $('sl-svg').closest('figure').addEventListener('keydown', function (ev) {
      if (ev.target.closest('.sl-seg') || ev.target.id === 'sl-prev' || ev.target.id === 'sl-next') {
        if (ev.key === 'ArrowLeft') { ev.preventDefault(); select(cur - 1); var b = document.querySelector('.sl-seg button[data-run="' + cur + '"]'); if (ev.target.closest('.sl-seg') && b) b.focus(); }
        if (ev.key === 'ArrowRight') { ev.preventDefault(); select(cur + 1); var c = document.querySelector('.sl-seg button[data-run="' + cur + '"]'); if (ev.target.closest('.sl-seg') && c) c.focus(); }
      }
    });
    var tb = $('sl-tbody');
    RUNS.forEach(function (r) {
      var tr = document.createElement('tr');
      [r.time, r.hash, r.valid ? 'true' : 'false', fmt(r.max, 6), r.label, r.desc].forEach(function (v, j) {
        var td = document.createElement('td'); td.textContent = v; if (j === 3) td.className = 'n'; if (j === 5 || j === 1) td.className = 'mono'; tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    select(4);
  })();
})();
