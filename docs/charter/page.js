/* Foundation0 · Charter page.
   1. "Two futures": three lanes (Asimov's books, the TV series, Foundation0), each drawn as two strands,
      people (gold) and machines (cyan), through five stages. Pick a path, step stages, or Play.
      Starts paused on the books' first stage. Data: charter/futures.json. SVG styled by tokens via CSS,
      so a theme change needs no redraw; layout redraws on resize.
   2. Principles filter (fear / dependence / secrecy).
   3. Founding members, rendered from data/members.json (a pre-rendered copy ships in the HTML).
   4. Draft a ledger entry: a form checked against data/ledger.schema.json's rules, with a live preview,
      a prefilled GitHub issue link and the JSON. Nothing is sent anywhere by this page. */
(function () {
  'use strict';
  var F0 = window.F0, esc = F0.esc;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  var NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }

  var GLYPH = { books: 'g-book', show: 'g-show', ours: 'g-ours' };
  var LYR = { books: 'b', show: 's', ours: 'o' };
  var FAIL = { fear: 'Fails through fear', dependence: 'Fails through dependence', secrecy: 'Fails through secrecy', fall: 'The fall still comes' };
  var OURS_PR = [['0.3', '0.4'], ['0.1', '0.3'], ['0.5', '0.6'], ['0.2', '0.8'], ['0.1', '0.7']];

  /* ===================== 1. two futures ===================== */
  /* strands: keys are [u, v] with u in 0..1 across the plot and v in lane half-heights (negative = up).
     segs: [u0, u1, style] with style solid | dash | dot | thin. p: carries the travelling marker. */
  var LANES = {
    books: [
      { c: 'bio', p: 1, keys: [[0, -.38], [.1, -.38], [.3, -.12], [.42, -.15], [.53, -.6], [.86, -.6]], segs: [[0, .21, 'solid'], [.21, .45, 'thin'], [.45, .8, 'solid'], [.8, .86, 'dot']] },
      { c: 'bio', keys: [[.86, -.6], [1, -.95]], segs: [[.86, 1, 'solid']] },
      { c: 'bio', keys: [[.86, -.6], [1, -.22]], segs: [[.86, 1, 'dash']] },
      { c: 'dig', p: 1, keys: [[0, .38], [.1, .38], [.3, .1], [.42, .15], [.53, .55], [.64, .82], [1, .82]], segs: [[0, .5, 'solid'], [.5, .6, 'thin'], [.6, 1, 'dash']] },
      { c: 'dig', keys: [[.17, .38], [.3, -.34], [.43, .16]], segs: [[.17, .43, 'thin']] },
      { c: 'dig', keys: [[.19, .38], [.3, .32], [.43, .16]], segs: [[.19, .43, 'thin']] },
      { c: 'dig', keys: [[.15, .38], [.27, -.05], [.33, .02], [.45, .2]], segs: [[.15, .45, 'thin']] }
    ],
    show: [
      { c: 'bio', p: 1, keys: [[0, -.38], [.3, -.38], [.44, -.08], [.5, 0], [.57, -.5], [1, -.5]], segs: [[0, .8, 'solid'], [.8, .86, 'dot'], [.86, 1, 'solid']] },
      { c: 'dig', p: 1, keys: [[0, .38], [.3, .38], [.44, .08], [.5, 0]], segs: [[0, .5, 'solid']] },
      { c: 'dig', keys: [[.16, .38], [.3, .62], [.44, .3], [.5, .02]], segs: [[.16, .49, 'thin']] },
      { c: 'dig', keys: [[.18, .38], [.3, .86], [.44, .45], [.5, .04]], segs: [[.18, .49, 'thin']] },
      { c: 'dig', p: 1, keys: [[.53, .5], [.62, .8], [1, .8]], segs: [[.53, 1, 'dash']] }
    ],
    ours: (function () {
      var g = [], d = [];
      for (var i = 0; i <= 40; i++) { var u = i / 40, v = .4 * Math.cos(Math.PI * 2 * u / .2); g.push([u, -v]); d.push([u, v]); }
      return [{ c: 'bio', p: 1, keys: g, segs: [[0, 1, 'solid']] }, { c: 'dig', p: 1, keys: d, segs: [[0, 1, 'solid']] }];
    })()
  };
  /* hidden guidance: faint ticks from the hidden machine thread up toward the people */
  var TICKS = { books: [.66, .72, .78, .9, .96], show: [.68, .76, .84, .92] };
  var CROSS = { show: [.5, 0] };
  var NOTES = {
    books: [[.3, -1.02, 'dependence'], [.75, 1.12, 'hidden'], [.83, -1.02, 'dark age'], [.94, .2, 'two Foundations']],
    show: [[.5, -1.02, 'war'], [.75, 1.12, 'hidden'], [.83, -1.02, 'the fall'], [.94, -1.02, 'in exile']],
    ours: [[.5, -1.02, 'in the open'], [.9, -1.02, 'no dark age']]
  };

  function vAt(keys, u) {
    if (u <= keys[0][0]) return keys[0][1];
    for (var i = 0; i < keys.length - 1; i++) {
      var a = keys[i], b = keys[i + 1];
      if (u <= b[0]) { var t = (u - a[0]) / (b[0] - a[0] || 1), s = (1 - Math.cos(Math.PI * t)) / 2; return a[1] + (b[1] - a[1]) * s; }
    }
    return keys[keys.length - 1][1];
  }

  function futures(D, ledgerCount) {
    var fig = $('#fut-fig'); if (!fig) return;
    var svg = $('#fut-svg'), stage = $('#fut-stage'), card = $('#fut-card'), out = $('#fut-out');
    var paths = D.paths, order = paths.map(function (p) { return p.key; });
    var st = { path: 'books', stage: 0, playing: false };
    var geo = null, marks = {};

    function laneOf(key) { return order.indexOf(key); }
    function draw() {
      var W = Math.max(300, Math.round(stage.getBoundingClientRect().width));
      var small = W < 640;
      var top = small ? 26 : 34, LH = small ? 96 : 112, pad = small ? 10 : 18, lab = 18;
      var H = top + LH * 3 + 6;
      var x0 = pad, x1 = W - pad, pw = x1 - x0;
      geo = { W: W, H: H, x0: x0, pw: pw, top: top, LH: LH, lab: lab, small: small };
      svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H); svg.setAttribute('width', W); svg.setAttribute('height', H);
      svg.innerHTML = '';
      var gBand = el('g', {}, svg);
      marks.band = el('rect', { class: 'fx-band', y: top - 4, height: H - top + 2, rx: 2 }, gBand);
      /* stage columns */
      var gCols = el('g', { class: 'fx-cols' }, svg);
      for (var k = 0; k < 5; k++) {
        var cx = x0 + (k + .5) * pw / 5;
        if (k) el('line', { x1: x0 + k * pw / 5, x2: x0 + k * pw / 5, y1: top - 6, y2: H - 4, class: 'fx-sep' }, gCols);
        var t = el('text', { x: cx, y: small ? 14 : 18, class: 'fx-stage', 'text-anchor': 'middle' }, gCols);
        t.textContent = small ? String(k + 1) : (k + 1) + ' · ' + D.stages[k];
      }
      /* lanes */
      marks.lanes = {};
      paths.forEach(function (P, li) {
        var yT = top + li * LH, cy = yT + lab + (LH - lab) / 2, h = (LH - lab) / 2 - 10;
        var g = el('g', { class: 'fx-lane fx-' + P.key }, svg);
        el('line', { x1: x0, x2: x1, y1: yT, y2: yT, class: 'fx-rule' }, g);
        var lt = el('text', { x: x0, y: yT + 14, class: 'fx-lt' }, g);
        lt.textContent = (P.layer + ' · ' + P.label).toUpperCase();
        function X(u) { return x0 + u * pw; }
        function Y(v) { return cy + v * h; }
        /* hidden guidance ticks */
        (TICKS[P.key] || []).forEach(function (u) {
          var s = LANES[P.key].filter(function (s) { return s.c === 'dig' && s.p && u >= s.keys[0][0] && u <= s.keys[s.keys.length - 1][0]; })[0];
          var gs = LANES[P.key][0];
          if (s) el('line', { x1: X(u), x2: X(u), y1: Y(vAt(s.keys, u)) - 4, y2: Y(vAt(gs.keys, u)) + 6, class: 'fx-tick' }, g);
        });
        LANES[P.key].forEach(function (s) {
          s.segs.forEach(function (sg) {
            var d = '', n = Math.max(2, Math.ceil((sg[1] - sg[0]) * 160));
            for (var i = 0; i <= n; i++) { var u = sg[0] + (sg[1] - sg[0]) * i / n; d += (i ? 'L' : 'M') + X(u).toFixed(1) + ' ' + Y(vAt(s.keys, u)).toFixed(1); }
            el('path', { d: d, class: 'fx-s fx-' + s.c + ' fx-' + sg[2] }, g);
          });
        });
        if (CROSS[P.key]) {
          var cxx = X(CROSS[P.key][0]), cyy = Y(CROSS[P.key][1]);
          el('path', { d: 'M' + (cxx - 7) + ' ' + (cyy - 7) + 'L' + (cxx + 7) + ' ' + (cyy + 7) + 'M' + (cxx + 7) + ' ' + (cyy - 7) + 'L' + (cxx - 7) + ' ' + (cyy + 7), class: 'fx-x' }, g);
        }
        if (!small) (NOTES[P.key] || []).forEach(function (n) {
          var tx = el('text', { x: X(n[0]), y: Y(n[1]) + (n[1] > 0 ? 4 : 0), class: 'fx-note', 'text-anchor': 'middle' }, g);
          tx.textContent = n[2];
        });
        /* travelling markers (people, machines) */
        var mb = el('circle', { r: 5, class: 'fx-mk fx-mk-bio' }, g), md = el('circle', { r: 5, class: 'fx-mk fx-mk-dig' }, g);
        marks.lanes[P.key] = { g: g, mb: mb, md: md, X: X, Y: Y };
      });
      /* clickable lane areas (pointer convenience; keyboard uses the buttons) */
      paths.forEach(function (P, li) {
        var r = el('rect', { x: 0, y: top + li * LH, width: W, height: LH, class: 'fx-hit' }, svg);
        r.addEventListener('click', function (e) {
          var bx = svg.getBoundingClientRect(), u = (e.clientX - bx.left - x0) / pw;
          go(P.key, Math.max(0, Math.min(4, Math.floor(u * 5))), true);
        });
      });
      paint(st.stage, false);
    }

    function uOf(k) { return (k + .5) / 5; }
    function placeMarkers(key, u) {
      var L = marks.lanes[key]; if (!L) return;
      ['bio', 'dig'].forEach(function (c) {
        var s = LANES[key].filter(function (s) { return s.c === c && s.p && u >= s.keys[0][0] - 1e-6 && u <= s.keys[s.keys.length - 1][0] + 1e-6; })[0];
        var m = c === 'bio' ? L.mb : L.md;
        if (!s) { m.setAttribute('opacity', 0); return; }
        m.setAttribute('opacity', 1);
        m.setAttribute('cx', L.X(u).toFixed(1)); m.setAttribute('cy', L.Y(vAt(s.keys, u)).toFixed(1));
      });
    }

    var tween = null, tw = { from: 0, to: 0, t0: 0, key: null };
    function paint(prevStage, animate) {
      if (!geo) return;
      order.forEach(function (k) {
        var L = marks.lanes[k];
        L.g.classList.toggle('on', k === st.path);
        L.mb.style.display = L.md.style.display = k === st.path ? '' : 'none';
      });
      var bw = geo.pw / 5;
      marks.band.setAttribute('x', (geo.x0 + st.stage * bw + 2).toFixed(1));
      marks.band.setAttribute('width', (bw - 4).toFixed(1));
      var to = uOf(st.stage);
      if (animate && F0.motion() && prevStage !== st.stage) {
        tw = { from: uOf(prevStage), to: to, t0: performance.now(), key: st.path };
        if (!tween) tween = F0.loop(function (now) {
          var t = Math.min(1, (now - tw.t0) / 900), e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
          placeMarkers(tw.key, tw.from + (tw.to - tw.from) * e);
          if (t >= 1) tween.stop();
        });
        tween.start();
      } else {
        if (tween) tween.stop();
        placeMarkers(st.path, to);
      }
    }

    function cardHTML(P, k) {
      var w = P.points[k], h = '';
      h += '<div class="fc-head"><span class="lyr ' + LYR[P.key] + '"><svg aria-hidden="true"><use href="#' + GLYPH[P.key] + '"/></svg>' + esc(P.layer) + '</span><span class="fc-stage">Stage ' + (k + 1) + ' of 5 &middot; ' + esc(D.stages[k]) + '</span></div>';
      h += '<h3 class="fc-t">' + esc(w.title) + '</h3>';
      if (P.key === 'ours') {
        if (w.fact) h += '<p class="fc-p fc-fact"><span class="fc-tag">On the record</span>' + esc(w.fact.replace('{ledger}', ledgerCount)) + '</p>';
        if (w.thesis) h += '<p class="fc-p fc-thesis"><span class="fc-tag o">Our thesis</span>' + esc(w.thesis) + '</p>';
        h += '<p class="fc-fail">Principles: ' + OURS_PR[k].map(function (n) { return '<a href="#principles">' + n + '</a>'; }).join(', ') + '</p>';
      } else {
        h += '<p class="fc-p">' + esc(w.text) + '</p>';
        if (w.fail) h += '<p class="fc-fail">' + esc(FAIL[w.fail]) + '</p>';
      }
      h += '<ul class="src-list fc-src" aria-label="Sources">' + w.src.map(function (id) {
        var s = D.sources[id]; if (!s) return '';
        var href = s.local ? '../' + s.url : s.url;
        return '<li><a href="' + esc(href) + '">' + esc(s.label) + '</a></li>';
      }).join('') + '</ul>';
      return h;
    }

    function go(key, k, animate) {
      var prev = key === st.path ? st.stage : -1;
      if (key !== st.path) animate = false;
      st.path = key; st.stage = k;
      var P = paths[laneOf(key)];
      $$('.fut-paths button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-path') === key ? 'true' : 'false'); });
      $$('#fut-stgs button').forEach(function (b, i) { b.setAttribute('aria-pressed', i === k ? 'true' : 'false'); });
      $('#fut-prev').disabled = k === 0 && laneOf(key) === 0;
      $('#fut-next').disabled = k === 4 && laneOf(key) === order.length - 1;
      out.textContent = P.short + ' · stage ' + (k + 1) + ' of 5 · ' + D.stages[k];
      card.innerHTML = cardHTML(P, k);
      card.setAttribute('data-path', key);
      paint(prev < 0 ? k : prev, animate);
    }
    function step(d) {
      var li = laneOf(st.path), k = st.stage + d;
      if (k > 4) { if (li < order.length - 1) { li++; k = 0; } else { k = 4; stopPlay(); } }
      else if (k < 0) { if (li > 0) { li--; k = 4; } else k = 0; }
      go(order[li], k, true);
    }

    /* play: every stage of every path, from where you are */
    var timer = 0, playBtn = $('#fut-play'), visible = true;
    function tick() { if (!st.playing) return; if (st.stage === 4 && laneOf(st.path) === order.length - 1) { stopPlay(); return; } step(1); timer = setTimeout(tick, 3800); }
    function startPlay() {
      if (st.stage === 4 && laneOf(st.path) === order.length - 1) go(order[0], 0, false);
      st.playing = true; playBtn.setAttribute('aria-pressed', 'true'); playBtn.setAttribute('aria-label', 'Pause');
      clearTimeout(timer); timer = setTimeout(tick, 2400);
    }
    function stopPlay() { st.playing = false; clearTimeout(timer); playBtn.setAttribute('aria-pressed', 'false'); playBtn.setAttribute('aria-label', 'Play every stage of every path'); }
    playBtn.addEventListener('click', function () { if (st.playing) stopPlay(); else startPlay(); });
    F0.onMotion(function (on) { if (!on) stopPlay(); });
    F0.whenVisible(fig, function () { visible = true; }, function () { visible = false; if (st.playing) stopPlay(); });

    $$('.fut-paths button').forEach(function (b) { b.addEventListener('click', function () { stopPlay(); go(b.getAttribute('data-path'), st.stage, false); }); });
    $$('#fut-stgs button').forEach(function (b, i) { b.addEventListener('click', function () { stopPlay(); go(st.path, i, true); }); });
    $('#fut-prev').addEventListener('click', function () { stopPlay(); step(-1); });
    $('#fut-next').addEventListener('click', function () { stopPlay(); step(1); });
    fig.addEventListener('keydown', function (e) {
      if (!e.target.closest('.fut-ctrl, .fut-paths')) return;
      var li = laneOf(st.path);
      if (e.key === 'ArrowRight') { stopPlay(); step(1); }
      else if (e.key === 'ArrowLeft') { stopPlay(); step(-1); }
      else if (e.key === 'ArrowDown' && e.target.closest('.fut-paths')) { stopPlay(); go(order[Math.min(order.length - 1, li + 1)], st.stage, false); }
      else if (e.key === 'ArrowUp' && e.target.closest('.fut-paths')) { stopPlay(); go(order[Math.max(0, li - 1)], st.stage, false); }
      else return;
      e.preventDefault();
      var b = e.target.closest('.fut-paths') ? $('.fut-paths button[aria-pressed="true"]') : e.target.closest('#fut-stgs') ? $('#fut-stgs button[aria-pressed="true"]') : null;
      if (b) b.focus();
    });

    if ('ResizeObserver' in window) { var lastW = 0; new ResizeObserver(function () { var w = Math.round(stage.getBoundingClientRect().width); if (w !== lastW) { lastW = w; draw(); } }).observe(stage); }
    else window.addEventListener('resize', draw);
    draw();
    go('books', 0, false);

    /* the table twin, with the live ledger count */
    var twin = $('#futures .twin .table-wrap');
    if (twin) twin.innerHTML = futTable(D, ledgerCount);
  }

  function futTable(D, ledgerCount) {
    var rows = '';
    D.paths.forEach(function (P) {
      P.points.forEach(function (w, k) {
        var txt = P.key === 'ours'
          ? (w.fact ? '<b>On the record:</b> ' + esc(w.fact.replace('{ledger}', ledgerCount)) + ' ' : '') + (w.thesis ? '<b>Our thesis:</b> ' + esc(w.thesis) : '')
          : esc(w.text);
        var src = w.src.map(function (id) { var s = D.sources[id]; return s ? '<a href="' + esc(s.local ? '../' + s.url : s.url) + '">' + esc(s.label) + '</a>' : ''; }).join('; ');
        rows += '<tr><th scope="row">' + esc(P.layer) + '</th><td>' + (k + 1) + ' &middot; ' + esc(D.stages[k]) + '</td><td><b>' + esc(w.title) + '.</b> ' + txt + '</td><td>' + src + '</td></tr>';
      });
    });
    return '<table class="tbl"><caption>Three paths, five stages each</caption><thead><tr><th scope="col">Telling</th><th scope="col">Stage</th><th scope="col">What happens</th><th scope="col">Sources</th></tr></thead><tbody>' + rows + '</tbody></table>';
  }

  /* ===================== 2. principles filter ===================== */
  function principles() {
    var seg = $('#pr-seg'), list = $('#prn'), outEl = $('#pr-out'); if (!seg) return;
    var cards = $$('.pc', list), counts = { fear: 0, dependence: 0, secrecy: 0 };
    cards.forEach(function (c) { c.getAttribute('data-f').split(' ').forEach(function (f) { counts[f]++; }); });
    $$('button', seg).forEach(function (b) { var f = b.getAttribute('data-f'), n = $('.n', b); if (n && counts[f] !== undefined) n.textContent = counts[f]; });
    seg.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var f = b.getAttribute('data-f'), n = 0;
      $$('button', seg).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      list.classList.toggle('filtered', f !== 'all');
      cards.forEach(function (c) { var hit = f === 'all' || c.getAttribute('data-f').split(' ').indexOf(f) >= 0; c.classList.toggle('hit', hit && f !== 'all'); if (hit) n++; });
      outEl.textContent = f === 'all' ? '' : n + ' of 8 principles answer ' + f + '.';
    });
  }

  /* ===================== 3. members ===================== */
  function firstSentence(s) { var m = String(s).match(/^.*?[.!?](?=\s+[A-Z(]|$)/); return m ? m[0] : s; }
  var PAGE_LBL = { 'research/incentre-lattice/': 'Incentre lattice', 'research/exoplanets/': 'Exoplanets', 'research/integer-multiplication/': 'Integer multiplication', 'research/mobius-x1/': 'mobius-x1', 'research/gf2m-circuits/': 'gf2m-circuits', 'instruments/#auto-research': 'Instruments: Auto-research-agent', 'instruments/#autofoundry': 'Instruments: autofoundry' };
  function memberHTML(m, i) {
    var mp = m.main_project || {};
    return '<article class="mcard" id="m-' + esc(m.login) + '"><div class="mc-id">' +
      '<p class="idx">M&middot;' + String(i + 1).padStart(2, '0') + ' &middot; founding member</p>' +
      '<h3>' + esc(m.name) + '</h3>' +
      '<a class="gh" href="' + esc(m.github) + '">@' + esc(m.login) + '</a>' +
      '<p class="mc-main"><span>Main project</span>' + (mp.page ? '<a href="../' + esc(mp.page) + '">' + esc(mp.name) + '</a>' : esc(mp.name)) +
      (mp.url ? '<a class="mc-repo" href="' + esc(mp.url) + '">repository</a>' : '') + (mp.site ? '<a class="mc-repo" href="' + esc(mp.site) + '">site</a>' : '') + '</p>' +
      '<p class="sum">' + esc(firstSentence(m.summary)) + '</p></div>' +
      '<div class="mc-work"><p class="mc-wk">Their research</p>' +
      '<ul class="worklist">' + (m.work || []).map(function (w) {
        return '<li><a href="' + esc(w.url) + '">' + esc(w.name) + '</a><span class="badges">' + F0.statusBadges(w.status) + '</span>' + (w.note ? '<p>' + esc(w.note) + (w.builds_on ? ' <span class="bo">Builds on ' + esc(w.builds_on) + '.</span>' : '') + '</p>' : '') +
          (w.page ? '<p class="bo mc-on">On Foundation0: <a href="../' + esc(w.page) + '">' + esc(PAGE_LBL[w.page] || w.name) + '</a></p>' : '') + '</li>';
      }).join('') + '</ul></div></article>';
  }
  function members(M) {
    var host = $('#mcards'); if (!host || !M) return;
    host.innerHTML = M.members.map(memberHTML).join('');
    var words = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'];
    $$('[data-ch="mcount"]').forEach(function (e) { e.textContent = words[M.members.length] || M.members.length; });
    $$('[data-ch="mupdated"]').forEach(function (e) { e.textContent = M.updated; });
  }

  /* ===================== 4. draft a ledger entry ===================== */
  var DOMAIN = { mathematics: 'Mathematics', computing: 'Computing', biology: 'Biology', medicine: 'Medicine', 'chemistry-materials': 'Chemistry and materials', physics: 'Physics', 'astronomy-space': 'Astronomy and space', 'earth-climate': 'Earth and climate', energy: 'Energy', 'engineering-robotics': 'Engineering and robotics', 'science-of-science': 'Science of science' };
  var EVID = { 'formally-verified': ['v', 5, 'Formally verified'], 'independently-replicated': ['v', 4, 'Replicated'], 'peer-reviewed': ['r', 3, 'Peer reviewed'], deployed: ['d', 3, 'Deployed'], preprint: ['p', 2, 'Preprint'], claimed: ['c', 1, 'Claimed'] };
  var ROLE = { instrument: ['Instrument', 'M0 0L0 -7A7 7 0 0 1 7 0Z'], collaborator: ['Collaborator', 'M0 0L0 -7A7 7 0 0 1 0 7Z'], originator: ['Originator', 'M0 0L0 -7A7 7 0 1 1 -7 0Z'] };
  var ISSUE = 'https://github.com/aska-digital/frontier-math/issues/new';
  var KEY = 'f0-ledger-draft';

  function draft() {
    var form = $('#draft-form'); if (!form) return;
    var f = form.elements, prev = $('#d-prev'), checks = $('#d-checks'), issue = $('#d-issue'), json = $('#d-json'), msg = $('#d-msg');
    function words(s) { return String(s).trim().split(/\s+/).filter(Boolean).length; }
    function list(s) { return String(s || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean); }
    function slugify(s) { return String(s).toLowerCase().normalize('NFKD').replace(/[^\w\s-]/g, '').trim().replace(/[\s_]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '').slice(0, 80).replace(/-$/, ''); }
    function role() { var r = form.querySelector('input[name="ai_role"]:checked'); return r ? r.value : ''; }

    /* restore an unsent draft (this browser only) */
    try { var saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved) Object.keys(saved).forEach(function (k) { var x = f[k]; if (!x) return; if (k === 'ai_role') { var r = form.querySelector('input[name="ai_role"][value="' + saved[k] + '"]'); if (r) r.checked = true; } else if (x.type === 'checkbox') x.checked = !!saved[k]; else x.value = saved[k]; }); } catch (e) { /* storage unavailable: start empty */ }

    function entry() {
      var e = {
        id: slugify(f.title.value), date: f.date.value.trim(), date_basis: f.date_basis.value, title: f.title.value.trim(),
        domain: f.domain.value, subfield: f.subfield.value.trim(), summary: f.summary.value.trim(), before_after: null,
        why_it_matters: f.why_it_matters.value.trim(), ai_systems: list(f.ai_systems.value), organizations: list(f.organizations.value),
        ai_role: role(), evidence: f.evidence.value, contested: f.contested.checked, contested_note: f.contested.checked ? f.contested_note.value.trim() : '',
        significance: null, sources: [{ label: f.source_label.value.trim(), url: f.source_url.value.trim() }], foundation0: false
      };
      return e;
    }
    function run() {
      var e = entry(), today = new Date().toISOString().slice(0, 10);
      f.contested_note.disabled = !f.contested.checked;
      $('#d-title-n').textContent = e.title.length + ' / 90';
      $('#d-sum-n').textContent = words(e.summary) + ' words, ' + e.summary.length + ' / 420 characters';
      var C = [
        [e.title.length >= 8 && e.title.length <= 90, 'A title of 8 to 90 characters'],
        [/^\d{4}(-\d{2}(-\d{2})?)?$/.test(e.date) && e.date <= today, 'A date it became public, not in the future'],
        [e.summary.length >= 20 && words(e.summary) <= 60, 'What happened, in 20 characters to 60 words'],
        [e.why_it_matters.length >= 10 && words(e.why_it_matters) <= 40, 'Why it matters, in at most 40 words'],
        [/^https:\/\/\S+\.\S+/.test(e.sources[0].url) && !!e.sources[0].label, 'A named source with an https link'],
        [!e.contested || e.contested_note.length > 0, 'If disputed, a note saying by whom and why'],
        [e.ai_systems.length > 0, 'The AI systems used (recommended)']
      ];
      var open = C.filter(function (c) { return !c[0]; }).length;
      checks.innerHTML = C.map(function (c) { return '<li class="' + (c[0] ? 'ok' : 'no') + '"><span class="ck" aria-hidden="true">' + (c[0] ? '✓' : '–') + '</span>' + esc(c[1]) + '<span class="sr-only">' + (c[0] ? ': done' : ': still open') + '</span></li>'; }).join('');
      /* preview */
      var ev = EVID[e.evidence], ro = ROLE[e.ai_role] || ROLE.collaborator;
      prev.innerHTML = '<p class="en-k">Encyclopedia // draft entry &middot; ' + esc(DOMAIN[e.domain]) + (e.subfield ? ' &middot; ' + esc(e.subfield) : '') + '</p>' +
        '<h3 class="en-t">' + (e.title ? esc(e.title) : '<span class="ph">Your title</span>') + '</h3>' +
        '<div class="en-meta"><span class="en-date">' + (e.date ? esc(F0.fmtDate(e.date)) : 'date') + '</span>' +
        '<span class="en-role"><svg viewBox="-9 -9 18 18" aria-hidden="true"><circle r="7" style="fill:var(--mark-bio)"/><path d="' + ro[1] + '" style="fill:var(--mark-dig)"/></svg>' + ro[0] + '</span>' +
        '<span class="badge ' + ev[0] + '">' + F0.ladderHTML(ev[1]) + ev[2] + '</span>' + (e.contested ? '<span class="badge x"><span class="xm" aria-hidden="true">×</span>Contested</span>' : '') + '</div>' +
        '<p class="en-p">' + (e.summary ? esc(e.summary) : '<span class="ph">What happened, in plain words.</span>') + '</p>' +
        (e.why_it_matters ? '<p class="en-why">' + esc(e.why_it_matters) + '</p>' : '') +
        '<div class="en-who"><div><span class="dot bio"></span><b>People</b>' + (e.organizations.length ? esc(e.organizations.join(', ')) : '<span class="ph">who</span>') + '</div><div><span class="dot dig"></span><b>Machines</b>' + (e.ai_systems.length ? esc(e.ai_systems.join(', ')) : '<span class="ph">which AI systems</span>') + '</div></div>' +
        (e.sources[0].url ? '<p class="en-src"><a href="' + esc(/^https:\/\//.test(e.sources[0].url) ? e.sources[0].url : '#draft') + '">' + esc(e.sources[0].label || e.sources[0].url) + '</a></p>' : '');
      /* JSON + issue */
      var js = JSON.stringify(e, null, 1);
      json.textContent = js;
      var body = '**Proposed ledger entry**, drafted with the form on the Foundation0 charter page.\n\n' +
        '- **Title:** ' + e.title + '\n- **Date it became public:** ' + e.date + ' (' + e.date_basis + ')\n- **Field:** ' + DOMAIN[e.domain] + (e.subfield ? ' / ' + e.subfield : '') +
        '\n- **What the AI did:** ' + e.ai_role + '\n- **How sure:** ' + e.evidence + '\n- **Disputed:** ' + (e.contested ? 'yes: ' + e.contested_note : 'no') +
        '\n- **Source:** [' + (e.sources[0].label || 'link') + '](' + e.sources[0].url + ')\n\n**What happened**\n\n' + e.summary + '\n\n**Why it matters**\n\n' + e.why_it_matters +
        '\n\n<details><summary>Draft JSON (significance left for the editors)</summary>\n\n```json\n' + js + '\n```\n</details>\n';
      issue.href = ISSUE + '?title=' + encodeURIComponent('Ledger entry: ' + (e.title || 'untitled')) + '&body=' + encodeURIComponent(body);
      msg.textContent = open ? open + (open === 1 ? ' check is' : ' checks are') + ' still open. You can still open the issue and finish it on GitHub.' : 'All checks pass.';
      try { var s = {}; ['title', 'date', 'date_basis', 'domain', 'subfield', 'evidence', 'summary', 'why_it_matters', 'ai_systems', 'organizations', 'source_label', 'source_url', 'contested_note'].forEach(function (k) { s[k] = f[k].value; }); s.ai_role = role(); s.contested = f.contested.checked; localStorage.setItem(KEY, JSON.stringify(s)); } catch (e2) { /* ignore */ }
    }
    form.addEventListener('input', run);
    form.addEventListener('change', run);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    $('#d-copy').addEventListener('click', function () {
      var txt = json.textContent;
      var done = function () { msg.textContent = 'Copied the JSON.'; };
      var fail = function () { var d = json.closest('details'); if (d) d.open = true; var r = document.createRange(); r.selectNodeContents(json); var s = getSelection(); s.removeAllRanges(); s.addRange(r); msg.textContent = 'Selected the JSON: copy it with your keyboard.'; };
      try { navigator.clipboard.writeText(txt).then(done, fail); } catch (e) { fail(); }
    });
    run();
  }

  /* ===================== boot ===================== */
  principles();
  draft();
  F0.json(F0.root + 'data/members.json').then(members).catch(function (e) { console.error(e); });
  Promise.all([F0.json('futures.json'), F0.json(F0.root + 'data/ledger.json').catch(function () { return null; })])
    .then(function (r) {
      var n = r[1] && r[1].milestones ? r[1].milestones.length : null;
      futures(r[0], n == null ? 'many' : String(n));
    })
    .catch(function (e) { console.error(e); });
})();
