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
     HERO: two tools, eight promises
     ====================================================================== */
  function initPromises() {
    var fig = $('.pm'), btn = $('#pm-gaps'); if (!fig || !btn) return;
    var cells = $$('#pm-tbl tbody td'), full = cells.filter(function (c) { return c.getAttribute('data-s') === 'yes'; }).length;
    var gaps = $$('#pm-tbl tbody tr[data-gap="1"]').length;
    function upd(on) {
      fig.classList.toggle('gaps', on); btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      btn.textContent = on ? 'Show all eight' : 'Show only the gaps';
      $('#pm-count').textContent = on ? gaps + ' promises with a gap' : '8 promises · ' + full + ' of ' + cells.length + ' kept in full';
    }
    btn.addEventListener('click', function () { upd(!fig.classList.contains('gaps')); });
    upd(false);
  }

  /* ======================================================================
     02: A DIAGNOSIS IS A COMPRESSED SENTENCE
     All codes and descriptions: CMS, 2027 ICD-10-CM code descriptions (checked against the file).
     ====================================================================== */
  var VISIT = {
    A: ['Visit', 'A = initial encounter: the patient is still getting active treatment'],
    D: ['Visit', 'D = subsequent encounter: routine care while the injury heals'],
    S: ['Visit', 'S = sequela: a later condition caused by the injury']
  };
  var PH = ['Placeholder', 'X holds a place: this code has no sixth level of detail, but the visit letter must sit in position 7'];
  var CODES = {
    e119: { name: 'Type 2 diabetes mellitus without complications', parts: [
      ['E', 'Chapter', 'Chapter 4: endocrine, nutritional and metabolic diseases'],
      ['11', 'Category', 'E11: type 2 diabetes mellitus'],
      ['.', 'dot'],
      ['9', 'Detail', 'E11.9: without complications']],
      near: [['E11.65', 'with hyperglycemia (high blood sugar)'], ['E11.649', 'with hypoglycemia (low blood sugar) without coma'], ['E11.621', 'with foot ulcer']] },
    i10: { name: 'Essential (primary) hypertension', parts: [
      ['I', 'Chapter', 'Chapter 9: diseases of the circulatory system'],
      ['10', 'Category', 'I10: high blood pressure with no other known cause. Three characters can be a complete code.']],
      near: [['I11.9', 'Hypertensive heart disease without heart failure'], ['I15.9', 'Secondary hypertension, unspecified'], ['I16.0', 'Hypertensive urgency']] },
    duck: { name: 'Struck by duck, initial encounter', parts: [
      ['W', 'Chapter', 'Chapter 20: external causes of injury (V to Y); W covers falls, objects and animals'],
      ['61', 'Category', 'W61: contact with birds (domestic) (wild)'],
      ['.', 'dot'],
      ['6', 'Detail', 'W61.6: contact with duck'],
      ['2', 'Detail', 'W61.62: struck by duck (1 would be bitten, 9 other contact)'],
      ['X', 'Placeholder', PH[1]],
      ['A', 'Visit', VISIT.A[1]]],
      near: [['W61.61XA', 'Bitten by duck, initial encounter'], ['W61.69XA', 'Other contact with duck, initial encounter'], ['W61.62XD', 'Struck by duck, subsequent encounter']] },
    jet: { name: 'Sucked into jet engine, subsequent encounter', parts: [
      ['V', 'Chapter', 'Chapter 20: external causes of injury; V covers transport accidents'],
      ['97', 'Category', 'V97: other specified air transport accidents'],
      ['.', 'dot'],
      ['3', 'Detail', 'V97.3: person on ground injured in air transport accident'],
      ['3', 'Detail', 'V97.33: sucked into jet engine'],
      ['X', 'Placeholder', PH[1]],
      ['D', 'Visit', VISIT.D[1]]],
      near: [['V97.33XA', 'Sucked into jet engine, initial encounter'], ['V97.33XS', 'Sucked into jet engine, sequela']] },
    lamp: { name: 'Walked into lamppost, initial encounter', parts: [
      ['W', 'Chapter', 'Chapter 20: external causes of injury; W covers falls, objects and animals'],
      ['22', 'Category', 'W22: striking against or struck by other objects'],
      ['.', 'dot'],
      ['0', 'Detail', 'W22.0: striking against stationary object'],
      ['2', 'Detail', 'W22.02: walked into lamppost'],
      ['X', 'Placeholder', PH[1]],
      ['A', 'Visit', VISIT.A[1]]],
      near: [['W22.01XA', 'Walked into wall, initial encounter'], ['W22.03XA', 'Walked into furniture, initial encounter'], ['W22.09XA', 'Striking against other stationary object, initial encounter']] }
  };
  var SIDE = { '1': 'right', '2': 'left', '9': 'unspecified' }, VISITW = { A: 'initial encounter', D: 'subsequent encounter', S: 'sequela' };
  function ankle(side, visit) {
    return { name: 'Sprain of unspecified ligament of ' + SIDE[side] + ' ankle, ' + VISITW[visit], parts: [
      ['S', 'Chapter', 'Chapter 19: injury, poisoning and other consequences of external causes; S covers injuries by body region'],
      ['93', 'Category', 'S93: dislocation and sprain of joints and ligaments at ankle, foot and toe level'],
      ['.', 'dot'],
      ['4', 'Detail', 'S93.4: sprain of ankle'],
      ['0', 'Detail', 'S93.40: unspecified ligament (the notes do not say which one)'],
      [side, 'Side', 'S93.40' + side + ': ' + SIDE[side] + ' ankle (1 right, 2 left, 9 unspecified)'],
      [visit, 'Visit', VISIT[visit][1]]] };
  }
  function codeStr(parts) { return parts.map(function (p) { return p[0]; }).join(''); }
  function initAnatomy() {
    var box = $('#ca-code'); if (!box) return;
    var cur = 'ankle', side = '1', visit = 'A';
    function data() { return cur === 'ankle' ? ankle(side, visit) : CODES[cur]; }
    function render() {
      var d = data(), code = codeStr(d.parts);
      // characters, grouped under their role
      box.innerHTML = '';
      var list = $('#ca-list'); list.innerHTML = '';
      var groups = [];
      d.parts.forEach(function (p, i) {
        if (p[1] === 'dot') { groups.push({ label: '', parts: [[p, i]] }); return; }
        var g = groups[groups.length - 1];
        if (g && g.label === p[1] && p[1] === 'Detail') g.parts.push([p, i]); else groups.push({ label: p[1], parts: [[p, i]] });
      });
      var idx = 0;
      groups.forEach(function (g) {
        var gEl = h('span', { cls: 'ca-grp' + (g.label ? '' : ' dotg') }, box);
        var short = { Chapter: 'Chap', Category: 'Category', Detail: 'Detail', Placeholder: 'X', Side: 'Side', Visit: 'Visit' }[g.label] || '\u00a0';
        h('span', { cls: 'ca-gl', 'aria-hidden': 'true' }, gEl, '<span class="lf">' + esc(g.label || '\u00a0') + '</span><span class="ls">' + esc(short) + '</span>');
        var cs = h('span', { cls: 'ca-chars' }, gEl);
        g.parts.forEach(function (pi) {
          var p = pi[0], i = pi[1];
          p[0].split('').forEach(function (ch) {
            var isDot = p[1] === 'dot';
            var b = h(isDot ? 'span' : 'button', { cls: 'ca-ch' + (isDot ? ' dot' : '') + (p[1] === 'Placeholder' ? ' ph' : ''), 'data-i': i, text: ch }, cs);
            if (!isDot) { b.setAttribute('type', 'button'); b.setAttribute('aria-label', ch + ': ' + p[1].toLowerCase() + '. ' + p[2]); }
            else b.setAttribute('aria-hidden', 'true');
            idx++;
          });
        });
      });
      d.parts.forEach(function (p, i) {
        if (p[1] === 'dot') return;
        h('li', { 'data-i': i }, list, '<span class="c">' + esc(p[0]) + '</span><span><span class="t">' + esc(p[1]) + '</span>' + esc(p[2]) + '</span>');
      });
      $('#ca-desc').innerHTML = '<span class="lbl">' + esc(code) + ' &middot; official description</span>' + esc(d.name);
      // light a character's line
      function light(i) {
        $$('.ca-ch', box).forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-i') === String(i)); });
        $$('li', list).forEach(function (l) { l.classList.toggle('on', l.getAttribute('data-i') === String(i)); });
      }
      $$('.ca-ch', box).forEach(function (c) {
        if (c.classList.contains('dot')) return;
        var i = c.getAttribute('data-i');
        c.addEventListener('pointerenter', function () { light(i); });
        c.addEventListener('focus', function () { light(i); });
        c.addEventListener('click', function () { light(i); });
      });
      $$('li', list).forEach(function (l) { l.addEventListener('pointerenter', function () { light(l.getAttribute('data-i')); }); });
      box.addEventListener('pointerleave', function () { light(-1); });
      side_();
    }
    function side_() {
      var sb = $('#ca-side'), build = $('.ca-build', sb), grid = $('#ca-grid'), near = $('.ca-near', sb);
      if (cur === 'ankle') {
        build.hidden = false; grid.hidden = false; if (near) near.remove();
        var tb = grid.querySelector('tbody'); tb.innerHTML = '';
        ['1', '2', '9'].forEach(function (s) {
          var tr = h('tr', null, tb);
          h('th', { scope: 'row' }, tr, s === '9' ? '<span class="lf">unspecified</span><span class="ls" title="unspecified">unsp.</span>' : SIDE[s]);
          ['A', 'D', 'S'].forEach(function (v) {
            var td = h('td', null, tr), on = s === side && v === visit;
            var b = h('button', { type: 'button', 'aria-pressed': on ? 'true' : 'false', 'aria-label': 'S93.40' + s + v + ': ' + SIDE[s] + ' ankle, ' + VISITW[v] }, td, 'S93.40<b>' + s + v + '</b>');
            b.addEventListener('click', function () { side = s; visit = v; syncSegs(); render(); var nb = grid.querySelector('[aria-pressed="true"]'); if (nb) nb.focus(); });
          });
        });
      } else {
        build.hidden = true; grid.hidden = true;
        if (!near) near = h('div', { cls: 'ca-near' }, sb);
        var code = codeStr(CODES[cur].parts);
        near.innerHTML = '<p class="label">Change a character, change the sentence</p><ul>' + CODES[cur].near.map(function (n) {
          var a = n[0].replace('.', ''), b = code.replace('.', ''), out = '', j = 0;
          for (var i = 0; i < n[0].length; i++) { var ch = n[0][i]; if (ch === '.') { out += '.'; continue; } out += (a[j] !== b[j] ? '<mark>' + ch + '</mark>' : ch); j++; }
          return '<li><code>' + out + '</code>' + esc(n[1]) + '</li>';
        }).join('') + '</ul>';
      }
    }
    function syncSegs() {
      $$('#ca-sideseg button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v') === side ? 'true' : 'false'); });
      $$('#ca-visitseg button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v') === visit ? 'true' : 'false'); });
    }
    $$('#ca-codes button').forEach(function (b) { b.addEventListener('click', function () { cur = b.getAttribute('data-c'); segPress($('#ca-codes'), b); render(); }); });
    arrows($('#ca-codes'), 'button', function (b) { b.click(); });
    $$('#ca-sideseg button').forEach(function (b) { b.addEventListener('click', function () { side = b.getAttribute('data-v'); syncSegs(); render(); }); });
    $$('#ca-visitseg button').forEach(function (b) { b.addEventListener('click', function () { visit = b.getAttribute('data-v'); syncSegs(); render(); }); });
    render();
  }

  /* codes by first letter, FY2027 (counted from CMS icd10cm_codes_2027.txt: 74,879 codes) */
  var LETTERS = [['A', 573, 'Infections'], ['B', 495, 'Infections'], ['C', 1229, 'Cancers'], ['D', 825, 'Other tumours; blood and immune system'], ['E', 973, 'Hormones, nutrition and metabolism'], ['F', 872, 'Mental and behavioural'], ['G', 700, 'Nervous system'], ['H', 3330, 'Eye and ear'], ['I', 1433, 'Heart and circulation'], ['J', 366, 'Breathing'], ['K', 863, 'Digestion'], ['L', 1001, 'Skin'], ['M', 6687, 'Muscles, bones and joints'], ['N', 838, 'Kidney, urinary and reproductive'], ['O', 2481, 'Pregnancy and childbirth'], ['P', 463, 'Newborns'], ['Q', 900, 'Present from birth'], ['R', 774, 'Symptoms and abnormal findings'], ['S', 31049, 'Injuries, by body region'], ['T', 10138, 'Injuries, poisoning, burns, complications of care'], ['U', 3, 'Special purposes'], ['V', 4086, 'Transport accidents'], ['W', 1290, 'Falls, objects, animals'], ['X', 495, 'Fire, nature, self-harm, assault'], ['Y', 1590, 'Assault, care complications, places and activities'], ['Z', 1425, 'Reasons for contact with health services']];
  var LTOTAL = 74879;
  function initLetters() {
    var host = $('#ca2-stage'); if (!host) return;
    var tb = $('#ca2-table tbody');
    LETTERS.forEach(function (l) { h('tr', null, tb, '<th scope="row">' + l[0] + '</th><td>' + esc(l[2]) + '</td><td class="n">' + fmt(l[1]) + '</td><td class="n">' + (100 * l[1] / LTOTAL).toFixed(1) + '%</td>'); });
    h('tr', null, tb, '<th scope="row">All</th><td></td><td class="n">' + fmt(LTOTAL) + '</td><td class="n">100%</td>');
    var svg = null;
    function draw(W) {
      if (svg) svg.remove();
      var H = W < 560 ? 220 : 260, padL = 40, padR = 8, padT = 22, padB = 24, ymax = 32000;
      var bw = (W - padL - padR) / LETTERS.length, barW = Math.min(24, bw - 2);
      var Y = function (v) { return padT + (1 - v / ymax) * (H - padT - padB); };
      svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': 'Column chart of 74,879 diagnosis codes by first letter. S has 31,049 and T has 10,138, together 55%. M has 6,687, V 4,086, H 3,330; every other letter has under 2,500.' }, host);
      [0, 10000, 20000, 30000].forEach(function (v) {
        el('line', { x1: padL, x2: W - padR, y1: Y(v), y2: Y(v), style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
        el('text', { x: padL - 6, y: Y(v) + 4, 'text-anchor': 'end', text: v ? (v / 1000) + 'K' : '0', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      });
      LETTERS.forEach(function (l, i) {
        var x = padL + i * bw + (bw - barW) / 2, inj = l[0] === 'S' || l[0] === 'T', y = Y(l[1]), bh = Math.max(1, Y(0) - y);
        var g = el('g', { class: 'bar' }, svg);
        el('rect', { x: padL + i * bw, y: padT, width: bw, height: H - padT - padB, fill: 'transparent' }, g); // hit area
        var r = Math.min(4, bh / 2, barW / 2);
        el('path', { d: 'M' + x + ' ' + Y(0) + 'V' + (y + r) + 'Q' + x + ' ' + y + ' ' + (x + r) + ' ' + y + 'H' + (x + barW - r) + 'Q' + (x + barW) + ' ' + y + ' ' + (x + barW) + ' ' + (y + r) + 'V' + Y(0) + 'Z', style: 'fill:' + (inj ? 'var(--acc-medcode)' : 'var(--line-ui)') }, g);
        el('text', { x: x + barW / 2, y: H - 8, 'text-anchor': 'middle', text: l[0], 'font-size': 11, 'font-weight': inj ? 700 : 400, style: 'fill:' + (inj ? 'var(--ink)' : 'var(--ink-3)') }, svg);
        if (inj) el('text', { x: l[0] === 'S' ? x - 4 : x + barW + 4, y: Math.max(14, y + (l[0] === 'S' ? 10 : -6)), 'text-anchor': l[0] === 'S' ? 'end' : 'start', text: fmt(l[1]), 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink)' }, svg);
        g.addEventListener('pointermove', function (e) { tipShow('<div class="tip-k">Letter ' + l[0] + '</div><div class="tip-t">' + esc(l[2]) + '</div><div class="tip-rows"><div class="tip-row"><span class="tip-v">' + fmt(l[1]) + '</span> codes &middot; ' + (100 * l[1] / LTOTAL).toFixed(1) + '%</div></div>', e.clientX, e.clientY); });
        g.addEventListener('pointerleave', tipHide);
      });
    }
    var re = sized(host, draw);
    onTheme(re);
  }

  /* ======================================================================
     03: WHO CHECKED THE CLAIM?  Counted from the public vendor table (snapshot 3 Oct 2026);
     names removed. v = verified, u = unverified, c = vendor claim, in the table's own order.
     ====================================================================== */
  var MODES = [
    ['auto', 'Autonomous', 'Codes without a person in the loop', ['vcv', 'uvuv', 'vuvu', 'uvu', 'uccv', 'cu', 'cccv']],
    ['assist', 'Assistive', 'Suggests codes for a person to check', ['uv', 'ucuv', 'uc', 'uuu', 'uu', 'uu', 'uucv', 'uc']],
    ['services', 'Services', 'People plus software, sold as a service', ['cu', 'ucuv', 'uccv']],
    ['scribe', 'Scribe', 'Writes the notes, suggests codes', ['v', 'uu', 'ucv', 'vu']],
    ['platform', 'Platform', 'Billing platforms, or both kinds', ['uu', 'vu', '']]
  ];
  function initEvidence() {
    var rows = $('#ev-rows'); if (!rows) return;
    var fig = $('.ev'), mode = 'all', n = 0, all = [];
    MODES.forEach(function (m) {
      m[3].map(function (tags) { return { mode: m[0], tags: tags, v: (tags.match(/v/g) || []).length, u: (tags.match(/u/g) || []).length, c: (tags.match(/c/g) || []).length }; })
        .sort(function (a, b) { return b.v - a.v || b.tags.length - a.tags.length; })
        .forEach(function (x) { n++; x.id = 'Vendor ' + (n < 10 ? '0' : '') + n; all.push(x); });
    });
    function shape(t) {
      var s = '<svg viewBox="0 0 18 18" class="' + t + '" aria-hidden="true">';
      if (t === 'v') s += '<circle cx="9" cy="9" r="6.5" style="fill:var(--nk-good)"/>';
      else if (t === 'u') s += '<circle cx="9" cy="9" r="6" fill="none" style="stroke:var(--ink-3)" stroke-width="1.6" stroke-dasharray="3 2.4"/>';
      else s += '<path d="M9 2.2L15.8 9L9 15.8L2.2 9Z" style="fill:var(--nk-near)"/>';
      return s + '</svg>';
    }
    // legend
    $('#ev-legend').innerHTML = '<li>' + shape('v') + '<span><b>Verified</b> against a named source</span></li><li>' + shape('u') + '<span><b>Unverified</b>: could not be corroborated</span></li><li>' + shape('c') + '<span><b>Vendor claim</b> only</span></li>';
    // rows, grouped by kind; within a group, most verified first
    MODES.forEach(function (m) {
      var vs = all.filter(function (x) { return x.mode === m[0]; });
      var g = h('section', { cls: 'ev-grp', 'data-mode': m[0], 'aria-label': m[1] + ' vendors' }, rows);
      var tv = vs.reduce(function (s, x) { return s + x.v; }, 0), tt = vs.reduce(function (s, x) { return s + x.v + x.u + x.c; }, 0);
      h('h3', null, g, esc(m[1]) + ' <span>' + vs.length + ' vendors &middot; ' + tv + ' of ' + tt + ' verified</span>');
      vs.forEach(function (x) {
        var label = x.id + ', ' + m[1].toLowerCase() + ': ' + x.v + ' verified, ' + x.u + ' unverified, ' + x.c + ' vendor claim' + (x.c === 1 ? '' : 's');
        var r = h('div', { cls: 'ev-row', tabindex: '0', role: 'group', 'aria-label': label }, g);
        h('span', { cls: 'ev-name', text: x.id }, r);
        var d = h('span', { cls: 'ev-dots', 'aria-hidden': 'true' }, r, x.tags ? x.tags.split('').map(shape).join('') : '<span class="none">no figure tagged</span>');
        h('span', { cls: 'ev-n', 'aria-hidden': 'true', text: x.v + ' / ' + x.tags.length }, r);
        function tip(e) { var rc = r.getBoundingClientRect(); tipShow('<div class="tip-k">' + esc(m[1]) + ' &middot; ' + esc(m[2]) + '</div><div class="tip-t">' + esc(x.id) + '</div><div class="tip-rows"><div class="tip-row"><span class="tip-v">' + x.v + '</span> verified</div><div class="tip-row"><span class="tip-v">' + x.u + '</span> unverified</div><div class="tip-row"><span class="tip-v">' + x.c + '</span> vendor claim</div></div>', e && e.clientX != null ? e.clientX : rc.right - 40, e && e.clientY != null ? e.clientY : rc.top); }
        r.addEventListener('pointermove', tip); r.addEventListener('pointerleave', tipHide);
        r.addEventListener('focus', function () { tip(null); }); r.addEventListener('blur', tipHide);
      });
    });
    // twin table
    var tb = $('#ev-table tbody');
    MODES.forEach(function (m) { all.filter(function (x) { return x.mode === m[0]; }).forEach(function (x) { h('tr', null, tb, '<th scope="row">' + x.id + '</th><td>' + esc(m[1]) + '</td><td class="n">' + x.v + '</td><td class="n">' + x.u + '</td><td class="n">' + x.c + '</td>'); }); });
    var sum = all.reduce(function (s, x) { s.v += x.v; s.u += x.u; s.c += x.c; return s; }, { v: 0, u: 0, c: 0 });
    h('tr', null, tb, '<th scope="row">All 25</th><td></td><td class="n">' + sum.v + '</td><td class="n">' + sum.u + '</td><td class="n">' + sum.c + '</td>');
    var barHost = $('#ev-bar'), barSvg = null;
    function drawBar(W) {
      var set = all.filter(function (x) { return mode === 'all' || x.mode === mode; });
      var s = set.reduce(function (a, x) { a.v += x.v; a.u += x.u; a.c += x.c; return a; }, { v: 0, u: 0, c: 0 }), tot = s.v + s.u + s.c;
      if (barSvg) barSvg.remove();
      var H = 64;
      barSvg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'aria-hidden': 'true' }, barHost);
      el('text', { x: 0, y: 12, text: (mode === 'all' ? 'ALL ' : MODES.filter(function (m) { return m[0] === mode; })[0][1].toUpperCase() + ': ') + tot + ' TAGGED FIGURES', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.06em' }, barSvg);
      var x = 0, parts = [['v', s.v, 'var(--nk-good)', 'verified'], ['u', s.u, 'transparent', 'unverified'], ['c', s.c, 'var(--nk-near)', 'claim']];
      parts.forEach(function (p, i) {
        if (!p[1]) return;
        var w = (W) * p[1] / tot - (i < 2 ? 2 : 0);
        el('rect', { x: x + 0.5, y: 20.5, width: Math.max(1, w - 1), height: 17, style: 'fill:' + p[2] + ';stroke:' + (p[0] === 'u' ? 'var(--ink-3)' : 'none'), 'stroke-dasharray': p[0] === 'u' ? '3 2' : null }, barSvg);
        if (w > 64) el('text', { x: x + 4, y: 54, text: p[1] + ' ' + p[3], 'font-size': 11, style: 'fill:var(--ink-2)' }, barSvg);
        else if (w > 18) el('text', { x: x + 2, y: 54, text: String(p[1]), 'font-size': 11, style: 'fill:var(--ink-2)' }, barSvg);
        x += w + 2;
      });
      barHost.setAttribute('aria-label', tot + ' tagged figures' + (mode === 'all' ? '' : ' in this group') + ': ' + s.v + ' verified, ' + s.u + ' unverified, ' + s.c + ' vendor claims only.');
    }
    var reBar = sized(barHost, drawBar);
    $$('#ev-modes button').forEach(function (b) {
      b.addEventListener('click', function () {
        mode = b.getAttribute('data-m'); segPress($('#ev-modes'), b);
        $$('.ev-grp', rows).forEach(function (g) { g.hidden = !(mode === 'all' || g.getAttribute('data-mode') === mode); });
        reBar();
      });
    });
    arrows($('#ev-modes'), 'button', function (b) { b.click(); });
    var only = $('#ev-only');
    only.addEventListener('click', function () { var on = only.getAttribute('aria-pressed') !== 'true'; only.setAttribute('aria-pressed', on ? 'true' : 'false'); fig.classList.toggle('only', on); });
    onTheme(reBar);
  }

  /* ======================================================================
     05: ONE DAY IS NOISE, A WEEK IS A SIGNAL (Nutrak demo data, calcium, 24-30 Aug 2026)
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
     06: ENOUGH FOR WHOM?  Needs ~ Normal(EAR 800, SD 100), from RDA = EAR + 2 SD.
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

  function init() { initPromises(); initAnatomy(); initLetters(); initEvidence(); initWeek(); initRDA(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
