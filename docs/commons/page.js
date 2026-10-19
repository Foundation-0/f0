/* Commons page: the promises table, code anatomy, the evidence ledger, calcium by day or by week,
   and what an RDA means. Vanilla JS, no dependencies. Colours come from tokens; every figure
   redraws on theme change, respects the motion toggle and starts on an informative still frame. */
(function () {
  'use strict';
  var F0 = window.F0 || {};
  var NS = 'http://www.w3.org/2000/svg';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) for (var k in attrs) { if (k === 'text') e.textContent = attrs[k]; else if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, attrs, parent, html) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) { if (k === 'text') e.textContent = attrs[k]; else if (k === 'cls') e.className = attrs[k]; else if (attrs[k] != null) e.setAttribute(k, attrs[k]); }
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }
  var esc = F0.esc || function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  function motion() { return F0.motion ? F0.motion() : true; }
  function fmt(n) { return Math.round(n).toLocaleString('en-US'); }
  function sized(host, build) {
    var lw = 0;
    function go(force) { var w = Math.round(host.getBoundingClientRect().width); if (!w || (w === lw && !force)) return; lw = w; build(w); }
    go(); if ('ResizeObserver' in window) new ResizeObserver(function () { go(); }).observe(host);
    return function () { go(true); };
  }
  function onTheme(fn) { if (F0.onTheme) F0.onTheme(fn); }
  function tipShow(html, x, y) { if (F0.tip) F0.tip.show(html, x, y); }
  function tipHide() { if (F0.tip) F0.tip.hide(); }
  function segPress(group, btn) { $$('button', group).forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); }); }
  function arrows(group, sel, onMove) {
    group.addEventListener('keydown', function (e) {
      var keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
      if (!(e.key in keys)) return;
      var bs = $$(sel, group), i = bs.indexOf(document.activeElement); if (i < 0) return;
      e.preventDefault();
      var j = (i + keys[e.key] + bs.length) % bs.length;
      bs[j].focus(); if (onMove) onMove(bs[j]);
    });
  }

  /* ======================================================================
     HERO: one tool, eight checks
     ====================================================================== */
  function initPromises() {
    var fig = $('.pm'), btn = $('#pm-gaps'); if (!fig || !btn) return;
    var cells = $$('#pm-tbl tbody td'), full = cells.filter(function (c) { return c.getAttribute('data-s') === 'yes'; }).length;
    var gaps = $$('#pm-tbl tbody tr[data-gap="1"]').length;
    function upd(on) {
      fig.classList.toggle('gaps', on); btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.textContent = on ? 'Show all eight' : 'Show only the gaps';
      $('#pm-count').textContent = on ? gaps + ' checks with a gap' : '8 checks · ' + full + ' of ' + cells.length + ' met in full';
    }
    btn.addEventListener('click', function () { upd(!fig.classList.contains('gaps')); });
    upd(false);
  }

  /* ======================================================================
     00b: PROMISE 03, MEASURED. Bytes over the wire for a first visit, divided by an assumed speed.
     ====================================================================== */
  var WC = [
    ['Nutrak', 'app and demo data', 30, 'var(--acc-nutrak)'],
    ['A median mobile web page', 'HTTP Archive, Sep 2026', 2629, 'var(--line-ui)']
  ];
  function initWeak() {
    var ul = $('#wc-bars'); if (!ul) return;
    var k = 50;
    function secs(kb) { var s = kb / k; return s < 1 ? (s < 0.1 ? 'under 0.1 s' : s.toFixed(1) + ' s') : s < 10 ? s.toFixed(1) + ' s' : Math.round(s) + ' s'; }
    function render() {
      var max = Math.max.apply(null, WC.map(function (w) { return w[2]; }));
      ul.innerHTML = WC.map(function (w) {
        var pct = Math.max(0.6, 100 * w[2] / max);
        return '<li><span class="wc-n"><b>' + esc(w[0]) + '</b> ' + esc(w[1]) + ' &middot; ' + (w[2] >= 1000 ? (w[2] / 1000).toFixed(w[2] >= 2000 ? 1 : 2) + ' MB' : w[2] + ' KB') + '</span>' +
          '<span class="wc-track"><span class="wc-bar" style="width:calc((100% - 76px) * ' + (pct / 100).toFixed(4) + ');background:' + w[3] + '"></span><span class="wc-t">' + secs(w[2]) + '</span></span></li>';
      }).join('');
    }
    $$('#wc-speed button').forEach(function (b) { b.addEventListener('click', function () { k = +b.getAttribute('data-k'); segPress($('#wc-speed'), b); render(); }); });
    arrows($('#wc-speed'), 'button', function (b) { b.click(); });
    render();
  }

  /* ======================================================================
     02: ONE DAY IS NOISE, A WEEK IS A SIGNAL (Nutrak demo data, calcium, 24-30 Aug 2026)
     ====================================================================== */
  var CA = [549, 944, 728, 1070, 685, 710, 754], DAYS = ['Mon 24 Aug', 'Tue 25 Aug', 'Wed 26 Aug', 'Thu 27 Aug', 'Fri 28 Aug', 'Sat 29 Aug', 'Sun 30 Aug'];
  var RDA = 1000, EAR = 800, HUGE = 5000;
  function status(v) { var p = v / RDA; return p < 0.75 ? 'under' : p < 1 ? 'near' : 'good'; }
  var ST = { under: ['Under', '↓', 'var(--nk-under)'], near: ['Approaching', '~', 'var(--nk-near)'], good: ['Good', '✓', 'var(--nk-good)'] };
  function initWeek() {
    var host = $('#wk-stage'); if (!host) return;
    var mode = 'day', day = 7, huge = false, svg = null, playing = false, timer = 0;
    function vals() { var a = CA.slice(); if (huge) a[6] = HUGE; return a; }
    function mean() { var a = vals(); return a.reduce(function (s, v) { return s + v; }, 0) / a.length; }
    function flipsUpTo(d) { var a = vals(), n = 0; for (var i = 1; i < d; i++) if (status(a[i]) !== status(a[i - 1])) n++; return n; }
    // twin table
    var tb = $('#wk-table tbody');
    CA.forEach(function (v, i) { h('tr', null, tb, '<th scope="row">' + DAYS[i] + '</th><td class="n">' + fmt(v) + '</td><td class="n">' + Math.round(v / 10) + '%</td><td>' + ST[status(v)][0] + '</td>'); });
    h('tr', null, tb, '<th scope="row">7-day mean</th><td class="n">777.1</td><td class="n">78%</td><td>Approaching (the week&rsquo;s one verdict)</td>');
    function draw(W) {
      if (svg) svg.remove();
      var a = vals(), m = mean(), small = W < 560;
      var H = small ? 270 : 300, padL = 50, padR = small ? 10 : 112, padT = 16, padB = 58, ymax = huge ? 1500 : 1300;
      var Y = function (v) { return padT + (1 - Math.min(v, ymax) / ymax) * (H - padT - padB); };
      var cw = (W - padL - padR) / 7, bw = Math.min(small ? 22 : 30, cw - 8);
      svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': aria() }, host);
      // zones
      [[0, 750, 'under'], [750, 1000, 'near'], [1000, ymax, 'good']].forEach(function (z) {
        el('rect', { x: padL, y: Y(z[1]), width: W - padL - padR, height: Y(z[0]) - Y(z[1]), style: 'fill:' + ST[z[2]][2], opacity: 0.08 }, svg);
        if (!small) el('text', { x: W - padR + 8, y: (Y(z[0]) + Y(z[1])) / 2 + 4, text: ST[z[2]][0].toUpperCase(), 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.06em' }, svg);
      });
      (huge ? [0, 250, 500, 750, 1000, 1250, 1500] : [0, 250, 500, 750, 1000, 1250]).forEach(function (v) {
        el('text', { x: padL - 6, y: Y(v) + 4, 'text-anchor': 'end', text: fmt(v), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      });
      el('line', { x1: padL, x2: W - padR, y1: Y(0), y2: Y(0), style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, svg);
      [[RDA, 'RDA 1,000'], [EAR, 'EAR 800']].forEach(function (r) {
        el('line', { x1: padL, x2: W - padR, y1: Y(r[0]), y2: Y(r[0]), style: 'stroke:var(--ink-3)', 'stroke-width': 1 }, svg);
      });
      a.forEach(function (v, i) {
        var x = padL + i * cw + (cw - bw) / 2, y = Y(v), s = status(v), shown = mode === 'week' || i < day;
        var col = mode === 'day' ? ST[s][2] : 'var(--line-ui)';
        var r = Math.min(4, bw / 2), path = 'M' + x + ' ' + Y(0) + 'V' + (y + r) + 'Q' + x + ' ' + y + ' ' + (x + r) + ' ' + y + 'H' + (x + bw - r) + 'Q' + (x + bw) + ' ' + y + ' ' + (x + bw) + ' ' + (y + r) + 'V' + Y(0) + 'Z';
        var g = el('g', { opacity: shown ? 1 : 0.18 }, svg);
        el('rect', { x: padL + i * cw, y: padT, width: cw, height: H - padT - 30, fill: 'transparent' }, g);
        el('path', { d: path, style: 'fill:' + col }, g);
        if (v > ymax) { // a broken bar: the value is far above the axis
          el('path', { d: 'M' + (x - 3) + ' ' + (y + 14) + 'l' + (bw + 6) + ' -6M' + (x - 3) + ' ' + (y + 20) + 'l' + (bw + 6) + ' -6', style: 'stroke:var(--bg-1)', 'stroke-width': 3 }, g);
          el('text', { x: x - 6, y: y + 12, 'text-anchor': 'end', text: '5,000 mg', 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink)' }, g);
        }
        // day label and the light under it
        el('text', { x: x + bw / 2, y: H - 36, 'text-anchor': 'middle', text: DAYS[i].slice(0, small ? 1 : 3), 'font-size': 11, style: 'fill:' + (i === day - 1 && mode === 'day' ? 'var(--ink)' : 'var(--ink-3)'), 'font-weight': i === day - 1 && mode === 'day' ? 700 : 400 }, svg);
        if (mode === 'day' && shown) {
          el('circle', { cx: x + bw / 2, cy: H - 16, r: 9, style: 'fill:color-mix(in srgb, ' + ST[s][2] + ' 22%, var(--bg-1));stroke:' + ST[s][2], 'stroke-width': 2 }, svg);
          el('text', { x: x + bw / 2, y: H - 12, 'text-anchor': 'middle', text: ST[s][1], 'font-size': 11, 'font-weight': 700, style: 'fill:var(--ink)' }, svg);
          if (i > 0 && status(a[i - 1]) !== s) el('path', { d: 'M' + (x - (cw - bw) / 2) + ' ' + (H - 26) + 'v20', style: 'stroke:var(--ink-3)', 'stroke-width': 1, 'stroke-dasharray': '2 2' }, svg);
        }
        g.addEventListener('pointermove', function (e) { tipShow('<div class="tip-k">' + DAYS[i] + '</div><div class="tip-rows"><div class="tip-row"><span class="tip-v">' + fmt(v) + ' mg</span> ' + Math.round(v / 10) + '% of 1,000</div></div><div class="tip-foot">judged that day: ' + ST[s][0] + '</div>', e.clientX, e.clientY); });
        g.addEventListener('pointerleave', tipHide);
      });
      [[RDA, 'RDA 1,000'], [EAR, 'EAR 800']].forEach(function (r) { // labels last, so no column covers them
        el('text', { x: padL + 4, y: Y(r[0]) - 4, text: r[1], 'font-size': 11, style: 'fill:var(--ink-2);paint-order:stroke;stroke:var(--bg-1);stroke-width:4px' }, svg);
      });
      if (mode === 'week') {
        var ms = status(m), my = Y(m);
        el('line', { x1: padL, x2: W - padR, y1: my, y2: my, style: 'stroke:' + ST[ms][2], 'stroke-width': 3, 'stroke-linecap': 'round' }, svg);
        var lab = '7-day mean ' + fmt(m) + ' mg';
        var leftSide = m > 1100; // a high mean sits above the RDA and EAR labels; otherwise keep clear of them on the right
        el('text', { x: leftSide ? padL + 6 : W - padR - 6, y: my - 8, 'text-anchor': leftSide ? 'start' : 'end', text: lab, 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink);paint-order:stroke;stroke:var(--bg-1);stroke-width:4px' }, svg);
        el('rect', { x: padL + 1, y: H - 26, width: W - padL - padR - 2, height: 20, rx: 10, style: 'fill:color-mix(in srgb, ' + ST[ms][2] + ' 22%, var(--bg-1));stroke:' + ST[ms][2], 'stroke-width': 2 }, svg);
        el('text', { x: (padL + W - padR) / 2, y: H - 12, 'text-anchor': 'middle', text: ST[ms][1] + (small ? '  THE WEEK: ' : '  ONE VERDICT FOR THE WEEK: ') + ST[ms][0].toUpperCase(), 'font-size': 11, 'font-weight': 700, style: 'fill:var(--ink)', 'letter-spacing': '.06em' }, svg);
      }
    }
    function aria() {
      var a = vals();
      if (mode === 'week') return 'Calcium for seven days, with the 7-day mean of ' + fmt(mean()) + ' mg, ' + Math.round(mean() / 10) + '% of the 1,000 mg target: one verdict, ' + ST[status(mean())][0] + '.';
      return 'Calcium judged each day up to ' + DAYS[day - 1] + ': ' + a.slice(0, day).map(function (v, i) { return DAYS[i].slice(0, 3) + ' ' + fmt(v) + ' mg ' + ST[status(v)][0]; }).join('; ') + '. The light changed ' + flipsUpTo(day) + ' times.';
    }
    function readout() {
      var a = vals(), s, txt;
      if (mode === 'week') { var m = mean(); s = status(m); txt = fmt(m) + ' mg = ' + Math.round(m / 10) + '% of 1,000 <small>7-day mean</small>'; }
      else { var v = a[day - 1]; s = status(v); txt = fmt(v) + ' mg = ' + Math.round(v / 10) + '% <small>' + DAYS[day - 1] + '</small>'; }
      var pill = $('#wk-pill');
      pill.style.setProperty('--c', ST[s][2]);
      pill.innerHTML = '<span class="g" aria-hidden="true">' + ST[s][1] + '</span><span>' + ST[s][0] + ' &middot; ' + txt + '</span>';
      var f = flipsUpTo(mode === 'week' ? 7 : day);
      $('#wk-flips').innerHTML = mode === 'week'
        ? '<b>1</b> steady signal for the whole week, against <b>' + flipsUpTo(7) + '</b> light changes if judged daily.'
        : '<b>' + f + '</b> light change' + (f === 1 ? '' : 's') + ' so far, in ' + day + ' day' + (day === 1 ? '' : 's') + '.';
      $('#wk-out').textContent = DAYS[day - 1];
      $('#wk-day').setAttribute('aria-valuetext', DAYS[day - 1] + ', ' + fmt(a[day - 1]) + ' mg, ' + ST[status(a[day - 1])][0]);
      $('#wk-day').disabled = mode === 'week';
    }
    var re = sized(host, draw);
    function update() { re(); readout(); }
    $$('#wk-mode button').forEach(function (b) { b.addEventListener('click', function () { mode = b.getAttribute('data-m'); segPress($('#wk-mode'), b); if (mode === 'week') stop(); update(); }); });
    arrows($('#wk-mode'), 'button', function (b) { b.click(); });
    $('#wk-day').addEventListener('input', function () { day = +this.value; update(); });
    $('#wk-huge').addEventListener('click', function () { huge = !huge; this.setAttribute('aria-pressed', huge ? 'true' : 'false'); update(); });
    var playBtn = $('#wk-play');
    function stop() { playing = false; clearInterval(timer); playBtn.setAttribute('aria-pressed', 'false'); }
    playBtn.addEventListener('click', function () {
      if (playing) { stop(); return; }
      if (mode === 'week') { mode = 'day'; segPress($('#wk-mode'), $('#wk-mode [data-m="day"]')); }
      if (!motion()) { day = day >= 7 ? 1 : day + 1; $('#wk-day').value = day; update(); return; } // stepped when motion is off
      day = 1; $('#wk-day').value = 1; update();
      playing = true; playBtn.setAttribute('aria-pressed', 'true');
      timer = setInterval(function () {
        if (!motion() || document.hidden) { stop(); return; }
        if (day >= 7) { stop(); return; }
        day++; $('#wk-day').value = day; update();
      }, 900);
    });
    if (F0.whenVisible) F0.whenVisible($('.wk'), null, function () { if (playing) stop(); });
    if (F0.onMotion) F0.onMotion(function (on) { if (!on && playing) stop(); });
    readout();
    onTheme(re);
  }

  /* ======================================================================
     03: ENOUGH FOR WHOM?  Needs ~ Normal(EAR 800, SD 100), from RDA = EAR + 2 SD.
     ====================================================================== */
  function erf(x) { // Abramowitz and Stegun 7.1.26
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    var t = 1 / (1 + 0.3275911 * x);
    var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  }
  function cover(x) { return 0.5 * (1 + erf((x - 800) / (100 * Math.SQRT2))); }
  function initRDA() {
    var host = $('#rc-stage'); if (!host) return;
    var X0 = 450, X1 = 1250, x = 777, svg = null, geo = null, range = $('#rc-x');
    var dots = $('#rc-dots'); for (var i = 0; i < 40; i++) h('i', null, dots);
    var tb = $('#rc-table tbody');
    [[600, ''], [700, ''], [777, 'the demo week’s average'], [800, 'the EAR: half covered'], [900, ''], [1000, 'the RDA: about 97.5% covered'], [1100, '']].forEach(function (r) {
      h('tr', null, tb, '<td class="n">' + fmt(r[0]) + '</td><td class="n">' + (100 * cover(r[0])).toFixed(1) + '%</td><td>' + esc(r[1]) + '</td>');
    });
    function pdf(v) { var z = (v - 800) / 100; return Math.exp(-z * z / 2); }
    function draw(W) {
      if (svg) svg.remove();
      var small = W < 560, H = small ? 230 : 260, padL = 14, padR = 14, padT = 34, padB = 30;
      var X = function (v) { return padL + (v - X0) / (X1 - X0) * (W - padL - padR); }, Y = function (p) { return padT + (1 - p) * (H - padT - padB); };
      geo = { X: X, Y: Y, W: W, H: H, padL: padL, padR: padR };
      svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'aria-hidden': 'true' }, host);
      var pts = []; for (var v = X0; v <= X1; v += 5) pts.push([X(v), Y(pdf(v))]);
      var curve = pts.map(function (p, i) { return (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join('');
      var cp = el('clipPath', { id: 'rc-clip' }, el('defs', null, svg));
      geo.clip = el('rect', { x: X(X0), y: 0, width: Math.max(0, X(x) - X(X0)), height: H }, cp);
      el('path', { d: curve + 'L' + X(X1) + ' ' + Y(0) + 'L' + X(X0) + ' ' + Y(0) + 'Z', style: 'fill:var(--mark-dig)', opacity: 0.3, 'clip-path': 'url(#rc-clip)' }, svg);
      el('path', { d: curve, fill: 'none', style: 'stroke:var(--ink-2)', 'stroke-width': 2 }, svg);
      el('line', { x1: X(X0), x2: X(X1), y1: Y(0), y2: Y(0), style: 'stroke:var(--line-ui)' }, svg);
      for (var t = small ? 600 : 500; t <= 1200; t += small ? 200 : 100) el('text', { x: X(t), y: H - 10, 'text-anchor': 'middle', text: fmt(t), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: W - padR, y: 14, 'text-anchor': 'end', text: small ? 'need, mg/day' : 'calcium need, mg a day', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      [[800, 'EAR 800', 'half of people need less'], [1000, 'RDA 1,000', 'covers about 97.5%']].forEach(function (m) {
        el('line', { x1: X(m[0]), x2: X(m[0]), y1: Y(m[0] === 800 ? 1 : pdf(1000)) - 6, y2: Y(0), style: 'stroke:var(--ink-3)', 'stroke-width': 1 }, svg);
        var tx = X(m[0]) + 6, ty = m[0] === 800 ? 14 : Y(pdf(1000)) - 30;
        el('text', { x: tx, y: ty, text: m[1], 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink)' }, svg);
        if (!small) el('text', { x: tx, y: ty + 14, text: m[2], 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      });
      // the intake marker
      geo.mark = el('g', null, svg);
      geo.hit = el('rect', { x: X(X0), y: padT - 20, width: X(X1) - X(X0), height: H - padT + 20 - padB, fill: 'transparent', style: 'cursor:ew-resize' }, svg);
      function fromEvent(e) { var r = svg.getBoundingClientRect(); var px = (e.clientX - r.left) * (W / r.width); return Math.round(X0 + (px - padL) / (W - padL - padR) * (X1 - X0)); }
      var drag = false;
      geo.hit.addEventListener('pointerdown', function (e) { drag = true; geo.hit.setPointerCapture(e.pointerId); set(fromEvent(e)); });
      geo.hit.addEventListener('pointermove', function (e) { if (drag) set(fromEvent(e)); });
      geo.hit.addEventListener('pointerup', function () { drag = false; });
      geo.hit.addEventListener('pointercancel', function () { drag = false; });
      mark();
    }
    function mark() {
      if (!geo) return;
      var g = geo.mark, X = geo.X, Y = geo.Y;
      while (g.firstChild) g.removeChild(g.firstChild);
      geo.clip.setAttribute('width', Math.max(0, X(x) - X(X0)));
      el('line', { x1: X(x), x2: X(x), y1: Y(pdf(x)), y2: Y(0), style: 'stroke:var(--ink)', 'stroke-width': 2 }, g);
      el('circle', { cx: X(x), cy: Y(pdf(x)), r: 6, style: 'fill:var(--bg-1);stroke:var(--ink)', 'stroke-width': 2 }, g);
      var right = x > 800 && x <= 900, lab = fmt(x) + ' mg', hy = Y(pdf(x));
      el('text', { x: X(x) + (right ? 12 : -12), y: hy - 10, 'text-anchor': right ? 'start' : 'end', text: lab, 'font-size': 12, 'font-weight': 700, style: 'fill:var(--ink);paint-order:stroke;stroke:var(--bg-1);stroke-width:4px' }, g);
      if (x !== 777) { el('line', { x1: X(777), x2: X(777), y1: Y(0) - 8, y2: Y(0), style: 'stroke:var(--nk-near)', 'stroke-width': 3 }, g); el('text', { x: X(777), y: Y(0) - 12, 'text-anchor': 'middle', text: 'demo week', 'font-size': 11, style: 'fill:var(--ink-2);paint-order:stroke;stroke:var(--bg-1);stroke-width:3px' }, g); }
    }
    function set(v) {
      x = Math.max(X0, Math.min(X1, v)); range.value = x;
      var c = cover(x), pct = Math.round(100 * c);
      $('#rc-out').textContent = fmt(x) + ' mg';
      $('#rc-pct').textContent = (c > 0.995 ? '>99' : pct < 1 ? '<1' : pct) + '%';
      $('#rc-say').textContent = 'of adults aged 19 to 50 would have their calcium need met by ' + fmt(x) + ' mg a day' + (x === 777 ? ', the demo week’s average' : x === 800 ? ', the EAR' : x === 1000 ? ', the RDA' : '');
      var n = Math.round(40 * c);
      $$('i', dots).forEach(function (d, i) { d.classList.toggle('on', i < n); });
      dots.setAttribute('aria-label', n + ' of 40 people covered');
      range.setAttribute('aria-valuetext', fmt(x) + ' mg a day: about ' + pct + '% of adults covered');
      $$('#rc-jump button').forEach(function (b) { b.setAttribute('aria-pressed', +b.getAttribute('data-x') === x ? 'true' : 'false'); });
      mark();
    }
    var re = sized(host, draw);
    range.addEventListener('input', function () { set(+range.value); });
    $$('#rc-jump button').forEach(function (b) { b.addEventListener('click', function () { set(+b.getAttribute('data-x')); }); });
    set(x);
    onTheme(function () { re(); set(x); });
  }

  function init() { initPromises(); initWeak(); initWeek(); initRDA(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
