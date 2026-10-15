/* After the 722 (research/machine-mathematics): page script.
   Five figures, all drawn from data at view time:
     1. hero timeline: manuscripts by folder date, then the refinement steps after release
     2. the map: OpenAI's 372 result families as a treemap, OpenAI's 17 subjects folded into 8 broad fields
     3. the slack chart: six refinements, before -> after on a log scale, with a time slider
     4. "pull out the foundation": what each refinement keeps if its manuscript had a gap
     5. one small figure in each of the seven family entries
   Every figure starts on its final, informative frame; nothing moves until the visitor presses play.
   Colours come from CSS tokens (var(--...)) so both themes work without a redraw. */
(function () {
  'use strict';
  var F0 = window.F0;
  if (!F0) return;
  var R = F0.root || '../../', esc = F0.esc;
  var NS = 'http://www.w3.org/2000/svg';
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function S(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'text') e.textContent = attrs[k];
      else if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    });
    if (parent) parent.appendChild(e);
    return e;
  }
  function H(tag, cls, parent, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }
  /* numbers are written with carets ("2^-182", "k^(c·k)"); these render them as HTML, SVG or plain words */
  function supHTML(str) {
    var U = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '−' };
    return esc(str).replace(/\^\(([^)]*)\)/g, '<sup>$1</sup>').replace(/\^([−-]?[0-9.]+)/g, function (m, e) { return '<sup>' + e.replace('-', '−') + '</sup>'; })
      .replace(/\^([A-Za-zθκδ′]+)/g, '<sup>$1</sup>').replace(/[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+/g, function (m) { return '<sup>' + m.replace(/./g, function (c) { return U[c]; }) + '</sup>'; });
  }
  function plain(str) {
    return String(str).replace(/\^\(([^)]*)\)/g, ' to the power $1').replace(/\^(-?[0-9.]+)/g, function (m, e) { return ' to the power ' + e.replace('-', 'minus '); });
  }
  function ST(parent, attrs, str) {
    var t = S('text', attrs, parent), parts = String(str).split(/\^(-?[0-9.]+)/);
    parts.forEach(function (p, i) {
      if (i % 2) { S('tspan', { dy: -5, 'font-size': '8.5px', text: p.replace('-', '−') }, t); if (parts[i + 1]) S('tspan', { dy: 5, text: parts[i + 1] }, t); }
      else if (i === 0 && p) t.appendChild(document.createTextNode(p));
    });
    return t;
  }
  function pow10(n) { return n === 0 ? '1' : '10^' + n; }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function dayLabel(t) { var d = new Date(t); return d.getUTCDate() + ' ' + MON[d.getUTCMonth()]; }
  function utc(t) { var d = new Date(t); return d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ', ' + ('0' + d.getUTCHours()).slice(-2) + ':' + ('0' + d.getUTCMinutes()).slice(-2) + ' UTC'; }
  function width(el) { return Math.round(el.getBoundingClientRect().width); }
  /* redraw a host at its own width; skip while hidden or unchanged */
  function sized(host, draw) {
    var lw = 0;
    function go(force) { var w = width(host); if (!w || w < 60 || (w === lw && !force)) return; lw = w; draw(w); } // under 60 px the host is not laid out yet
    go();
    if ('ResizeObserver' in window) new ResizeObserver(function () { go(); }).observe(host);
    else window.addEventListener('resize', function () { go(); });
    return function () { go(true); };
  }
  function tipShowAt(html, el) { var b = el.getBoundingClientRect(); F0.tip.show(html, b.left + b.width / 2, b.top + Math.min(b.height, 24)); }

  /* ================= data that is not in a data file (all sourced) ================= */
  var RELEASE = Date.parse('2026-10-06T21:58:50Z'); // openai/math first commit adc7f12, 14:58:50 -0700
  var END = Date.parse('2026-10-14T00:00:00Z');
  /* manuscripts per folder date at adc7f12 (sums to 722); dossier blog.md §9.2, from the preprints/ folder names */
  var DAYS = [['2026-09-10', 2], ['2026-09-17', 1], ['2026-09-18', 1], ['2026-09-22', 3], ['2026-09-23', 177], ['2026-09-24', 194], ['2026-09-25', 90], ['2026-09-26', 53],
    ['2026-09-27', 51], ['2026-09-30', 5], ['2026-10-01', 1], ['2026-10-02', 1], ['2026-10-03', 6], ['2026-10-04', 24], ['2026-10-05', 112], ['2026-10-06', 1]];

  /* step checks: lean = Lean proof rebuilt and kernel-checked by an outside leaderboard; rev = exact certificates
     replayed by the race's maintainer (not the author); own = the author's own exact checks; claim = posted as a claim */
  var CHECK = {
    lean: 'Lean proof rebuilt and checked by the Big O Speedrun leaderboard',
    rev: 'Exact certificates replayed and selected by the maintainer',
    own: 'The author’s own exact checks',
    claim: 'Posted as a claim; nobody else had checked it'
  };
  var L2 = Math.LN2 / Math.LN10;
  function st(t, v, s, who, ck, note, src) { return { t: Date.parse(t), lv: Math.log10(v), s: s, who: who, ck: ck, note: note || '', src: src || '' }; }
  var IMB = 'https://github.com/CrocSwap/integer-mult-bounds/commit/';
  var ROWS = [
    { id: 'kappa', fam: '109', name: 'Integer multiplication', sym: 'κ', up: true,
      what: 'κ is the saving in n·(log n)^(1−κ) steps to multiply two n-digit numbers. Bigger is better.',
      before: { lv: -182 * L2, s: '2^-182', note: 'OpenAI manuscript dated 23 Sep 2026' },
      status: 'Conditional · maintainer-reviewed · not peer reviewed',
      src: 'https://github.com/CrocSwap/integer-mult-bounds/commits/main/certificates/selected-result.json', srcL: 'selected-result.json history',
      steps: [
        st('2026-10-07T02:22Z', 5.8e-33, '5.8×10^-33', 'Doug Colkitt, with OpenAI Codex', 'own', 'First commit: better parameters for the same construction', IMB + '5cf29ecd'),
        st('2026-10-07T13:35Z', Math.pow(2, -78), '2^-78', 'Doug Colkitt, with OpenAI Codex', 'own', 'Direct axis routing', IMB + '52ce3bee'),
        st('2026-10-07T19:27Z', Math.pow(2, -59), '2^-59', 'Doug Colkitt, with OpenAI Codex', 'own', 'Paired circuits', IMB + 'bcd4ebde'),
        st('2026-10-08T00:27Z', 8.3e-11, '83/10^12', 'Doug Colkitt; the idea came from a separate research agent', 'own', 'Compact controls', IMB + '6e564879'),
        st('2026-10-08T01:10Z', Math.pow(2, -31), '2^-31', 'eumemic’s Claude-assisted PR #3, integrated by the maintainer', 'rev', 'Complex-network compression', IMB + '1c09a588'),
        st('2026-10-08T13:10Z', Math.pow(2, -30), '2^-30', 'Doug Colkitt, with OpenAI Codex', 'own', 'Ternary checkpoint', IMB + '1a74950c'),
        st('2026-10-08T15:18Z', 3.886675852e-5, '3.886675852×10^-5', 'First community release; its last step was rohanarun’s PR #39', 'rev', 'Tagged community-kappa-15', IMB + '0605a24a'),
        st('2026-10-08T18:24Z', 5.1016920170078e-5, '5.1016920170078×10^-5', 'PRs #50 to #62, reviewed together', 'rev', '', IMB + '0d235fe5'),
        st('2026-10-09T04:53Z', 0.0004609169, '0.0004609169', 'icekylinx, PR #144 (GPT-6 Astra via Codex)', 'rev', 'The first entry in selected-result.json', IMB + '6aed8701'),
        st('2026-10-09T05:55Z', 0.000472143085, '0.000472143085', 'PRs #146, #147, #148 and #150 combined', 'rev', '', IMB + 'e2a02cac'),
        st('2026-10-09T06:01Z', 0.000472154791, '0.000472154791', 'adds PR #151', 'rev', '', IMB + '86b30e03'),
        st('2026-10-09T12:32Z', 0.000661885549259598, '0.000661885549259598', 'Dugongue, PR #186', 'rev', '', IMB + 'd697aaa7'),
        st('2026-10-10T14:08Z', 0.000723571590007464, '0.000723571590007464', 'DreamingOfClouds, PR #276, with rohanarun, PR #279', 'rev', '', IMB + '91e29e7b'),
        st('2026-10-12T01:55Z', 0.001517760977820331, '0.001517760977820331', 'icekylinx, PR #531, building on eumemic’s PR #493', 'rev', '', IMB + 'a1e7d848'),
        st('2026-10-12T13:10Z', 0.001584931111785787, '0.001584931111785787', 'PR #535 with PR #510', 'rev', '', IMB + '1c1e42f0'),
        st('2026-10-12T14:41Z', 0.001602278921983212, '0.001602278921983212', 'Jeremy Kothe’s PR #588, with PR #543', 'rev', '', IMB + '270c2458'),
        st('2026-10-12T16:59Z', 0.0016127213726553, '0.0016127213726553', 'reviewed through PR #599', 'rev', '', IMB + '1db1fbe6'),
        st('2026-10-12T21:01Z', 0.001635183729255778, '0.001635183729255778', 'PR #617', 'rev', '', IMB + '2e9ed969'),
        st('2026-10-12T22:36Z', 0.001635527380375392, '0.001635527380375392', 'PR #626', 'rev', '', IMB + '5c5567d1'),
        st('2026-10-13T05:57Z', 0.001661202643272239, '0.001661202643272239', 'PR #741 (“SW4”)', 'rev', '', IMB + '2cdd93d0'),
        st('2026-10-13T06:44Z', 0.001661634653669567, '0.001661634653669567', 'PR #799 (“X4”)', 'rev', '', IMB + 'd6dfd8f2'),
        st('2026-10-13T13:30Z', 0.001661957774647029, '0.001661957774647029', 'PR #890 (“U8/T21”)', 'rev', '', IMB + '3b83e4f1'),
        st('2026-10-13T15:06Z', 0.001661960547713947, '0.001661960547713947', 'PR #942 (“T37”)', 'rev', '', IMB + '3825dc0e'),
        st('2026-10-13T18:05Z', 0.001672188119205421, '0.001672188119205421', 'PR #1042', 'rev', '', IMB + '87db776d'),
        st('2026-10-13T18:45Z', 0.001672660197076918, '0.001672660197076918', 'rohanarun, PR #1094, with OpenAI Codex', 'rev', 'The reviewed record on 14 Oct', IMB + '0a31ad88')
      ] },
    { id: 'dft', fam: '130', name: 'Exact Fourier transform', sym: 'δ', up: true,
      what: 'δ is the saving in n·(log n)^(1−δ) steps for an exact discrete Fourier transform. Bigger is better.',
      before: { lv: -13, s: '10^-13', note: 'OpenAI manuscript dated 25 Sep 2026' },
      status: 'Lean-verified · human review pending',
      src: 'https://bigospeedrun.com/exact-dft', srcL: 'Big O Speedrun exact-DFT leaderboard',
      steps: [
        st('2026-10-08T05:20Z', 2e-11, '2×10^-11', 'OpenAI’s own follow-up', 'lean', 'Listed by OpenAI on the leaderboard', 'https://bigospeedrun.com/exact-dft'),
        st('2026-10-08T23:56Z', 7.3e-5, '7.3×10^-5', 'Ryan Shea, with OpenAI models and Codex', 'claim', '', 'https://github.com/shea256/fourier-transform-below-nlogn'),
        st('2026-10-09T09:34Z', 607 / 1250000, '607/1,250,000 ≈ 0.000486', 'eumemic, with Claude', 'claim', 'Exact certificate, no formal proof; the best claim for about six hours', 'https://github.com/eumemic/exact-dft-bounds'),
        st('2026-10-09T15:24Z', 0.00067, '0.00067', 'Ryan Shea', 'claim', '', 'https://github.com/shea256/fourier-transform-below-nlogn'),
        st('2026-10-09T19:00Z', 3737273 / 5e9, '≈ 0.000747', 'jacobalansussman', 'claim', '', 'https://bigospeedrun.com/exact-dft'),
        st('2026-10-10T01:43Z', 47171 / 62500000, '≈ 0.000755', 'jacobalansussman and chafreaky', 'lean', '', 'https://bigospeedrun.com/exact-dft'),
        st('2026-10-10T22:44Z', 4381239 / 5e9, '≈ 0.000876', 'jacobalansussman', 'lean', '', 'https://bigospeedrun.com/exact-dft'),
        st('2026-10-11T13:07Z', 2555269 / 2.5e9, '≈ 0.00102', 'Nil Mamano', 'lean', '', 'https://bigospeedrun.com/exact-dft'),
        st('2026-10-12T18:43Z', 0.0012331685, '0.0012331685', 'Jeremy Kothe and Ryan Shea; Kothe’s circuit, Shea’s conversion and checked instance', 'lean', 'Rank 1 on the leaderboard on 14 Oct', 'https://github.com/shea256/fourier-transform-below-nlogn')
      ] },
    { id: 'vdw', fam: '160', name: 'Van der Waerden numbers', sym: 'c', up: true,
      what: 'c sets how long a coloured row must be before an evenly spaced one-colour run is forced: k^(c·k·⌊log₂ r⌋). Bigger proves longer rows.',
      before: { lv: -5, s: '1/100000', note: 'OpenAI manuscript dated 23 Sep 2026' },
      status: 'Conditional · no human review',
      src: 'https://github.com/rohanarun/van-der-waerden-refinement/pulls?q=is%3Apr', srcL: 'van-der-waerden-refinement pull requests',
      steps: [
        st('2026-10-09T11:02:17Z', 1 / 200, '1/200', 'rohanarun, with Codex', 'own', 'At most 2 points of one “key” fit in a thin band, not 4', 'https://github.com/rohanarun/van-der-waerden-refinement/commit/14a9529'),
        st('2026-10-09T12:28:12Z', 1 / 193, '1/193', 'rohanarun, with Codex', 'own', 'PR #1', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/1'),
        st('2026-10-10T05:45:50Z', 1 / 25, '1/25', 'rohanarun, with Claude', 'own', 'PR #2; PR #3 then proved this route stops at 1/24', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/2'),
        st('2026-10-11T04:30:35Z', 1 / 19, '1/19', 'artuskg, with GPT-6 Pro and Codex', 'own', 'PR #4: a new construction', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/4'),
        st('2026-10-13T01:58:21Z', 1 / 16, '1/16', 'DaysSky, with Claude', 'own', 'PR #6', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/6'),
        st('2026-10-13T02:24:47Z', 2 / 25, '2/25', 'DaysSky, with Claude', 'own', 'PR #7', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/7'),
        st('2026-10-13T02:24:47Z', 1 / 9, '1/9', 'DaysSky, with Claude', 'own', 'PR #7, about 11,111 times the manuscript’s constant', 'https://github.com/rohanarun/van-der-waerden-refinement/pull/7')
      ] },
    { id: 'matroid', fam: '111', name: 'Matroid prophet inequality', sym: 'C', up: true,
      what: 'The fraction of the best possible total that a one-sample strategy is guaranteed. Bigger is better.',
      before: { lv: -293 * L2, s: '2^-293', note: 'derived in OpenAI’s manuscript (its headline says 2^-310)' },
      status: 'Written proof + exact certificates · not reviewed · not formalized',
      src: 'https://github.com/shea256/matroid-prophet-inequality', srcL: 'matroid-prophet-inequality README',
      steps: [
        st('2026-10-10T04:19:11Z', Math.pow(2, -36), '2^-36', 'Ryan Shea, with Codex', 'own', 'First public version', 'https://github.com/shea256/matroid-prophet-inequality/commit/7cffa2a'),
        st('2026-10-10T06:29:15Z', Math.pow(2, -34), '2^-34', 'Ryan Shea, with Codex', 'own', 'Joint residual encoding', 'https://github.com/shea256/matroid-prophet-inequality/commit/6e41803'),
        st('2026-10-10T06:52:50Z', Math.pow(2, -32), '2^-32', 'Ryan Shea, with Codex', 'own', 'Rank-charged residual entropy', 'https://github.com/shea256/matroid-prophet-inequality/commit/ff4187f'),
        st('2026-10-10T15:12:32Z', 1.75 * Math.pow(2, -32), '(7/4)·2^-32', 'Ryan Shea, with Codex', 'own', 'Retained bases', 'https://github.com/shea256/matroid-prophet-inequality/commit/8ba515a'),
        st('2026-10-10T18:23:14Z', 1.02 * Math.pow(2, -31), '(51/50)·2^-31', 'Ryan Shea, with Codex', 'own', 'Activation generators', 'https://github.com/shea256/matroid-prophet-inequality/commit/deb20b2'),
        st('2026-10-11T18:43:11Z', 5.100145024820285e-10, '(35/32)·2^-31 ≈ 5.1×10^-10', 'Ryan Shea, with Codex', 'own', 'Three-state generator encoding; the exact certificate is slightly above (35/32)·2^-31', 'https://github.com/shea256/matroid-prophet-inequality/commit/8bafc1f')
      ] },
    { id: 'sid', fam: '161', name: 'Sidorenko counterexample', sym: 'R', up: false,
      what: 'A constant in one counting step of the proof. Smaller is better.',
      before: { lv: Math.log10(1641), s: '1641', note: 'OpenAI manuscript dated 23 Sep 2026' },
      status: 'Exact certificates · not peer reviewed',
      src: 'https://github.com/rohanarun/sidorenko-template-refinements/blob/main/progress.md', srcL: 'sidorenko-template-refinements progress.md',
      steps: [
        st('2026-10-09T11:40:42Z', 1032, '1032', 'rohanarun, with Codex', 'own', 'Initial draft', 'https://github.com/rohanarun/sidorenko-template-refinements/commit/9e6e659'),
        st('2026-10-09T12:28:13Z', 978, '978', 'rohanarun, with Codex', 'own', 'PR #1: active vertex supports', 'https://github.com/rohanarun/sidorenko-template-refinements/pull/1'),
        st('2026-10-10T06:41:45Z', 189, '189', 'rohanarun, with Codex and Claude', 'own', 'PR #2: a sequential basis count', 'https://github.com/rohanarun/sidorenko-template-refinements/pull/2')
      ] },
    { id: 'unit', fam: '167', name: 'Unit distances', sym: 'N', up: false,
      what: 'How many selected pairs the proof’s last algebra step needs. Smaller is better; the headline bound does not change.',
      before: { lv: 2, s: '100 (20×5)', note: 'OpenAI manuscript dated 23 Sep 2026' },
      status: 'Conditional · not peer reviewed',
      src: 'https://github.com/rohanarun/unit-distance-grid-refinement', srcL: 'unit-distance-grid-refinement README',
      steps: [
        st('2026-10-09T11:40:48Z', 36, '36 (9×4)', 'rohanarun, with Codex', 'own', 'First version', 'https://github.com/rohanarun/unit-distance-grid-refinement/commit/a1486a9'),
        st('2026-10-10T05:36:32Z', 32, '32 (8×4)', 'rohanarun, with Codex and Claude', 'own', 'Scaling symmetry', 'https://github.com/rohanarun/unit-distance-grid-refinement/commit/dd9b3e2')
      ] }
  ];
  ROWS.forEach(function (r) { r.steps.forEach(function (s, i) { s.row = r; s.i = i; }); });
  var ALL = [];
  ROWS.forEach(function (r) { ALL = ALL.concat(r.steps); });
  ALL.sort(function (a, b) { return a.t - b.t || a.lv - b.lv; });
  var NSTEPS = ALL.length;

  /* the seven families founding members built on (verified against openai-math-families.json titles at load) */
  var BUILT = {
    '109': { t: 'Integer multiplication below n log n', who: 'Doug Colkitt’s race; rohanarun holds the reviewed record; eumemic; Aska' },
    '130': { t: 'Exact Fourier transforms below n log n', who: 'Ryan Shea with Jeremy Kothe (Lean-verified record); eumemic’s claim; Swapnil Jain’s mobius-x1, with Aska' },
    '160': { t: 'Superexponential van der Waerden numbers', who: 'rohanarun, with contributors artuskg and DaysSky' },
    '161': { t: 'Counterexamples to Sidorenko', who: 'rohanarun' },
    '167': { t: 'Planar distinct distances and unit-distance bounds', who: 'rohanarun' },
    '107': { t: 'Matrix multiplication with exponent at most 9/4', who: 'rohanarun' },
    '111': { t: 'One-sample matroid prophet inequalities', who: 'Ryan Shea' }
  };

  /* family titles carry a little HTML (<i>, <sub>, <sup>) and some TeX; render both safely */
  function titleHTML(t) {
    var s = esc(t).replace(/&lt;(\/?)(i|sub|sup)&gt;/g, '<$1$2>');
    s = s.replace(/\\log\s*/g, ' log ').replace(/\\mathsf\{([^}]*)\}/g, '$1').replace(/\\mathsf\s*/g, '').replace(/\\mathcal\s*/g, '')
      .replace(/\\alpha/g, 'α').replace(/\^\{([^}]*)\}/g, '<sup>$1</sup>').replace(/_(\d)/g, '<sub>$1</sub>').replace(/\s{2,}/g, ' ');
    return s;
  }
  function titleText(t) { return titleHTML(t).replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&#39;/g, '’').replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>'); }

  /* ================= 1. hero timeline ================= */
  function timeline() {
    var host = $('#tl-stage'), out = $('#tl-out'), tbl = $('#tl-table');
    if (!host) return;
    var D0 = Date.parse('2026-09-10T00:00Z'), DAY = 864e5, ND = 34; // 10 Sep .. 13 Oct
    var days = [];
    for (var i = 0; i < ND; i++) days.push({ i: i, t: D0 + i * DAY, n: 0, steps: [] });
    DAYS.forEach(function (d) { days[Math.round((Date.parse(d[0] + 'T00:00Z') - D0) / DAY)].n = d[1]; });
    ALL.forEach(function (s) { var k = Math.floor((s.t - D0) / DAY); if (days[k]) days[k].steps.push(s); });
    var live = days.filter(function (d) { return d.n || d.steps.length; });
    var total = DAYS.reduce(function (a, d) { return a + d[1]; }, 0);
    var mid = DAYS.reduce(function (a, d) { return a + (d[0] >= '2026-09-22' && d[0] <= '2026-10-05' ? d[1] : 0); }, 0);
    var DEF = '<b>' + mid + ' of the ' + total + ' manuscripts</b> carry dates between 22 September and 5 October. In the seven days after release, <b>' + NSTEPS + ' public steps</b> tightened six results.';
    var active = -1, cols = [];
    function say(k) {
      if (k < 0) { out.innerHTML = DEF; return; }
      var d = days[k], parts = [];
      var date = '<b>' + dayLabel(d.t) + ' 2026</b>: ';
      if (d.n) parts.push(d.n + ' manuscript' + (d.n > 1 ? 's' : '') + ' carry this date');
      if (d.steps.length) {
        var by = {};
        d.steps.forEach(function (s) { by[s.row.id] = (by[s.row.id] || 0) + 1; });
        parts.push(d.steps.length + ' step' + (d.steps.length > 1 ? 's' : '') + ' tightened ' + ROWS.filter(function (r) { return by[r.id]; }).map(function (r) { return esc(r.name.toLowerCase().replace('van der waerden', 'van der Waerden').replace('sidorenko', 'Sidorenko').replace('fourier', 'Fourier')) + ' (' + by[r.id] + ')'; }).join(', '));
      }
      if (+d.t === Date.parse('2026-10-06T00:00Z')) parts.push('OpenAI made the collection public at 21:58 UTC');
      out.innerHTML = date + parts.join('; ') + '.';
    }
    function tipHTML(d) {
      var h = '<div class="tip-k">' + esc(dayLabel(d.t)) + ' 2026</div>';
      if (d.n) h += '<div class="tip-t">' + d.n + ' manuscript' + (d.n > 1 ? 's' : '') + '</div><div class="tip-note">dated this day by their folder names</div>';
      if (d.steps.length) {
        h += '<div class="tip-t">' + d.steps.length + ' refinement step' + (d.steps.length > 1 ? 's' : '') + '</div><div class="tip-rows">';
        d.steps.slice(0, 8).forEach(function (s) { h += '<div class="tip-row"><span>' + esc(s.row.sym) + ' → ' + supHTML(s.s) + '</span></div>'; });
        if (d.steps.length > 8) h += '<div class="tip-row"><span>+' + (d.steps.length - 8) + ' more</span></div>';
        h += '</div>';
      }
      return h;
    }
    function draw(W) {
      host.innerHTML = '';
      var small = W < 520, L = 34, Rm = 10, T = 30, HB = small ? 92 : 122, colW = (W - L - Rm) / ND;
      var dot = Math.max(5.5, Math.min(8, colW * 0.78)), pitch = dot + 2.2;
      var maxS = Math.max.apply(null, days.map(function (d) { return d.steps.length; }));
      var base = T + HB, H = base + 10 + maxS * pitch + 30;
      var svg = S('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'mm-svg', 'aria-hidden': 'true' }, host);
      var X = function (k) { return L + k * colW; };
      var ymax = 200, Y = function (v) { return base - HB * v / ymax; };
      var bgs = S('g', null, svg);
      [0, 100, 200].forEach(function (v) {
        S('line', { x1: L, x2: W - Rm, y1: Y(v), y2: Y(v), class: v ? 'grid' : 'axis' }, svg);
        S('text', { x: L - 6, y: Y(v) + 4, 'text-anchor': 'end', text: v }, svg);
      });
      S('text', { x: L, y: 12, class: 't-ink', text: small ? 'MANUSCRIPTS PER DAY' : 'MANUSCRIPTS WRITTEN, BY FOLDER DATE' }, svg);
      cols = [];
      days.forEach(function (d, k) {
        var bg = S('rect', { x: X(k), y: T - 6, width: colW, height: H - T - 18, class: 'daybg' }, bgs);
        cols.push(bg);
        if (d.n) {
          var bw = Math.max(2, Math.min(24, colW * 0.74)), x0 = X(k) + (colW - bw) / 2, y0 = Y(d.n), r = Math.min(3, bw / 2, base - y0);
          S('path', { d: 'M' + x0 + ',' + base + 'V' + (y0 + r) + 'Q' + x0 + ',' + y0 + ' ' + (x0 + r) + ',' + y0 + 'H' + (x0 + bw - r) + 'Q' + (x0 + bw) + ',' + y0 + ' ' + (x0 + bw) + ',' + (y0 + r) + 'V' + base + 'Z', class: 'bar', 'data-k': k }, svg);
        }
        d.steps.forEach(function (s, j) {
          var cx = X(k) + colW / 2, cy = base + 10 + dot / 2 + j * pitch, r = dot / 2;
          S('circle', { cx: cx, cy: cy, r: r + 1.2, style: 'fill:var(--bg-2)' }, svg);
          if (s.row.id === 'dft' && s.i === 0) S('circle', { cx: cx, cy: cy, r: r, style: 'fill:var(--mark-dig)' }, svg);
          else {
            S('circle', { cx: cx, cy: cy, r: r, style: 'fill:var(--mark-bio)' }, svg);
            S('path', { d: 'M' + cx + ',' + (cy - r) + 'A' + r + ',' + r + ' 0 0 1 ' + cx + ',' + (cy + r) + 'Z', style: 'fill:var(--mark-dig)' }, svg);
          }
        });
      });
      // release marker
      var xr = L + (RELEASE - D0) / DAY * colW;
      S('line', { x1: xr, x2: xr, y1: T - 8, y2: H - 22, class: 'pub' }, svg);
      S('text', { x: xr - 5, y: T - 12 + (small ? 0 : 0), 'text-anchor': 'end', class: 'pub-t', text: small ? 'PUBLIC 6 OCT' : 'MADE PUBLIC · 6 OCT' }, svg);
      // x labels
      var lab = [['2026-09-10', '10 SEP'], ['2026-09-23', '23 SEP'], ['2026-10-01', '1 OCT'], ['2026-10-13', '13 OCT']];
      lab.forEach(function (l) { var k = Math.round((Date.parse(l[0] + 'T00:00Z') - D0) / DAY); S('text', { x: X(k) + colW / 2, y: H - 6, 'text-anchor': k === ND - 1 ? 'end' : 'middle', text: l[1] }, svg); });
      S('text', { x: X(27) - 8, y: base + 17, 'text-anchor': 'end', class: 't-ink', text: small ? 'STEPS →' : 'STEPS THAT TIGHTENED A RESULT →' }, svg);
      if (active >= 0 && cols[active]) cols[active].setAttribute('class', 'daybg on');
      // pointer
      svg.addEventListener('pointermove', function (e) {
        var b = svg.getBoundingClientRect(), k = Math.floor((e.clientX - b.left - L) / colW);
        if (k < 0 || k >= ND) { F0.tip.hide(); return; }
        setActive(k, false);
        var d = days[k];
        if (d.n || d.steps.length) F0.tip.show(tipHTML(d), e.clientX, e.clientY); else F0.tip.hide();
      });
      svg.addEventListener('pointerleave', function () { F0.tip.hide(); setActive(-1, false); });
    }
    function setActive(k, fromKey) {
      if (active >= 0 && cols[active]) cols[active].setAttribute('class', 'daybg');
      active = k;
      if (k >= 0 && cols[k]) cols[k].setAttribute('class', 'daybg on');
      say(k);
      if (fromKey && k >= 0) { var d = days[k]; if (d.n || d.steps.length) tipShowAt(tipHTML(d), cols[k]); }
    }
    host.addEventListener('keydown', function (e) {
      var idx = live.map(function (d) { return d.i; }), p = idx.indexOf(active);
      var k = null;
      if (e.key === 'ArrowRight') k = idx[Math.min(idx.length - 1, p + 1)];
      else if (e.key === 'ArrowLeft') k = idx[p < 0 ? idx.length - 1 : Math.max(0, p - 1)];
      else if (e.key === 'Home') k = idx[0];
      else if (e.key === 'End') k = idx[idx.length - 1];
      else if (e.key === 'Escape') { setActive(-1, false); F0.tip.hide(); return; }
      if (k == null) return;
      e.preventDefault(); setActive(k, true);
    });
    host.addEventListener('blur', function () { F0.tip.hide(); });
    sized(host, draw);
    say(-1);
    if (tbl) {
      var rows = live.map(function (d) {
        var by = {};
        d.steps.forEach(function (s) { by[s.row.name] = (by[s.row.name] || 0) + 1; });
        return '<tr><td>' + esc(dayLabel(d.t)) + '</td><td class="n">' + (d.n || '') + '</td><td class="n">' + (d.steps.length || '') + '</td><td>' + esc(Object.keys(by).map(function (k) { return k + ' (' + by[k] + ')'; }).join(', ')) + '</td></tr>';
      }).join('');
      tbl.innerHTML = '<table class="tbl"><caption>Manuscripts by folder date, and refinement steps by day (UTC), 2026</caption><thead><tr><th scope="col">Day</th><th scope="col" class="n">Manuscripts</th><th scope="col" class="n">Steps</th><th scope="col">Results moved</th></tr></thead><tbody>' + rows +
        '<tr><td><b>Total</b></td><td class="n"><b>' + total + '</b></td><td class="n"><b>' + NSTEPS + '</b></td><td></td></tr></tbody></table>';
    }
  }

  /* ================= 2. the map ================= */
  function squarify(items, x, y, w, h) {
    var out = [], total = 0;
    items.forEach(function (it) { total += it.w; });
    if (!total || w <= 0 || h <= 0) return out;
    var k = w * h / total, rest = items.map(function (it) { return { it: it, a: it.w * k }; });
    function worst(row, s) {
      var sum = 0, mx = 0, mn = Infinity;
      row.forEach(function (r) { sum += r.a; if (r.a > mx) mx = r.a; if (r.a < mn) mn = r.a; });
      return Math.max(s * s * mx / (sum * sum), (sum * sum) / (s * s * mn));
    }
    while (rest.length) {
      var s = Math.min(w, h), row = [rest[0]], i = 1, wp = worst(row, s);
      while (i < rest.length) { var c = row.concat([rest[i]]), wc = worst(c, s); if (wc > wp) break; row = c; wp = wc; i++; }
      var sum = 0; row.forEach(function (r) { sum += r.a; });
      if (w >= h) { var cw = sum / h, yy = y; row.forEach(function (r) { var rh = r.a / cw; out.push({ it: r.it, x: x, y: yy, w: cw, h: rh }); yy += rh; }); x += cw; w -= cw; }
      else { var rh = sum / w, xx = x; row.forEach(function (r) { var rw = r.a / rh; out.push({ it: r.it, x: xx, y: y, w: rw, h: rh }); xx += rw; }); y += rh; h -= rh; }
      rest = rest.slice(i);
    }
    return out;
  }

  function map(FD, SUB) {
    var SUBJ = (SUB && SUB.family) || {};
    function subj(f) { return SUBJ[f.id] || ''; }
    var stage = $('#map-stage'), info = $('#map-info'), fieldsUl = $('#map-fields'), q = $('#map-q'), count = $('#map-count'), table = $('#map-table');
    if (!stage || !FD || !FD.families) return null;
    var fams = FD.families, sum = FD.summary || {}, FN = sum.fields || {};
    var ORDER = ['algorithms', 'combinatorics', 'number-theory', 'analysis', 'geometry', 'algebra', 'probability', 'other'];
    var SHORT = { 'number-theory': 'Number theory', combinatorics: 'Combinatorics', analysis: 'Analysis', geometry: 'Geometry', algebra: 'Algebra', probability: 'Probability', algorithms: 'Algorithms', other: 'Other' };
    var byId = {};
    fams.forEach(function (f) { byId[f.id] = f; f._t = titleText(f.title); f._t7 = titleText(f.title_oct7 || f.title); });
    Object.keys(BUILT).forEach(function (id) {
      var f = byId[id];
      if (!f) console.warn('family ' + id + ' missing from openai-math-families.json');
      else if (f._t.toLowerCase().indexOf(BUILT[id].t.toLowerCase().slice(0, 18)) !== 0) console.warn('family ' + id + ' title mismatch: ' + f._t);
    });
    var size = 'n', snap = 'oct7', field = null, query = '', active = null, cells = [], order = [], focusRect = null, svg = null;
    function nOf(f) { return snap === 'day1' ? f.n_manuscripts_day1 : f.n_manuscripts_oct7; }
    function leanOf(f) { return snap === 'day1' ? f.lean_doc_day1 : f.lean_doc_oct7; }
    function tOf(f) { return snap === 'day1' ? f._t : f._t7; }
    function tHTML(f) { return titleHTML(snap === 'day1' ? f.title : (f.title_oct7 || f.title)); }
    function matches(f) {
      if (field && f.field !== field) return false;
      if (!query) return true;
      var qq = query.replace(/^#/, '');
      if (/^\d{1,3}$/.test(qq)) return f.id === ('00' + qq).slice(-3) || f.id.indexOf(qq) === 0;
      return tOf(f).toLowerCase().indexOf(qq.toLowerCase()) >= 0;
    }
    // field buttons
    if (fieldsUl) {
      var cnt = {};
      fams.forEach(function (f) { cnt[f.field] = (cnt[f.field] || 0) + 1; });
      fieldsUl.innerHTML = ORDER.filter(function (k) { return cnt[k]; }).map(function (k) {
        return '<li><button type="button" data-field="' + k + '" aria-pressed="false">' + esc(FN[k] || SHORT[k]) + ' <b>' + cnt[k] + '</b></button></li>';
      }).join('');
      fieldsUl.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-field]'); if (!b) return;
        var k = b.getAttribute('data-field');
        field = field === k ? null : k;
        $$('button[data-field]', fieldsUl).forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-field') === field ? 'true' : 'false'); });
        apply();
      });
    }
    function apply() {
      var n = 0, m = 0;
      cells.forEach(function (c) {
        var on = matches(c.f);
        c.g.setAttribute('class', 'cell' + (on ? '' : ' dim'));
        if (on) { n++; m += nOf(c.f); }
      });
      if (count) count.textContent = (n === fams.length ? fams.length + ' families' : n + ' of ' + fams.length + ' families') + ' · ' + m + ' manuscripts';
    }
    function draw() {
      var W = width(stage); if (!W || W < 60) return;
      var H = Math.round(W >= 900 ? W * 0.54 : W >= 600 ? W * 0.82 : W * 1.5);
      stage.innerHTML = '';
      svg = S('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, class: 'mm-svg', role: 'presentation' }, stage);
      var groups = ORDER.map(function (k) {
        var fs = fams.filter(function (f) { return f.field === k; }).map(function (f) { return { f: f, w: size === 'n' ? nOf(f) : 1 }; });
        fs.sort(function (a, b) { return b.w - a.w || (a.f.id < b.f.id ? -1 : 1); });
        var w = 0; fs.forEach(function (x) { w += x.w; });
        return { k: k, items: fs, w: w };
      }).filter(function (g) { return g.w > 0; });
      groups.sort(function (a, b) { return b.w - a.w; });
      var gl = squarify(groups, 0, 0, W, H);
      cells = []; order = [];
      var labels = S('g', { 'pointer-events': 'none' }), plates = [];
      gl.forEach(function (gr) {
        var g = gr.it, gx = gr.x + 2, gy = gr.y + 2, gw = gr.w - 4, gh = gr.h - 4;
        if (gw <= 0 || gh <= 0) return;
        S('rect', { x: gx - 1, y: gy - 1, width: gw + 2, height: gh + 2, style: 'fill:none;stroke:var(--line-ui);stroke-opacity:.55', 'stroke-width': 1 }, svg);
        var cl = squarify(g.items, gx, gy, gw, gh);
        cl.forEach(function (c) {
          var f = c.it.f, lean = leanOf(f), hl = !!BUILT[f.id], x = c.x + 1, y = c.y + 1, w = Math.max(1, c.w - 2), h = Math.max(1, c.h - 2);
          var cg = S('g', { class: 'cell', 'data-id': f.id }, svg);
          S('rect', { x: x, y: y, width: w, height: h, class: lean ? 'c-lean' : 'c-none' }, cg);
          if (hl) {
            S('rect', { x: x + 1, y: y + 1, width: Math.max(0, w - 2), height: Math.max(0, h - 2), style: 'fill:none;stroke:var(--hair)', 'stroke-width': 2 }, cg);
            if (w >= 26 && h >= 16) S('text', { x: x + w / 2, y: y + h / 2 + 4, 'text-anchor': 'middle', class: 'clab ' + (lean ? 'on-lean' : 'on-none'), text: f.id }, cg);
          }
          var rec = { f: f, g: cg, x: x, y: y, w: w, h: h, gk: g.k };
          cells.push(rec); order.push(rec);
        });
        // label plate, top-left of the group (over the corner of its biggest cell; pointer events pass through)
        if (gh > 22) plates.push({ gx: gx, gy: gy, gw: gw, opts: [(FN[g.k] || SHORT[g.k]).toUpperCase() + ' · ' + g.items.length, SHORT[g.k].toUpperCase() + ' · ' + g.items.length, SHORT[g.k].toUpperCase()] });
      });
      svg.appendChild(labels);
      // label plates sized from the rendered text, longest label that fits
      plates.forEach(function (p) {
        var rect = S('rect', { x: p.gx, y: p.gy, width: 0, height: 18, class: 'gplate' }, labels), t = S('text', { x: p.gx + 6, y: p.gy + 13, class: 'glab' }, labels);
        for (var i = 0; i < p.opts.length; i++) {
          t.textContent = p.opts[i];
          var tw = t.getComputedTextLength ? t.getComputedTextLength() : p.opts[i].length * 7.6;
          if (tw + 12 <= p.gw) { rect.setAttribute('width', Math.ceil(tw + 12)); return; }
        }
        labels.removeChild(rect); labels.removeChild(t);
      });
      focusRect = S('rect', { x: -10, y: -10, width: 0, height: 0, style: 'fill:none;stroke:var(--focus);pointer-events:none', 'stroke-width': 2, visibility: 'hidden' }, svg);
      apply();
      if (active) mark(active, false);
      svg.addEventListener('pointermove', function (e) {
        var g = e.target.closest && e.target.closest('.cell');
        if (!g) { F0.tip.hide(); return; }
        var f = byId[g.getAttribute('data-id')];
        if (f !== active) mark(f, false);
        F0.tip.show(tip(f), e.clientX, e.clientY);
      });
      svg.addEventListener('pointerleave', function () { F0.tip.hide(); });
      svg.addEventListener('click', function (e) {
        var g = e.target.closest && e.target.closest('.cell'); if (!g) return;
        mark(byId[g.getAttribute('data-id')], false);
      });
    }
    function tip(f) {
      var n1 = f.n_manuscripts_day1, n7 = f.n_manuscripts_oct7, b = BUILT[f.id];
      return '<div class="tip-k">Family ' + esc(f.id) + ' · ' + esc(subj(f) || FN[f.field] || f.field) + '</div><div class="tip-t">' + tHTML(f) + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span class="tip-v">' + nOf(f) + '</span><span>manuscript' + (nOf(f) > 1 ? 's' : '') + (n1 !== n7 ? ' (' + n1 + ' on 6 Oct, ' + n7 + ' on 7 Oct)' : '') + '</span></div>' +
        '<div class="tip-row"><span>' + (leanOf(f) ? 'Links a Lean scope document' : 'No Lean scope document') + '</span></div>' +
        '<div class="tip-row"><span>Dated ' + esc(F0.fmtDate(f.earliest_date)) + (f.latest_date !== f.earliest_date ? ' to ' + esc(F0.fmtDate(f.latest_date)) : '') + '</span></div></div>' +
        (b ? '<div class="tip-note"><span class="h"></span>' + esc(b.who) + '</div>' : '');
    }
    function mark(f, scroll) {
      active = f;
      var c = cells.filter(function (x) { return x.f === f; })[0];
      if (c && focusRect) { focusRect.setAttribute('x', c.x - 2); focusRect.setAttribute('y', c.y - 2); focusRect.setAttribute('width', c.w + 4); focusRect.setAttribute('height', c.h + 4); focusRect.setAttribute('visibility', 'visible'); }
      var b = BUILT[f.id], n1 = f.n_manuscripts_day1, n7 = f.n_manuscripts_oct7;
      info.innerHTML = '<p class="mm-info-k">Family ' + esc(f.id) + (subj(f) ? ' · OpenAI subject: ' + esc(subj(f)) : '') + ' · on the map under ' + esc(FN[f.field] || f.field) + '</p>' +
        '<p class="mm-info-t">' + tHTML(f) + '</p>' +
        '<p class="mm-info-r"><span>' + n1 + ' manuscript' + (n1 > 1 ? 's' : '') + ' on 6 Oct' + (n7 !== n1 ? ', ' + n7 + ' on 7 Oct' : '') + '</span><span>' + (leanOf(f) ? 'Lean scope document' : 'No Lean scope document') + (f.lean_doc_day1 !== f.lean_doc_oct7 ? ' (added 7 Oct)' : '') + '</span><span>Dated ' + esc(F0.fmtDate(f.earliest_date)) + (f.latest_date !== f.earliest_date ? ' to ' + esc(F0.fmtDate(f.latest_date)) : '') + '</span>' +
        (b ? '<a href="#f-' + esc(f.id) + '">Read the entry</a>' : '') + '</p>' +
        (b ? '<p class="mm-info-r"><span><span class="h" aria-hidden="true"></span>Built on by ' + esc(b.who) + '</span></p>' : '');
      if (scroll && c) stage.scrollIntoView({ block: 'center', behavior: F0.motion() ? 'smooth' : 'auto' });
    }
    stage.addEventListener('keydown', function (e) {
      if (!order.length) return;
      var vis = order.filter(function (c) { return matches(c.f); });
      if (!vis.length) vis = order;
      var i = active ? vis.map(function (c) { return c.f; }).indexOf(active) : -1, next = null;
      if (e.key === 'ArrowRight') next = vis[Math.min(vis.length - 1, i + 1)];
      else if (e.key === 'ArrowLeft') next = vis[i < 0 ? 0 : Math.max(0, i - 1)];
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        var gk = i < 0 ? null : vis[i].gk, gks = [];
        vis.forEach(function (c) { if (gks.indexOf(c.gk) < 0) gks.push(c.gk); });
        var gi = gk == null ? -1 : gks.indexOf(gk), ng = gks[e.key === 'ArrowDown' ? Math.min(gks.length - 1, gi + 1) : Math.max(0, gi - 1)];
        next = vis.filter(function (c) { return c.gk === ng; })[0];
      } else if (e.key === 'Home') next = vis[0];
      else if (e.key === 'End') next = vis[vis.length - 1];
      else if (e.key === 'Enter' && active && BUILT[active.id]) { e.preventDefault(); location.hash = '#f-' + active.id; var h3 = $('#f-' + active.id + ' h3'); if (h3) { h3.setAttribute('tabindex', '-1'); h3.focus(); } return; }
      else if (e.key === 'Escape') { F0.tip.hide(); return; }
      if (!next) return;
      e.preventDefault();
      mark(next.f, false);
      tipShowAt(tip(next.f), next.g);
    });
    stage.addEventListener('focus', function () { if (!active && order.length) mark(order[0].f, false); });
    stage.addEventListener('blur', function () { F0.tip.hide(); });
    $$('.mm-map-ctrl [data-size]').forEach(function (b) { b.addEventListener('click', function () { size = b.getAttribute('data-size'); $$('.mm-map-ctrl [data-size]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); draw(); }); });
    $$('.mm-map-ctrl [data-snap]').forEach(function (b) { b.addEventListener('click', function () { snap = b.getAttribute('data-snap'); $$('.mm-map-ctrl [data-snap]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); draw(); if (active) mark(active, false); }); });
    if (q) q.addEventListener('input', function () { query = q.value.trim(); apply(); });
    var redraw = sized(stage, function () { draw(); });
    // table twin
    if (table) {
      var rows = fams.slice().sort(function (a, b) { return a.id < b.id ? -1 : 1; }).map(function (f) {
        var b = BUILT[f.id];
        return '<tr' + (b ? ' class="hl"' : '') + '><td class="n">' + esc(f.id) + '</td><td class="ti">' + titleHTML(f.title) + (f.title_oct7 && f.title_oct7 !== f.title ? '<br><span style="color:var(--ink-3)">7 Oct: ' + titleHTML(f.title_oct7) + '</span>' : '') + '</td><td>' + esc(subj(f)) + '</td><td>' + esc(FN[f.field] || f.field) + '</td>' +
          '<td class="n">' + f.n_manuscripts_day1 + (f.n_manuscripts_oct7 !== f.n_manuscripts_day1 ? ' → ' + f.n_manuscripts_oct7 : '') + '</td><td>' + (f.lean_doc_day1 ? 'yes' : f.lean_doc_oct7 ? 'from 7 Oct' : 'no') + '</td>' +
          '<td>' + esc(f.earliest_date === f.latest_date ? f.earliest_date : f.earliest_date + ' to ' + f.latest_date) + '</td><td>' + (b ? esc(b.who) : '') + '</td></tr>';
      }).join('');
      table.innerHTML = '<table class="tbl"><caption>OpenAI’s 372 result families. Subject is OpenAI’s own (overview.tex @ adc7f12); field is the broader group the map uses. Manuscripts: 6 Oct (→ 7 Oct where it changed).</caption><thead><tr><th scope="col" class="n">Family</th><th scope="col">Title</th><th scope="col">OpenAI subject</th><th scope="col">Map field</th><th scope="col" class="n">Manuscripts</th><th scope="col">Lean scope document</th><th scope="col">Folder dates</th><th scope="col">Founding members built on it</th></tr></thead><tbody>' + rows + '</tbody></table>';
    }
    return {
      show: function (id) {
        var f = byId[id]; if (!f) return;
        if (field && f.field !== field) { field = null; $$('button[data-field]', fieldsUl).forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); }
        if (query && !matches(f)) { query = ''; if (q) q.value = ''; }
        apply(); mark(f, true);
        setTimeout(function () { stage.focus({ preventScroll: true }); var c = cells.filter(function (x) { return x.f === f; })[0]; if (c) tipShowAt(tip(f), c.g); }, F0.motion() ? 450 : 0);
      },
      redraw: redraw
    };
  }

  /* ================= 3. the slack ================= */
  /* Built once per width and view; while the slider moves or play runs, only attributes and changed text are updated
     (no SVG rebuilds per frame), and the text readouts are quiet to screen readers until play stops. */
  function slack() {
    var host = $('#sk-host'), detail = $('#sk-detail'), range = $('#sk-range'), outp = $('#sk-out'), play = $('#sk-play'), prev = $('#sk-prev'), next = $('#sk-next'), tbl = $('#sk-table');
    if (!host || !range) return;
    var view = 'value', sel = ROWS[0], now = END, dstep = -1;
    var times = ALL.map(function (s) { return s.t; });
    function tAt(v) { return RELEASE + (END - RELEASE) * v / 1000; }
    function vAt(t) { return Math.round(1000 * (t - RELEASE) / (END - RELEASE)); }
    function best(r, t) { var b = null; r.steps.forEach(function (s) { if (s.t <= t) b = s; }); return b; }
    function nDone(t) { return times.filter(function (x) { return x <= t; }).length; }
    function factor(r, lv) { return r.up ? lv - r.before.lv : r.before.lv - lv; }
    function fmtFactor(d) {
      if (d < 1e-9) return '×1';
      if (d < 3) { var f = Math.pow(10, d); return '×' + (f < 10 ? f.toFixed(1) : Math.round(f)); }
      var e = Math.floor(d), m = Math.pow(10, d - e);
      return '×' + m.toFixed(1) + '×10^' + e;
    }
    function short(s) { return String(s).split(' ')[0]; }
    function sa(el, k, v) { v = String(v); if (el.getAttribute(k) !== v) el.setAttribute(k, v); } // set only what changed
    var VALUE = { lo: -90, hi: 4, ticks: [-80, -60, -40, -20, 0], lab: function (t) { return pow10(t); } };
    var FACTOR = { lo: 0, hi: 80, ticks: [0, 20, 40, 60, 80], lab: function (t) { return t === 0 ? '×1' : '×10^' + t; } };
    function scale() { return view === 'value' ? VALUE : FACTOR; }
    var playing = false;
    // build rows
    host.innerHTML = '';
    var axis = H('div', 'mm-sk-axis', host, '<span class="ax-l" id="sk-axl">Result · before → after</span>');
    var axHost = H('div', 'mm-sk-axhost', axis), axKey = '';
    var ol = H('ol', 'mm-sk-rows', host);
    ol.setAttribute('aria-label', 'Six refinements; choose one to see its steps');
    var rowEls = ROWS.map(function (r) {
      var li = H('li', 'mm-sk-row', ol), left = H('div', 'mm-sk-left', li);
      var b = H('button', 'mm-sk-sel', left);
      var tmp = document.createElement('div'); tmp.innerHTML = F0.statusBadges(r.status, { ladder: 1 });
      H('p', 'mm-sk-src', left, (tmp.firstElementChild ? tmp.firstElementChild.outerHTML : '') + '<a href="' + esc(r.src) + '">' + esc(r.srcL) + '</a>');
      b.type = 'button'; b.setAttribute('aria-pressed', 'false'); b.setAttribute('aria-controls', 'sk-detail');
      var tr = H('div', 'mm-sk-track', li);
      tr.setAttribute('aria-hidden', 'true');
      b.addEventListener('click', function () { select(r, true); });
      tr.addEventListener('click', function () { select(r, true); });
      tr.addEventListener('pointermove', function (e) { F0.tip.show(rowTip(r), e.clientX, e.clientY); });
      tr.addEventListener('pointerleave', function () { F0.tip.hide(); });
      return { r: r, li: li, b: b, tr: tr, key: '', bi: -2 };
    });
    function rowTip(r) {
      var b = best(r, now), lv = b ? b.lv : r.before.lv;
      return '<div class="tip-k">Family ' + r.fam + ' · ' + esc(r.name) + '</div><div class="tip-t">' + esc(r.sym) + ': ' + supHTML(r.before.s) + ' → ' + supHTML(b ? b.s : r.before.s) + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span class="tip-v">' + supHTML(fmtFactor(factor(r, lv))) + '</span><span>' + (r.up ? 'larger' : 'smaller') + ' · ' + (b ? (b.i + 1) + ' of ' + r.steps.length + ' steps' : 'no steps yet') + '</span></div></div>' +
        '<div class="tip-note">' + supHTML(r.what) + '</div>';
    }
    function drawAxis() {
      var w = width(axHost); if (!w || axKey === w + view) return;
      axKey = w + view;
      axHost.innerHTML = '';
      var sc = scale(), svg = S('svg', { viewBox: '0 0 ' + w + ' 40', width: w, height: 40, class: 'mm-svg', 'aria-hidden': 'true' }, axHost);
      var pad = 14, X = function (v) { return pad + (w - 2 * pad) * (v - sc.lo) / (sc.hi - sc.lo); };
      sc.ticks.forEach(function (t, i) { ST(svg, { x: X(t), y: 29, 'text-anchor': i === 0 && X(t) < 30 ? 'start' : i === sc.ticks.length - 1 && X(t) > w - 30 ? 'end' : 'middle' }, sc.lab(t)); S('line', { x1: X(t), x2: X(t), y1: 33, y2: 40, class: 'axis' }, svg); });
      S('text', { x: w - pad, y: 10, 'text-anchor': 'end', class: 't-ink', text: view === 'value' ? 'VALUE, LOG SCALE' : 'TIMES BETTER, LOG SCALE' }, svg);
    }
    /* each row: a hollow circle (before), a filled one (after) and the line between. When the two ends sit under
       8 px apart the dumbbell would read as one blob, so the row draws a ring around the dot and prints the values. */
    function drawRow(re) {
      var r = re.r, w = width(re.tr); if (!w) return;
      var h = Math.max(44, Math.round(re.tr.getBoundingClientRect().height) || 54), key = w + 'x' + h + view;
      var sc = scale(), pad = 14, X = function (v) { return pad + (w - 2 * pad) * (Math.max(sc.lo, Math.min(sc.hi, v)) - sc.lo) / (sc.hi - sc.lo); }, cy = h / 2;
      if (re.key !== key) {
        re.key = key; re.tr.innerHTML = '';
        var svg = S('svg', { viewBox: '0 0 ' + w + ' ' + h, width: w, height: h, class: 'mm-svg' }, re.tr);
        sc.ticks.forEach(function (t) { S('line', { x1: X(t), x2: X(t), y1: 0, y2: h, class: 'grid' }, svg); });
        re.line = S('line', { y1: cy, y2: cy, style: 'stroke:var(--acc-mm)', 'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
        re.c0 = S('circle', { cy: cy, r: 5.5, style: 'fill:var(--bg-1);stroke:var(--ink-2)', 'stroke-width': 1.6 }, svg);
        re.ring = S('circle', { cy: cy, r: 8.5, style: 'fill:var(--bg-1);stroke:var(--ink-2)', 'stroke-width': 1.6 }, svg);
        re.c1b = S('circle', { cy: cy, r: 7.5, style: 'fill:var(--bg-1)' }, svg);
        re.c1 = S('circle', { cy: cy, r: 5.5, style: 'fill:var(--acc-mm)' }, svg);
        re.lab = S('text', { y: cy + 4, class: 't-ink mm-halo' }, svg);
        S('rect', { x: 0, y: 0, width: w, height: h, class: 'hit' }, svg);
        re.labS = null;
      }
      var b = best(r, now), lvA = b ? b.lv : r.before.lv;
      var x0 = view === 'value' ? X(r.before.lv) : X(0), x1 = view === 'value' ? X(lvA) : X(factor(r, lvA));
      var close = !!b && Math.abs(x1 - x0) < 8;
      sa(re.line, 'x1', x0); sa(re.line, 'x2', x1);
      sa(re.line, 'visibility', !close && Math.abs(x1 - x0) > 0.5 ? 'visible' : 'hidden');
      sa(re.c0, 'cx', x0); sa(re.c0, 'visibility', close ? 'hidden' : 'visible');
      sa(re.ring, 'cx', x1); sa(re.ring, 'visibility', close ? 'visible' : 'hidden');
      [re.c1b, re.c1].forEach(function (c) { sa(c, 'cx', x1); sa(c, 'visibility', b ? 'visible' : 'hidden'); });
      sa(re.c1, 'r', close ? 4.2 : 5.5); sa(re.c1b, 'r', close ? 0 : 7.5);
      var txt = close ? short(r.before.s) + ' → ' + short(b.s) : '';
      if (txt !== re.labS) {
        re.labS = txt;
        while (re.lab.firstChild) re.lab.removeChild(re.lab.firstChild);
        if (txt) { var tmp = ST(re.lab.parentNode, {}, txt); while (tmp.firstChild) re.lab.appendChild(tmp.firstChild); tmp.parentNode.removeChild(tmp); }
      }
      if (txt) { var left = x1 > w / 2; sa(re.lab, 'x', left ? Math.min(x0, x1) - 14 : Math.max(x0, x1) + 14); sa(re.lab, 'text-anchor', left ? 'end' : 'start'); }
    }
    function fillRow(re) {
      var r = re.r, b = best(r, now), bi = b ? b.i : -1;
      if (re.bi === bi) return;
      re.bi = bi;
      var lv = b ? b.lv : r.before.lv;
      re.b.innerHTML = '<span class="nm">' + esc(r.name) + '<i>#' + r.fam + '</i></span>' +
        '<span class="ba">' + esc(r.sym) + ': ' + supHTML(r.before.s) + (b ? ' → <b>' + supHTML(b.s) + '</b>' : ' <i class="ns">no public step yet</i>') + '</span>' +
        '<span class="fx">' + supHTML(fmtFactor(factor(r, lv))) + ' ' + (r.up ? 'larger' : 'smaller') + ' · ' + (r.up ? 'bigger is better' : 'smaller is better') + '</span>';
      re.b.setAttribute('aria-label', r.name + ', family ' + r.fam + ': ' + r.sym + ' from ' + plain(r.before.s) + ' to ' + plain(b ? b.s : r.before.s) + ', ' + plain(fmtFactor(factor(r, lv)).replace('×', '').replace('×', ' times ')) + ' times ' + (r.up ? 'larger' : 'smaller') + '. Show its steps.');
    }
    var lastOut = 0;
    function writeOut(force) {
      var t = performance.now();
      if (!force && playing && t - lastOut < 250) return; // a few times a second at most while playing
      lastOut = t;
      var txt = (now >= END ? '14 Oct 2026' : utc(now)) + ' · ' + nDone(now) + ' of ' + NSTEPS + ' steps';
      if (outp.textContent !== txt) outp.textContent = txt;
      sa(range, 'aria-valuetext', txt);
    }
    function render(force) {
      drawAxis();
      rowEls.forEach(function (re) { fillRow(re); drawRow(re); if (re.li.classList.contains('sel') !== (re.r === sel)) re.li.classList.toggle('sel', re.r === sel); sa(re.b, 'aria-pressed', re.r === sel ? 'true' : 'false'); });
      writeOut(force);
      renderDetail();
    }
    /* detail: the selected row's own staircase over time, on a log axis fitted to that row */
    var dsvgHost = null, dout = null, D = null, hdrFor = null;
    function renderDetail() {
      if (!detail) return;
      var r = sel, b = best(r, now);
      if (!dsvgHost) {
        detail.innerHTML = '<div class="mm-sk-dh"><p class="mm-sk-dt" id="sk-dt"></p><div class="badges" id="sk-db"></div></div><p class="mm-sk-dn" id="sk-dn"></p><div id="sk-dsvg" class="mm-sk-dhost" tabindex="0" role="application" aria-roledescription="interactive chart" aria-labelledby="sk-dt" aria-describedby="sk-dout sk-dhelp"></div><p class="sr-only" id="sk-dhelp">Left and right arrow keys step through this result’s steps; Home and End jump to the first and last. Every step is also in the table below.</p><p class="mm-readout" id="sk-dout" aria-live="polite"></p>' +
          '<ul class="vlegend mm-sk-dleg" aria-label="How each step was checked"><li>' + markSVG('lean') + '<span><b>Lean</b> · rebuilt and checked by an outside leaderboard</span></li><li>' + markSVG('rev') + '<span><b>Reviewed</b> · certificates replayed by the maintainer</span></li><li>' + markSVG('own') + '<span><b>Own checks</b> · the author’s exact checks</span></li><li>' + markSVG('claim') + '<span><b>Claim</b> · not yet checked by anyone else</span></li></ul>';
        dsvgHost = $('#sk-dsvg', detail); dout = $('#sk-dout', detail);
        dsvgHost.addEventListener('keydown', function (e) {
          var n = sel.steps.length, k = null;
          if (e.key === 'ArrowRight') k = Math.min(n - 1, dstep + 1);
          else if (e.key === 'ArrowLeft') k = dstep < 0 ? n - 1 : Math.max(0, dstep - 1);
          else if (e.key === 'Home') k = 0; else if (e.key === 'End') k = n - 1;
          else if (e.key === 'Escape') { F0.tip.hide(); return; }
          if (k == null) return;
          e.preventDefault(); dstep = k; drawDetail(true); var m = $('[data-s="' + k + '"]', dsvgHost); if (m) tipShowAt(stepTip(sel.steps[k]), m);
        });
        dsvgHost.addEventListener('blur', function () { F0.tip.hide(); });
        sized(dsvgHost, function () { drawDetail(true); });
      }
      if (hdrFor !== r) {
        hdrFor = r;
        $('#sk-dt', detail).innerHTML = esc(r.name) + ' · family ' + r.fam + ' · ' + esc(r.sym) + ': ' + supHTML(r.before.s) + ' → <span id="sk-dt-v">' + supHTML(b ? b.s : r.before.s) + '</span>';
        $('#sk-db', detail).innerHTML = '<span class="mm-sk-dbk">Record on 14 Oct</span>' + F0.statusBadges(r.status, { ladder: 1 });
        $('#sk-dn', detail).innerHTML = supHTML(r.what) + ' Before: ' + supHTML(r.before.s) + ', ' + supHTML(r.before.note) + '. Source: <a href="' + esc(r.src) + '">' + esc(r.srcL) + '</a>.';
      }
      drawDetail(false);
    }
    function markSVG(ck) {
      var c = 'var(--acc-mm)';
      var inner = ck === 'lean' ? '<circle r="6.5" style="fill:none;stroke:' + c + '" stroke-width="1.4"/><circle r="4.2" style="fill:' + c + '"/>'
        : ck === 'rev' ? '<circle r="5" style="fill:' + c + '"/>'
          : ck === 'own' ? '<circle r="4.4" style="fill:var(--bg-2);stroke:' + c + '" stroke-width="1.6"/><path d="M0 -4.4A4.4 4.4 0 0 0 0 4.4Z" style="fill:' + c + '"/>'
            : '<circle r="4.4" style="fill:var(--bg-2);stroke:' + c + '" stroke-width="1.6"/>';
      return '<svg viewBox="-8 -8 16 16" aria-hidden="true">' + inner + '</svg>';
    }
    function stepTip(s) {
      return '<div class="tip-k">' + esc(utc(s.t)) + '</div><div class="tip-t">' + esc(s.row.sym) + ' = ' + supHTML(s.s) + '</div>' +
        '<div class="tip-rows"><div class="tip-row"><span>' + esc(s.who) + '</span></div><div class="tip-row"><span>' + esc(CHECK[s.ck]) + '</span></div></div>' +
        (s.note ? '<div class="tip-note">' + supHTML(s.note) + '</div>' : '');
    }
    function niceLogTicks(lo, hi) {
      var span = hi - lo, out = [];
      if (span <= 1.6) {
        for (var e = Math.floor(lo); e <= Math.ceil(hi); e++) [1, 2, 5].forEach(function (m) { var v = e + Math.log10(m); if (v >= lo - 1e-9 && v <= hi + 1e-9) out.push(v); });
        return out;
      }
      var step = [1, 2, 5, 10, 20, 25, 50].filter(function (s) { return span / s <= 5.5; })[0] || 50;
      for (var t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) out.push(t);
      return out;
    }
    function tickLabel(v) {
      var e = Math.round(v);
      if (Math.abs(v - e) < 1e-9) return e >= 0 && e <= 4 ? String(Math.pow(10, e)) : pow10(e);
      var x = Math.pow(10, v); return x >= 1 ? String(Math.round(x)) : x.toPrecision(1);
    }
    /* builds the staircase when the row, size or chosen step changes; otherwise only moves what time changes */
    function drawDetail(rebuild) {
      if (!dsvgHost) return;
      var r = sel, W = width(dsvgHost); if (!W) return;
      var key = r.id + '|' + W + '|' + dstep;
      if (rebuild || !D || D.key !== key) {
        dsvgHost.innerHTML = '';
        var small = W < 520, L = small ? 46 : 58, Rm = 14, T = 16, Hh = small ? 168 : 196, B = T + Hh, Ht = B + 30;
        var svg = S('svg', { viewBox: '0 0 ' + W + ' ' + Ht, width: W, height: Ht, class: 'mm-svg mm-sk-dsvg', 'aria-hidden': 'true' }, dsvgHost);
        var lvs = [r.before.lv].concat(r.steps.map(function (s) { return s.lv; }));
        var lo = Math.min.apply(null, lvs), hi = Math.max.apply(null, lvs), padv = Math.max(0.06, (hi - lo) * 0.08); lo -= padv; hi += padv;
        var t0 = RELEASE - 6 * 3600e3, t1 = END, X = function (t) { return L + (W - L - Rm) * (t - t0) / (t1 - t0); }, Y = function (v) { return B - Hh * (v - lo) / (hi - lo); };
        niceLogTicks(lo, hi).forEach(function (v) { S('line', { x1: L, x2: W - Rm, y1: Y(v), y2: Y(v), class: 'grid' }, svg); ST(svg, { x: L - 6, y: Y(v) + 4, 'text-anchor': 'end' }, tickLabel(v)); });
        for (var d = Date.parse('2026-10-07T00:00Z'); d <= END; d += 864e5) {
          S('line', { x1: X(d), x2: X(d), y1: B, y2: B + 5, class: 'axis' }, svg);
          if (!small || (new Date(d).getUTCDate() % 2 === 1)) S('text', { x: X(d), y: B + 18, 'text-anchor': d + 864e5 > END ? 'end' : 'middle', text: dayLabel(d).toUpperCase() }, svg);
        }
        S('line', { x1: L, x2: W - Rm, y1: B, y2: B, class: 'axis' }, svg);
        D = { key: key, r: r, X: X, Y: Y, W: W, labS: null, bi: -2 };
        var nowL = S('line', { y1: T, y2: B, style: 'stroke:var(--ink-3)', 'stroke-width': 1 }, svg);
        S('path', { d: pathFor(r, END), style: 'fill:none;stroke:var(--acc-mm);stroke-opacity:.28', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
        var solid = S('path', { style: 'fill:none;stroke:var(--acc-mm)', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
        S('circle', { cx: X(RELEASE), cy: Y(r.before.lv), r: 5, style: 'fill:var(--bg-1);stroke:var(--ink-2)', 'stroke-width': 1.6 }, svg);
        ST(svg, { x: X(r.steps[0].t) + 9, y: Y(r.before.lv) + 4, class: 't-ink mm-halo' }, 'OpenAI’s manuscript: ' + r.before.s);
        /* on a narrow chart, steps closer than a marker's width share one marker (the staircase still shows every step;
           the arrow keys and the table reach each one) */
        var gs = [], lastX = -1e9, lastY = -1e9, minGap = small ? 10 : 7;
        r.steps.forEach(function (s, k) {
          var cx = X(s.t), cy = Y(s.lv), isLast = k === r.steps.length - 1;
          if (minGap && k !== dstep && !isLast && Math.hypot(cx - lastX, cy - lastY) < minGap) return;
          lastX = cx; lastY = cy;
          var g = S('g', { class: 'stp', 'data-s': k }, svg), c = 'var(--acc-mm)';
          S('circle', { cx: cx, cy: cy, r: 12, style: 'fill:transparent' }, g);
          S('circle', { cx: cx, cy: cy, r: 7.5, style: 'fill:var(--bg-1)' }, g);
          if (s.ck === 'lean') { S('circle', { cx: cx, cy: cy, r: 6.4, style: 'fill:none;stroke:' + c, 'stroke-width': 1.4 }, g); S('circle', { cx: cx, cy: cy, r: 4, style: 'fill:' + c }, g); }
          else if (s.ck === 'rev') S('circle', { cx: cx, cy: cy, r: 4.6, style: 'fill:' + c }, g);
          else if (s.ck === 'own') { S('circle', { cx: cx, cy: cy, r: 4.4, style: 'fill:var(--bg-2);stroke:' + c, 'stroke-width': 1.6 }, g); S('path', { d: 'M' + cx + ',' + (cy - 4.4) + 'A4.4,4.4 0 0 0 ' + cx + ',' + (cy + 4.4) + 'Z', style: 'fill:' + c }, g); }
          else S('circle', { cx: cx, cy: cy, r: 4.4, style: 'fill:var(--bg-2);stroke:' + c, 'stroke-width': 1.6 }, g);
          if (k === dstep) S('circle', { cx: cx, cy: cy, r: 9.5, class: 'ring', style: 'fill:none;stroke:var(--focus)', 'stroke-width': 2 }, g);
          g.addEventListener('pointerenter', function (e) { dstep = k; setDout(); F0.tip.show(stepTip(s), e.clientX, e.clientY); });
          g.addEventListener('pointermove', function (e) { F0.tip.show(stepTip(s), e.clientX, e.clientY); });
          g.addEventListener('pointerleave', function () { F0.tip.hide(); });
          gs.push({ g: g, s: s });
        });
        var lab = S('text', { class: 't-strong mm-halo' }, svg);
        D.nowL = nowL; D.solid = solid; D.gs = gs; D.lab = lab;
      }
      tick();
      setDout();
    }
    function pathFor(r, upto) {
      var X = D.X, Y = D.Y, p = 'M' + X(RELEASE) + ',' + Y(r.before.lv);
      r.steps.forEach(function (s) { if (s.t > upto) return; p += 'H' + X(s.t) + 'V' + Y(s.lv); });
      return p + 'H' + X(Math.min(upto, END));
    }
    /* per frame: the slider's line, the solid staircase, which markers are past, the latest value's label */
    function tick() {
      if (!D) return;
      var r = D.r, X = D.X, Y = D.Y;
      sa(D.nowL, 'x1', X(now)); sa(D.nowL, 'x2', X(now)); sa(D.nowL, 'visibility', now < END ? 'visible' : 'hidden');
      sa(D.solid, 'd', pathFor(r, now));
      D.gs.forEach(function (o) { var op = o.s.t <= now ? '1' : '0.35'; if (o.g.getAttribute('opacity') !== op) o.g.setAttribute('opacity', op); });
      var b = best(r, now), bi = b ? b.i : -1;
      if (bi !== D.bi) {
        D.bi = bi;
        while (D.lab.firstChild) D.lab.removeChild(D.lab.firstChild);
        if (b) {
          var lx = X(b.t), ly = Y(b.lv), right = lx > D.W * 0.62;
          var tmp = ST(D.lab.parentNode, {}, b.s.length > 26 ? b.s.split(' ')[0] : b.s);
          while (tmp.firstChild) D.lab.appendChild(tmp.firstChild); tmp.parentNode.removeChild(tmp);
          D.lab.setAttribute('x', right ? lx - 12 : lx + 12); D.lab.setAttribute('y', ly + (r.up ? 20 : -11)); D.lab.setAttribute('text-anchor', right ? 'end' : 'start');
        }
        var v = $('#sk-dt-v', detail); if (v) v.innerHTML = supHTML(b ? b.s : r.before.s);
      }
    }
    var doutS = null;
    function setDout() {
      if (!dout) return;
      var r = sel, h;
      if (dstep >= 0 && r.steps[dstep]) { var s = r.steps[dstep]; h = '<b>Step ' + (dstep + 1) + ' of ' + r.steps.length + ', ' + esc(utc(s.t)) + ':</b> ' + esc(r.sym) + ' = ' + supHTML(s.s) + '. ' + esc(s.who) + '. ' + (s.note ? supHTML(s.note) + '. ' : '') + esc(CHECK[s.ck]) + '.' + (s.src ? ' <a href="' + esc(s.src) + '">Source</a>.' : ''); }
      else h = 'Focus the chart and use the arrow keys, or point at a step, to see who took it and how it was checked.';
      if (h !== doutS) { doutS = h; dout.innerHTML = h; }
    }
    function select(r, focus) {
      sel = r; dstep = -1; render(true);
      if (focus && window.matchMedia('(max-width: 760px)').matches) detail.scrollIntoView({ block: 'nearest', behavior: F0.motion() ? 'smooth' : 'auto' });
    }
    function setNow(t, fromRange) { now = Math.max(RELEASE, Math.min(END, t)); if (!fromRange) range.value = vAt(now); render(false); }
    range.addEventListener('input', function () { stop(); setNow(tAt(+range.value), true); writeOut(true); });
    prev.addEventListener('click', function () { stop(); var p = times.filter(function (x) { return x < now - 1000; }); setNow(p.length ? p[p.length - 1] : RELEASE); writeOut(true); });
    next.addEventListener('click', function () { stop(); var n = times.filter(function (x) { return x > now + 1000; }); setNow(n.length ? n[0] : END); writeOut(true); });
    $$('.mm-sk-ctrl [data-view]').forEach(function (b) {
      b.addEventListener('click', function () {
        view = b.getAttribute('data-view');
        $$('.mm-sk-ctrl [data-view]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        $$('.mm-only-factor').forEach(function (x) { x.style.display = view === 'factor' ? 'inline' : 'none'; });
        render(true);
      });
    });
    /* while playing, the readouts change many times a second: keep them quiet, then speak once when play stops */
    function quiet(on) {
      outp.setAttribute('aria-live', on ? 'off' : 'polite');
      if (dout) dout.setAttribute('aria-live', on ? 'off' : 'polite');
    }
    // play: walk the week in about 14 seconds, then stop on the last frame
    var t0 = 0, from = RELEASE, loop = F0.loop(function (ts) {
      if (!t0) t0 = ts;
      var t = from + (ts - t0) * (END - RELEASE) / 14000;
      if (t >= END) { setNow(END); stop(); return; }
      setNow(t);
    });
    function stop() {
      if (!playing) return;
      playing = false; loop.stop(); play.setAttribute('aria-pressed', 'false'); play.setAttribute('aria-label', 'Play the week from 6 October');
      quiet(false);
      setTimeout(function () { outp.textContent = ''; writeOut(true); }, 60); // one announcement of where play stopped
    }
    play.addEventListener('click', function () {
      if (playing) { stop(); return; }
      if (!F0.motion()) { // motion off: step instead of animating
        var n = times.filter(function (x) { return x > now + 1000; });
        setNow(now >= END ? times[0] : n.length ? n[0] : END); writeOut(true);
        return;
      }
      if (now >= END) now = RELEASE;
      from = now; t0 = 0; playing = true; quiet(true); loop.start();
      play.setAttribute('aria-pressed', 'true'); play.setAttribute('aria-label', 'Pause');
    });
    F0.onMotion(function (on) { if (!on) stop(); });
    F0.whenVisible(host, null, stop);
    var lw = 0;
    function onResize() { var w = width(host); if (w && w !== lw) { lw = w; render(true); } }
    if ('ResizeObserver' in window) new ResizeObserver(onResize).observe(host); else window.addEventListener('resize', onResize);
    render(true);
    // table twin: every step
    if (tbl) {
      var rows = ROWS.map(function (r) {
        return '<tr class="hl"><td colspan="5"><b>' + esc(r.name) + '</b> · family ' + r.fam + ' · ' + esc(r.sym) + ', ' + (r.up ? 'bigger is better' : 'smaller is better') + ' · before: ' + supHTML(r.before.s) + ' (' + supHTML(r.before.note) + ')</td></tr>' +
          r.steps.map(function (s) {
            return '<tr><td>' + esc(utc(s.t)) + '</td><td>' + supHTML(s.s) + '</td><td>' + esc(s.who) + (s.note ? '. ' + supHTML(s.note) : '') + '</td><td>' + esc(CHECK[s.ck]) + '</td><td>' + (s.src ? '<a href="' + esc(s.src) + '">link</a>' : '') + '</td></tr>';
          }).join('');
      }).join('');
      tbl.innerHTML = '<table class="tbl"><caption>' + NSTEPS + ' public steps, 7 to 13 October 2026 (UTC)</caption><thead><tr><th scope="col">When</th><th scope="col">Value</th><th scope="col">Who, and what</th><th scope="col">Checked how</th><th scope="col">Source</th></tr></thead><tbody>' + rows + '</tbody></table>';
    }
    // counts in prose
    $$('[data-nsteps]').forEach(function (e) { e.textContent = NSTEPS; });
  }

  /* ================= 4. pull out the foundation ================= */
  function foundation() {
    var b = $('#fd-btn'), list = $('#fd-list'), out = $('#fd-out');
    if (!b || !list) return;
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-pressed') !== 'true';
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? 'Put the manuscript back' : 'Suppose the manuscript had a gap';
      list.classList.toggle('pulled', on);
      var c = { falls: 0, stands: 0, part: 0, check: 0 };
      $$('li[data-fate]', list).forEach(function (li) { c[li.getAttribute('data-fate')]++; });
      out.innerHTML = on ? '<b>' + c.stands + ' of 6 would still stand</b> (the Lean-checked Fourier record, if its formal statement is the right one). ' + c.falls + ' would lose their footing, ' + c.part + ' would keep only its finite search, and ' + c.check + ' would need checking again.' : 'All six stand today. Five of them stand only as long as the OpenAI manuscripts beneath them hold; the Lean-checked Fourier record does not depend on its manuscript.';
    });
  }

  /* ================= 5. the seven entries' small figures =================
     One small figure per family, drawn from numbers already on this page (ROWS, the entries' own text).
     Each has a title, an SVG with an aria-label, and its caption is the text twin. Only the van der Waerden
     figure is interactive: its cells are real buttons. */
  function minis() {
    var rowBy = {}; ROWS.forEach(function (r) { rowBy[r.fam] = r; });
    var L10_2 = Math.log10(2);
    function svgIn(stage, W, Hh, label) {
      stage.innerHTML = '';
      return S('svg', { viewBox: '0 0 ' + W + ' ' + Hh, width: W, height: Hh, class: 'mm-svg mm-mini-svg', role: 'img', 'aria-label': label }, stage);
    }
    function mark(svg, x, y, filled, r) {
      S('circle', { cx: x, cy: y, r: (r || 5) + 2, style: 'fill:var(--bg-1)' }, svg);
      S('circle', { cx: x, cy: y, r: r || 5, style: filled ? 'fill:var(--acc-mm)' : 'fill:var(--bg-1);stroke:var(--ink-2)', 'stroke-width': 1.6 }, svg);
    }
    /* a horizontal log scale (log10 units) from the manuscript's value to the best public value, with each step as a tick */
    function logBar(svg, W, y, o) {
      var pad = 14, X = function (v) { return pad + (W - 2 * pad) * (v - o.lo) / (o.hi - o.lo); };
      S('line', { x1: pad, x2: W - pad, y1: y, y2: y, class: 'axis' }, svg);
      o.ticks.forEach(function (t, i) {
        S('line', { x1: X(t), x2: X(t), y1: y, y2: y + 5, class: 'axis' }, svg);
        ST(svg, { x: X(t), y: y + 18, 'text-anchor': i === 0 && X(t) < 30 ? 'start' : i === o.ticks.length - 1 && X(t) > W - 30 ? 'end' : 'middle' }, o.tickLab ? o.tickLab(t) : pow10(t));
      });
      S('line', { x1: X(o.before), x2: X(o.after), y1: y, y2: y, style: 'stroke:var(--acc-mm)', 'stroke-width': 2 }, svg);
      (o.steps || []).forEach(function (v) { S('line', { x1: X(v), x2: X(v), y1: y - 6, y2: y + 1, style: 'stroke:var(--acc-mm)', 'stroke-width': 1.2 }, svg); });
      mark(svg, X(o.before), y, false); mark(svg, X(o.after), y, true);
      var bx = X(o.before), ax = X(o.after);
      ST(svg, { x: bx, y: y - 12, 'text-anchor': bx < 40 ? 'start' : 'middle', class: 't-ink mm-halo' }, o.beforeLab);
      ST(svg, { x: ax, y: y - 12, 'text-anchor': ax > W - 60 ? 'end' : 'middle', class: 't-strong mm-halo' }, o.afterLab);
      if (o.factor) ST(svg, { x: (bx + ax) / 2, y: y + 34, 'text-anchor': 'middle', class: 't-ink' }, o.factor);
    }
    var DRAW = {
      /* 109: the κ staircase on a halvings scale, ending at the reviewed κ as F0.kappa() reports it */
      '109': function (stage, W, extra) {
        var r = rowBy['109'], pts = [[RELEASE, -182]].concat(r.steps.map(function (s) { return [s.t, s.lv / L10_2]; }));
        if (extra && extra.lg > pts[pts.length - 1][1] + 1e-9) pts.push([Math.min(END, extra.t), extra.lg]);
        var Hh = 150, L = 48, Rm = 14, T = 16, B = Hh - 26, svg = svgIn(stage, W, Hh, 'Staircase of log base 2 of kappa from minus 182 in the manuscript to about minus 9.22 on 13 October 2026, in 25 public steps.');
        var X = function (t) { return L + (W - L - Rm) * (t - RELEASE) / (END - RELEASE); }, Y = function (v) { return B - (B - T) * (v + 200) / 200; };
        [-160, -80, 0].forEach(function (v) { S('line', { x1: L, x2: W - Rm, y1: Y(v), y2: Y(v), class: 'grid' }, svg); ST(svg, { x: L - 6, y: Y(v) + 4, 'text-anchor': 'end' }, v === 0 ? '1' : '2^' + v); });
        S('line', { x1: L, x2: W - Rm, y1: B, y2: B, class: 'axis' }, svg);
        [['2026-10-07T00:00Z', '7 OCT'], ['2026-10-10T00:00Z', '10 OCT'], ['2026-10-13T00:00Z', '13 OCT']].forEach(function (d) { S('text', { x: X(Date.parse(d[0])), y: Hh - 8, 'text-anchor': 'middle', text: d[1] }, svg); });
        var d = 'M' + X(pts[0][0]) + ',' + Y(pts[0][1]);
        pts.slice(1).forEach(function (p) { d += 'H' + X(p[0]) + 'V' + Y(p[1]); });
        d += 'H' + X(END);
        S('path', { d: d, style: 'fill:none;stroke:var(--acc-mm)', 'stroke-width': 2, 'stroke-linejoin': 'round' }, svg);
        mark(svg, X(pts[0][0]), Y(-182), false, 4.5);
        var last = pts[pts.length - 1];
        mark(svg, X(last[0]), Y(last[1]), true, 4.5);
        ST(svg, { x: X(pts[1][0]) + 8, y: Y(-182) - 5, class: 't-ink mm-halo' }, '2^-182 · manuscript');
        ST(svg, { x: X(last[0]) - 8, y: Y(last[1]) + 18, 'text-anchor': 'end', class: 't-strong mm-halo' }, '2^' + last[1].toFixed(2));
      },
      /* 130: δ on a log scale */
      '130': function (stage, W) {
        var r = rowBy['130'], svg = svgIn(stage, W, 96, 'Log scale from 10 to the minus 13 to 10 to the minus 2: delta rose from 10 to the minus 13 in the manuscript, through 9 public steps, to 0.0012331685, about 1.2 times 10 to the 10 times larger.');
        logBar(svg, W, 44, { lo: -14, hi: -2, ticks: [-13, -10, -7, -4], before: -13, after: r.steps[r.steps.length - 1].lv, steps: r.steps.map(function (s) { return s.lv; }), beforeLab: '10^-13', afterLab: '0.00123', factor: '×1.2×10^10' });
      },
      /* 111: the guaranteed fraction on a log scale */
      '111': function (stage, W) {
        var r = rowBy['111'], svg = svgIn(stage, W, 96, 'Log scale from 10 to the minus 90 to 1: the guaranteed fraction rose from 2 to the minus 293 to (35/32) times 2 to the minus 31, about 5.1 times 10 to the minus 10, in six versions.');
        logBar(svg, W, 44, { lo: -95, hi: 0, ticks: [-80, -60, -40, -20, 0], before: r.before.lv, after: r.steps[r.steps.length - 1].lv, steps: r.steps.map(function (s) { return s.lv; }), beforeLab: '2^-293', afterLab: '5.1×10^-10', factor: '×8.1×10^78', tickLab: function (t) { return pow10(t); } });
      },
      /* 161: the counting constant, as bars */
      '161': function (stage, W) {
        var r = rowBy['161'], vals = [['manuscript', 1641]].concat(r.steps.map(function (s) { return [dayLabel(s.t), Math.round(Math.pow(10, s.lv))]; }));
        var Hh = 140, L = 14, Rm = 14, T = 20, B = Hh - 24, svg = svgIn(stage, W, Hh, 'Bar chart of the counting constant: 1641 in the manuscript, then 1032 and 978 on 9 October and 189 on 10 October.');
        var bw = Math.min(64, (W - L - Rm) / vals.length * 0.62), gap = (W - L - Rm) / vals.length, Y = function (v) { return B - (B - T) * v / 1700; };
        S('line', { x1: L, x2: W - Rm, y1: B, y2: B, class: 'axis' }, svg);
        vals.forEach(function (v, i) {
          var x = L + gap * (i + 0.5) - bw / 2, y = Y(v[1]);
          S('rect', { x: x, y: y, width: bw, height: B - y, style: i ? 'fill:var(--acc-mm)' : 'fill:var(--bg-1);stroke:var(--ink-2)', 'stroke-width': 1.4 }, svg);
          S('text', { x: x + bw / 2, y: y - 5, 'text-anchor': 'middle', class: i === vals.length - 1 ? 't-strong' : 't-ink', text: String(v[1]) }, svg);
          S('text', { x: x + bw / 2, y: Hh - 8, 'text-anchor': 'middle', text: v[0].toUpperCase() }, svg);
        });
      },
      /* 167: the two grids, one dot per selected pair */
      '167': function (stage, W) {
        var gaps = 18, avail = W - 28 - gaps, p = Math.min(14, avail / 28.5), y0 = 22, Hh = Math.round(y0 + 5 * p + 8), narrow = W < 460;
        var svg = svgIn(stage, W, Hh, 'Two grids of dots: 20 by 5, 100 selected pairs, in the manuscript; 8 by 4, 32 pairs, after the refinement.');
        function grid(x0, cols, rows, filled, lab) {
          for (var i = 0; i < cols; i++) for (var j = 0; j < rows; j++) S('circle', { cx: x0 + i * p + p / 2, cy: y0 + j * p + p / 2, r: Math.max(1.6, p * 0.28), style: filled ? 'fill:var(--acc-mm)' : 'fill:none;stroke:var(--ink-2)', 'stroke-width': 1 }, svg);
          S('text', { x: x0, y: y0 - 8, class: filled ? 't-strong' : 't-ink', text: lab }, svg);
        }
        grid(14, 20, 5, false, narrow ? '20×5 = 100 · BEFORE' : '20×5 = 100 · MANUSCRIPT');
        grid(14 + 20 * p + gaps, 8, 4, true, narrow ? '8×4 = 32' : '8×4 = 32 · AFTER');
      },
      /* 107: the exponent ω on a number line from 2 to 3 */
      '107': function (stage, W) {
        var Hh = 128, pad = 18, y = 58, svg = svgIn(stage, W, Hh, 'Number line of the matrix multiplication exponent from 2 to 3: 3 for the school method, 2.807 Strassen 1969, 2.371177 the best published bound in August 2026, 9/4 equals 2.25 claimed by OpenAI, and 2, the floor.');
        var X = function (v) { return W - pad - (W - 2 * pad) * (v - 2); }; // 3 on the left, 2 on the right: smaller is better
        S('line', { x1: X(3), x2: X(2), y1: y, y2: y, class: 'axis' }, svg);
        var narrow = W < 460, P = [[3, '3', 'school', 'up'], [2.80735, '2.807', 'Strassen 1969', 'down'], [2.371177, '2.371', narrow ? 'Aug 2026' : 'record, Aug 2026', 'up'], [2.25, '9/4', 'OpenAI claim', 'down'], [2, '2', 'floor', 'up']];
        P.forEach(function (q) {
          var x = X(q[0]), up = q[3] === 'up', claim = q[1] === '9/4';
          S('line', { x1: x, x2: x, y1: y - 5, y2: y + 5, class: 'axis' }, svg);
          if (claim) mark(svg, x, y, true, 4.5); else S('circle', { cx: x, cy: y, r: 3.2, style: 'fill:var(--ink-2)' }, svg);
          var anchor = x < 40 ? 'start' : x > W - 40 ? 'end' : 'middle';
          S('text', { x: x, y: up ? y - 22 : y + 24, 'text-anchor': anchor, class: claim ? 't-strong' : 't-ink', text: q[1] }, svg);
          S('text', { x: x, y: up ? y - 10 : y + 36, 'text-anchor': anchor, text: q[2].toUpperCase() }, svg);
        });
        // the barrier: a limit on one step of the 9/4 method, not a new bound
        var xb = X(2.25);
        S('line', { x1: xb, x2: xb, y1: y + 42, y2: y + 52, style: 'stroke:var(--hair)', 'stroke-width': 1.4 }, svg);
        S('text', narrow ? { x: pad, y: Hh - 6, 'text-anchor': 'start', class: 't-ink', text: 'rohanarun: a limit, not a new bound' } : { x: Math.min(xb + 8, W - pad), y: Hh - 6, 'text-anchor': 'end', class: 't-ink', text: 'rohanarun: a limit on one step, not a new bound' }, svg);
      }
    };
    $$('.mm-mini[data-mini]').forEach(function (fig) {
      var fam = fig.getAttribute('data-mini'), stage = $('.mm-mini-stage', fig);
      if (fam === '160') { vdw(fig, stage); return; }
      var fn = DRAW[fam]; if (!fn || !stage) return;
      var extra = null, redraw = sized(stage, function (w) { fn(stage, w, extra); });
      if (fam === '109' && F0.kappa) F0.kappa().then(function (k) {
        if (!k || !/^0\.\d+$/.test(String(k.decimal))) return;
        var lg = Math.log2(parseFloat(k.decimal)), live = k.source === 'live';
        extra = { lg: lg, t: Date.parse(k.at) || END };
        var sp = $('[data-mini-live]', fig);
        if (sp) sp.textContent = 'Last point: ' + k.decimal + (live ? ', fetched just now from the race’s repository' : k.source === 'snapshot' ? ', the snapshot of 13 Oct (the live file could not be reached)' : ', from this site’s own feed') + '.';
        redraw();
      }).catch(function () {});
    });
    /* 160: colour 1..N with two colours and look for a one-colour evenly spaced triple */
    function vdw(fig, stage) {
      var start = [0, 0, 1, 1, 0, 0, 1, 1], col = start.slice(), N = 8;
      stage.innerHTML = '<div class="mm-vdw-ctrl" role="group" aria-label="How many numbers"><div class="seg" role="group" aria-label="Numbers"><button type="button" data-n="8" aria-pressed="true">1–8</button><button type="button" data-n="9" aria-pressed="false">1–9</button></div><button type="button" class="tbtn" data-act="mix">Mix the colours</button><button type="button" class="tbtn" data-act="reset">Start again</button></div>' +
        '<div class="mm-vdw" role="group" aria-label="The numbers; press one to switch its colour"></div><svg class="mm-svg mm-vdw-arc" aria-hidden="true"></svg><p class="mm-vdw-out" aria-live="polite"></p><div class="mm-vdw-c"></div>';
      var row = $('.mm-vdw', stage), arc = $('.mm-vdw-arc', stage), out = $('.mm-vdw-out', stage), cbar = $('.mm-vdw-c', stage);
      function triple() {
        for (var d = 1; d <= 4; d++) for (var a = 1; a + 2 * d <= N; a++) if (col[a - 1] === col[a + d - 1] && col[a - 1] === col[a + 2 * d - 1]) return [a, a + d, a + 2 * d];
        return null;
      }
      function paint(say) {
        row.innerHTML = '';
        for (var i = 1; i <= N; i++) {
          var b = document.createElement('button');
          b.type = 'button'; b.className = 'c' + col[i - 1]; b.textContent = i; b.setAttribute('data-i', i);
          b.setAttribute('aria-label', i + ', ' + (col[i - 1] ? 'second' : 'first') + ' colour');
          row.appendChild(b);
        }
        var t = triple();
        $$('button', row).forEach(function (b) { if (t && t.indexOf(+b.getAttribute('data-i')) >= 0) b.classList.add('hit'); });
        // arc joining the triple
        arc.innerHTML = '';
        var w = row.getBoundingClientRect().width;
        arc.setAttribute('viewBox', '0 0 ' + Math.max(1, w) + ' 22'); arc.setAttribute('width', Math.max(1, w)); arc.setAttribute('height', 22);
        if (t) {
          var bs = $$('button', row), r0 = row.getBoundingClientRect();
          var xs = t.map(function (k) { var bb = bs[k - 1].getBoundingClientRect(); return bb.left - r0.left + bb.width / 2; });
          S('path', { d: 'M' + xs[0] + ',2 Q' + (xs[0] + xs[1]) / 2 + ',20 ' + xs[1] + ',2 Q' + (xs[1] + xs[2]) / 2 + ',20 ' + xs[2] + ',2', style: 'fill:none;stroke:var(--ink)', 'stroke-width': 1.6 }, arc);
        }
        var txt = t ? 'Found: ' + t.join(', ') + ' are one colour and evenly spaced (step ' + (t[1] - t[0]) + ').' + (N === 9 ? ' With 9 numbers this always happens: W(3;2) = 9.' : '')
          : 'No one-colour evenly spaced triple among 1–' + N + '.' + (N === 8 ? ' Now choose 1–9 and try both colours for 9.' : '');
        if (say !== false) out.textContent = txt; else out.textContent = txt;
      }
      row.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-i]'); if (!b) return;
        var i = +b.getAttribute('data-i'); col[i - 1] = 1 - col[i - 1]; paint();
        var nb = $('button[data-i="' + i + '"]', row); if (nb) nb.focus();
      });
      $$('[data-n]', stage).forEach(function (b) { b.addEventListener('click', function () {
        N = +b.getAttribute('data-n'); while (col.length < N) col.push(0); col.length = N;
        $$('[data-n]', stage).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); paint();
      }); });
      $('[data-act="mix"]', stage).addEventListener('click', function () { for (var i = 0; i < N; i++) col[i] = Math.random() < 0.5 ? 0 : 1; paint(); });
      $('[data-act="reset"]', stage).addEventListener('click', function () { col = start.slice(); if (N === 9) col.push(0); paint(); });
      sized(cbar, function (w) {
        cbar.innerHTML = '';
        var svg = S('svg', { viewBox: '0 0 ' + w + ' 70', width: w, height: 70, class: 'mm-svg mm-mini-svg', role: 'img', 'aria-label': 'Log scale of the constant c: from 1 over 100000 in the manuscript, through 7 public steps, to 1 over 9, about 11,111 times larger.' }, cbar);
        var r = rowBy['160'];
        logBar(svg, w, 26, { lo: -5.4, hi: 0, ticks: [-5, -4, -3, -2, -1, 0], before: -5, after: r.steps[r.steps.length - 1].lv, steps: r.steps.map(function (s) { return s.lv; }), beforeLab: 'c = 1/100000', afterLab: '1/9', tickLab: function (t) { return t === 0 ? '1' : pow10(t); } });
      });
      paint(false);
      window.addEventListener('resize', function () { paint(false); });
    }
  }

  /* ================= the live reviewed κ (family 109 entry) ================= */
  function kappa() {
    var box = $('#kappa-live'); if (!box || !F0.kappa) return;
    var AUTHOR = { 1094: 'founding member rohanarun' };
    F0.kappa().then(function (k) {
      if (!k || !/^0\.\d+$/.test(String(k.decimal))) return;
      var live = k.source === 'live';
      if (!live && !(Date.parse(k.at) > Date.parse('2026-10-13T18:45:23Z'))) return; // the local feed is older than the figure printed above
      $('[data-k-when]', box).textContent = live ? 'live · fetched ' + utc(k.at) : 'feed.json snapshot · ' + (k.at ? utc(k.at) : 'date unknown');
      $('.dot', box).className = 'dot ' + (live ? 'live' : 'stale');
      if (!live) box.querySelector('[data-k-src]').href = R + 'feed.json';
      $('[data-k-v]', box).textContent = k.decimal;
      $('[data-k-k]', box).textContent = live
        ? 'the maintainer-reviewed κ right now' + (k.pr ? ', PR #' + k.pr + (AUTHOR[k.pr] ? ' by ' + AUTHOR[k.pr] : '') : '') + (k.decimal === '0.001672660197076918' ? ' (unchanged since 13 Oct)' : ' (newer than this page’s 13 Oct figure)')
        : 'the last value in this site’s own κ feed, which may be older than the race';
      box.hidden = false;
    }).catch(function () {});
  }

  /* ================= wire up ================= */
  function boot() {
    timeline();
    slack();
    foundation();
    kappa();
    minis();
    Promise.all([F0.json(R + 'data/openai-math-families.json'), F0.json('openai-subjects.json').catch(function () { return null; })]).then(function (d) {
      var m = map(d[0], d[1]);
      $$('.mm-show[data-show]').forEach(function (b) {
        b.addEventListener('click', function () { if (m) m.show(('00' + b.getAttribute('data-show')).slice(-3)); });
      });
    }).catch(function (e) {
      console.warn('families:', e);
      var st = $('#map-stage'); if (st) st.innerHTML = '<p class="mm-noscript">The map could not load its data. The family list is in <a href="' + R + 'data/openai-math-families.json">data/openai-math-families.json</a>.</p>';
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { window.dispatchEvent(new Event('resize')); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
