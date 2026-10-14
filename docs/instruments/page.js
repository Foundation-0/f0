/* Instruments page: the harness diagram, the consent gate, the summary tree, the auto-research loop,
   and autofoundry's fan-out. Vanilla JS, no dependencies. Colours come from tokens (F0.css); every
   figure redraws on theme change, respects the motion toggle and starts paused. */
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
  function kfmt(n) { return n >= 1000 ? (Math.round(n / 100) / 10).toString().replace(/\.0$/, '') + 'K' : String(Math.round(n)); }
  /* build an SVG at the host's real width so 11px text stays 11px */
  function sized(host, build) {
    var lw = 0;
    function go(force) { var w = Math.round(host.getBoundingClientRect().width); if (!w || (w === lw && !force)) return; lw = w; build(w); }
    go(); if ('ResizeObserver' in window) new ResizeObserver(function () { go(); }).observe(host);
    return function () { go(true); };
  }
  function onTheme(fn) { if (F0.onTheme) F0.onTheme(fn); }
  function tipShow(html, x, y) { if (F0.tip) F0.tip.show(html, x, y); }
  function tipHide() { if (F0.tip) F0.tip.hide(); }
  /* a one-shot animation on the shared loop; finishes at once when motion is off */
  function animate(ms, step, done) {
    if (!motion() || !F0.loop) { step(1); if (done) done(); return { stop: function () {} }; }
    var t0 = 0, job = F0.loop(function (now) {
      if (!t0) t0 = now;
      var p = Math.min(1, (now - t0) / ms);
      step(p);
      if (p >= 1) { job.stop(); if (done) done(); }
    });
    job.start();
    // if the loop cannot run (hidden tab), finish on the next visible frame is fine; also guard motion toggled off mid-way
    return job;
  }
  /* roving arrow keys inside a group of buttons */
  function arrows(group, sel, onMove) {
    group.addEventListener('keydown', function (e) {
      var keys = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
      if (!(e.key in keys) && e.key !== 'Home' && e.key !== 'End') return;
      var bs = $$(sel, group), i = bs.indexOf(document.activeElement); if (i < 0) return;
      e.preventDefault();
      var j = e.key === 'Home' ? 0 : e.key === 'End' ? bs.length - 1 : (i + keys[e.key] + bs.length) % bs.length;
      bs[j].focus(); if (onMove) onMove(bs[j]);
    });
  }

  /* ---------------- SHA-256 (sync, UTF-8; checked against Node's crypto) ---------------- */
  var SHA = (function () {
    function frac(x) { return (x - Math.floor(x)) * 4294967296 | 0; }
    var K = [], H0 = [], n = 2, c = 0;
    while (c < 64) {
      var prime = true;
      for (var d = 2; d * d <= n; d++) if (n % d === 0) { prime = false; break; }
      if (prime) { if (c < 8) H0[c] = frac(Math.pow(n, 1 / 2)); K[c] = frac(Math.pow(n, 1 / 3)); c++; }
      n++;
    }
    var enc = window.TextEncoder ? new TextEncoder() : null;
    function utf8(s) { if (enc) return enc.encode(s); var b = unescape(encodeURIComponent(s)), a = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; }
    return function (str) {
      var bytes = utf8(str), l = bytes.length, total = ((l + 9 + 63) >> 6) << 6;
      var buf = new Uint8Array(total); buf.set(bytes); buf[l] = 0x80;
      var dv = new DataView(buf.buffer), bits = l * 8;
      dv.setUint32(total - 4, bits >>> 0); dv.setUint32(total - 8, Math.floor(bits / 4294967296));
      var H = H0.slice(), W = new Array(64);
      for (var off = 0; off < total; off += 64) {
        var i;
        for (i = 0; i < 16; i++) W[i] = dv.getUint32(off + i * 4) | 0;
        for (i = 16; i < 64; i++) {
          var a15 = W[i - 15], a2 = W[i - 2];
          var s0 = ((a15 >>> 7) | (a15 << 25)) ^ ((a15 >>> 18) | (a15 << 14)) ^ (a15 >>> 3);
          var s1 = ((a2 >>> 17) | (a2 << 15)) ^ ((a2 >>> 19) | (a2 << 13)) ^ (a2 >>> 10);
          W[i] = (W[i - 16] + s0 + W[i - 7] + s1) | 0;
        }
        var a = H[0], b = H[1], cc = H[2], dd = H[3], e = H[4], f = H[5], g = H[6], hh = H[7];
        for (i = 0; i < 64; i++) {
          var S1 = ((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7));
          var ch = (e & f) ^ (~e & g);
          var t1 = (hh + S1 + ch + K[i] + W[i]) | 0;
          var S0 = ((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10));
          var maj = (a & b) ^ (a & cc) ^ (b & cc);
          var t2 = (S0 + maj) | 0;
          hh = g; g = f; f = e; e = (dd + t1) | 0; dd = cc; cc = b; b = a; a = (t1 + t2) | 0;
        }
        H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + cc) | 0; H[3] = (H[3] + dd) | 0;
        H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + hh) | 0;
      }
      return H.map(function (x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }).join('');
    };
  })();

  /* ======================================================================
     HERO: the harness, part by part
     ====================================================================== */
  var PARTS = {
    memory: { name: 'Memory', ang: -90,
      without: 'Each request starts from nothing but the text sent with it. Yesterday is gone unless someone pastes it back in.',
      with_: 'A memory that outlives the session: every message kept in a searchable log, and each request built from short layered summaries plus the latest messages word for word.',
      lab: 'Colleagues who remember last month’s dead ends, and the group’s shared notes.',
      built: '<a href="#memory">Exo’s summary tree</a>; <a href="#auto-research">Auto-research-agent’s shared summary</a>' },
    record: { name: 'Record', ang: -18,
      without: 'No trace of who asked for what, which model answered, or what a person accepted.',
      with_: 'A log that can only grow. Each entry is signed and carries the fingerprint of the one before, so a changed entry is easy to detect.',
      lab: 'The bound lab notebook, dated and signed.',
      built: '<a href="#exo">Exo’s signed ledger</a>' },
    gate: { name: 'Permissions', ang: 54,
      without: 'A model that can act can also push, post or pay in your name, with nobody asking first.',
      with_: 'A gate that sorts actions by consequence and asks before anything public, irreversible, paid or touching other people. Your yes covers the exact words.',
      lab: 'The safety officer, and the rule that the principal investigator signs off.',
      built: '<a href="#consent">Exo’s gate</a>' },
    tools: { name: 'Tools', ang: 126,
      without: 'It can describe an experiment but cannot run one; it can write code but cannot execute it.',
      with_: 'Hands: reading and editing files, running code, cloning a project, renting a GPU.',
      lab: 'Equipment and technicians.',
      built: '<a href="#exo">Exo’s file, search and shell tools</a>; <a href="#auto-research">Auto-research-agent</a> (drives Codex or Claude Code); <a href="#autofoundry">autofoundry</a> (rents GPUs)' },
    meter: { name: 'Cost meter', ang: 198,
      without: 'You cannot see which model answered, whether a silent fallback happened, or what it cost.',
      with_: 'Every call records the model asked for, the model that served, the wait, the tokens and the price. A price nobody knows reads “unknown”, never $0.',
      lab: 'The grant office’s ledger of spending.',
      built: '<a href="#exo">Exo’s trace and findings</a>' }
  };
  var ORDER = ['memory', 'record', 'gate', 'tools', 'meter'];
  function icon(g, id, cx, cy) {
    var s = { fill: 'none', 'stroke-width': 1.6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    function p(d) { var o = Object.assign({ d: d }, s); return el('path', o, g); }
    if (id === 'memory') { p('M' + (cx - 12) + ' ' + (cy - 8) + 'h24M' + (cx - 9) + ' ' + cy + 'h18M' + (cx - 5) + ' ' + (cy + 8) + 'h10'); }
    if (id === 'record') { [-11, 0, 11].forEach(function (dx) { el('rect', Object.assign({ x: cx + dx - 4, y: cy - 4, width: 8, height: 8 }, s), g); }); p('M' + (cx - 7) + ' ' + cy + 'h3M' + (cx + 4) + ' ' + cy + 'h3'); }
    if (id === 'gate') { p('M' + cx + ' ' + (cy - 12) + 'l10 4v6c0 6-4 10-10 13c-6-3-10-7-10-13v-6z'); p('M' + (cx - 4) + ' ' + (cy + 1) + 'l3 3l6-6'); }
    if (id === 'tools') { p('M' + (cx - 11) + ' ' + (cy - 6) + 'l6 6l-6 6M' + (cx + 1) + ' ' + (cy + 7) + 'h10'); }
    if (id === 'meter') { p('M' + (cx - 12) + ' ' + (cy + 6) + 'a12 12 0 0 1 24 0'); p('M' + cx + ' ' + (cy + 6) + 'l6-8'); }
  }
  function initHero() {
    var svg = $('#hx-svg'); if (!svg) return;
    var stage = svg.parentNode, cur = 'memory', packet = null, job = null;
    var W = 520, H = 400, CX, CY, RX, RY, PR, EW, EH;
    function geo() {
      var r = stage.getBoundingClientRect();
      W = Math.max(280, Math.round(r.width)); H = Math.max(260, Math.round(r.height));
      var small = W < 460;
      PR = small ? 23 : 28; EW = small ? 104 : 132; EH = small ? 66 : 80;
      CX = W / 2; CY = H / 2 + (small ? 18 : 10);
      RX = W / 2 - (small ? 44 : 78); RY = H / 2 - (small ? 64 : 66);
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    }
    function pos(id) { var a = PARTS[id].ang * Math.PI / 180; return [CX + RX * Math.cos(a), CY + RY * Math.sin(a)]; }
    function draw() {
      geo();
      while (svg.lastChild && svg.lastChild.nodeName !== 'title') svg.removeChild(svg.lastChild);
      // the car body: a faint octagon (the Foundation0 zero)
      var oct = [];
      for (var i = 0; i < 8; i++) { var a = (22.5 + 45 * i) * Math.PI / 180; oct.push((CX + (W / 2 - 10) * Math.cos(a)).toFixed(1) + ',' + (CY + (H / 2 - 16) * Math.sin(a)).toFixed(1)); }
      el('polygon', { points: oct.join(' '), fill: 'none', style: 'stroke:var(--line)', 'stroke-width': 1 }, svg);
      // spokes
      ORDER.forEach(function (id) {
        var p = pos(id), on = id === cur;
        var dx = p[0] - CX, dy = p[1] - CY, L = Math.hypot(dx, dy);
        var t0 = Math.min(EW / 2 / Math.abs(dx || 1e-6), EH / 2 / Math.abs(dy || 1e-6)); // leave the engine at its edge
        el('line', { x1: CX + dx * t0, y1: CY + dy * t0, x2: p[0] - dx / L * (PR + 3), y2: p[1] - dy / L * (PR + 3), style: 'stroke:' + (on ? 'var(--dig)' : 'var(--line-ui)'), 'stroke-width': on ? 2 : 1 }, svg);
      });
      // engine
      el('rect', { x: CX - EW / 2, y: CY - EH / 2, width: EW, height: EH, rx: 2, style: 'fill:var(--bg-2);stroke:var(--dig)', 'stroke-width': 1.6 }, svg);
      el('text', { x: CX, y: CY - EH / 2 + 24, 'text-anchor': 'middle', text: 'THE MODEL', style: 'fill:var(--ink)', 'font-size': 12, 'font-weight': 600, 'letter-spacing': '.12em' }, svg);
      el('text', { x: CX, y: CY - EH / 2 + 24 + (EH > 70 ? 22 : 18), 'text-anchor': 'middle', text: 'reads text,', style: 'fill:var(--ink-2)', 'font-size': 11 }, svg);
      el('text', { x: CX, y: CY - EH / 2 + 24 + (EH > 70 ? 38 : 32), 'text-anchor': 'middle', text: 'writes text', style: 'fill:var(--ink-2)', 'font-size': 11 }, svg);
      // parts
      ORDER.forEach(function (id) {
        var p = pos(id), on = id === cur;
        var g = el('g', { class: 'hx-part', 'data-part': id, 'aria-hidden': 'true' }, svg);
        el('circle', { cx: p[0], cy: p[1], r: PR + 8, fill: 'transparent' }, g); // hit area
        el('circle', { cx: p[0], cy: p[1], r: PR, style: 'fill:var(--bg-2);stroke:' + (on ? 'var(--bio)' : 'var(--line-ui)'), 'stroke-width': on ? 2 : 1 }, g);
        var ig = el('g', { style: 'stroke:' + (on ? 'var(--ink)' : 'var(--ink-2)') }, g);
        icon(ig, id, p[0], p[1]);
        var ly = p[1] + (PARTS[id].ang === -90 ? -(PR + 10) : PR + 18);
        el('text', { x: p[0], y: ly, 'text-anchor': 'middle', text: PARTS[id].name.toUpperCase(), style: 'fill:' + (on ? 'var(--ink)' : 'var(--ink-2)'), 'font-size': 11, 'font-weight': on ? 600 : 500, 'letter-spacing': '.08em' }, g);
        g.addEventListener('click', function () { select(id, true); });
      });
      packet = el('circle', { r: 4, cx: CX, cy: CY, style: 'fill:var(--bio)', opacity: 0 }, svg);
    }
    function readout() {
      var P = PARTS[cur], box = $('#hx-read');
      box.innerHTML = '<p class="hx-name">' + esc(P.name) + '</p><dl class="hx-dl">' +
        '<div><dt>Without it</dt><dd>' + esc(P.without) + '</dd></div>' +
        '<div><dt>With it</dt><dd>' + esc(P.with_) + '</dd></div>' +
        '<div><dt>In a lab</dt><dd>' + esc(P.lab) + '</dd></div>' +
        '<div><dt>Built here by</dt><dd>' + P.built + '</dd></div></dl>';
      $('#hx-corner').textContent = 'Part ' + (ORDER.indexOf(cur) + 1) + ' of 5';
    }
    function select(id, fly) {
      cur = id;
      $$('#hx-seg button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-part') === id ? 'true' : 'false'); });
      draw(); readout();
      if (fly && motion()) {
        var p = pos(id);
        if (job) job.stop();
        job = animate(650, function (t) {
          var e = 1 - Math.pow(1 - t, 3);
          packet.setAttribute('cx', CX + (p[0] - CX) * e); packet.setAttribute('cy', CY + (p[1] - CY) * e);
          packet.setAttribute('opacity', t < 1 ? 1 : 0);
        });
      }
    }
    $$('#hx-seg button').forEach(function (b) { b.addEventListener('click', function () { select(b.getAttribute('data-part'), true); }); });
    arrows($('#hx-seg'), 'button', function (b) { select(b.getAttribute('data-part'), true); });
    select('memory', false);
    if ('ResizeObserver' in window) { var lw = 0; new ResizeObserver(function () { var w = Math.round(stage.getBoundingClientRect().width); if (w && w !== lw) { lw = w; draw(); } }).observe(stage); }
    onTheme(draw);
  }

  /* ======================================================================
     02: CONSENT TO THE EXACT WORDS
     ====================================================================== */
  var ACTIONS = [
    { id: 'notes', label: 'Edit a local notes file', tool: 'edit_file', target: 'notes/ideas.md', undo: true, seen: 'me',
      text: 'Add: try leaves of 8 on the long thread, then compare the summaries.', field: 'The edit' },
    { id: 'tests', label: 'Run the test suite', tool: 'shell', target: 'pytest -q (this project)', undo: true, seen: 'me',
      text: 'pytest -q', field: 'The command' },
    { id: 'secret', label: 'Read a password file', tool: 'read_file', target: 'the password store', undo: true, seen: 'me', cred: true,
      text: 'Open the password store and read the entry for the cloud account.', field: 'What the agent asks for', risk: 'touches credentials' },
    { id: 'push', label: 'Push a commit to a public repository', tool: 'git push', target: 'your public notebook repository', undo: false, seen: 'others', out: true, pub: true,
      text: 'Fix the sign error in lemma 3; rerun all checks.', field: 'Commit message', risk: 'public · cannot be undone', kind: 'pushes' },
    { id: 'post', label: 'Post a preprint announcement', tool: 'post', target: 'your public feed', undo: false, seen: 'others', out: true, pub: true,
      text: 'New preprint: a tighter bound for the packing problem, with every certificate public. Plots and scripts are in /home/sam/runs/v3.', field: 'Post', risk: 'public · cannot be undone', kind: 'posts' },
    { id: 'email', label: 'Email a co-author', tool: 'send_email', target: 'your co-author, Dr Rivera', undo: false, seen: 'others', out: true, other: true,
      text: 'Hi Ana, the new bound holds for n up to 40. Can we go through the proof on Tuesday?', field: 'Email', risk: 'reaches another person · cannot be unsent', kind: 'emails' },
    { id: 'pay', label: 'Pay an API invoice', tool: 'pay', target: 'your model provider, September invoice', undo: false, seen: 'others', out: true, other: true, money: true,
      text: 'Pay $42.10 from the research card.', field: 'Payment', risk: 'costs money · cannot be undone', kind: 'payments' },
    { id: 'reply', label: 'Reply in public to a named critic', tool: 'post_reply', target: 'a public thread, replying to a named person', undo: false, seen: 'others', out: true, pub: true, other: true,
      text: 'Thanks for the careful read. You are right about the edge case; the fix is in version 2.', field: 'Reply', risk: 'public · cannot be undone · touches another person', operator: true }
  ];
  function outcome(a) {
    if (a.cred) return 'ask';
    if (a.undo && a.seen === 'me' && !a.money && !a.other) return 'run';
    return 'ask';
  }
  function binding(a, text) { return SHA(JSON.stringify({ tool: a.tool, target: a.target, title: a.field, text: text })); }
  var SCRUB = /(\/home\/[^\s,;]+|\/Users\/[^\s,;]+|[A-Z]:\\Users\\[^\s,;]+|~\/[^\s,;]+)/g;
  function initConsent() {
    var box = $('#cg-actions'); if (!box) return;
    var state = {}, curId = 'email', ledger = [], prev = '0'.repeat(64), fullHex = false;
    ACTIONS.forEach(function (a) { state[a.id] = { text: a.text, approved: null, approvedText: null, grant: false, denied: false }; });
    // action buttons
    ACTIONS.forEach(function (a) {
      var o = outcome(a);
      var b = h('button', { type: 'button', cls: 'cg-act', 'data-id': a.id, 'aria-pressed': 'false' }, box,
        '<span class="dot ' + (a.cred || a.operator ? 'cred' : o === 'ask' ? 'ask' : '') + '" aria-hidden="true"></span><span>' + esc(a.label) + '</span>');
      b.addEventListener('click', function () { select(a.id); });
    });
    arrows(box, '.cg-act', function (b) { select(b.getAttribute('data-id')); });
    // the twin table
    var tb = $('#cg-table tbody');
    ACTIONS.forEach(function (a) {
      var o = outcome(a), flags = [];
      if (a.money) flags.push('costs money'); if (a.other) flags.push('reaches another person'); if (a.cred) flags.push('credentials'); if (a.out) flags.push('leaves your machine');
      var grant = a.cred ? 'Never: credentials floor' : a.operator ? 'Never: operator floor' : o === 'run' ? 'Not needed' : '7 days, this exact text';
      h('tr', null, tb, '<th scope="row">' + esc(a.label) + '</th><td>' + (a.undo ? 'Yes' : 'No') + '</td><td>' + (a.seen === 'me' ? 'Only you' : 'Others') + '</td><td>' + esc(flags.join(', ') || 'none') + '</td><td>' + (o === 'run' ? 'Runs at once, logged' : 'Asks you') + '</td><td>' + esc(grant) + '</td>');
    });
    function log(kind, a, fp) {
      var entry = { n: ledger.length + 1, kind: kind, target: a.target, fp: fp ? fp.slice(0, 8) : null };
      var hsh = SHA(prev + JSON.stringify(entry));
      ledger.push({ e: entry, prev: prev, hash: hsh }); prev = hsh;
    }
    function grid() {
      var svg = $('#cg-svg'); while (svg.lastChild && svg.lastChild.nodeName !== 'title') svg.removeChild(svg.lastChild);
      var X0 = 70, Y0 = 36, CW = 122, CH = 104;
      el('text', { x: X0 + CW / 2, y: 24, 'text-anchor': 'middle', text: 'ONLY YOU SEE IT', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.06em' }, svg);
      el('text', { x: X0 + CW * 1.5, y: 24, 'text-anchor': 'middle', text: 'OTHERS SEE IT', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.06em' }, svg);
      el('text', { x: X0 - 8, y: Y0 + CH / 2 - 2, 'text-anchor': 'end', text: 'CAN BE', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: X0 - 8, y: Y0 + CH / 2 + 12, 'text-anchor': 'end', text: 'UNDONE', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: X0 - 8, y: Y0 + CH * 1.5 - 2, 'text-anchor': 'end', text: 'CANNOT', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: X0 - 8, y: Y0 + CH * 1.5 + 12, 'text-anchor': 'end', text: 'BE UNDONE', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(function (c) {
        var run = c[0] === 0 && c[1] === 0;
        el('rect', { x: X0 + c[0] * CW + 1, y: Y0 + c[1] * CH + 1, width: CW - 2, height: CH - 2, style: 'fill:' + (run ? 'var(--bg-2)' : 'color-mix(in srgb, var(--acc-exo) 7%, var(--bg-2))') + ';stroke:var(--line)' }, svg);
        el('text', { x: X0 + c[0] * CW + 9, y: Y0 + c[1] * CH + 18, text: run ? 'RUNS AT ONCE' : 'ASKS YOU', 'font-size': 11, 'font-weight': 600, style: 'fill:' + (run ? 'var(--ink-2)' : 'var(--ink)'), 'letter-spacing': '.06em' }, svg);
      });
      var slots = {};
      ACTIONS.forEach(function (a) {
        var cx = a.seen === 'me' ? 0 : 1, cy = a.undo ? 0 : 1, key = cx + ',' + cy;
        var k = slots[key] = (slots[key] || 0) + 1;
        var px = X0 + cx * CW + 24 + ((k - 1) % 3) * 36, py = Y0 + cy * CH + 46 + Math.floor((k - 1) / 3) * 32;
        var on = a.id === curId, o = outcome(a), g = el('g', { 'aria-hidden': 'true', style: 'cursor:pointer' }, svg);
        el('circle', { cx: px, cy: py, r: 14, fill: 'transparent' }, g);
        if (on) el('circle', { cx: px, cy: py, r: 12, fill: 'none', style: 'stroke:var(--bio)', 'stroke-width': 2 }, g);
        if (a.cred || a.operator) el('rect', { x: px - 6, y: py - 6, width: 12, height: 12, fill: 'none', style: 'stroke:var(--acc-exo)', 'stroke-width': 2.2 }, g);
        else if (o === 'ask') el('circle', { cx: px, cy: py, r: 6, style: 'fill:var(--acc-exo)' }, g);
        else el('circle', { cx: px, cy: py, r: 6, fill: 'none', style: 'stroke:var(--ink-2)', 'stroke-width': 1.8 }, g);
        g.addEventListener('click', function () { select(a.id); });
        g.addEventListener('pointermove', function (e) { tipShow('<div class="tip-k">' + (o === 'run' ? 'Runs at once' : 'Asks you') + '</div><div class="tip-t">' + esc(a.label) + '</div>', e.clientX, e.clientY); });
        g.addEventListener('pointerleave', tipHide);
      });
      // legend under the grid (inside the SVG, bottom)
      var ly = Y0 + CH * 2 + 4;
      svg.setAttribute('viewBox', '0 0 320 ' + (ly + 14));
    }
    function flags(a) {
      var f = [['Leaves your machine', a.out], ['Costs money', a.money], ['Reaches another person', a.other], ['Touches credentials', a.cred]];
      $('#cg-flags').innerHTML = f.map(function (x) { return '<li class="' + (x[1] ? 'on' : '') + '"><span class="m" aria-hidden="true">' + (x[1] ? '&#10003;' : '&ndash;') + '</span>' + esc(x[0]) + '<span class="sr-only">: ' + (x[1] ? 'yes' : 'no') + '</span></li>'; }).join('');
      var o = outcome(a), msg;
      if (a.cred) msg = 'Always asks you.<small>The credentials floor: logins, key files and password stores always ask, and no rule can change that.</small>';
      else if (a.operator) msg = 'Always asks you.<small>The operator floor: an irreversible public act that touches another person always asks. Your own settings cannot lower it.</small>';
      else if (o === 'run') msg = 'Runs at once, and is logged.<small>Private and undoable: asking would only train you to click yes.</small>';
      else msg = 'Waits for you, with a one-line summary.<small>' + (a.money ? 'It costs money and cannot be undone.' : a.other ? 'It reaches another person and cannot be taken back.' : 'It is public and cannot be undone.') + '</small>';
      $('#cg-outcome').innerHTML = msg;
    }
    function hexHTML(hex, ref) {
      var shown = fullHex ? hex : hex.slice(0, 16);
      var out = '';
      for (var i = 0; i < shown.length; i++) {
        var ch = shown[i], diff = ref && ref[i] !== ch;
        out += (i && i % 4 === 0 ? ' ' : '') + (diff ? '<span class="chg">' + ch + '</span>' : ch);
      }
      return out + (fullHex ? '' : ' &hellip;');
    }
    function diffHTML(a, b) {
      var p = 0; while (p < a.length && p < b.length && a[p] === b[p]) p++;
      var s = 0; while (s < a.length - p && s < b.length - p && a[a.length - 1 - s] === b[b.length - 1 - s]) s++;
      var pre = a.slice(Math.max(0, p - 18), p), post = a.slice(a.length - s, Math.min(a.length, a.length - s + 18));
      return (p > 18 ? '&hellip;' : '') + esc(pre) + '<del>' + esc(a.slice(p, a.length - s) || ' ') + '</del><ins>' + esc(b.slice(p, b.length - s) || ' ') + '</ins>' + esc(post) + (a.length - s + 18 < a.length ? '&hellip;' : '');
    }
    function logHTML() {
      return '<ul class="cg-log" aria-label="The record (this illustration)">' + (ledger.length ? ledger.slice(-3).map(function (r) {
        return '<li><b>#' + r.e.n + ' ' + esc(r.e.kind) + '</b> &middot; prev ' + r.prev.slice(0, 8) + ' &middot; hash ' + r.hash.slice(0, 8) + '</li>';
      }).join('') : '<li>The record is empty. Each decision you make here is added to it, every entry carrying the hash of the one before.</li>') + '</ul>';
    }
    /* build the card once per action; typing only refreshes the parts around the textarea */
    function card() {
      var a = ACTIONS.filter(function (x) { return x.id === curId; })[0], st = state[a.id], o = outcome(a);
      var c = $('#cg-card'); c.className = 'cg-card';
      if (o === 'run') {
        c.innerHTML = '<p class="cg-k">No question asked</p><p class="cg-sum">' + esc(a.label) + '</p>' +
          '<dl class="cg-meta"><dt>Tool</dt><dd>' + esc(a.tool) + '</dd><dt>Target</dt><dd>' + esc(a.target) + '</dd><dt>' + esc(a.field) + '</dt><dd>' + esc(st.text) + '</dd></dl>' +
          '<div class="cg-btns"><button class="tbtn pri" type="button" data-do="run">Let the agent do it</button></div>' +
          '<p class="cg-note">It runs at once and a line is added to the record. You can read the record later, and undo the step.</p><div class="cg-logbox">' + logHTML() + '</div>';
        c.querySelector('[data-do="run"]').addEventListener('click', function () {
          log('tool.' + a.tool, a, binding(a, st.text)); c.querySelector('.cg-logbox').innerHTML = logHTML();
          announce('Done, and written to the record as entry ' + ledger.length + '.');
        });
        return;
      }
      var noGrant = a.cred || a.operator;
      c.innerHTML = '<p class="cg-k">Approval requested &middot; ' + esc(a.risk) + '</p><p class="cg-sum">' + esc(a.label) + '?</p>' +
        '<dl class="cg-meta"><dt>Tool</dt><dd>' + esc(a.tool) + '</dd><dt>Target</dt><dd>' + esc(a.target) + '</dd></dl>' +
        '<label for="cg-draft">' + esc(a.field) + ' (you can edit it)</label><textarea id="cg-draft" spellcheck="false">' + esc(st.text) + '</textarea>' +
        '<div class="cg-fp"><span class="cg-k">Fingerprint &middot; SHA-256 of tool, target, field and text</span><span class="hex" id="cg-hex"></span><span class="was" id="cg-was" hidden></span>' +
        '<button type="button" id="cg-full" aria-pressed="false">Show all 64</button></div>' +
        '<div class="cg-statebox" id="cg-statebox"></div>' +
        '<div class="cg-btns">' +
        '<button class="tbtn pri" type="button" data-do="once">Approve once</button>' +
        '<button class="tbtn" type="button" data-do="always">Always allow</button>' +
        '<button class="tbtn" type="button" data-do="deny">Deny</button>' +
        '<button class="tbtn" type="button" data-do="nudge">Let the agent change one character</button></div>' +
        (noGrant ? '<p class="cg-note">' + (a.cred ? 'Credentials always ask. No grant can cover them.' : 'Operator floor: no grant can cover an irreversible public act that touches another person.') + '</p>'
          : '<p class="cg-note">&ldquo;Always allow&rdquo; covers one kind of act on one target and, for anything that leaves your machine, one exact text. It expires after 7 days (30 for other kinds of act).</p>') +
        '<div class="cg-logbox">' + logHTML() + '</div>';
      var ta = c.querySelector('#cg-draft'), wasStale = false;
      function refresh() {
        var fp = binding(a, st.text), hits = a.pub ? (st.text.match(SCRUB) || []) : [];
        var match = !!st.approved && st.approved === fp, stale = !!st.approved && st.approved !== fp;
        c.className = 'cg-card ' + (stale ? 'bad' : match ? 'ok' : 'ask');
        $('#cg-hex').innerHTML = hexHTML(fp, stale ? st.approved : null);
        var was = $('#cg-was'); was.hidden = !stale; if (stale) was.innerHTML = 'approved: ' + hexHTML(st.approved, null);
        var fb = $('#cg-full'); fb.setAttribute('aria-pressed', fullHex ? 'true' : 'false'); fb.textContent = fullHex ? 'Show 16 characters' : 'Show all 64';
        var html;
        if (hits.length) html = '<div class="cg-state hold"><b>Held by the outbound scrub.</b> This goes somewhere public and contains ' + hits.map(function (x) { return '<code>' + esc(x) + '</code>'; }).join(', ') + ', which looks like a home-folder path. Remove it from the draft to continue.</div>';
        else if (stale) html = '<div class="cg-state bad"><b>This is not what you approved. Asking again.</b> The ' + (st.grant ? 'grant covered one exact text' : 'approval covered fingerprint ' + st.approved.slice(0, 8)) + '; the draft changed, so the fingerprint changed.<div class="cg-diff" aria-label="What changed">' + diffHTML(st.approvedText, st.text) + '</div></div>';
        else if (match && st.grant) html = '<div class="cg-state ok"><b>Always allowed, narrowly.</b> This kind of act, to this target, for this exact text, until ' + expiry(7) + '. The grant is written to the record, and you can list and revoke it.</div>';
        else if (match) html = '<div class="cg-state ok"><b>Approved once.</b> Your yes covers fingerprint ' + fp.slice(0, 8) + '&hellip; and nothing else. Now change one character.</div>';
        else if (st.denied) html = '<div class="cg-state"><b>Denied.</b> Nothing was sent, and the refusal is in the record.</div>';
        else html = '<div class="cg-state"><b>Waiting for you.</b> Nothing has been sent.</div>';
        $('#cg-statebox').innerHTML = html;
        c.querySelector('[data-do="once"]').disabled = !!(hits.length || match);
        c.querySelector('[data-do="always"]').disabled = !!(hits.length || noGrant || (match && st.grant));
        if (stale && !wasStale) announce('The draft changed after your approval. The fingerprint no longer matches, so it asks again.');
        wasStale = stale;
        return fp;
      }
      ta.addEventListener('input', function () { st.text = ta.value; st.denied = false; refresh(); });
      c.querySelector('#cg-full').addEventListener('click', function () { fullHex = !fullHex; refresh(); });
      c.querySelectorAll('[data-do]').forEach(function (b) {
        b.addEventListener('click', function () {
          var d = b.getAttribute('data-do'), fp = binding(a, st.text);
          if (d === 'once') { st.approved = fp; st.approvedText = st.text; st.grant = false; st.denied = false; log('approval.allow', a, fp); announce('Approved once. Your approval covers fingerprint ' + fp.slice(0, 8) + '.'); }
          if (d === 'always') { st.approved = fp; st.approvedText = st.text; st.grant = true; st.denied = false; log('grant.create', a, fp); announce('Always allowed for this exact text, for 7 days.'); }
          if (d === 'deny') { st.approved = null; st.grant = false; st.denied = true; log('approval.deny', a, fp); announce('Denied. Nothing was sent.'); }
          if (d === 'nudge') { st.text = nudge(st.text); ta.value = st.text; st.denied = false; }
          c.querySelector('.cg-logbox').innerHTML = logHTML();
          refresh();
          if (b.disabled) { var nb = c.querySelector('[data-do="deny"]'); nb.focus(); }
        });
      });
      refresh();
    }
    function nudge(t) { // the smallest change an agent might make: one digit or one letter
      var m = /\d/.exec(t);
      if (m) { var d = +m[0]; return t.slice(0, m.index) + ((d + 1) % 10) + t.slice(m.index + 1); }
      var i = t.indexOf('e'); if (i >= 0) return t.slice(0, i) + 'a' + t.slice(i + 1);
      return t + '.';
    }
    function expiry(days) { var d = new Date(Date.now() + days * 864e5); return F0.fmtDate ? F0.fmtDate(d.toISOString().slice(0, 10)) : d.toDateString(); }
    var live = h('p', { cls: 'sr-only', 'aria-live': 'polite' }, $('.cg'));
    function announce(s) { live.textContent = s; }
    function select(id) {
      curId = id;
      $$('.cg-act', box).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-id') === id ? 'true' : 'false'); });
      var a = ACTIONS.filter(function (x) { return x.id === id; })[0];
      grid(); flags(a); card();
    }
    select(curId);
    onTheme(grid);
  }

  /* ======================================================================
     03: MEMORY THAT STAYS ONE PAGE LONG
     ====================================================================== */
  var TAIL = 12, LEAF = 8, BUDGET = 6000, SUMT = 500, MSGT = 250, NMAX = 1000;
  function treeFor(L) {
    var view = [], all = [];
    for (var i = 0; i < L; i++) {
      var n = { lv: 0, ix: i, a: i * LEAF + 1, b: i * LEAF + LEAF };
      view.push(n); all.push(n);
      while (view.length * SUMT > BUDGET) {
        var done = false;
        for (var j = 0; j < view.length - 1; j++) {
          var x = view[j], y = view[j + 1];
          if (x.lv === y.lv && x.ix % 2 === 0 && y.ix === x.ix + 1) {
            var p = { lv: x.lv + 1, ix: x.ix / 2, a: x.a, b: y.b };
            x.gone = y.gone = true; view.splice(j, 2, p); all.push(p); done = true; break;
          }
        }
        if (!done) break;
      }
    }
    return { view: view, all: all };
  }
  function memAt(N) {
    var L = Math.floor(Math.max(0, N - TAIL) / LEAF), t = treeFor(L), verb = N - L * LEAF;
    return { N: N, L: L, tree: t, verb: verb, sums: t.view.length, exo: t.view.length * SUMT + verb * MSGT, plain: N * MSGT };
  }
  function initMemory() {
    var range = $('#mt-n'); if (!range) return;
    var N = +range.value, series = [];
    for (var n = 1; n <= NMAX; n++) { var m = memAt(n); series.push([n, m.exo, m.plain]); }
    // twin table
    var tb = $('#mt-table tbody');
    [12, 20, 52, 100, 200, 500, 1000].forEach(function (k) { var m = memAt(k); h('tr', null, tb, '<td class="n">' + fmt(k) + '</td><td class="n">' + m.sums + '</td><td class="n">' + m.verb + '</td><td class="n">' + fmt(m.exo) + '</td><td class="n">' + fmt(m.plain) + '</td>'); });
    var treeHost = $('#mt-tree'), chartHost = $('#mt-chart'), treeSvg = null, chartSvg = null, chartGeo = null;
    function drawTree(W) {
      var m = memAt(N), t = m.tree;
      if (treeSvg) treeSvg.remove();
      var maxLv = t.all.reduce(function (a, n) { return Math.max(a, n.lv); }, -1);
      var rows = maxLv + 1, rowH = 26, top = 6, padL = 40, padR = 14, stripY = top + rows * rowH + (rows ? 8 : 0), H = stripY + 18 + 30;
      var svg = treeSvg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': ariaMem(m) });
      treeHost.insertBefore(svg, treeHost.firstChild);
      var X = function (msg) { return padL + (msg - 1) / N * (W - padL - padR); };
      for (var lv = maxLv; lv >= 0; lv--) {
        var y = top + (maxLv - lv) * rowH;
        el('text', { x: 4, y: y + 15, text: 'L' + lv, 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      }
      t.all.forEach(function (n) {
        var y = top + (maxLv - n.lv) * rowH, x0 = X(n.a), x1 = X(n.b + 1), w = Math.max(1, x1 - x0 - 2);
        var inView = !n.gone;
        el('rect', { x: x0 + 1, y: y + 2, width: w, height: rowH - 6, rx: 1, style: inView ? 'fill:color-mix(in srgb, var(--dig) 22%, var(--bg-1));stroke:var(--dig)' : 'fill:none;stroke:var(--line-ui)', 'stroke-width': inView ? 1.3 : 1, opacity: inView ? 1 : 0.7 }, svg);
        var lab = n.a + '–' + n.b;
        if (inView && w > lab.length * 6.8 + 8) el('text', { x: x0 + 1 + w / 2, y: y + 16, 'text-anchor': 'middle', text: lab, 'font-size': 11, style: 'fill:var(--ink)' }, svg);
      });
      // the conversation strip
      var sumEnd = m.L * LEAF;
      if (sumEnd > 0) el('rect', { x: X(1), y: stripY, width: Math.max(1, X(sumEnd + 1) - X(1) - 1), height: 14, style: 'fill:var(--line)' }, svg);
      el('rect', { x: X(sumEnd + 1), y: stripY, width: Math.max(2, X(N + 1) - X(sumEnd + 1)), height: 14, style: 'fill:var(--mark-dig)' }, svg);
      if (N <= 160) for (var k = 2; k <= N; k++) el('line', { x1: X(k), x2: X(k), y1: stripY, y2: stripY + 14, style: 'stroke:var(--bg-1)', 'stroke-width': N > 80 ? 0.6 : 1 }, svg);
      el('text', { x: padL, y: stripY + 30, text: '1', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: W - padR, y: stripY + 30, 'text-anchor': 'end', text: fmt(N), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      el('text', { x: 4, y: stripY + 11, text: 'msgs', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      var tailX = X(sumEnd + 1), tailW = X(N + 1) - tailX;
      var tlab = m.verb + ' word for word';
      var tx = Math.min(W - padR, Math.max(padL + tlab.length * 6.6, tailX + tailW));
      el('text', { x: tx, y: stripY + 44, 'text-anchor': 'end', text: tlab, 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
      var sumLab = W < 560 ? 'summarized, searchable' : 'summarized: kept in the log, searchable';
      if (sumEnd > 0 && tx - tlab.length * 6.8 - padL > sumLab.length * 6.8 + 16) el('text', { x: padL, y: stripY + 44, text: sumLab, 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      svg.setAttribute('height', stripY + 50); svg.setAttribute('viewBox', '0 0 ' + W + ' ' + (stripY + 50));
    }
    function ariaMem(m) {
      return 'At ' + m.N + ' messages the next request carries ' + m.sums + ' summaries and ' + m.verb + ' messages word for word, about ' + fmt(m.exo) + ' tokens; a plain transcript would send all ' + m.N + ' messages, about ' + fmt(m.plain) + ' tokens.';
    }
    function drawChart(W) {
      if (chartSvg) chartSvg.remove();
      var H = W < 520 ? 200 : 220, padL = 46, padR = W < 520 ? 64 : 132, padT = 26, padB = 26;
      var ymax = NMAX * MSGT;
      var X = function (n) { return padL + (n / NMAX) * (W - padL - padR); }, Y = function (v) { return padT + (1 - v / ymax) * (H - padT - padB); };
      chartGeo = { X: X, Y: Y, padL: padL, padR: padR, W: W, H: H };
      var svg = chartSvg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': 'Line chart: tokens per request against conversation length, from 1 to 1,000 messages. A plain transcript grows in a straight line to 250,000 tokens; Exo stays near 10,000.' }, chartHost);
      [0, 50000, 100000, 150000, 200000, 250000].forEach(function (v) {
        el('line', { x1: padL, x2: W - padR, y1: Y(v), y2: Y(v), style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
        el('text', { x: padL - 6, y: Y(v) + 4, 'text-anchor': 'end', text: kfmt(v), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      });
      [0, 250, 500, 750, 1000].forEach(function (n) { el('text', { x: X(n), y: H - 8, 'text-anchor': n === 0 ? 'start' : n === 1000 ? 'end' : 'middle', text: fmt(n), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg); });
      el('text', { x: padL, y: 12, text: 'TOKENS PER REQUEST', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.08em' }, svg);
      function path(idx) { return series.map(function (s, i) { return (i ? 'L' : 'M') + X(s[0]).toFixed(1) + ' ' + Y(s[idx]).toFixed(1); }).join(''); }
      el('path', { d: path(2), fill: 'none', style: 'stroke:var(--ink-3)', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
      el('path', { d: path(1), fill: 'none', style: 'stroke:var(--mark-dig)', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
      // end labels (text in ink, a line-key beside it)
      var ex = W - padR + 8;
      el('line', { x1: ex, x2: ex + 10, y1: Y(250000), y2: Y(250000), style: 'stroke:var(--ink-3)', 'stroke-width': 2 }, svg);
      el('text', { x: ex + 14, y: Y(250000) + 4, text: W < 520 ? 'Plain' : 'Plain transcript', 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
      var ey = Y(series[NMAX - 1][1]);
      el('line', { x1: ex, x2: ex + 10, y1: ey, y2: ey, style: 'stroke:var(--mark-dig)', 'stroke-width': 2 }, svg);
      el('text', { x: ex + 14, y: ey - 2, text: 'Exo', 'font-size': 11, style: 'fill:var(--ink)' }, svg);
      // the current N
      var g = el('g', { class: 'mt-cur' }, svg);
      chartGeo.cur = g;
      // crosshair layer
      var hair = el('line', { y1: padT, y2: H - padB, style: 'stroke:var(--line-ui)', 'stroke-width': 1, opacity: 0 }, svg);
      var hit = el('rect', { x: padL, y: padT, width: W - padL - padR, height: H - padT - padB, fill: 'transparent', style: 'cursor:crosshair' }, svg);
      hit.addEventListener('pointermove', function (e) {
        var r = svg.getBoundingClientRect(), x = (e.clientX - r.left) * (W / r.width);
        var n = Math.max(1, Math.min(NMAX, Math.round((x - padL) / (W - padL - padR) * NMAX))), s = series[n - 1];
        hair.setAttribute('x1', X(n)); hair.setAttribute('x2', X(n)); hair.setAttribute('opacity', 1);
        tipShow('<div class="tip-k">' + fmt(n) + ' messages</div><div class="tip-rows"><div class="tip-row"><svg viewBox="0 0 16 16"><path d="M1 8H15" style="stroke:var(--mark-dig)" stroke-width="2"/></svg><span class="tip-v">' + fmt(s[1]) + '</span> Exo</div><div class="tip-row"><svg viewBox="0 0 16 16"><path d="M1 8H15" style="stroke:var(--ink-3)" stroke-width="2"/></svg><span class="tip-v">' + fmt(s[2]) + '</span> plain transcript</div></div><div class="tip-foot">tokens per request &middot; assumed sizes</div>', e.clientX, e.clientY);
      });
      hit.addEventListener('pointerleave', function () { hair.setAttribute('opacity', 0); tipHide(); });
      hit.addEventListener('click', function (e) {
        var r = svg.getBoundingClientRect(), x = (e.clientX - r.left) * (W / r.width);
        setN(Math.max(1, Math.min(NMAX, Math.round((x - padL) / (W - padL - padR) * NMAX))));
      });
      drawCur();
    }
    function drawCur() {
      if (!chartGeo) return;
      var g = chartGeo.cur, X = chartGeo.X, Y = chartGeo.Y, s = series[N - 1];
      while (g.firstChild) g.removeChild(g.firstChild);
      el('line', { x1: X(N), x2: X(N), y1: Y(250000), y2: Y(0), style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, g);
      [[s[2], 'var(--ink-3)'], [s[1], 'var(--mark-dig)']].forEach(function (p) {
        el('circle', { cx: X(N), cy: Y(p[0]), r: 6, style: 'fill:var(--bg-1)' }, g);
        el('circle', { cx: X(N), cy: Y(p[0]), r: 4, style: 'fill:' + p[1] }, g);
      });
    }
    var redrawTree = sized(treeHost, drawTree), redrawChart = sized(chartHost, drawChart);
    function readout() {
      var m = memAt(N);
      $('#mt-read').innerHTML =
        '<div><div class="v">' + m.sums + ' + ' + m.verb + '</div><div class="k"><i style="background:var(--mark-dig)"></i>' + (m.sums ? (m.sums === 1 ? 'summary' : 'summaries') + ' plus messages word for word, sent with the next request' : 'nothing to summarize yet: every message goes word for word') + '</div></div>' +
        '<div><div class="v">&asymp; ' + fmt(m.exo) + '</div><div class="k">tokens in that request (assumed sizes)</div></div>' +
        '<div><div class="v">&asymp; ' + fmt(m.plain) + '</div><div class="k"><i style="background:var(--ink-3)"></i>tokens if a plain transcript sent all ' + fmt(N) + ' messages</div></div>';
      $('#mt-corner').textContent = fmt(N) + ' messages · ' + m.L + (m.L === 1 ? ' leaf' : ' leaves');
      range.setAttribute('aria-valuetext', ariaMem(m));
    }
    var playing = false, job = null, playBtn = $('#mt-play');
    function setN(n) { N = Math.max(1, Math.min(NMAX, n)); range.value = N; $('#mt-out').textContent = fmt(N); redrawTree(); drawCur(); readout(); }
    range.addEventListener('input', function () { setN(+range.value); });
    $('#mt-add1').addEventListener('click', function () { setN(N + 1); });
    $('#mt-add8').addEventListener('click', function () { setN(N + 8); });
    function stop() { playing = false; playBtn.setAttribute('aria-pressed', 'false'); if (job) job.stop(); }
    playBtn.addEventListener('click', function () {
      if (playing) { stop(); return; }
      if (!motion() || !F0.loop) { setN(N >= NMAX ? 1 : N + 50); return; } // stepped when motion is off
      if (N >= NMAX) setN(1);
      playing = true; playBtn.setAttribute('aria-pressed', 'true');
      job = F0.loop(function () { if (N >= NMAX) { stop(); return; } setN(N + 3); });
      job.start();
    });
    if (F0.whenVisible) F0.whenVisible($('.mt'), null, function () { if (playing) stop(); });
    if (F0.onMotion) F0.onMotion(function (on) { if (!on && playing) stop(); });
    setN(N);
    onTheme(function () { redrawTree(); redrawChart(); });
  }

  /* ======================================================================
     05: THE AUTO-RESEARCH LOOP
     ====================================================================== */
  var AR_STEPS = [
    { id: 'pick', k: 'Step 1 · pick', h: 'Pick an open problem', t: 'A sidebar lists open research projects from the “Auto Research by Super” catalog: GitHub repositories that publish an <code>auto-research.md</code> guide for agents. Press play and the app clones the project.' },
    { id: 'propose', k: 'Step 2 · propose', h: 'Agents work in parallel', t: 'The app hands the guide, word for word, to the coding agent you already have (OpenAI Codex or Claude Code) and shows the conversation live. With parallel agents on, several work at once on the same problem.' },
    { id: 'check', k: 'Step 3 · check', h: 'Keep claims at their true strength', t: 'Every agent carries the same policy: “Separate formal proof, exact finite checks, empirical measurements, conditional results and maintainer acceptance. Never manufacture a record, passing check, publication, or external outcome.” Acceptance itself happens upstream, with each project’s maintainers.' },
    { id: 'pool', k: 'Step 4 · pool', h: 'The timer stops them and the findings merge', t: 'On a timer (every 10 minutes by default) the app stops the agents and asks the model to merge what they found into one shared summary.' },
    { id: 'restart', k: 'Step 5 · restart', h: 'Fresh agents start from the summary', t: 'New agents start again from that shared summary, and the loop goes round. Each round begins with what every agent learned in the last one.' }
  ];
  function initLoop() {
    var svg = $('#ar-svg'); if (!svg) return;
    var step = 1, round = 1, k = 2, timer = 0, playing = false, visible = true;
    var stage = svg.parentNode, W = 360, H = 360, C = [180, 196], R = 108, small = false;
    var ST = { propose: -90, check: 0, pool: 90, restart: 180 };
    function sp(id) { var a = ST[id] * Math.PI / 180; return [C[0] + R * Math.cos(a), C[1] + R * Math.sin(a)]; }
    function geo() {
      var r = stage.getBoundingClientRect();
      W = Math.max(280, Math.round(r.width)); H = Math.max(280, Math.round(r.height)); small = W < 460;
      C = [W / 2, H / 2 + (small ? 24 : 20)]; R = Math.min(W, H) * (small ? 0.27 : 0.3);
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    }
    function draw() {
      geo();
      while (svg.lastChild && svg.lastChild.nodeName !== 'title') svg.removeChild(svg.lastChild);
      var cur = AR_STEPS[step].id;
      // ring arcs between stations, the one leading into the current station lit
      var ids = ['propose', 'check', 'pool', 'restart'];
      ids.forEach(function (id, i) {
        var a0 = (ST[id] + 15) * Math.PI / 180, a1 = (ST[id] + 75) * Math.PI / 180;
        var x0 = C[0] + R * Math.cos(a0), y0 = C[1] + R * Math.sin(a0), x1 = C[0] + R * Math.cos(a1), y1 = C[1] + R * Math.sin(a1);
        var next = ids[(i + 1) % 4], on = next === cur, col = on ? 'var(--bio)' : 'var(--line-ui)';
        el('path', { d: 'M' + x0.toFixed(1) + ' ' + y0.toFixed(1) + 'A' + R + ' ' + R + ' 0 0 1 ' + x1.toFixed(1) + ' ' + y1.toFixed(1), fill: 'none', style: 'stroke:' + col, 'stroke-width': on ? 2 : 1 }, svg);
        var ah = a1, tx = -Math.sin(ah), ty = Math.cos(ah);
        el('path', { d: 'M' + (x1 - tx * 7 + Math.cos(ah) * 4).toFixed(1) + ' ' + (y1 - ty * 7 + Math.sin(ah) * 4).toFixed(1) + 'L' + x1.toFixed(1) + ' ' + y1.toFixed(1) + 'L' + (x1 - tx * 7 - Math.cos(ah) * 4).toFixed(1) + ' ' + (y1 - ty * 7 - Math.sin(ah) * 4).toFixed(1), fill: 'none', style: 'stroke:' + col, 'stroke-width': on ? 2 : 1 }, svg);
      });
      // catalog box feeding the loop
      var onPick = cur === 'pick', pp = sp('propose');
      el('rect', { x: 8, y: 10, width: 124, height: 44, style: 'fill:var(--bg-2);stroke:' + (onPick ? 'var(--bio)' : 'var(--line-ui)'), 'stroke-width': onPick ? 2 : 1 }, svg);
      el('text', { x: 18, y: 28, text: 'CATALOG', 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink)', 'letter-spacing': '.1em' }, svg);
      el('text', { x: 18, y: 44, text: 'auto-research.md', 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
      el('path', { d: 'M132 32 C ' + (pp[0] - 20) + ' 32, ' + (pp[0] - 44) + ' ' + pp[1] + ', ' + (pp[0] - 26) + ' ' + pp[1], fill: 'none', style: 'stroke:' + (onPick ? 'var(--bio)' : 'var(--line-ui)'), 'stroke-width': onPick ? 2 : 1, 'stroke-dasharray': '3 3' }, svg);
      // the shared summary at the centre
      var dw = small ? 46 : 60, dh = small ? 56 : 72;
      el('rect', { x: C[0] - dw / 2, y: C[1] - dh / 2, width: dw, height: dh, style: 'fill:var(--bg-2);stroke:' + (cur === 'pool' || cur === 'restart' ? 'var(--dig)' : 'var(--line-ui)'), 'stroke-width': cur === 'pool' ? 2 : 1 }, svg);
      var filled = Math.max(0, Math.min(6, (round - 1) + (step >= 3 ? 1 : 0)));
      for (var i = 0; i < 6; i++) { var ly = C[1] - dh / 2 + 12 + i * (dh - 20) / 5; el('line', { x1: C[0] - dw / 2 + 9, x2: C[0] + dw / 2 - (i % 2 ? 17 : 9), y1: ly, y2: ly, style: 'stroke:' + (i < filled ? 'var(--dig)' : 'var(--line)'), 'stroke-width': 2, 'stroke-linecap': 'round' }, svg); }
      el('text', { x: C[0], y: C[1] + dh / 2 + 16, 'text-anchor': 'middle', text: 'SHARED', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.08em' }, svg);
      el('text', { x: C[0], y: C[1] + dh / 2 + 30, 'text-anchor': 'middle', text: 'SUMMARY', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.08em' }, svg);
      // stations
      ids.forEach(function (id) {
        var p = sp(id), on = id === cur;
        el('circle', { cx: p[0], cy: p[1], r: 22, style: 'fill:var(--bg-2);stroke:' + (on ? 'var(--bio)' : 'var(--line-ui)'), 'stroke-width': on ? 2 : 1 }, svg);
        var lab = { propose: 'PROPOSE', check: 'CHECK', pool: 'POOL', restart: 'RESTART' }[id];
        var lx = p[0], ly = p[1] + (id === 'propose' ? -30 : 40), anchor = 'middle';
        if (small && id === 'pool') { lx += 30; ly = p[1] + 4; anchor = 'start'; }
        if (!small && id === 'check') { lx += 30; ly = p[1] + 4; anchor = 'start'; }
        if (!small && id === 'restart') { lx -= 30; ly = p[1] + 4; anchor = 'end'; }
        el('text', { x: lx, y: ly, 'text-anchor': anchor, text: lab, 'font-size': 11, 'font-weight': on ? 600 : 500, style: 'fill:' + (on ? 'var(--ink)' : 'var(--ink-2)'), 'letter-spacing': '.1em' }, svg);
        var ink = 'stroke:' + (on ? 'var(--ink)' : 'var(--ink-2)');
        if (id === 'check') el('path', { d: 'M' + (p[0] - 7) + ' ' + p[1] + 'l5 5l9-10', fill: 'none', style: ink, 'stroke-width': 1.8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
        if (id === 'pool') el('path', { d: 'M' + (p[0] - 9) + ' ' + (p[1] - 7) + 'L' + p[0] + ' ' + (p[1] + 3) + 'L' + (p[0] + 9) + ' ' + (p[1] - 7) + 'M' + p[0] + ' ' + (p[1] + 3) + 'V' + (p[1] + 9), fill: 'none', style: ink, 'stroke-width': 1.8, 'stroke-linecap': 'round' }, svg);
        if (id === 'restart') el('path', { d: 'M' + (p[0] + 8) + ' ' + (p[1] - 4) + 'A9 9 0 1 0 ' + (p[0] + 8) + ' ' + (p[1] + 5) + 'M' + (p[0] + 8) + ' ' + (p[1] - 10) + 'V' + (p[1] - 3) + 'H' + (p[0] + 2), fill: 'none', style: ink, 'stroke-width': 1.8, 'stroke-linecap': 'round' }, svg);
      });
      // agents: k dots on the propose station; during pool they feed the summary
      var pr = sp('propose');
      for (var a = 0; a < k; a++) {
        var ax = pr[0] + (a - (k - 1) / 2) * 12, ay = pr[1];
        if (cur === 'pool') el('line', { x1: ax, y1: ay + 4, x2: C[0], y2: C[1] - dh / 2, style: 'stroke:var(--dig)', 'stroke-width': 1.2, opacity: 0.8 }, svg);
        var active = cur === 'propose' || cur === 'check';
        el('circle', { cx: ax, cy: ay, r: 5, style: 'fill:' + (active ? 'var(--mark-dig)' : cur === 'restart' ? 'var(--bg-2)' : 'var(--ink-3)') + ';stroke:' + (cur === 'restart' ? 'var(--mark-dig)' : 'var(--bg-2)'), 'stroke-width': 2 }, svg);
      }
      if (cur === 'check') {
        var cp = sp('check'), lines = ['proof', 'exact check', 'measured', 'conditional'];
        lines.forEach(function (t, i) {
          if (!small) el('text', { x: cp[0] - 16, y: cp[1] + 46 + i * 14, text: '· ' + t, 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
        });
      }
      el('text', { x: W - 8, y: H - 8, 'text-anchor': 'end', text: k + (k === 1 ? ' AGENT' : ' AGENTS') + ' · 10 MIN', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.08em' }, svg);
    }
    function readout() {
      var s = AR_STEPS[step];
      $('#ar-read').innerHTML = '<p class="ar-k">' + esc(s.k) + (step > 0 ? ' &middot; round ' + round : '') + '</p><p class="ar-h">' + esc(s.h) + '</p><p>' + s.t + '</p>';
      $('#ar-corner').textContent = 'Step ' + (step + 1) + ' of 5' + (step > 0 ? ' · round ' + round : '');
    }
    function go(d) {
      step += d;
      if (step > 4) { step = 1; round = Math.min(round + 1, 9); }
      if (step < 0) step = 0;
      if (step === 0 && d < 0) round = 1;
      draw(); readout();
    }
    $('#ar-next').addEventListener('click', function () { go(1); });
    $('#ar-prev').addEventListener('click', function () { if (step === 1 && round > 1) { step = 4; round--; draw(); readout(); } else go(-1); });
    $$('#ar-k button').forEach(function (b) {
      b.addEventListener('click', function () { k = +b.getAttribute('data-k'); $$('#ar-k button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); draw(); });
    });
    var playBtn = $('#ar-play');
    function stop() { playing = false; clearInterval(timer); playBtn.setAttribute('aria-pressed', 'false'); }
    playBtn.addEventListener('click', function () {
      if (playing) { stop(); return; }
      if (!motion()) { go(1); return; } // stepped when motion is off
      playing = true; playBtn.setAttribute('aria-pressed', 'true');
      timer = setInterval(function () { if (!visible || document.hidden || !motion()) { stop(); return; } go(1); }, 2400);
    });
    if (F0.whenVisible) F0.whenVisible($('.ar'), function () { visible = true; }, function () { visible = false; if (playing) stop(); });
    if (F0.onMotion) F0.onMotion(function (on) { if (!on && playing) stop(); });
    // text twin
    var ol = $('#ar-list');
    AR_STEPS.forEach(function (s) { h('li', null, ol, '<b>' + esc(s.h) + '.</b> ' + s.t); });
    draw(); readout();
    if ('ResizeObserver' in window) { var lw = 0; new ResizeObserver(function () { var w = Math.round(stage.getBoundingClientRect().width); if (w && w !== lw) { lw = w; draw(); } }).observe(stage); }
    onTheme(draw);
  }

  /* ======================================================================
     06: AUTOFOUNDRY, one experiment fanned out over four clouds (simulated)
     ====================================================================== */
  var CLOUDS = ['RunPod', 'Vast.ai', 'PRIME Intellect', 'Lambda Labs'];
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function gauss(r) { var u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  var MU = { A: 1.000, B: 0.995 }, SD = 0.006;
  function draw4(k, seed) {
    var r = rng(seed), runs = { A: [], B: [] }, speed = {};
    ['A', 'B'].forEach(function (x) {
      CLOUDS.forEach(function (c) { for (var m = 1; m <= k; m++) { runs[x].push({ cloud: c, m: m, v: MU[x] + SD * gauss(r), sp: 0.55 + 0.45 * r() }); } });
    });
    return runs;
  }
  function stats(a) {
    var n = a.length, vs = a.map(function (x) { return x.v; }), mean = vs.reduce(function (s, v) { return s + v; }, 0) / n;
    var sd = n > 1 ? Math.sqrt(vs.reduce(function (s, v) { return s + (v - mean) * (v - mean); }, 0) / (n - 1)) : 0;
    return { n: n, mean: mean, sd: sd, best: Math.min.apply(null, vs), worst: Math.max.apply(null, vs) };
  }
  function initFoundry() {
    var fan = $('#af-fan'), strip = $('#af-strip'); if (!fan) return;
    var k = 1, seed = 11, runs = draw4(k, seed), phase = { exp: null, p: 1 }, job = null, running = false;
    var fanSvg = null, stripSvg = null;
    function drawFan(W) {
      if (fanSvg) fanSvg.remove();
      var small = W < 560, boxW = small ? 76 : 120, labW = small ? 96 : 128, gap = small ? 18 : 40, rowH = 34, top = 4;
      var cellsX = boxW + gap + labW, cellsW = W - cellsX - 10, cw = Math.min(150, (cellsW - (k - 1) * 6) / k);
      var H = top + CLOUDS.length * rowH + 4;
      var svg = fanSvg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': 'autofoundry sends one training script to ' + (4 * k) + ' rented machines: ' + k + ' on each of RunPod, Vast.ai, PRIME Intellect and Lambda Labs.' });
      fan.insertBefore(svg, fan.firstChild);
      var by = top + (CLOUDS.length * rowH) / 2;
      el('rect', { x: 1, y: by - 26, width: boxW - 2, height: 52, style: 'fill:var(--bg-2);stroke:var(--line-ui)' }, svg);
      el('text', { x: 12, y: by - 6, text: 'train.py', 'font-size': 12, 'font-weight': 600, style: 'fill:var(--ink)' }, svg);
      el('text', { x: 12, y: by + 12, text: phase.exp ? 'running ' + phase.exp : 'A and B', 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
      CLOUDS.forEach(function (c, i) {
        var y = top + i * rowH + rowH / 2;
        el('path', { d: 'M' + boxW + ' ' + by + ' C ' + (boxW + gap * 0.6) + ' ' + by + ', ' + (boxW + gap * 0.4) + ' ' + y + ', ' + (boxW + gap) + ' ' + y, fill: 'none', style: 'stroke:var(--line-ui)', 'stroke-width': 1 }, svg);
        el('text', { x: boxW + gap + 6, y: y + 4, text: small && c === 'PRIME Intellect' ? 'PRIME Int.' : c, 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
        for (var m = 0; m < k; m++) {
          var x = cellsX + m * (cw + 6), exp = phase.exp || 'B', run = runs[exp].filter(function (r) { return r.cloud === c; })[m];
          var p = phase.exp ? Math.min(1, phase.p / run.sp) : 1, live = phase.exp && p < 1;
          el('rect', { x: x, y: y - 11, width: cw, height: 22, style: 'fill:var(--bg-2);stroke:' + (live ? 'var(--ink-2)' : 'var(--line-ui)') }, svg);
          if (live) el('rect', { x: x + 1, y: y - 10, width: Math.max(0, (cw - 2) * p), height: 20, style: 'fill:color-mix(in srgb, ' + (exp === 'B' ? 'var(--mark-dig)' : 'var(--ink-3)') + ' 35%, transparent)' }, svg);
          var ra = runs.A.filter(function (r) { return r.cloud === c; })[m], rb = runs.B.filter(function (r) { return r.cloud === c; })[m];
          var label = live ? Math.round(p * 100) + '%' : cw >= 132 ? 'off · A ' + ra.v.toFixed(3) + ' B ' + rb.v.toFixed(3) : 'off';
          if (cw >= 30) el('text', { x: x + cw / 2, y: y + 4, 'text-anchor': 'middle', text: label, 'font-size': 11, style: 'fill:' + (live ? 'var(--ink)' : 'var(--ink-3)') }, svg);
        }
      });
      $('#af-corner').textContent = (4 * k) + ' machines · ' + (phase.exp ? 'running ' + phase.exp : 'shut down');
    }
    function drawStrip(W) {
      if (stripSvg) stripSvg.remove();
      var small = W < 560, padL = small ? 70 : 104, padR = small ? 16 : 150, H = 156, x0 = 0.975, x1 = 1.025;
      var X = function (v) { return padL + (Math.max(x0, Math.min(x1, v)) - x0) / (x1 - x0) * (W - padL - padR); };
      var svg = stripSvg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, role: 'img', 'aria-label': ariaStrip() }, strip);
      [0.98, 0.99, 1.00, 1.01, 1.02].forEach(function (t) {
        el('line', { x1: X(t), x2: X(t), y1: 14, y2: H - 24, style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
        el('text', { x: X(t), y: H - 8, 'text-anchor': 'middle', text: t.toFixed(2), 'font-size': 11, style: 'fill:var(--ink-3)' }, svg);
      });
      el('text', { x: padL, y: 10, text: '← LOWER IS BETTER', 'font-size': 11, style: 'fill:var(--ink-3)', 'letter-spacing': '.06em' }, svg);
      [['A', 50, 'var(--ink-3)', small ? 'A' : 'A · baseline'], ['B', 102, 'var(--mark-dig)', small ? 'B' : 'B · change']].forEach(function (row) {
        var e = row[0], y = row[1], col = row[2], rs = runs[e];
        el('text', { x: 4, y: y + 4, text: row[3], 'font-size': 11, 'font-weight': 600, style: 'fill:var(--ink)' }, svg);
        if (!rs.length || (phase.exp === e) || (phase.exp === 'A' && e === 'B')) { el('text', { x: padL, y: y + 4, text: phase.exp ? 'running…' : '', 'font-size': 11, style: 'fill:var(--ink-3)' }, svg); return; }
        var s = stats(rs);
        el('line', { x1: X(s.best), x2: X(s.worst), y1: y, y2: y, style: 'stroke:' + col, 'stroke-width': 2, opacity: 0.55, 'stroke-linecap': 'round' }, svg);
        el('line', { x1: X(s.mean), x2: X(s.mean), y1: y - 15, y2: y + 15, style: 'stroke:var(--ink)', 'stroke-width': 2 }, svg);
        rs.forEach(function (r, i) {
          var jy = y + ((i % 3) - 1) * 7;
          var g = el('g', { class: 'dot' }, svg);
          el('circle', { class: 'hit', cx: X(r.v), cy: jy, r: 11, fill: 'transparent' }, g);
          el('circle', { cx: X(r.v), cy: jy, r: 6, style: 'fill:var(--bg-1)' }, g);
          el('circle', { cx: X(r.v), cy: jy, r: 4, style: 'fill:' + col }, g);
          g.addEventListener('pointermove', function (ev) { tipShow('<div class="tip-k">' + e + ' &middot; ' + esc(r.cloud) + ' &middot; machine ' + r.m + '</div><div class="tip-rows"><div class="tip-row"><span class="tip-v">' + r.v.toFixed(4) + '</span> validation loss</div></div><div class="tip-foot">simulated</div>', ev.clientX, ev.clientY); });
          g.addEventListener('pointerleave', tipHide);
        });
        if (!small) el('text', { x: W - padR + 12, y: y + 4, text: 'mean ' + s.mean.toFixed(4), 'font-size': 11, style: 'fill:var(--ink-2)' }, svg);
      });
    }
    function ariaStrip() {
      if (!runs.A.length || !runs.B.length) return 'Results: running.';
      var a = stats(runs.A), b = stats(runs.B);
      return 'Dot strip of validation loss, lower is better. A: ' + a.n + ' runs, best ' + a.best.toFixed(4) + ', mean ' + a.mean.toFixed(4) + ', worst ' + a.worst.toFixed(4) + '. B: ' + b.n + ' runs, best ' + b.best.toFixed(4) + ', mean ' + b.mean.toFixed(4) + ', worst ' + b.worst.toFixed(4) + '.';
    }
    function verdict() {
      var v = $('#af-verdict');
      if (running) { v.innerHTML = '<b>Running.</b> autofoundry streams each machine&rsquo;s output back as it trains, then collects the numbers it prints after a <code>---</code> line.'; return; }
      var a = stats(runs.A), b = stats(runs.B), diff = a.mean - b.mean, se = Math.sqrt(a.sd * a.sd / a.n + b.sd * b.sd / b.n), z = se > 0 ? diff / se : 0;
      var line = function (n, s) { return '<span class="mono">' + n + ' &nbsp;best ' + s.best.toFixed(4) + ' &middot; mean ' + s.mean.toFixed(4) + ' &middot; worst ' + s.worst.toFixed(4) + '</span>'; };
      var need = 1.96 + 2.4 / Math.max(1, a.n + b.n - 2); // a rough small-sample (Student t) bar for 95% confidence
      var word = z >= need ? '<b>B&rsquo;s lead is ' + z.toFixed(1) + ' times its uncertainty, above the ' + need.toFixed(1) + ' this many runs need: probably real.</b>' : z > 0 ? '<b>B&rsquo;s lead is only ' + z.toFixed(1) + ' times its uncertainty; with ' + a.n + ' runs each it needs about ' + need.toFixed(1) + '. It could still be noise.</b> Rent more machines.' : '<b>In this draw B is not ahead at all</b>, though its true setting is better. That is what noise does with few runs.';
      v.innerHTML = 'What autofoundry reports, for ' + a.n + ' runs each:<br>' + line('A', a) + '<br>' + line('B', b) + '<br>' +
        'B&rsquo;s mean is lower by ' + Math.abs(diff).toFixed(4) + (diff < 0 ? ' (it is higher, so worse)' : '') + '. The means themselves wobble by about &plusmn;' + se.toFixed(4) + ' from draw to draw (the <i>standard error</i>). ' + word;
    }
    function table() {
      var tb = $('#af-table tbody'); tb.innerHTML = '';
      ['A', 'B'].forEach(function (e) { runs[e].forEach(function (r) { h('tr', null, tb, '<td>' + e + '</td><td>' + esc(r.cloud) + '</td><td class="n">' + r.m + '</td><td class="n">' + r.v.toFixed(4) + '</td>'); }); });
    }
    var redrawFan = sized(fan, drawFan), redrawStrip = sized(strip, drawStrip);
    function render() { redrawFan(); redrawStrip(); verdict(); }
    function run() {
      if (running) return;
      seed += 1; runs = draw4(k, seed); running = true;
      var btn = $('#af-run'); btn.setAttribute('aria-pressed', 'true');
      function pass(exp, next) {
        phase = { exp: exp, p: 0 }; render();
        job = animate(1500, function (p) { phase.p = p; redrawFan(); }, function () { next(); });
      }
      pass('A', function () { pass('B', function () { phase = { exp: null, p: 1 }; running = false; btn.setAttribute('aria-pressed', 'false'); render(); table(); }); });
    }
    $('#af-run').addEventListener('click', run);
    $$('#af-k button').forEach(function (b) {
      b.addEventListener('click', function () {
        if (running) return;
        k = +b.getAttribute('data-k'); $$('#af-k button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        run();
      });
    });
    if (F0.onMotion) F0.onMotion(function (on) { if (!on && running && job) { job.stop(); phase = { exp: null, p: 1 }; running = false; $('#af-run').setAttribute('aria-pressed', 'false'); render(); table(); } });
    render(); table();
    onTheme(function () { redrawFan(); redrawStrip(); });
  }

  /* ======================================================================
     05b: rohanarun's record, checked live
     ====================================================================== */
  function initKappa() {
    var box = $('#ar-live'); if (!box || !F0.kappa) return;
    F0.kappa().then(function (r) {
      var k = box.querySelector('.k'), when = r.at ? String(r.at).replace('T', ' ').slice(0, 16) + ' UTC' : '';
      if (r.source === 'live' && String(r.pr) === '1094') {
        box.querySelector('.v').textContent = 'κ = ' + r.decimal;
        k.innerHTML = 'Still the maintainer-reviewed record from PR #1094: checked live against <a href="' + esc(r.url) + '">certificates/selected-result.json</a> <span class="chip"><span class="dot live" aria-hidden="true"></span>live &middot; ' + esc(when) + '</span>';
      } else if (r.source === 'live') {
        box.querySelector('.v').textContent = 'κ = ' + r.decimal + ' (PR #' + r.pr + ')';
        k.innerHTML = 'The reviewed record has moved on since we wrote this: it now comes from PR #' + esc(r.pr) + '. rohanarun&rsquo;s PR #1094 held it on 13&ndash;14 Oct 2026. <span class="chip"><span class="dot live" aria-hidden="true"></span>live &middot; ' + esc(when) + '</span>';
      } else {
        k.innerHTML = 'Reviewed record at the time of writing (selected 13 Oct 2026). The live check could not be reached. <span class="chip"><span class="dot stale" aria-hidden="true"></span>not live</span>';
      }
    }).catch(function () {});
  }

  function init() { initHero(); initConsent(); initMemory(); initLoop(); initFoundry(); initKappa(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
