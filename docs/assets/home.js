/* Home page: wires the Radiant, the role chart (with table twin), the evidence strip,
   the live research glyphs and the Nutrak week. Every number is computed from the ledger
   or copied, with its source, from the project dossiers. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var LEDGER = 'data/ledger.json';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) { if (k === 'text') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e); return e;
  }
  function pct(a, b) { return b ? Math.round(100 * a / b) : 0; }
  function tk(n) { return F0.css(n); }
  function mono(px, wt) { return (wt || 500) + ' ' + px + 'px ' + tk('--f-mono'); }

  function start() {
    F0.json(LEDGER).then(function (L) {
      stats(L); radiant(L); roleChart(L); evidence(L);
    }).catch(function (e) {
      console.error(e);
      var r = $('#radiant-readout'); if (r) r.textContent = 'Ledger failed to load';
    });
    glyphs(); nutrak(); medcode();
  }

  /* ---------- hero numbers (pre-rendered in HTML, refreshed from data) ---------- */
  function stats(L) {
    var M = L.milestones, years = M.map(function (m) { return +m.date.slice(0, 4); });
    var set = function (k, v) { $$('[data-stat="' + k + '"]').forEach(function (e) { e.textContent = v; }); };
    set('count', M.length);
    set('span', Math.min.apply(null, years) + '–' + Math.max.apply(null, years));
    set('verified', M.filter(function (m) { return m.evidence === 'formally-verified'; }).length);
    set('contested', M.filter(function (m) { return m.contested; }).length);
    set('updated', 'updated ' + L.updated);
    set('stamp', 'Ledger updated ' + L.updated + ' · ' + M.length + ' milestones');
  }

  /* ---------- the Radiant ---------- */
  function radiant(L) {
    var stage = $('#radiant-stage');
    var R = new F0.Radiant(stage, L, { list: $('#radiant-list'), readout: $('#radiant-readout'), centre: $('#radiant-centre'), base: 'ledger/' });
    $$('.legend [data-filter]').forEach(function (b) {
      b.addEventListener('click', function () {
        var on = b.getAttribute('aria-pressed') !== 'true';
        $$('.legend [data-filter]').forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        R.setFilter(on ? b.getAttribute('data-filter') : null);
      });
    });
    var btn = $('#rad-table-btn'), wrap = $('#rad-table');
    btn.addEventListener('click', function () {
      if (!wrap.firstChild) wrap.appendChild(ledgerTable(L));
      var open = wrap.hidden; wrap.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Hide the table' : 'Show as a table';
    });
  }
  function ledgerTable(L) {
    var t = document.createElement('table'); t.className = 'tbl';
    t.innerHTML = '<caption>' + L.milestones.length + ' milestones, oldest first</caption><thead><tr><th scope="col">Date</th><th scope="col">Milestone</th><th scope="col">Field</th><th scope="col">AI role</th><th scope="col">Evidence</th></tr></thead>';
    var tb = document.createElement('tbody');
    L.milestones.slice().sort(function (a, b) { return F0.decYear(a.date) - F0.decYear(b.date); }).forEach(function (m) {
      var tr = document.createElement('tr');
      [F0.fmtDate(m.date), null, F0.PLAIN[m.domain], m.ai_role, F0.EVID[m.evidence] + (m.contested ? ' · contested' : '')].forEach(function (v, i) {
        var td = document.createElement(i === 1 ? 'th' : 'td');
        if (i === 1) { td.scope = 'row'; var a = document.createElement('a'); a.href = 'ledger/#' + encodeURIComponent(m.id); a.textContent = m.title; td.appendChild(a); }
        else td.textContent = v;
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    t.appendChild(tb); return t;
  }

  /* ---------- 01: what AI did, by period (100% stacked bars, one axis) ---------- */
  var ROLES = ['instrument', 'collaborator', 'originator'];
  var FILL = { instrument: 'var(--mark-bio)', collaborator: 'var(--mark-mid)', originator: 'var(--mark-dig)' };
  function periods(M) {
    var by = {};
    M.forEach(function (m) { var y = +m.date.slice(0, 4); (by[y] = by[y] || []).push(m); });
    var years = Object.keys(by).map(Number).sort(function (a, b) { return b - a; });
    var bins = [], cur = [], ys = [];
    years.forEach(function (y) { cur = cur.concat(by[y]); ys.push(y); if (cur.length >= 20) { bins.push(mk(ys, cur)); cur = []; ys = []; } });
    function mk(ys, items) {
      var from = Math.min.apply(null, ys), to = Math.max.apply(null, ys), c = { instrument: 0, collaborator: 0, originator: 0 };
      items.forEach(function (m) { c[m.ai_role]++; });
      return { from: from, to: to, n: items.length, c: c, label: from === to ? String(from) : from + '–' + String(to).slice(2) };
    }
    return { bins: bins.reverse(), rest: cur.length ? mk(ys, cur) : null };
  }
  function roleChart(L) {
    var P = periods(L.milestones), bins = P.bins, host = $('#role-svg-host');
    var nowYear = +L.updated.slice(0, 4);
    var first = bins[0], last = bins[bins.length - 1];
    var i0 = pct(first.c.instrument, first.n), o0 = pct(first.c.originator, first.n), i1 = pct(last.c.instrument, last.n), o1 = pct(last.c.originator, last.n);
    var lastLabel = last.to === nowYear ? last.label + ' so far' : last.label;
    var h = $('[data-insight-h]'), p = $('[data-insight-p]');
    if (o1 > o0 && i1 < i0) {
      h.textContent = 'AI is moving from instrument to colleague.';
      p.textContent = 'In ' + first.label + ', AI was only the instrument in ' + i0 + '% of the milestones we record, and produced the result itself in ' + o0 + '%. In ' + lastLabel + ', those shares are ' + i1 + '% and ' + o1 + '%.';
    } else {
      h.textContent = 'How the role of AI in recorded milestones has changed.';
      p.textContent = 'In ' + first.label + ', AI was the instrument in ' + i0 + '% of milestones and the originator in ' + o0 + '%; in ' + lastLabel + ', ' + i1 + '% and ' + o1 + '%.';
    }
    var foot = $('#role-foot');
    foot.innerHTML = '';
    var f1 = document.createElement('p');
    f1.textContent = (P.rest ? 'Not charted: ' + P.rest.n + ' milestones from ' + P.rest.from + '–' + P.rest.to + ', too few per year for a share (' + P.rest.c.originator + ' originator, ' + P.rest.c.collaborator + ' collaborator, ' + P.rest.c.instrument + ' instrument; see the table). ' : '') +
      (last.to === nowYear ? last.label + ' runs to ' + F0.fmtDate(L.updated) + '. ' : '');
    var f2 = document.createElement('p');
    f2.textContent = 'Caveat: this is a curated record, so it shows what we chose to log, and recent years are logged in more detail. Roles are editorial judgements under the rules in the ledger schema. Source: ' + LEDGER + ', ' + L.milestones.length + ' milestones, updated ' + L.updated + '.';
    foot.appendChild(f1); foot.appendChild(f2);

    function render() {
      host.innerHTML = '';
      var W = Math.max(280, Math.round(host.getBoundingClientRect().width)), small = W < 520;
      var labW = small ? 58 : 74, colW = small ? 44 : 64, nW = small ? 34 : 46, rowH = 22, gap = small ? 14 : 16, top = 30;
      var x0 = labW, x1 = W - (2 * colW + nW + (small ? 6 : 12));
      var H = top + bins.length * (rowH + gap) - gap + 30;
      var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'chart-svg', role: 'group', 'aria-label': 'Share of milestones by AI role, per period. Each row can be focused to read its values.' }, host);
      // header for the value columns
      var hy = 14;
      var ci = x1 + (small ? 6 : 12) + colW - 2, co = ci + colW, cn = co + nW;
      el('rect', { x: ci - colW + 4, y: hy - 8, width: 9, height: 9, rx: 1.5, style: 'fill:var(--mark-bio)' }, svg);
      el('text', { x: ci, y: hy, 'text-anchor': 'end', 'font-size': 11, style: 'fill:var(--ink-3);letter-spacing:.08em', text: 'TOOL' }, svg);
      el('rect', { x: co - colW + 4, y: hy - 8, width: 9, height: 9, rx: 1.5, style: 'fill:var(--mark-dig)' }, svg);
      el('text', { x: co, y: hy, 'text-anchor': 'end', 'font-size': 11, style: 'fill:var(--ink-3);letter-spacing:.08em', text: small ? 'ORIG' : 'ORIGIN' }, svg);
      el('text', { x: cn, y: hy, 'text-anchor': 'end', 'font-size': 11, style: 'fill:var(--ink-3);letter-spacing:.08em', text: 'N' }, svg);
      // one axis: share 0..100%, solid hairline grid
      var X = function (f) { return x0 + (x1 - x0) * f; };
      [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
        el('line', { x1: X(f), x2: X(f), y1: top - 6, y2: H - 22, style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
        if (!small || f % 0.5 === 0) el('text', { x: X(f), y: H - 6, 'text-anchor': f === 0 ? 'start' : f === 1 ? 'end' : 'middle', 'font-size': 11, style: 'fill:var(--ink-3)', text: Math.round(f * 100) + '%' }, svg);
      });
      bins.forEach(function (b, r) {
        var y = top + r * (rowH + gap);
        var lab = b.to === nowYear ? b.label + '*' : b.label;
        var shares = ROLES.map(function (k) { return b.c[k] / b.n; });
        var g = el('g', { class: 'row', tabindex: 0, role: 'img', 'aria-label': lab + ': instrument ' + pct(b.c.instrument, b.n) + '%, collaborator ' + pct(b.c.collaborator, b.n) + '%, originator ' + pct(b.c.originator, b.n) + '%, of ' + b.n + ' milestones' }, svg);
        el('rect', { class: 'rowbg', x: 0, y: y - 5, width: W, height: rowH + 10, fill: 'transparent' }, g);
        el('text', { x: 0, y: y + rowH / 2 + 4, 'font-size': small ? 11.5 : 12.5, style: 'fill:var(--ink-2)', text: lab }, g);
        var acc = 0;
        ROLES.forEach(function (k, j) {
          var s = shares[j]; if (s <= 0) { acc += s; return; }
          var a = X(acc) + (acc > 0 ? 1 : 0), e = X(acc + s) - (acc + s < 0.9999 ? 1 : 0), w = Math.max(0.5, e - a);
          var isEnd = acc + s >= 0.9999, rr = Math.min(4, w / 2);
          var d = isEnd
            ? 'M' + a + ' ' + y + 'H' + (a + w - rr) + 'Q' + (a + w) + ' ' + y + ' ' + (a + w) + ' ' + (y + rr) + 'V' + (y + rowH - rr) + 'Q' + (a + w) + ' ' + (y + rowH) + ' ' + (a + w - rr) + ' ' + (y + rowH) + 'H' + a + 'Z'
            : 'M' + a + ' ' + y + 'H' + (a + w) + 'V' + (y + rowH) + 'H' + a + 'Z';
          var seg = el('path', { d: d, style: 'fill:' + FILL[k], 'data-role': k }, g);
          seg.addEventListener('pointermove', function (ev) { seg.style.opacity = '.85'; F0.tip.show(rowTip(b, lab, k), ev.clientX, ev.clientY); });
          seg.addEventListener('pointerleave', function () { seg.style.opacity = ''; F0.tip.hide(); });
          acc += s;
        });
        el('text', { x: ci, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12.5, class: 'num', style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: pct(b.c.instrument, b.n) + '%' }, g);
        el('text', { x: co, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12.5, style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: pct(b.c.originator, b.n) + '%' }, g);
        el('text', { x: cn, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12, style: 'fill:var(--ink-3);font-variant-numeric:tabular-nums', text: b.n }, g);
        g.addEventListener('focus', function () { var bb = g.getBoundingClientRect(); F0.tip.show(rowTip(b, lab, null), bb.left + X(0.5) * bb.width / W, bb.top + bb.height); });
        g.addEventListener('blur', function () { F0.tip.hide(); });
      });
    }
    function rowTip(b, lab, focus) {
      var rows = ROLES.slice().reverse().map(function (k) {
        var strong = !focus || focus === k;
        return '<div class="tip-row" style="opacity:' + (strong ? 1 : 0.7) + '"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="7" width="14" height="2.5" rx="1" style="fill:' + FILL[k] + '"/></svg><span class="tip-v">' + pct(b.c[k], b.n) + '%</span><span>' + F0.esc(k.toUpperCase()) + ' · ' + b.c[k] + ' of ' + b.n + '</span></div>';
      }).join('');
      return '<div class="tip-k">' + F0.esc(lab) + ' · ' + b.n + ' milestones</div><div class="tip-rows">' + rows + '</div>';
    }
    render();
    if ('ResizeObserver' in window) { var lw = 0; new ResizeObserver(function () { var w = Math.round(host.getBoundingClientRect().width); if (w !== lw) { lw = w; render(); } }).observe(host); }

    // table twin
    var tbtn = $('#role-table-btn'), twrap = $('#role-table');
    tbtn.addEventListener('click', function () {
      if (!twrap.firstChild) {
        var t = document.createElement('table'); t.className = 'tbl';
        t.innerHTML = '<caption>Milestones by AI role and period</caption><thead><tr><th scope="col">Period</th><th scope="col" class="n">Milestones</th><th scope="col" class="n">Instrument</th><th scope="col" class="n">Collaborator</th><th scope="col" class="n">Originator</th></tr></thead>';
        var tb = document.createElement('tbody');
        var all = (P.rest ? [Object.assign({}, P.rest, { label: P.rest.from + '–' + P.rest.to + ' (not charted)' })] : []).concat(bins);
        all.forEach(function (b) {
          var tr = document.createElement('tr');
          var cells = [b.to === nowYear ? b.label + ' (to ' + L.updated + ')' : b.label, b.n].concat(ROLES.map(function (k) { return b.c[k] + ' (' + pct(b.c[k], b.n) + '%)'; }));
          cells.forEach(function (v, i) { var td = document.createElement(i ? 'td' : 'th'); if (!i) td.scope = 'row'; else td.className = 'n'; td.textContent = v; tr.appendChild(td); });
          tb.appendChild(tr);
        });
        t.appendChild(tb); twrap.appendChild(t);
      }
      var open = twrap.hidden; twrap.hidden = !open;
      tbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      tbtn.textContent = open ? 'Hide the numbers' : 'Show the numbers';
    });
  }

  /* ---------- evidence strip ---------- */
  function evidence(L) {
    var order = ['formally-verified', 'independently-replicated', 'peer-reviewed', 'deployed', 'preprint', 'claimed'];
    var ul = $('#evid-list'), c = {}; ul.innerHTML = '';
    L.milestones.forEach(function (m) { c[m.evidence] = (c[m.evidence] || 0) + 1; });
    order.forEach(function (k) {
      var li = document.createElement('li');
      li.innerHTML = F0.ladderHTML(F0.RUNG[k]) + '<span class="nm">' + F0.esc(F0.EVID[k]) + '</span><span class="ct">' + (c[k] || 0) + '</span>';
      ul.appendChild(li);
    });
    var li = document.createElement('li');
    li.innerHTML = '<span aria-hidden="true" style="font:600 15px/1 var(--f-mono);color:var(--st-contested);text-align:center">×</span><span class="nm">Contested (any rung)</span><span class="ct">' + L.milestones.filter(function (m) { return m.contested; }).length + '</span>';
    ul.appendChild(li);
  }

  /* ---------- live research glyphs ---------- */
  var KAPPA = [ // reviewed records, CrocSwap/integer-mult-bounds certificates/selected-result.json history (dossier integer-mult.json)
    ['2026-09-23T00:00Z', Math.pow(2, -182)], ['2026-10-07T02:22Z', 5.8e-33], ['2026-10-07T13:35Z', Math.pow(2, -78)], ['2026-10-07T19:27Z', Math.pow(2, -59)],
    ['2026-10-08T00:27Z', 8.3e-11], ['2026-10-08T01:10Z', Math.pow(2, -31)], ['2026-10-08T13:10Z', Math.pow(2, -30)], ['2026-10-08T15:18Z', 3.886675852e-5],
    ['2026-10-08T18:24Z', 5.1016920170078e-5], ['2026-10-09T04:53Z', 0.0004609169], ['2026-10-09T05:55Z', 0.000472143085], ['2026-10-09T06:01Z', 0.000472154791],
    ['2026-10-09T12:32Z', 0.000661885549259598], ['2026-10-10T14:08Z', 0.000723571590007464], ['2026-10-12T01:55Z', 0.001517760977820331],
    ['2026-10-12T13:10Z', 0.001584931111785787], ['2026-10-12T14:41Z', 0.001602278921983212], ['2026-10-12T16:59Z', 0.0016127213726553],
    ['2026-10-12T21:01Z', 0.001635183729255778], ['2026-10-12T22:36Z', 0.001635527380375392], ['2026-10-13T05:57Z', 0.001661202643272239],
    ['2026-10-13T06:44Z', 0.001661634653669567], ['2026-10-13T13:30Z', 0.001661957774647029], ['2026-10-13T15:06Z', 0.001661960547713947],
    ['2026-10-13T18:05Z', 0.001672188119205421], ['2026-10-13T18:45Z', 0.001672660197076918]
  ].map(function (d) { return [Date.parse(d[0]), Math.log2(d[1])]; });
  var VDW = [ // van der Waerden constant c (rohanarun/van-der-waerden-refinement; member-rohanarun dossier table)
    { c: 1e-5, who: 'openai' }, { c: 1 / 200, who: 'r' }, { c: 1 / 193, who: 'r' }, { c: 1 / 25, who: 'r' },
    { c: 1 / 19, who: 'o' }, { c: 1 / 16, who: 'o' }, { c: 2 / 25, who: 'o' }, { c: 1 / 9, who: 'o' }];
  var GATES = { rec: [6, 117], pareto: [[6, 112], [7, 110], [12, 108], [13, 107]] }; // gf2m-circuits paper 1, Tables 1-3
  function foldDensity(s) { var t = 2 * s / (1 + s * s), a = Math.SQRT2 * (1 - s * s) / (1 + s * s), d = 2 + a; return 2 * Math.SQRT2 * Math.PI / (d * d * d + d * t * t + 2 * t * t * t); }
  function ring(x, cx, cy, r, fill, bg) { x.fillStyle = bg; x.beginPath(); x.arc(cx, cy, r + 2, 0, Math.PI * 2); x.fill(); x.fillStyle = fill; x.beginPath(); x.arc(cx, cy, r, 0, Math.PI * 2); x.fill(); }

  var G = {
    incentre: { anim: true, still: 0.5, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-incentre'), L0 = 12, R0 = w - 14, T = 34, B = h - 12, y0 = 0.2, y1 = 0.76;
      var X = function (s) { return L0 + (R0 - L0) * s; }, Y = function (v) { return B - (B - T) * (v - y0) / (y1 - y0); };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, Y(0.74048)); x.lineTo(R0, Y(0.74048)); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'left'; x.fillText('π/√18', L0, Y(0.74048) - 6);
      x.textAlign = 'left'; x.fillText('0.2233', L0 + 4, B - 6);
      x.strokeStyle = acc; x.lineWidth = 2; x.lineJoin = x.lineCap = 'round'; x.beginPath();
      for (var i = 0; i <= 100; i++) { var s = i / 100; i ? x.lineTo(X(s), Y(foldDensity(s))) : x.moveTo(X(s), Y(foldDensity(s))); }
      x.stroke();
      var sNow = ph == null ? 1 : 0.5 - 0.5 * Math.cos(ph * Math.PI * 2);
      ring(x, X(sNow), Y(foldDensity(sNow)), 4, acc, tk('--bg-1'));
      out('ρ ' + foldDensity(sNow).toFixed(4));
    }, period: 7000 },
    transit: { anim: true, still: 0.5, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-exoplanets'), sr = Math.min(h * 0.3, 36), sx = 18 + sr, sy = h / 2 + 10;
      var g = x.createRadialGradient(sx, sy, 0, sx, sy, sr);
      g.addColorStop(0, acc); g.addColorStop(0.75, acc); g.addColorStop(1, tk('--bg-3'));
      x.fillStyle = g; x.beginPath(); x.arc(sx, sy, sr, 0, Math.PI * 2); x.fill();
      var p = ph == null ? 0.5 : ph, q = (p - 0.5) / 0.5; // -1..1 across the window
      var half = 0.3, inT = Math.abs(q) < half + 0.06, pr = sr * 0.16;
      var px = sx + (q / half) * (sr + pr), py = sy + sr * 0.15;
      if (Math.abs(q) < half * (sr + pr * 2) / (sr + pr) + 0.02) { x.fillStyle = tk('--bg-1'); x.beginPath(); x.arc(px, py, pr, 0, Math.PI * 2); x.fill(); x.strokeStyle = tk('--ink-3'); x.lineWidth = 1; x.stroke(); }
      var L0 = sx + sr + 18, R0 = w - 12, base = sy - 6, dep = 22, ing = 0.05;
      function flux(q) { var a = Math.abs(q); if (a >= half) return 0; if (a <= half - ing) return 1; return (half - a) / ing; }
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, base + dep + 10); x.lineTo(R0, base + dep + 10); x.stroke();
      x.strokeStyle = acc; x.lineWidth = 2; x.lineJoin = 'round'; x.beginPath();
      for (var i = 0; i <= 120; i++) { var qq = -1 + 2 * i / 120, xx = L0 + (R0 - L0) * i / 120, yy = base + dep * flux(qq); i ? x.lineTo(xx, yy) : x.moveTo(xx, yy); }
      x.stroke();
      ring(x, L0 + (R0 - L0) * p, base + dep * flux(q), 3.5, acc, tk('--bg-1'));
      out('Δ −' + Math.round(398 * flux(q)) + ' ppm');
    }, period: 6000 },
    kappa: { anim: true, once: true, still: 1, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-intmult'), L0 = 12, R0 = w - 14, T = 30, B = h - 14;
      var t0 = KAPPA[0][0], t1 = KAPPA[KAPPA.length - 1][0] + 6 * 3600e3, X = function (t) { return L0 + (R0 - L0) * (t - t0) / (t1 - t0); }, Y = function (v) { return B - (B - T) * (v + 190) / 190; };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B); x.lineTo(R0, B); x.stroke();
      var prog = ph == null ? 1 : Math.min(1, ph), upto = t0 + (t1 - t0) * prog;
      x.strokeStyle = acc; x.lineWidth = 2; x.lineJoin = 'miter'; x.beginPath();
      var last = KAPPA[0];
      KAPPA.forEach(function (k, i) { if (k[0] > upto) return; if (!i) x.moveTo(X(k[0]), Y(k[1])); else { x.lineTo(X(k[0]), Y(last[1])); x.lineTo(X(k[0]), Y(k[1])); } last = k; });
      x.lineTo(X(Math.min(upto, t1 - 6 * 3600e3)), Y(last[1])); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'left'; x.fillText('−182 · AI-written paper', L0 + 2, Y(-182) - 7);
      ring(x, X(Math.min(upto, t1 - 6 * 3600e3)), Y(last[1]), 3.5, acc, tk('--bg-1'));
      out('log₂κ ' + last[1].toFixed(2).replace('-', '−'));
    }, period: 2200 },
    pascal: { anim: true, still: 31 / 32, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-mobius'), N = 32, size = Math.min(h - 26, w * 0.5), cell = size / N, ox = w - size - 14, oy = h - size - 8;
      var row = ph == null ? 31 : Math.floor(ph * N) % N;
      for (var i = 0; i < N; i++) for (var j = 0; j <= i; j++) {
        if ((j & i) !== j) continue;
        x.fillStyle = i === row ? acc : tk('--ink-3'); x.globalAlpha = i === row ? 1 : 0.55;
        x.fillRect(ox + j * cell, oy + i * cell, Math.max(1, cell - 0.6), Math.max(1, cell - 0.6));
      }
      x.globalAlpha = 1;
      var bx = 12, bw = ox - bx - 18, by = oy + 14;
      [['NAIVE', 211], ['YATES 1937', 80]].forEach(function (b, k) {
        var yy = by + k * 34;
        x.fillStyle = tk('--ink-2'); x.font = mono(11); x.textAlign = 'left'; x.fillText(b[0] + ' · ' + b[1] + ' XOR', bx, yy);
        x.fillStyle = k ? acc : tk('--ink-3'); x.globalAlpha = k ? 1 : 0.6; x.fillRect(bx, yy + 6, Math.max(2, bw * b[1] / 211), 6); x.globalAlpha = 1;
      });
      var ones = 0; for (var jj = 0; jj <= row; jj++) if ((jj & row) === jj) ones++;
      out('row ' + row + ' · ' + ones + ' input' + (ones > 1 ? 's' : ''));
    }, period: 6400 },
    gates: { anim: true, once: true, still: 1, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-gf2m'), L0 = 34, R0 = w - 14, T = 30, B = h - 22;
      var X = function (d) { return L0 + (R0 - L0) * (d - 5) / 9; }, Y = function (g) { return B - (B - T) * (g - 105) / 14; };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B); x.lineTo(R0, B); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'center';
      [6, 9, 12].forEach(function (d) { x.fillText(d, X(d), B + 14); });
      x.textAlign = 'right'; x.fillText('DEPTH', R0, B + 14);
      x.textAlign = 'right'; [107, 112, 117].forEach(function (g) { x.fillText(g, L0 - 6, Y(g) + 4); });
      var prog = ph == null ? 1 : Math.min(1, ph);
      // the 2010 record: hollow
      x.strokeStyle = tk('--ink-2'); x.lineWidth = 1.5; x.beginPath(); x.arc(X(6), Y(117), 4, 0, Math.PI * 2); x.stroke();
      x.fillStyle = tk('--ink-3'); x.textAlign = 'left'; x.fillText('2010', X(6) + 9, Y(117) + 4);
      // arrow down to 112
      var yA = Y(117) + 6, yB = Y(112) - 7, yE = yA + (yB - yA) * Math.min(1, prog * 2);
      x.strokeStyle = tk('--ink-3'); x.lineWidth = 1; x.beginPath(); x.moveTo(X(6), yA); x.lineTo(X(6), yE); x.stroke();
      if (prog > 0.5) { x.beginPath(); x.moveTo(X(6) - 3, yB - 4); x.lineTo(X(6), yB); x.lineTo(X(6) + 3, yB - 4); x.stroke(); }
      // the 2026 frontier as a staircase
      var pts = GATES.pareto, n = Math.max(1, Math.round(prog * pts.length));
      x.strokeStyle = acc; x.lineWidth = 2; x.beginPath();
      for (var i = 0; i < n; i++) { var p = pts[i]; if (!i) x.moveTo(X(p[0]), Y(p[1])); else { x.lineTo(X(p[0]), Y(pts[i - 1][1])); x.lineTo(X(p[0]), Y(p[1])); } }
      if (n === pts.length) x.lineTo(X(14), Y(pts[n - 1][1]));
      x.stroke();
      for (var k = 0; k < n; k++) ring(x, X(pts[k][0]), Y(pts[k][1]), 4, acc, tk('--bg-1'));
      out('−5 gates at depth 6');
    }, period: 1800 },
    vdw: { anim: true, once: true, still: 1, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-rohan'), L0 = 14, R0 = w - 16, T = 32, B = h - 26;
      var X = function (c) { return L0 + (R0 - L0) * (Math.log10(c) + 5) / 5; }, Y = function (i) { return B - (B - T) * i / (VDW.length - 1); };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B + 8); x.lineTo(R0, B + 8); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11);
      [[1e-5, '1/100,000', 'left'], [1e-3, '1/1,000', 'center'], [1, '1', 'right']].forEach(function (t) { x.textAlign = t[2]; x.fillText(t[1], X(t[0]), h - 4); });
      // rohanarun's 1/24 ceiling for one method
      x.strokeStyle = tk('--ink-3'); x.globalAlpha = 0.6; x.beginPath(); x.moveTo(X(1 / 24), T - 4); x.lineTo(X(1 / 24), B + 8); x.stroke(); x.globalAlpha = 1;
      x.fillStyle = tk('--ink-3'); x.textAlign = 'right'; x.fillText('1/24 limit', X(1 / 24) - 6, B + 2);
      var n = ph == null ? VDW.length : Math.max(1, Math.round(Math.min(1, ph) * VDW.length));
      x.strokeStyle = tk('--ink-3'); x.lineWidth = 1; x.beginPath();
      for (var i = 0; i < n; i++) i ? x.lineTo(X(VDW[i].c), Y(i)) : x.moveTo(X(VDW[i].c), Y(i));
      x.stroke();
      for (var j = 0; j < n; j++) {
        var v = VDW[j], cx = X(v.c), cy = Y(j);
        x.fillStyle = tk('--bg-1'); x.beginPath(); x.arc(cx, cy, 6, 0, Math.PI * 2); x.fill();
        x.beginPath(); x.arc(cx, cy, 4, 0, Math.PI * 2);
        if (v.who === 'r') { x.fillStyle = acc; x.fill(); } else { x.strokeStyle = v.who === 'openai' ? tk('--ink-2') : acc; x.lineWidth = 1.6; x.stroke(); }
      }
      x.fillStyle = tk('--ink-2'); x.textAlign = 'left'; x.fillText('OpenAI', X(1e-5) + 9, Y(0) + 4);
      if (n === VDW.length) { x.textAlign = 'left'; x.fillText('1/9', X(1 / 9) + 9, Y(VDW.length - 1) + 4); }
      out('\u00d711,111');
    }, period: 2000 },
    shrink: { anim: true, still: 3 / 4 + 0.01, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-shea'), sizes = [66, 5, 4, 3], names = ['66×66', '5×5', '4×4', '3×3'], pat = ['011', '101', '110'];
      var gap = 16, B = Math.min(h - 46, (w - 24 - gap * 3) / 4), ox = (w - (4 * B + 3 * gap)) / 2, oy = 30;
      var cur = ph == null ? 3 : Math.floor(ph * 4) % 4;
      sizes.forEach(function (n, k) {
        var bx = ox + k * (B + gap), c = B / n, on = k === cur;
        x.strokeStyle = tk('--ink-3'); x.globalAlpha = n > 10 ? 0.28 : 0.6; x.lineWidth = 1; x.beginPath();
        for (var i = 1; i < n; i++) { x.moveTo(bx + i * c, oy); x.lineTo(bx + i * c, oy + B); x.moveTo(bx, oy + i * c); x.lineTo(bx + B, oy + i * c); }
        x.stroke(); x.globalAlpha = 1;
        if (n === 3) { x.fillStyle = acc; for (var r = 0; r < 3; r++) for (var q = 0; q < 3; q++) if (pat[r][q] === '1') x.fillRect(bx + q * c + 2, oy + r * c + 2, c - 4, c - 4); }
        x.strokeStyle = on ? acc : tk('--line-ui'); x.lineWidth = on ? 2 : 1; x.strokeRect(bx + 0.5, oy + 0.5, B - 1, B - 1);
        x.fillStyle = on ? tk('--ink') : tk('--ink-3'); x.font = mono(11); x.textAlign = 'center'; x.fillText(names[k], bx + B / 2, oy + B + 14);
      });
      out([4356, 25, 16, 9][cur].toLocaleString('en-US') + ' entries');
    }, period: 4800 }
  };

  function glyphs() {
    $$('canvas[data-glyph]').forEach(function (cv) {
      var spec = G[cv.getAttribute('data-glyph')]; if (!spec) return;
      var c = F0.canvas(cv), box = cv.parentNode, ro = box.querySelector('[data-readout]');
      var out = function (s) { if (ro && ro.textContent !== s) ro.textContent = s; };
      var t0 = 0, done = false, visible = false;
      function paint(ph) { var x = c.ctx; x.setTransform(c.dpr, 0, 0, c.dpr, 0, 0); x.clearRect(0, 0, c.w, c.h); spec.draw(x, c.w, c.h, ph, out); }
      var loop = F0.loop(function (now) {
        if (!t0) t0 = now;
        var ph = (now - t0) / spec.period;
        if (spec.once) { if (ph >= 1) { paint(1); done = true; loop.stop(); return; } paint(ph); }
        else paint(ph % 1);
      });
      function still() { paint(spec.once ? null : spec.still); }
      function sync() {
        if (visible && F0.motion() && !F0.idle() && !(spec.once && done)) { if (!loop.running) t0 = 0; loop.start(); }
        else { loop.stop(); if (!(spec.once && done) || !F0.motion()) still(); }
      }
      still();
      c.resize(function () { if (!loop.running) still(); });
      F0.onTheme(function () { if (!loop.running) still(); });
      F0.whenVisible(box, function () { visible = true; sync(); }, function () { visible = false; sync(); });
      F0.onMotion(sync); F0.onIdle(sync);
    });
  }

  /* ---------- Commons glyphs: SVG drawn at the box's real width so text stays 11px ---------- */
  function sized(host, build) {
    var lw = 0;
    function go() { var w = Math.round(host.getBoundingClientRect().width); if (!w || w === lw) return; lw = w; host.innerHTML = ''; build(w); }
    go(); if ('ResizeObserver' in window) new ResizeObserver(go).observe(host);
  }
  function nutrak() {
    var host = $('#nutrak-host'); if (!host) return;
    var mg = [549, 944, 728, 1070, 685, 710, 754], days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'], mean = 777.1; // Nutrak demo fixture, 2026-08-24..30
    sized(host, function (W) {
      var H = 132, L0 = 40, R0 = W - (W < 420 ? 96 : 120), T = 26, B = H - 26;
      var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'gsvg', role: 'img', 'aria-label': 'Calcium in the Nutrak demo week: 549, 944, 728, 1070, 685, 710 and 754 milligrams a day. Judged day by day the verdict flips five times; the 7-day average, 777 milligrams, gives one steady signal.' }, host);
      var Y = function (v) { return B - (B - T) * (v - 500) / 620; }, X = function (i) { return L0 + 8 + (R0 - L0 - 16) * i / 6; };
      el('text', { x: 0, y: 11, text: 'CALCIUM, MG A DAY · DEMO WEEK', style: 'fill:var(--ink-3)' }, svg);
      [[1000, 'RDA'], [800, 'EAR']].forEach(function (r) {
        el('line', { x1: L0, x2: R0, y1: Y(r[0]), y2: Y(r[0]), style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, svg);
        el('text', { x: L0 - 8, y: Y(r[0]) + 4, 'text-anchor': 'end', text: r[1] }, svg);
      });
      mg.forEach(function (v, i) {
        el('line', { x1: X(i), x2: X(i), y1: Y(mean), y2: Y(v), style: 'stroke:var(--ink-3)', 'stroke-width': 1, opacity: 0.7 }, svg);
      });
      el('line', { x1: L0, x2: R0, y1: Y(mean), y2: Y(mean), style: 'stroke:var(--acc-nutrak)', 'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
      mg.forEach(function (v, i) {
        el('circle', { cx: X(i), cy: Y(v), r: 6, style: 'fill:var(--bg-1)' }, svg);
        el('circle', { cx: X(i), cy: Y(v), r: 4, style: 'fill:var(--ink-2)' }, svg);
        el('text', { x: X(i), y: H - 6, 'text-anchor': 'middle', text: days[i], style: 'fill:var(--ink-3)' }, svg);
      });
      el('text', { x: R0 + 10, y: Y(mean) + 4, text: 'week: 777', style: 'fill:var(--ink)' }, svg);
      el('text', { x: R0 + 10, y: Y(mean) + 19, text: 'one verdict', style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: R0 + 10, y: Y(1040) + 4, text: 'days: 5 flips', style: 'fill:var(--ink-3)' }, svg);
    });
  }
  function medcode() {
    var host = $('#medcode-host'); if (!host) return;
    var parts = [[18, 'verified', '--st-verified', 1], [33, 'unverified', '--st-claimed', 0.55], [16, 'vendor claim only', '--st-preprint', 0.8]], tot = 67; // medcode index.html vendor table, snapshot 2026-10-03
    sized(host, function (W) {
      var H = 44, svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'gsvg', role: 'img', 'aria-label': 'Evidence behind the vendor table: 18 of 67 tags verified, 33 unverified, 16 vendor claims only.' }, host);
      el('text', { x: 0, y: 11, text: '67 EVIDENCE TAGS IN THE VENDOR TABLE', style: 'fill:var(--ink-3)' }, svg);
      var x = 0;
      parts.forEach(function (p, i) {
        var w = W * p[0] / tot - (i < parts.length - 1 ? 2 : 0);
        el('rect', { x: x, y: 22, width: Math.max(1, w), height: 16, style: 'fill:var(' + p[2] + ')', opacity: p[3] }, svg);
        x += w + 2;
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
