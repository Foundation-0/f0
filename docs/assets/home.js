/* Home page: wires the Radiant (with its time control), the role chart (with table twin), the evidence strip,
   the founding members (data/members.json), the research cards (data/projects.json, with the live reviewed κ),
   the instrument and commons numbers (data/projects.json) and the writing list (data/writing.json).
   The HTML carries a pre-rendered copy of every list, so the page reads without JS; this file re-renders
   each one from its data file. The κ records come from research/integer-multiplication/kappa-history.json; the few
   hard-coded series below (gate counts, the Nutrak week) cite their source. */
(function () {
  'use strict';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var R = (window.F0 && F0.root) || '';
  var LEDGER = R + 'data/ledger.json', MEMBERS = R + 'data/members.json', PROJECTS = R + 'data/projects.json',
    WRITING = R + 'data/writing.json', FAMILIES = R + 'data/openai-math-families.json';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) { if (k === 'text') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e); return e;
  }
  function esc(s) { return F0.esc(s); }
  function pct(a, b) { return b ? Math.round(100 * a / b) : 0; }
  function tk(n) { return F0.css(n); }
  function mono(px, wt) { return (wt || 500) + ' ' + px + 'px ' + tk('--f-mono'); }
  function firstSentence(s) { var m = String(s || '').match(/^(.+?[.!?])(?=\s+[A-Z(“"]|\s*$)/); return m ? m[1] : String(s || ''); }
  function rel(u) { return /^(https?:)?\/\//.test(u) ? u : R + u; }
  var WORDS = ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve'];
  function utc(iso) { var d = new Date(iso); if (isNaN(d)) return String(iso || ''); return F0.fmtDate(d.toISOString().slice(0, 10)) + ', ' + d.toISOString().slice(11, 16) + ' UTC'; }
  function soft(p) { return p.catch(function (e) { console.warn(e); return null; }); }

  function start() {
    var led = F0.json(LEDGER), mem = soft(F0.json(MEMBERS)), proj = soft(F0.json(PROJECTS)), fam = soft(F0.json(FAMILIES));
    Promise.all([led, mem]).then(function (r) {
      var L = r[0]; stats(L); radiant(L, r[1]); roleChart(L); evidence(L);
    }).catch(function (e) {
      console.error(e);
      var ro = $('#radiant-readout'); if (ro) ro.textContent = 'Ledger failed to load';
    });
    Promise.all([mem, proj, fam]).then(function (r) {
      if (r[0]) members(r[0]);
      if (r[1]) { cards(r[1], r[0], r[2]); bindProjects(r[1]); medcode(r[1]); }
      glyphs(); liveKappa(r[0]);
    });
    soft(F0.json(WRITING)).then(function (W) { if (W) posts(W); });
    nutrak(); homeEgg();
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
  function radiant(L, MB) {
    var stage = $('#radiant-stage');
    var people = MB && MB.members ? MB.members.map(function (m) { return { name: m.name, login: m.login }; }) : undefined;
    var RD = new F0.Radiant(stage, L, {
      list: $('#radiant-list'), readout: $('#radiant-readout'), centre: $('#radiant-centre'), base: R + 'ledger/', members: people,
      time: { range: $('#rad-range'), play: $('#rad-play'), output: $('#rad-out') }
    });
    $$('.legend [data-filter]').forEach(function (b) {
      b.addEventListener('click', function () {
        var on = b.getAttribute('aria-pressed') !== 'true';
        $$('.legend [data-filter]').forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
        RD.setFilter(on ? b.getAttribute('data-filter') : null);
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
        if (i === 1) { td.scope = 'row'; var a = document.createElement('a'); a.href = R + 'ledger/#' + encodeURIComponent(m.id); a.textContent = m.title; td.appendChild(a); }
        else td.textContent = v;
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    t.appendChild(tb); return t;
  }

  /* ---------- 01: what AI did, by period (100% stacked bars, one axis). The periods, numbers and headline come
     from F0.rolePeriods / F0.roleInsight, the same functions the Ledger page uses, so both pages say the same. ---------- */
  var ROLES = ['instrument', 'collaborator', 'originator'];
  var FILL = { instrument: 'var(--mark-bio)', collaborator: 'var(--mark-mid)', originator: 'var(--mark-dig)' };
  var NAME = { instrument: 'Instrument', collaborator: 'Collaborator', originator: 'Originator' };
  function roleChart(L) {
    var nowYear = +L.updated.slice(0, 4);
    var P = F0.rolePeriods(L.milestones, { nowYear: nowYear }), host = $('#role-svg-host');
    var ins = F0.roleInsight(P);
    $('[data-insight-h]').textContent = ins.h;
    $('[data-insight-p]').textContent = ins.p;
    var last = P[P.length - 1], few = P.some(function (p) { return p.n > 0 && p.n < 10; });
    var foot = $('#role-foot');
    foot.innerHTML = '';
    var f1 = document.createElement('p');
    f1.textContent = (last.now ? last.label + ' runs to ' + F0.fmtDate(L.updated) + '. ' : '') + 'The periods are the Ledger’s: they get shorter as the record gets denser.' + (few ? ' * fewer than 10 milestones: drawn faint.' : '');
    var f2 = document.createElement('p');
    f2.textContent = 'Caveat: this is a curated record, so it shows what we chose to log, and recent years are logged in more detail. Roles are editorial judgements under the rules in the ledger schema. Source: data/ledger.json, ' + L.milestones.length + ' milestones, updated ' + L.updated + '.';
    foot.appendChild(f1); foot.appendChild(f2);
    var MONO = 0.6; // Geist Mono (and its size-matched fallback) advance width, in em
    function textW(t, fs, ls) { return String(t).length * fs * (MONO + (ls || 0)); }
    function lab(p) { return p.label + (p.n > 0 && p.n < 10 ? '*' : ''); }
    function rowAria(p) { return p.label + (p.now ? ' (to ' + F0.fmtDate(L.updated) + ')' : '') + ': instrument ' + pct(p.c.instrument, p.n) + '%, collaborator ' + pct(p.c.collaborator, p.n) + '%, originator ' + pct(p.c.originator, p.n) + '%, of ' + p.n + ' milestones'; }

    function render() {
      host.innerHTML = '';
      var W = Math.max(260, Math.round(host.getBoundingClientRect().width)), wide = W >= 600;
      var labFS = wide ? 12.5 : 12, rowH = wide ? 22 : 16, gap = wide ? 16 : 14;
      var labW = Math.ceil(Math.max.apply(null, P.map(function (p) { return textW(lab(p), labFS); }))) + 14;
      var colW = Math.ceil(textW('MILESTONES', 11, 0.08)) + 30; // header text + its 9px swatch + a gap
      var x0 = wide ? labW : 0, x1 = wide ? W - 3 * colW : W;
      var lineH = wide ? 0 : 18, top = wide ? 30 : 4, step = lineH + rowH + gap;
      var H = top + P.length * step - gap + 30;
      var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'chart-svg', role: 'group', 'aria-label': 'Share of milestones by AI role, per period. Focus a row, then use the up and down arrow keys to read each period.' }, host);
      var X = function (f) { return x0 + (x1 - x0) * f; };
      var colX = function (k) { return x1 + (k + 1) * colW; };
      if (wide) {
        [['INSTRUMENT', 'instrument'], ['ORIGINATOR', 'originator'], ['MILESTONES', null]].forEach(function (h, k) {
          var tx = colX(k);
          if (h[1]) el('rect', { x: tx - textW(h[0], 11, 0.08) - 14, y: 6, width: 9, height: 9, rx: 1.5, style: 'fill:' + FILL[h[1]] }, svg);
          el('text', { x: tx, y: 14, 'text-anchor': 'end', 'font-size': 11, style: 'fill:var(--ink-3);letter-spacing:.08em', text: h[0] }, svg);
        });
      }
      [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
        el('line', { x1: X(f), x2: X(f), y1: top + lineH - 6, y2: H - 22, style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
        if (wide || f % 0.5 === 0) el('text', { x: X(f), y: H - 6, 'text-anchor': f === 0 ? 'start' : f === 1 ? 'end' : 'middle', 'font-size': 11, style: 'fill:var(--ink-3)', text: Math.round(f * 100) + '%' }, svg);
      });
      var rows = [];
      P.forEach(function (b, r) {
        var y0 = top + r * step, y = y0 + lineH, faint = b.n > 0 && b.n < 10;
        var g = el('g', { class: 'row', tabindex: r === 0 ? 0 : -1, role: 'img', 'aria-label': rowAria(b) }, svg);
        rows.push(g);
        el('rect', { class: 'rowbg', x: 0, y: y0 - 5, width: W, height: lineH + rowH + 10, fill: 'transparent', rx: 2 }, g);
        var i0 = pct(b.c.instrument, b.n) + '%', o0 = pct(b.c.originator, b.n) + '%';
        if (wide) {
          el('text', { x: 0, y: y + rowH / 2 + 4, 'font-size': labFS, style: 'fill:var(--ink-2)', text: lab(b) }, g);
          [i0, o0].forEach(function (v, k) { el('text', { x: colX(k), y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12.5, style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: v }, g); });
          el('text', { x: colX(2), y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12, style: 'fill:var(--ink-3);font-variant-numeric:tabular-nums', text: b.n }, g);
        } else {
          el('text', { x: 0, y: y0 + 11, 'font-size': labFS, style: 'fill:var(--ink-2)', text: lab(b) }, g);
          var full = 'instrument ' + i0 + ' · originator ' + o0, short = 'instr. ' + i0 + ' · orig. ' + o0;
          var room = W - textW(lab(b), labFS) - 12, txt = textW(full, 11.5) <= room ? full : short;
          el('text', { x: W, y: y0 + 11, 'text-anchor': 'end', 'font-size': 11.5, style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: txt }, g);
        }
        var acc = 0;
        ROLES.forEach(function (k, j) {
          var sh = b.n ? b.c[k] / b.n : 0; if (sh <= 0) return;
          var a = X(acc) + (acc > 0 ? 1 : 0), e = X(acc + sh) - (acc + sh < 0.9999 ? 1 : 0), w = Math.max(0.5, e - a);
          var isEnd = acc + sh >= 0.9999, rr = Math.min(4, w / 2);
          var d = isEnd
            ? 'M' + a + ' ' + y + 'H' + (a + w - rr) + 'Q' + (a + w) + ' ' + y + ' ' + (a + w) + ' ' + (y + rr) + 'V' + (y + rowH - rr) + 'Q' + (a + w) + ' ' + (y + rowH) + ' ' + (a + w - rr) + ' ' + (y + rowH) + 'H' + a + 'Z'
            : 'M' + a + ' ' + y + 'H' + (a + w) + 'V' + (y + rowH) + 'H' + a + 'Z';
          var seg = el('path', { d: d, style: 'fill:' + FILL[k] + (faint ? ';opacity:.45' : ''), 'data-role': k }, g);
          seg.addEventListener('pointermove', function (ev) { seg.style.opacity = faint ? '.6' : '.85'; F0.tip.show(rowTip(b, k), ev.clientX, ev.clientY); });
          seg.addEventListener('pointerleave', function () { seg.style.opacity = faint ? '.45' : ''; F0.tip.hide(); });
          acc += sh;
        });
        g.addEventListener('focus', function () { var bb = g.getBoundingClientRect(); F0.tip.show(rowTip(b, null), bb.left + Math.min(bb.width * 0.45, X(0.5) * bb.width / W), bb.bottom); });
        g.addEventListener('blur', function () { F0.tip.hide(true); });
        g.addEventListener('keydown', function (e) {
          var j = e.key === 'ArrowDown' ? r + 1 : e.key === 'ArrowUp' ? r - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? rows.length - 1 : -2;
          if (j === -2) return;
          e.preventDefault(); j = Math.max(0, Math.min(rows.length - 1, j));
          rows.forEach(function (q, qi) { q.setAttribute('tabindex', qi === j ? 0 : -1); });
          rows[j].focus();
        });
      });
    }
    function rowTip(b, focus) {
      var rws = ROLES.slice().reverse().map(function (k) {
        var strong = !focus || focus === k;
        return '<div class="tip-row" style="opacity:' + (strong ? 1 : 0.7) + '"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="7" width="14" height="2.5" rx="1" style="fill:' + FILL[k] + '"/></svg><span class="tip-v">' + pct(b.c[k], b.n) + '%</span><span>' + esc(NAME[k].toUpperCase()) + ' · ' + b.c[k] + ' of ' + b.n + '</span></div>';
      }).join('');
      return '<div class="tip-k">' + esc(b.label + (b.now ? ' (to ' + F0.fmtDate(L.updated) + ')' : '')) + ' · ' + b.n + ' milestones</div><div class="tip-rows">' + rws + '</div>';
    }
    render();
    if ('ResizeObserver' in window) { var lw = 0; new ResizeObserver(function () { var w = Math.round(host.getBoundingClientRect().width); if (w && w !== lw) { lw = w; render(); } }).observe(host); }

    var tbtn = $('#role-table-btn'), twrap = $('#role-table');
    tbtn.addEventListener('click', function () {
      if (!twrap.firstChild) {
        var t = document.createElement('table'); t.className = 'tbl';
        t.innerHTML = '<caption>Milestones by AI role and period (the Ledger’s periods)</caption><thead><tr><th scope="col">Period</th><th scope="col" class="n">Milestones</th><th scope="col" class="n">Instrument</th><th scope="col" class="n">Collaborator</th><th scope="col" class="n">Originator</th></tr></thead>';
        var tb = document.createElement('tbody');
        P.forEach(function (b) {
          var tr = document.createElement('tr');
          var cells = [b.label + (b.now ? ' (to ' + L.updated + ')' : ''), b.n].concat(ROLES.map(function (k) { return b.c[k] + ' (' + pct(b.c[k], b.n) + '%)'; }));
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
      li.innerHTML = F0.ladderHTML(F0.RUNG[k]) + '<span class="nm">' + esc(F0.EVID[k]) + '</span><span class="ct">' + (c[k] || 0) + '</span>';
      ul.appendChild(li);
    });
    var li = document.createElement('li');
    li.innerHTML = '<span aria-hidden="true" style="font:600 15px/1 var(--f-mono);color:var(--st-contested);text-align:center">×</span><span class="nm">Contested (any rung)</span><span class="ct">' + L.milestones.filter(function (m) { return m.contested; }).length + '</span>';
    ul.appendChild(li);
  }

  /* ---------- 02: founding members, from data/members.json (no pictures, by design) ---------- */
  function members(MB) {
    var list = MB.members || [], host = $('#members-list'); if (!host || !list.length) return;
    host.innerHTML = list.map(function (m, i) {
      var main = m.main_project || {};
      var others = (m.work || []).filter(function (w) { return w.url !== main.url; });
      return '<li class="member" id="m-' + esc(m.login) + '"><span class="idx">M·' + String(i + 1).padStart(2, '0') + '</span>' +
        '<h3>' + esc(m.name) + '</h3><a class="gh" href="' + esc(m.github) + '">@' + esc(m.login) + '</a>' +
        '<div class="mp">Main project<a href="' + esc(main.page ? R + main.page : main.url) + '">' + esc(main.name) + '</a></div>' +
        '<p>' + esc(firstSentence(m.summary)) + '</p>' +
        (others.length ? '<div class="mw"><span>Also</span><ul>' + others.slice(0, 3).map(function (w) { return '<li><a href="' + esc(w.url) + '">' + esc(w.name) + '</a></li>'; }).join('') +
          (others.length > 3 ? '<li class="more-n"><a href="' + R + 'charter/#m-' + esc(m.login) + '">+' + (others.length - 3) + ' more on the charter page</a></li>' : '') + '</ul></div>' : '') +
        '</li>';
    }).join('');
    $$('[data-members-count]').forEach(function (e) { e.textContent = WORDS[list.length] || String(list.length); });
  }

  /* ---------- 03: research cards, from data/projects.json ---------- */
  /* Presentation per project: field label, who, glyph and caption. Every number shown comes from the data
     files; the fact labels here are plain-words versions of the data labels (the full label is the tooltip). */
  var CARD = {
    'incentre-lattice': { field: 'Geometry', role: 'Our own work', who: 'Aska Digital', acc: '--acc-incentre', feature: true, fact: 1, factK: 'exact certificate coefficients, all ≥ 0, rule out any collision along the fold',
      glyph: 'incentre', gk: 'PACKING DENSITY ALONG THE FOLD', gr: 'ρ 0.7405', aria: 'Packing density along the exact fold rises from 0.2233 to 0.7405, the Kepler bound pi over root 18.',
      cap: 'Computed in your browser from the fold’s exact formula, from the open scaffold (22.3%) to π/√18 ≈ 74.05%, the densest packing possible.' },
    'exoplanets': { field: 'Astronomy', role: 'Member’s project', acc: '--acc-exoplanets', fact: 1, factK: 'candidates on 14 Oct 2026; none confirmed',
      glyph: 'transit', gk: 'MODEL · 3.18-DAY SIGNAL', gr: 'Δ −398 ppm', aria: 'Model of a planet crossing its star and the dip it makes in the star’s light.',
      cap: 'A planet crossing TIC 4206066, the star that inspired the method, modelled from its published dip: 398 parts per million (the star dims by 0.04%) for 1.7 hours. Depth exaggerated.' },
    'integer-multiplication': { field: 'Algorithms', role: 'Member’s race', who: 'Doug Colkitt + crowd', acc: '--acc-intmult', fact: 'kappa',
      glyph: 'kappa', gk: 'LOG₂ κ · DATED 23 SEP → NOW', gr: 'log₂κ −9.22', aria: 'Staircase of the exponent saving kappa on a log scale, from 2 to the minus 182 in the paper dated 23 September to about 2 to the minus 9.22 by 13 October 2026.',
      gloss: '<b>n log n</b> is the best speed proven so far for multiplying two n-digit numbers. <b>κ</b> (kappa) measures how far below it a method gets: the work grows like n·(log n)<sup>1−κ</sup>, so a bigger κ is faster. <b>Conditional</b> means it holds only if an unreviewed, machine-written paper is right.',
      cap: 'Every reviewed record, from the AI-written paper’s 2⁻¹⁸² to today, on a halvings scale. All rest on that unreviewed paper.' },
    'machine-mathematics': { field: 'Mathematics', role: 'What came next', who: 'Members + crowd', acc: '--acc-mm', fact: 'families',
      glyph: 'families', hit: true, gk: 'THE 372 FAMILIES', gr: '', aria: '',
      cap: 'One square per family of OpenAI’s papers.',
      capHTML: '<span class="lg"><i class="sq" style="background:var(--acc-mm)"></i>links a Lean scope document by 7 Oct</span><span class="lg"><i class="sq" style="border:1px solid var(--ink-3)"></i>no such document</span><span class="lg"><i class="sq" style="border:1.5px solid var(--hair)"></i>founding members built on it</span><span class="gdef">Lean is a program that checks proofs step by step; a scope document is a plan for such a check, not a finished one.</span>' },
    'mobius-x1': { field: 'Circuits', role: 'Aska contributed', acc: '--acc-mobius', fact: 1, factK: 'failures in Aska’s full-network check',
      glyph: 'pascal', gk: 'PASCAL MOD 2 · N = 32', gr: 'row 31', aria: 'Pascal’s triangle modulo 2 for 32 inputs, the matrix the transform computes, beside the XOR counts of the naive method (211) and Yates’ method (80).',
      cap: 'The transform’s matrix, computed here. The claimed saving only appears when the input size has billions of digits.' },
    'gf2m-circuits': { field: 'Cryptography', role: 'Aska contributed', acc: '--acc-gf2m', fact: 0, factK: 'gates at depth 6, the 2010 record’s depth',
      glyph: 'gates', gk: 'GATES vs DEPTH', gr: '−5 at depth 6', aria: 'Gates against circuit depth: the 2010 record of 117 gates at depth 6, and the 2026 circuits of 112 gates at depth 6, 110 at 7, 108 at 12 and 107 at 13.',
      cap: 'Each new circuit is checked on all 65,536 input pairs and proved in Lean. Hollow mark: the 2010 record.' }
  };
  var PR_AUTHOR = {}; // PR number -> GitHub login, from kappa-history.json ("who") or the GitHub API
  var FAM = null; // families data + who built on what, for the glyph

  function famIndex(FD, MB, PJ) {
    if (!FD || !FD.families) return null;
    var built = {};
    function add(tag, who) { var m = /#(\d+)/.exec(tag || ''); if (!m) return; var id = ('00' + m[1]).slice(-3); (built[id] = built[id] || []); if (built[id].indexOf(who) < 0) built[id].push(who); }
    ((MB && MB.members) || []).forEach(function (m) { (m.work || []).forEach(function (w) { if (w.builds_on) add(w.builds_on, m.name); }); });
    ((PJ && PJ.projects) || []).forEach(function (p) { if (p.builds_on && !p.member) add(p.builds_on, p.owner + (p.contribution ? ', with Aska' : '')); });
    var memberIds = Object.keys(built).filter(function (id) { return built[id].some(function (w) { return ((MB && MB.members) || []).some(function (m) { return m.name === w; }); }); });
    var builders = [];
    ((MB && MB.members) || []).forEach(function (m) { if ((m.work || []).some(function (w) { return w.builds_on; })) builders.push(m.name); });
    return { fams: FD.families, sum: FD.summary || {}, built: built, memberIds: memberIds, builders: builders };
  }
  function andList(a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]; }
  function credit(p, M) {
    var mem = p.member && M[p.member], paren = /\(([^)]+)\)\s*$/.exec(p.owner || '');
    if (mem && /^Aska/.test(p.owner || '')) return '<b>Aska Digital’s own work</b>: founding member ' + esc(mem.name) + ' with a team of AI agents.';
    if (mem) return '<b>Founding member ' + esc(mem.name) + '’s project' + (paren ? ' (' + esc(paren[1]) + ')' : '') + '.</b> ' + esc(p.contribution || '');
    if (p.contribution) return '<b>' + esc(p.owner) + '’s repository.</b> ' + esc(p.contribution);
    if (p.slug === 'machine-mathematics' && FAM) return '<b>OpenAI published ' + (FAM.sum.manuscripts_day1 || 722) + ' machine-written papers</b> in ' + FAM.fams.length + ' families. Founding members ' + esc(andList(FAM.builders)) + ' then built on ' + FAM.memberIds.length + ' of those families, alongside many others.';
    return '<b>' + esc(p.owner || '') + '.</b>';
  }
  var KLABEL = 'κ, the saving below n log n: current reviewed record, conditional';
  function factHTML(p, c) {
    var K = F0.KAPPA_SNAPSHOT;
    if (c.fact === 'kappa') return '<div class="fact live-val" data-kappa><a class="chip" data-k-src href="' + esc(K.url) + '"><span class="dot stale" aria-hidden="true"></span><span data-k-when>snapshot · ' + esc(utc(K.at)) + '</span></a>' +
      '<span class="v" data-k-v>' + esc(K.decimal) + '</span><span class="k" data-k-k>' + KLABEL + (K.pr ? ' · PR #' + K.pr : '') + '</span></div>';
    if (c.fact === 'families' && FAM) return '<div class="fact"><span class="v">' + (FAM.sum.manuscripts_day1 || 722) + '</span><span class="k">machine-written papers in ' + FAM.fams.length + ' families on day one; ' +
      (FAM.sum.families_with_lean_doc_day1 || '') + ' families then linked a Lean scope document (' + (FAM.sum.families_with_lean_doc_oct7 || '') + ' by 7 Oct)</span></div>';
    var s = (p.stats || [])[c.fact]; if (!s) return '';
    return '<div class="fact" title="' + esc(s.label + ' · source: ' + s.source) + '"><span class="v">' + esc(s.value) + '</span><span class="k">' + esc(c.factK || s.label) + '</span></div>';
  }
  function famAria() {
    if (!FAM) return '';
    var lean = FAM.fams.filter(function (f) { return f.lean_doc_oct7; }).length;
    return FAM.fams.length + ' squares, one per family of OpenAI’s machine-written papers; ' + lean + ' linked a Lean scope document by 7 October. Founding members built on ' + FAM.memberIds.length + ': ' +
      FAM.memberIds.map(function (id) { var f = FAM.fams.filter(function (x) { return x.id === id; })[0]; return f ? F0.titleText(f.title) : id; }).join('; ') + '.';
  }
  function cardHTML(p, M) {
    var c = CARD[p.slug] || { field: p.kind === 'contribution' ? 'Contribution' : 'Research', role: p.kind === 'contribution' ? 'Aska contributed' : '', fact: 0 };
    var mem = p.member && M[p.member];
    var who = c.who || (mem ? mem.name + (p.contribution ? ' + Aska' : '') : (p.owner || '') + (p.contribution ? ' + Aska' : ''));
    var glyph = c.glyph ? '<div class="glyph' + (c.hit ? ' hit' : '') + '"><canvas data-glyph="' + c.glyph + '" role="img" aria-label="' + esc(c.glyph === 'families' ? famAria() : c.aria) + '"></canvas><div class="ghead"><span class="gk">' + esc(c.gk) + '</span><span class="gr" data-readout>' + esc(c.gr) + '</span></div></div><p class="gcap">' + esc(c.cap) + (c.capHTML ? ' ' + c.capHTML : '') + '</p>' : '';
    var links = (p.links || []).map(function (l) { return '<a href="' + esc(rel(l.url)) + '">' + esc(l.label) + '</a>'; }).join('');
    var head = '<p class="kick"><span>' + esc(c.field) + '</span><span>' + esc(who) + '</span></p>' +
      '<h3><a href="' + esc(rel(p.page)) + '">' + esc(p.title) + '</a></h3><p class="dek">' + esc(p.dek || '') + '</p>' + (c.gloss ? '<p class="gloss">' + c.gloss + '</p>' : '') +
      '<div class="badges">' + F0.statusBadges(p.status, { ladder: 1 }) + '</div><p class="credit">' + credit(p, M) + '</p>';
    var style = ' style="--acc:var(' + (c.acc || '--ink-3') + ')"';
    if (c.feature) return '<article class="card feature" data-slug="' + esc(p.slug) + '"' + style + '><div class="f-text">' + head + factHTML(p, c) + '<p class="links">' + links + '</p></div><div class="f-fig">' + glyph + '</div></article>';
    return '<article class="card" data-slug="' + esc(p.slug) + '"' + style + '>' + head + glyph + factHTML(p, c) + '<p class="links">' + links + '</p></article>';
  }
  function cards(PJ, MB, FD) {
    var host = $('#research-cards'); if (!host) return;
    var M = {}; ((MB && MB.members) || []).forEach(function (m) { M[m.login] = m; });
    FAM = famIndex(FD, MB, PJ);
    var list = (PJ.projects || []).filter(function (p) { return p.kind === 'research' || p.kind === 'contribution'; });
    list.sort(function (a, b) { return (CARD[b.slug] && CARD[b.slug].feature ? 1 : 0) - (CARD[a.slug] && CARD[a.slug].feature ? 1 : 0); });
    host.innerHTML = list.map(function (p) { return cardHTML(p, M); }).join('');
    var plain = $$('.card:not(.feature)', host), n = plain.length;
    host.classList.add('bal');
    if (n % 3 === 2) plain.slice(-2).forEach(function (c) { c.classList.add('tail2'); });
    if (n % 2 === 1) plain[n - 1].classList.add('tail1');
  }

  /* ---------- the live reviewed κ (F0.kappa: live file, else feed.json; the newer of that and our snapshot) ---------- */
  function liveKappa(MB) {
    var box = $('[data-kappa]'); if (!box || !F0.kappa) return;
    var logins = {}; ((MB && MB.members) || []).forEach(function (m) { logins[m.login.toLowerCase()] = m.name; });
    Promise.all([F0.kappa(), kappaSeries()]).then(function (r) {
      var use = r[0];
      if (!use || !/^0\.\d+$/.test(use.decimal)) return;
      var live = use.source === 'live';
      $('[data-k-when]', box).textContent = F0.kappaWhen(use, utc);
      var dot = $('.dot', box); dot.className = 'dot ' + (live ? 'live' : 'stale');
      box.querySelector('[data-k-src]').href = use.source === 'feed' ? R + 'feed.json' : (use.url || F0.KAPPA_URL);
      $('[data-k-v]', box).textContent = use.decimal;
      var kk = $('[data-k-k]', box);
      function who(login) { return login ? (logins[login.toLowerCase()] ? 'founding member ' + logins[login.toLowerCase()] : '@' + login) : ''; }
      function setK(login) { kk.textContent = KLABEL + (use.pr ? ' · PR #' + use.pr + (login ? ' by ' + who(login) : '') : ''); }
      setK(PR_AUTHOR[use.pr]);
      if (use.pr && !PR_AUTHOR[use.pr] && !F0.prerendering) fetch('https://api.github.com/repos/CrocSwap/integer-mult-bounds/pulls/' + use.pr).then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d && d.user && d.user.login) { PR_AUTHOR[use.pr] = d.user.login; setK(d.user.login); } }).catch(function () {});
      var v = parseFloat(use.decimal), lg = Math.log2(v), lastK = KAPPA[KAPPA.length - 1];
      if (lastK && v > 0 && lg > lastK[1] + 1e-9) { KAPPA.push([Math.max(Date.parse(use.at) || Date.now(), lastK[0] + 3600e3), lg]); if (GL.kappa) GL.kappa(); }
    }).catch(function (e) { console.warn('κ:', e); });
  }

  /* ---------- live research glyphs ---------- */
  /* reviewed κ records as [time, log2 κ], read from research/integer-multiplication/kappa-history.json (the file the
     integer-multiplication pages cite); the PR authors it names fill PR_AUTHOR */
  var KAPPA = [], kappaP = null;
  function kappaSeries() {
    if (!kappaP) kappaP = F0.kappaHistory().then(function (recs) {
      recs.forEach(function (r) {
        var lg = typeof r.log2 === 'number' ? r.log2 : Math.log2(parseFloat(r.decimal)), t = Date.parse(r.t);
        if (isFinite(lg) && isFinite(t)) KAPPA.push([t, lg]);
        var pr = /#(\d+)/.exec(r.what || ''); if (pr && r.who && /^[A-Za-z0-9-]+$/.test(r.who)) PR_AUTHOR[+pr[1]] = r.who;
      });
      KAPPA.sort(function (a, b) { return a[0] - b[0]; });
      if (GL.kappa) GL.kappa();
      return KAPPA;
    });
    return kappaP;
  }
  var GATES = { rec: [6, 117], pareto: [[6, 112], [7, 110], [12, 108], [13, 107]] }; // gf2m-circuits paper 1, Tables 1-3
  function foldDensity(s) { var t = 2 * s / (1 + s * s), a = Math.SQRT2 * (1 - s * s) / (1 + s * s), d = 2 + a; return 2 * Math.SQRT2 * Math.PI / (d * d * d + d * t * t + 2 * t * t * t); }
  function ring(x, cx, cy, r, fill, bg) { x.fillStyle = bg; x.beginPath(); x.arc(cx, cy, r + 2, 0, Math.PI * 2); x.fill(); x.fillStyle = fill; x.beginPath(); x.arc(cx, cy, r, 0, Math.PI * 2); x.fill(); }
  var GL = {}; // repaint hooks by glyph key

  var G = {
    incentre: { still: 0.5, draw: function (x, w, h, ph, out, st) {
      var acc = tk('--acc-incentre'), L0 = 12, R0 = w - 14, T = Math.max(34, st.top + 6), B = h - 24, y0 = 0.2233, y1 = 0.76;
      var X = function (s) { return L0 + (R0 - L0) * s; }, Y = function (v) { return B - (B - T) * (v - y0) / (y1 - y0); };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, Y(0.74048)); x.lineTo(R0, Y(0.74048)); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'left'; x.fillText('π/√18 · densest', L0, Y(0.74048) - 6);
      x.fillText('0.2233 · open scaffold', L0, h - 7);
      x.strokeStyle = acc; x.lineWidth = 2; x.lineJoin = x.lineCap = 'round'; x.beginPath();
      for (var i = 0; i <= 100; i++) { var s = i / 100; i ? x.lineTo(X(s), Y(foldDensity(s))) : x.moveTo(X(s), Y(foldDensity(s))); }
      x.stroke();
      var sNow = ph == null ? 1 : 0.5 - 0.5 * Math.cos(ph * Math.PI * 2);
      ring(x, X(sNow), Y(foldDensity(sNow)), 4, acc, tk('--bg-1'));
      out('ρ ' + foldDensity(sNow).toFixed(4));
    }, period: 7000 },
    transit: { still: 0.5, draw: function (x, w, h, ph, out, st) {
      var acc = tk('--acc-exoplanets'), sr = Math.max(4, Math.min(h * 0.3, 36, (h - st.top - 8) / 2)), sx = 18 + sr, sy = Math.max(h / 2 + 10, st.top + sr + 4);
      var g = x.createRadialGradient(sx, sy, 0, sx, sy, sr);
      g.addColorStop(0, acc); g.addColorStop(0.75, acc); g.addColorStop(1, tk('--bg-3'));
      x.fillStyle = g; x.beginPath(); x.arc(sx, sy, sr, 0, Math.PI * 2); x.fill();
      var p = ph == null ? 0.5 : ph, q = (p - 0.5) / 0.5;
      var half = 0.3, pr = sr * 0.16;
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
    kappa: { once: true, draw: function (x, w, h, ph, out, st) {
      if (!KAPPA.length) return;
      var acc = tk('--acc-intmult'), L0 = 12, R0 = w - 14, T = Math.max(30, st.top + 6), B = h - 14;
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
    pascal: { still: 31 / 32, draw: function (x, w, h, ph, out, st) {
      var acc = tk('--acc-mobius'), N = 32, size = Math.max(32, Math.min(h - st.top - 10, w * 0.5)), cell = size / N, ox = w - size - 14, oy = h - size - 8;
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
    gates: { once: true, draw: function (x, w, h, ph, out, st) {
      var acc = tk('--acc-gf2m'), L0 = 34, R0 = w - 14, T = Math.max(30, st.top + 8), B = h - 22;
      var X = function (d) { return L0 + (R0 - L0) * (d - 5) / 9; }, Y = function (g) { return B - (B - T) * (g - 105) / 14; };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B); x.lineTo(R0, B); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'center';
      [6, 9, 12].forEach(function (d) { x.fillText(d, X(d), B + 14); });
      x.textAlign = 'right'; x.fillText('DEPTH', R0, B + 14);
      x.textAlign = 'right'; [107, 112, 117].forEach(function (g) { x.fillText(g, L0 - 6, Y(g) + 4); });
      var prog = ph == null ? 1 : Math.min(1, ph);
      x.strokeStyle = tk('--ink-2'); x.lineWidth = 1.5; x.beginPath(); x.arc(X(6), Y(117), 4, 0, Math.PI * 2); x.stroke();
      x.fillStyle = tk('--ink-3'); x.textAlign = 'left'; x.fillText('2010', X(6) + 9, Y(117) + 4);
      var yA = Y(117) + 6, yB = Y(112) - 7, yE = yA + (yB - yA) * Math.min(1, prog * 2);
      x.strokeStyle = tk('--ink-3'); x.lineWidth = 1; x.beginPath(); x.moveTo(X(6), yA); x.lineTo(X(6), yE); x.stroke();
      if (prog > 0.5) { x.beginPath(); x.moveTo(X(6) - 3, yB - 4); x.lineTo(X(6), yB); x.lineTo(X(6) + 3, yB - 4); x.stroke(); }
      var pts = GATES.pareto, n = Math.max(1, Math.round(prog * pts.length));
      x.strokeStyle = acc; x.lineWidth = 2; x.beginPath();
      for (var i = 0; i < n; i++) { var p = pts[i]; if (!i) x.moveTo(X(p[0]), Y(p[1])); else { x.lineTo(X(p[0]), Y(pts[i - 1][1])); x.lineTo(X(p[0]), Y(p[1])); } }
      if (n === pts.length) x.lineTo(X(14), Y(pts[n - 1][1]));
      x.stroke();
      for (var k = 0; k < n; k++) ring(x, X(pts[k][0]), Y(pts[k][1]), 4, acc, tk('--bg-1'));
      out('−5 gates at depth 6');
    }, period: 1800 },
    /* OpenAI's 372 families as a waffle: filled = links a Lean scope document; red outline = members built on it.
       Playing reveals the families in the order they were first dated (23 Sep to 6 Oct 2026). */
    families: { once: true, draw: function (x, w, h, ph, out, st) {
      if (!FAM) return;
      var F = FAM.fams, N = F.length, T = Math.max(28, st.top + 4), B = h - 8, Hh = B - T, Ww = w - 24, best = null;
      for (var rows = 4; rows <= 16; rows++) { var cols = Math.ceil(N / rows), s = Math.min(Ww / cols, Hh / rows); if (!best || s > best.s) best = { rows: rows, cols: cols, s: s }; }
      var s = best.s, gap = Math.max(1, s * 0.2), ox = (w - best.cols * s) / 2 + gap / 2, oy = T + (Hh - best.rows * s) / 2 + gap / 2;
      if (!st.order) { st.order = {}; F.slice().sort(function (a, b) { return a.earliest_date < b.earliest_date ? -1 : a.earliest_date > b.earliest_date ? 1 : (a.id < b.id ? -1 : 1); }).forEach(function (f, i) { st.order[f.id] = i; }); }
      var shown = ph == null ? N : Math.floor(Math.min(1, ph) * N), acc = tk('--acc-mm'), hair = tk('--hair'), ink3 = tk('--ink-3');
      st.cells = [];
      F.forEach(function (f, i) {
        var c = i % best.cols, r = Math.floor(i / best.cols), cx = ox + c * s, cy = oy + r * s, sz = s - gap, on = st.order[f.id] < shown;
        st.cells.push([cx, cy, sz, f]);
        if (!on) return; // not yet dated (while playing)
        if (f.lean_doc_oct7) { x.fillStyle = acc; x.fillRect(cx, cy, sz, sz); }
        else { x.strokeStyle = ink3; x.lineWidth = 1; x.strokeRect(cx + 0.5, cy + 0.5, sz - 1, sz - 1); }
        if (FAM.memberIds.indexOf(f.id) >= 0) { x.strokeStyle = hair; x.lineWidth = 1.6; x.strokeRect(cx - 1.5, cy - 1.5, sz + 3, sz + 3); }
      });
      out(ph == null ? FAM.memberIds.length + ' built on by members' : 'to ' + (F.filter(function (f) { return st.order[f.id] === Math.max(0, shown - 1); })[0] || F[0]).earliest_date.slice(5).replace('-', '/') + ' · ' + shown);
    }, tip: function (st, px, py) {
      var hit = (st.cells || []).filter(function (c) { return px >= c[0] - 1 && px <= c[0] + c[2] + 1 && py >= c[1] - 1 && py <= c[1] + c[2] + 1; })[0];
      if (!hit) return null;
      var f = hit[3], who = FAM.built[f.id];
      var lean = f.lean_doc_day1 ? 'Linked a Lean scope document on day one' : f.lean_doc_oct7 ? 'Linked a Lean scope document by 7 Oct (not on day one)' : 'No Lean scope document by 7 Oct';
      return '<div class="tip-k">Family ' + esc(f.id) + ' · first dated ' + esc(F0.fmtDate(f.earliest_date)) + '</div><div class="tip-t">' + F0.titleHTML(f.title) + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span>' + f.n_manuscripts_day1 + ' manuscript' + (f.n_manuscripts_day1 > 1 ? 's' : '') + ' on day one</span></div>' +
        '<div class="tip-row"><span>' + lean + '</span></div></div>' +
        (who ? '<div class="tip-note"><span class="h"></span>Built on by ' + esc(andList(who)) + '</div>' : '');
    }, period: 3200 }
  };

  /* Card figures start on their informative still frame. With motion on:
     - pointer devices: when a figure first scrolls into view it plays once, quickly, and ends on that frame
       (F0.enter); pointing at or focusing its card runs it (loops start from the still frame, so nothing jumps);
     - touch screens (no hover): the card that is at least 60% in view runs its figure, one card at a time, and
       stops on the still frame when it scrolls away or after 60 s without input.
     Off-screen figures never run. */
  var touchOnly = !!(window.matchMedia && matchMedia('(hover: none)').matches), touchActive = null;
  function glyphs() {
    $$('canvas[data-glyph]').forEach(function (cv) {
      if (cv._f0) return; cv._f0 = true;
      var key = cv.getAttribute('data-glyph'), spec = G[key]; if (!spec) return;
      var c = F0.canvas(cv), box = cv.parentNode, card = cv.closest('.card') || box, ro = box.querySelector('[data-readout]'), head = box.querySelector('.ghead'), st = { top: 24 };
      var out = function (s) { if (ro && ro.textContent !== s) ro.textContent = s; };
      var t0 = 0, from = 0, hov = false, foc = false, inview = false, visible = false, ent = null;
      function paint(ph) {
        if (!c.ready) return; // not laid out yet: c.resize() repaints
        st.top = head ? head.offsetTop + head.offsetHeight : 24;
        var x = c.ctx; x.setTransform(c.dpr, 0, 0, c.dpr, 0, 0); x.clearRect(0, 0, c.w, c.h); spec.draw(x, c.w, c.h, ph, out, st);
      }
      function still() { paint(spec.once ? null : spec.still); }
      var loop = F0.loop(function (now) {
        if (!t0) t0 = now;
        var ph = (now - t0) / spec.period;
        if (spec.once) { if (ph >= 1) { paint(null); loop.stop(); return; } paint(ph); }
        else paint((from + ph) % 1);
      });
      var api = { release: function () { inview = false; sync(); } };
      function wanted() { return hov || foc || (touchOnly && inview && touchActive === api && !F0.idle()); }
      function sync() {
        if (wanted() && visible && F0.motion()) {
          if (ent && ent.running) ent.finish();
          if (!loop.running) { t0 = 0; from = spec.once ? 0 : spec.still; loop.start(); }
        } else { loop.stop(); if (!(ent && ent.running)) still(); }
      }
      function on(e) { if (e.type === 'focusin') foc = true; else hov = true; sync(); }
      function off(e) {
        if (e.type === 'focusout') { if (card.contains(e.relatedTarget)) return; foc = false; } else hov = false;
        sync();
      }
      if (!touchOnly) { card.addEventListener('pointerenter', on); card.addEventListener('pointerleave', off); }
      card.addEventListener('focusin', on); card.addEventListener('focusout', off);
      if (spec.tip) {
        cv.addEventListener('pointermove', function (e) { var b = cv.getBoundingClientRect(), html = spec.tip(st, e.clientX - b.left, e.clientY - b.top); if (html) F0.tip.show(html, e.clientX, e.clientY); else F0.tip.hide(); });
        cv.addEventListener('pointerleave', function () { F0.tip.hide(); });
      }
      still();
      GL[key] = function () { if (!loop.running && !(ent && ent.running)) still(); };
      c.resize(function () { if (!loop.running) still(); });
      F0.onTheme(function () { if (!loop.running) still(); });
      F0.whenVisible(box, function () { visible = true; sync(); }, function () { visible = false; sync(); });
      F0.onMotion(sync); F0.onIdle(sync);
      if (touchOnly && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            var now = e.intersectionRatio >= 0.6;
            if (now === inview) return;
            inview = now;
            if (now) { if (touchActive && touchActive !== api) touchActive.release(); touchActive = api; }
            else if (touchActive === api) touchActive = null;
            sync();
          });
        }, { threshold: [0, 0.6, 1] }).observe(box);
      } else if (F0.enter) {
        ent = F0.enter(box, function (t) { if (loop.running) return; if (t >= 1) still(); else paint(spec.once ? t : t * spec.still); }, { duration: 1200, threshold: 0.6 });
      }
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!loop.running) still(); });
    });
  }

  /* ---------- 04: the Exo mark, Project Exo's living lattice egg (instruments/egg.js: lattice egg renderer from
     Project Exo, (c) 2026 Aska Digital, MIT). Drawn still; it moves only while the card is pointed at or focused,
     with motion on, on screen and not idle (README section 5). The vault-door SVG stays as the no-JavaScript picture. ---------- */
  function homeEgg() {
    var cv = $('#home-egg'); if (!cv || !window.ExoEgg || F0.prerendering) return;
    var card = cv.closest('.vault'), door = card && card.querySelector('svg.vault-door');
    function rgbOf(col) {
      var m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(String(col).trim());
      if (m) { var hx = m[1].length === 3 ? m[1].replace(/(.)/g, '$1$1') : m[1]; return [parseInt(hx.slice(0, 2), 16), parseInt(hx.slice(2, 4), 16), parseInt(hx.slice(4, 6), 16)]; }
      var n = String(col).match(/[\d.]+/g); return n && n.length >= 3 ? [+n[0], +n[1], +n[2]] : [128, 128, 128];
    }
    function colors() {
      var dark = F0.theme() === 'dark', acc = rgbOf(F0.css('--acc-exo') || '#b23a06');
      var acc2 = acc.map(function (v) { return Math.round(v + (255 - v) * (dark ? 0.3 : 0.12)); });
      return { acc: acc.join(','), acc2: acc2.join(','), fg: rgbOf(F0.css('--ink')).join(','), cold: rgbOf(F0.css('--dig')).join(','), blend: dark ? 'lighter' : 'source-over', glowA: dark ? 1 : 0.45 };
    }
    cv.hidden = false; if (door) door.setAttribute('hidden', '');   /* an SVG element has no .hidden property */
    var egg = ExoEgg.mount(cv, { stage: 2, activity: 0.45, seed: 7, auto: false, reducedMotion: true, colors: colors(),
      layout: function (w, h) { return { cx: w / 2, cy: h / 2, r: Math.min(w, h) * 0.52 }; } });   /* fill the small card frame */
    var hov = false, foc = false, visible = false, last = 0;
    var loop = F0.loop(function (now) { var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.033; last = now; egg.draw(dt); });
    function sync() {
      if ((hov || foc) && visible && F0.motion() && !F0.idle()) { if (!loop.running) { egg.reduce = false; last = 0; loop.start(); } }
      else if (loop.running) { loop.stop(); egg.reduce = true; egg.still(7); }
    }
    card.addEventListener('pointerenter', function () { hov = true; sync(); });
    card.addEventListener('pointerleave', function () { hov = false; sync(); });
    card.addEventListener('focusin', function () { foc = true; sync(); });
    card.addEventListener('focusout', function (e) { if (card.contains(e.relatedTarget)) return; foc = false; sync(); });
    F0.whenVisible(card, function () { visible = true; sync(); }, function () { visible = false; sync(); });
    F0.onMotion(sync); F0.onIdle(sync);
    F0.onTheme(function () { egg.setColors(colors()); if (!loop.running) egg.still(7); });
    if ('ResizeObserver' in window) { var lw = 0; new ResizeObserver(function () { var w = cv.getBoundingClientRect().width; if (w < 2 || w === lw) return; lw = w; egg.resize(); if (!loop.running) egg.still(7); }).observe(cv); }
  }

  /* ---------- instruments and commons: numbers from data/projects.json ---------- */
  function bindProjects(PJ) {
    var by = {}; (PJ.projects || []).forEach(function (p) { by[p.slug] = p; });
    $$('[data-stat-v]').forEach(function (e) {
      var a = e.getAttribute('data-stat-v').split(':'), p = by[a[0]], s = p && p.stats && p.stats[+a[1]];
      if (!s) return;
      e.textContent = e.hasAttribute('data-words') && /^\d+$/.test(s.value) ? (+s.value === 0 ? 'none' : s.value) : s.value;
      e.title = s.label + ' · source: ' + s.source;
    });
    $$('[data-stat-k]').forEach(function (e) { var a = e.getAttribute('data-stat-k').split(':'), p = by[a[0]], s = p && p.stats && p.stats[+a[1]]; if (s) e.textContent = s.label; });
    $$('[data-proj]').forEach(function (e) { var a = e.getAttribute('data-proj').split(':'), p = by[a[0]]; if (p && p[a[1]]) e.textContent = p[a[1]]; });
  }

  /* ---------- Commons glyphs: SVG drawn at the box's real width so text stays 11px ---------- */
  function sized(host, build) {
    var lw = 0;
    function go() { var w = Math.round(host.getBoundingClientRect().width); if (!w || w === lw) return; lw = w; host.innerHTML = ''; build(w); }
    go(); if ('ResizeObserver' in window) new ResizeObserver(go).observe(host);
  }
  function nutrak() {
    var host = $('#nutrak-host'); if (!host) return;
    var mg = [549, 944, 728, 1070, 685, 710, 754], days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'], mean = 777.1; // Nutrak demo fixture (demo/fixture.json), 2026-08-24..30
    sized(host, function (W) {
      var H = 132, L0 = 74, R0 = W - (W < 420 ? 96 : 120), T = 26, B = H - 26;
      var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'gsvg', role: 'img', 'aria-label': 'Calcium in the Nutrak demo week: 549, 944, 728, 1070, 685, 710 and 754 milligrams a day, against the RDA of 1,000 and the EAR of 800. Judged day by day, Nutrak’s light would change five times; the 7-day average, 777 milligrams, gives one steady signal.' }, host);
      var Y = function (v) { return B - (B - T) * (v - 500) / 620; }, X = function (i) { return L0 + 8 + (R0 - L0 - 16) * i / 6; };
      el('text', { x: 0, y: 11, text: 'CALCIUM, MG A DAY · DEMO WEEK', style: 'fill:var(--ink-3)' }, svg);
      [[1000, 'RDA 1,000'], [800, 'EAR 800']].forEach(function (r) {
        el('line', { x1: L0, x2: R0, y1: Y(r[0]), y2: Y(r[0]), style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, svg);
        el('text', { x: L0 - 8, y: Y(r[0]) + 4, 'text-anchor': 'end', text: r[1] }, svg);
      });
      mg.forEach(function (v, i) { el('line', { x1: X(i), x2: X(i), y1: Y(mean), y2: Y(v), style: 'stroke:var(--ink-3)', 'stroke-width': 1, opacity: 0.7 }, svg); });
      el('line', { x1: L0, x2: R0, y1: Y(mean), y2: Y(mean), style: 'stroke:var(--acc-nutrak)', 'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
      mg.forEach(function (v, i) {
        el('circle', { cx: X(i), cy: Y(v), r: 6, style: 'fill:var(--bg-1)' }, svg);
        el('circle', { cx: X(i), cy: Y(v), r: 4, style: 'fill:var(--ink-2)' }, svg);
        el('text', { x: X(i), y: H - 6, 'text-anchor': 'middle', text: days[i], style: 'fill:var(--ink-3)' }, svg);
      });
      el('text', { x: R0 + 10, y: Y(mean) + 4, text: 'week: 777 mg', style: 'fill:var(--ink)' }, svg);
      el('text', { x: R0 + 10, y: Y(mean) + 19, text: 'one verdict', style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: R0 + 10, y: Y(1070) + 4, text: 'by the day:', style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: R0 + 10, y: Y(1070) + 19, text: '5 changes', style: 'fill:var(--ink-3)' }, svg);
    });
  }
  function medcode(PJ) {
    var host = $('#medcode-host'); if (!host) return;
    var parts = [[18, 'verified', '--st-verified', 1], [33, 'unverified', '--st-claimed', 0.55], [16, 'vendor claim only', '--st-preprint', 0.8]], tot = 67; // medcode vendor table, snapshot 2026-10-03
    var p = PJ && (PJ.projects || []).filter(function (q) { return q.slug === 'medcode'; })[0], s = p && p.stats && p.stats[3];
    var a = s && /(\d+)\s+of\s+(\d+)/.exec(s.value), b = s && /(\d+)\s+unverified,\s*(\d+)\s+vendor/.exec(s.label);
    if (a && b) { parts[0][0] = +a[1]; tot = +a[2]; parts[1][0] = +b[1]; parts[2][0] = +b[2]; }
    var lg = $('#medcode-legend'); if (lg) $$('b', lg).forEach(function (e, i) { if (parts[i]) e.textContent = parts[i][0]; });
    sized(host, function (W) {
      var H = 44, svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'gsvg', role: 'img', 'aria-label': 'Evidence behind the vendor table: ' + parts[0][0] + ' of ' + tot + ' tags verified, ' + parts[1][0] + ' unverified, ' + parts[2][0] + ' vendor claims only.' }, host);
      el('text', { x: 0, y: 11, text: tot + ' EVIDENCE TAGS IN THE VENDOR TABLE', style: 'fill:var(--ink-3)' }, svg);
      var x = 0;
      parts.forEach(function (q, i) {
        var w = W * q[0] / tot - (i < parts.length - 1 ? 2 : 0);
        el('rect', { x: x, y: 22, width: Math.max(1, w), height: 16, style: 'fill:var(' + q[2] + ')', opacity: q[3] }, svg);
        x += w + 2;
      });
    });
  }

  /* ---------- 06: writing, from data/writing.json (latest four, dated market notes left to the Writing page) ---------- */
  function posts(W) {
    var host = $('#posts-list'); if (!host) return;
    var list = (W.posts || []).filter(function (p) { return (p.themes || []).indexOf('markets') < 0; })
      .sort(function (a, b) { return a.date < b.date ? 1 : -1; }).slice(0, 4);
    if (!list.length) return;
    host.innerHTML = list.map(function (p) {
      return '<li class="post"><time datetime="' + esc(p.date) + '">' + esc(p.date) + '</time><div><h3><a href="' + esc(p.url) + '">' + esc(p.title) + '</a></h3><p>' + esc(firstSentence(p.summary)) + '</p></div><span class="cat">' + esc(String(p.category || '').replace(/\s*\/\s*/g, ' · ')) + '</span></li>';
    }).join('');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
