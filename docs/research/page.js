/* Research index (research/): page script.
   Renders, from data/projects.json, data/members.json and data/openai-math-families.json:
     - the hero figure: each project's numbers at the three steps (agents propose, checkers verify, people decide)
     - the evidence ladder: where each project's own status line puts it
     - the project cards, each with a small live figure drawn in the browser
     - every founding member's repositories, with a filter
   Figures start on a still, informative frame and only move on hover, focus or play (and never with motion off). */
(function () {
  'use strict';
  var F0 = window.F0;
  if (!F0) return;
  var R = F0.root || '../', esc = F0.esc;
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function tk(n) { return F0.css(n); }
  function mono(px) { return '500 ' + px + 'px ' + (tk('--f-mono') || 'monospace'); }
  function rel(u) { return u && !/^(https?:|mailto:|#|\.{1,2}\/|\/)/.test(u) ? R + u : u; } // data-file pages are relative to docs/
  function fmtN(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function utc(t) { var d = new Date(t); return d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear() + ', ' + ('0' + d.getUTCHours()).slice(-2) + ':' + ('0' + d.getUTCMinutes()).slice(-2) + ' UTC'; }
  /* data strings write powers with a caret ("2^-182", "(log n)^(1−δ)"); show them as superscripts */
  function supHTML(str) {
    var U = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '−' };
    return esc(str).replace(/\^\(([^)]*)\)/g, '<sup>$1</sup>').replace(/\^([−-]?[0-9.]+)/g, function (m, e) { return '<sup>' + e.replace('-', '−') + '</sup>'; })
      .replace(/\^([A-Za-zθκδ′]+)/g, '<sup>$1</sup>').replace(/[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+/g, function (m) { return '<sup>' + m.replace(/./g, function (c) { return U[c]; }) + '</sup>'; });
  }
  /* canvas text with a real superscript: the exponent drawn smaller and raised, never Unicode superscript digits */
  function fillSup(x, base, exp, px, py, size) {
    var al = x.textAlign; x.textAlign = 'left';
    var w0 = x.measureText(base).width;
    x.fillText(base, px, py);
    var f = x.font; x.font = mono(Math.max(9, Math.round(size * 0.78)));
    x.save(); x.textBaseline = 'alphabetic'; x.fillText(exp, px + w0 + 0.5, py - size * 0.12); x.restore();
    x.font = f; x.textAlign = al;
  }

  /* ---------- presentation per project (all numbers either from projects.json or sourced here) ---------- */
  var P = {
    'incentre-lattice': {
      acc: '--acc-incentre', field: 'Geometry', who: 'Ahraz Arifuddin · Aska Digital',
      credit: '<b>Aska Digital’s own work.</b> Founding member Ahraz Arifuddin chose the questions and signs the claims; AI models from Anthropic and OpenAI drafted most of the proofs, code and checks, and the paper records which model did what.',
      glyph: 'doodle', gk: 'THE DOODLE, DRAWN EXACTLY', gr: 'r = (√2−1)/2',
      aria: 'A row of squares, each with its two diagonals and one dot at the incentre of each of its four triangles. Each dot sits (root 2 minus 1) over 2 of a side in from the edge.',
      cap: 'A square, its diagonals, one dot per triangle at its incentre (the centre of the circle that fits inside it). Neighbouring dots end up √2 − 1 apart.',
      loop: [
        ['5 runs', 'an AI search loop went from density 0.4686 to the Kepler bound 0.7405 in about 11 minutes', 'autoresearch-fold/results.tsv'],
        ['16,240', 'exact numbers, every one ≥ 0, that rule out a collision anywhere along the fold (3,248 pair tests)', 'results/fold-continuous-fcc/certificate.json'],
        ['v2', 'preprint published and signed by Ahraz Arifuddin on Zenodo, 13 Oct 2026; no person other than the author has checked the proofs yet', 'doi.org/10.5281/zenodo.23340326']
      ],
      /* the index's own wording for each card's numbers (plain words, as on the project page); each keeps its source */
      stats: [
        { value: '22.3% → 74.05%', label: 'space filled by the balls along the exact fold, from loose scaffold to the densest possible stacking, π/√18', source: 'results/fold-continuous-fcc/certificate.json; PROOF.md', href: 'https://foundation-0.github.io/incentre-lattices/results/fold-continuous-fcc/certificate.json' },
        { value: '16,240', label: 'exact numbers, every one ≥ 0, ruling out a collision anywhere along the fold (3,248 pair tests)', source: 'results/fold-continuous-fcc/PROOF.md', href: 'https://github.com/Foundation-0/incentre-lattices/blob/main/results/fold-continuous-fcc/PROOF.md' },
        { value: '1/(n^2−n−1)', label: 'how much the framework thins sideways when stretched, in every dimension n ≥ 3 (written proof, reviewed only by AI models)', source: 'results/rigidity-nd/PROOF.md', href: 'https://github.com/Foundation-0/incentre-lattices/blob/main/results/rigidity-nd/PROOF.md' },
        { value: '~11 min', label: 'for an AI search loop to climb from 46.9% to the 74.05% ceiling, in 5 logged runs', source: 'autoresearch-fold/results.tsv (07:56:10 to 08:06:56)', href: 'https://foundation-0.github.io/incentre-lattices/autoresearch-fold/results.tsv' }
      ] },
    'exoplanets': {
      acc: '--acc-exoplanets', field: 'Astronomy', who: 'eumemic, with Aska',
      credit: '<b>Founding member eumemic’s project</b>, built with Claude Code. Aska sent ten merged pull requests, one of which built the first version of its website; one fix, restoring light curves the data reader had dropped (PR #6), led to a re-search that added 120 counted candidates.',
      glyph: 'stack', gk: 'SCHEMATIC · STACKING PASSES', gr: '',
      aria: 'Schematic: as more passes of a planet are stacked, simulated noise shrinks and a 398 parts-per-million dip in the star’s light stands out.',
      cap: 'Why stacking works: noise shrinks like 1/√N as passes are added, until a dip too small to see once stands out. The dip is TIC 4206066’s published 398 ppm, 1.7 h signal; the noise is simulated.',
      loop: [
        ['7,459,491', 'repeating dips found by the first full-sky search in NASA’s public TESS data', 'eumemic/exoplanets README.md, full-sky search table'],
        ['13,986', 'of them matched no known planet or TESS Object of Interest and passed all 17 automated tests of LEO-Vetter, a published vetting tool', 'README.md, full-sky search table'],
        ['665', 'counted as planet candidates on 14 Oct 2026, each with predicted transit times anyone can test; none confirmed yet', 'README.md, note of 14 Oct 2026 (58c6318)']
      ],
      stats: [
        { value: '4,039,203', label: 'stars searched in the full-sky search, using every TESS sector from 1 to 104 (2018 to 2026)', source: 'README.md, full-sky search table, at 58c6318', href: 'https://github.com/eumemic/exoplanets/blob/58c6318/README.md#full-sky-search-8-october-2026' },
        { value: '665', label: 'planet candidates counted on 14 Oct 2026 (607 from the full-sky search, 58 from earlier ones); none confirmed', source: 'results_public/candidates_allsky.csv + tiers_earlier_candidates.csv at 58c6318', href: 'exoplanets/candidates.json' },
        { value: '7,459,491 → 13,986', label: 'repeating dips found; of them, those that matched no known planet or TESS Object of Interest and passed all 17 automated tests of LEO-Vetter, a published vetting tool', source: 'README.md, full-sky funnel, at 58c6318', href: 'https://github.com/eumemic/exoplanets/blob/58c6318/results_public/funnel_allsky.csv' },
        { value: '82%', label: 'of the full-sky candidates checked are on stars seen only in wide-field images, which NASA’s multi-sector search does not cover', source: 'validation/findability.md (404 of 494, 13 Oct 2026)', href: 'https://github.com/eumemic/exoplanets/blob/58c6318/validation/findability.md' }
      ] },
    'integer-multiplication': {
      acc: '--acc-intmult', field: 'Algorithms', who: 'Doug Colkitt + crowd',
      credit: '<b>Founding member Doug Colkitt’s race (CrocSwap).</b> Founding member rohanarun held the reviewed record on 14 Oct (PR #1094), and eumemic sent 80 pull requests. Aska built the live race tracker that grew into this site, and submitted two small claims that were never reviewed and were soon overtaken.',
      glyph: 'kappa', gk: 'LOG₂ κ · DATED 23 SEP → 13 OCT', gr: 'log₂κ −9.22',
      aria: 'Staircase of the exponent saving kappa on a halvings scale: from 2 to the minus 182 in the machine-written paper dated 23 September to about 2 to the minus 9.22 on 13 October 2026.',
      cap: 'Every reviewed record on a halvings scale, from the machine-written paper’s 2^-182 to 2^-9.22. All of them rest on that unreviewed paper.',
      loop: [
        ['1,334', 'pull requests opened by people and their agents in the first week', 'git ls-remote refs/pull/*/head, 13 Oct 2026'],
        ['47', 'assembly inequalities the current record passes in exact arithmetic, with independent owner and pricing audits', 'CrocSwap/integer-mult-bounds README, PR #1094 review'],
        ['17', 'reviewed records selected by maintainer Doug Colkitt, 9 to 13 Oct; all conditional on the unreviewed manuscript', 'certificates/selected-result.json history (20 commits, 17 distinct values)']
      ],
      stats: [
        { live: true, value: '0.001672660197076918', label: 'reviewed κ, conditional, PR #1094 by founding member rohanarun', source: 'certificates/selected-result.json @ 0a31ad884' },
        { value: '2^-182 → 2^-9.22', label: 'κ since the machine-written preprint dated 23 Sep 2026 (about 1.03×10^52 times larger)', source: 'upstream/build/sections/00-introduction.tex; log2 of selected κ (computed)' },
        { value: '17', label: 'successive reviewed κ records in 5 days (9–13 Oct)', source: 'git log -- certificates/selected-result.json (20 commits, 17 distinct values)', href: 'https://github.com/CrocSwap/integer-mult-bounds/commits/main/certificates/selected-result.json' },
        { value: '1,334', label: 'pull requests opened upstream by 13 Oct 2026 (highest #1374)', source: 'git ls-remote origin refs/pull/*/head, 13 Oct 2026, about 23:40 UTC' }
      ] },
    'machine-mathematics': {
      acc: '--acc-mm', field: 'Mathematics', who: 'Members + crowd',
      credit: '<b>Starts from OpenAI’s 722 machine-written manuscripts.</b> Founding members rohanarun and Ryan Shea took six of its families further within a week, and Doug Colkitt’s race a seventh; eumemic and many others joined in.',
      glyph: 'slack', gk: 'TIMES BETTER, LOG SCALE', gr: '',
      aria: 'Six bars on a logarithmic scale, one per refined result, showing how many times better each number became: about 10 to the 79 for the matroid fraction, 10 to the 52 for kappa, 10 to the 10 for the Fourier saving, 11,111 for the van der Waerden constant, 8.7 for the Sidorenko constant and 3.1 for the unit-distance grid.',
      cap: 'How many times better six numbers got in a week, on a log scale. Long bars mean loose first proofs, not important results.',
      loop: [
        ['722', 'manuscripts written by one OpenAI model, with about three hours of computing per result on average', 'openai/math README @ adc7f12 and fd4aeeb'],
        ['300 / 719', 'top-line results formalized in Lean by OpenAI’s own count on 7 Oct; its catalogue marks them unreviewed', 'openai/math history.md @ fd4aeeb'],
        ['3', 'manuscripts withdrawn by OpenAI on 7 Oct after a sign error; none refereed by people so far', 'openai/math history.md @ fd4aeeb']
      ] },
    'mobius-x1': {
      acc: '--acc-mobius', field: 'Circuits', who: 'Swapnil Jain + Aska',
      credit: '<b>Swapnil Jain’s repository.</b> Aska wrote and ran the full-network check behind Theorem 2, its strongest version: 3,456,000 bank swaps tested in a network of size h = 10, with zero failures (merged PR #1).',
      glyph: 'pascal', gk: 'PASCAL MOD 2 · 32 INPUTS', gr: 'row 31',
      aria: 'Pascal’s triangle modulo 2 for 32 inputs: the zero-one matrix the Möbius transform computes, a Sierpinski triangle.',
      cap: 'The matrix the transform computes, made here from Pascal’s triangle with the odd entries filled. The claimed saving only appears when the input has billions of digits.',
      loop: [
        ['3', 'versions of the claimed theorem, researched and drafted with Claude', 'mobius-x1 README.md, NOTICE'],
        ['0 / 3,456,000', 'failures in Aska’s full-network check of Theorem 2; Lean checks the arithmetic core', 'certificates/run_e1_rep_h10_bad0.txt'],
        ['0', 'human referees so far; it was refereed only by AI agents, and says so', 'mobius-x1 README.md']
      ],
      stats: [
        { value: '4.37 × 10^-11', label: 'how far below 1 the claimed exponent drops: N·(log N)^θ′ with θ′ = 1 − 4.3713·10^-11 (Theorem 2)', source: 'README.md; Lean bound in lean/MobiusLean/Prepass.lean', href: 'https://github.com/Swapnil-jain/mobius-x1/blob/main/README.md' },
        { value: '0 / 3,456,000', label: 'failed checks in Aska’s full run of the network at label size h = 10 (all 43,200 runs of the step)', source: 'certificates/run_e1_rep_h10_bad0.txt', href: 'https://github.com/Swapnil-jain/mobius-x1/blob/main/certificates/run_e1_rep_h10_bad0.txt' },
        { value: '92', label: 'supporting theorems checked by Lean; the main theorem is not one of them', source: 'lean/axioms.out', href: 'https://github.com/Swapnil-jain/mobius-x1/blob/main/lean/axioms.out' },
        { value: '0', label: 'human referees so far; AI referees read it (2 for Theorem 1, 1 each for Theorems 1′ and 2)', source: 'docs/RESULT.md', href: 'https://github.com/Swapnil-jain/mobius-x1/blob/main/docs/RESULT.md' }
      ] },
    'gf2m-circuits': {
      acc: '--acc-gf2m', field: 'Cryptography', who: 'Swapnil Jain + Aska',
      credit: '<b>Swapnil Jain’s repository.</b> Aska contributed verified multipliers for four more binary fields, built with the papers’ method (merged PR #1); they are not records.',
      glyph: 'gates', gk: 'GATES vs DEPTH · AES FIELD', gr: '−5 at depth 6',
      aria: 'Gates against circuit depth for multiplying in the AES field: the 2010 record of 117 gates at depth 6, and the 2026 circuits of 112 gates at depth 6, 110 at 7, 108 at 12 and 107 at 13.',
      cap: 'Each new multiplier is checked on all 65,536 input pairs and proved in Lean. Hollow mark: the 2010 record.',
      loop: [
        ['112', 'gates for an AES-field multiplier at depth 6, found by a search that scores every candidate wiring by total gates (2010 record: 117)', 'papers/Jain_GF2m_multipliers_2026.pdf, Table 1'],
        ['65,536', 'input pairs every AES-field multiplier is tested on, all of them; 30 Lean proofs that circuits compute the right answer (their gate counts are not Lean-checked)', 'multipliers/tools/verify.py; multipliers/lean, sbox/lean'],
        ['2', 'papers posted in the repository by Swapnil Jain, who signs them; not peer reviewed', 'papers/ in the repository']
      ],
      /* the ladder ranks a project by its headline claim: the papers' gate counts are preprint claims, though every circuit's correctness is Lean-proved */
      rung: 2, rungNote: 'Preprint: circuit correctness is Lean-proved; gate counts and comparisons are not.',
      stats: [
        { value: '117 → 112', label: 'gates to multiply in the AES field at the 2010 record’s depth (6); 107 if depth 13 is allowed (Jain 2026)', source: 'papers/Jain_GF2m_multipliers_2026.pdf Tables 1–2; re-verified with multipliers/tools/verify.py', href: 'https://github.com/Swapnil-jain/gf2m-circuits/blob/main/papers/Jain_GF2m_multipliers_2026.pdf' },
        { value: '106', label: 'gates for the AES S-box from AND, XOR and XNOR gates (Jain 2026, depth 24; the smallest found before was 110 at depth 22, NIST 2026)', source: 'papers/Jain_AES_Sbox_circuits_2026.pdf Table 1; sbox/verify_results.txt', href: 'https://github.com/Swapnil-jain/gf2m-circuits/blob/main/papers/Jain_AES_Sbox_circuits_2026.pdf' },
        { value: '109', label: 'gates for the inverse AES S-box (Jain 2026, depth 30; NIST 2026: 112 at depth 26)', source: 'papers/Jain_AES_Sbox_circuits_2026.pdf Table 1; sbox/verify_results.txt', href: 'https://github.com/Swapnil-jain/gf2m-circuits/blob/main/sbox/verify_results.txt' },
        { value: '30', label: 'Lean 4 proofs that a circuit computes the right answer (19 multipliers, 11 S-boxes); gate counts and depths are not Lean-checked', source: 'multipliers/lean, sbox/lean and their .out files', href: 'https://github.com/Swapnil-jain/gf2m-circuits/tree/main/multipliers/lean' }
      ] }
  };
  var ORDER_RESEARCH = ['incentre-lattice', 'exoplanets', 'integer-multiplication', 'machine-mathematics'];
  var ORDER_CONTRIB = ['mobius-x1', 'gf2m-circuits'];
  var LOOP_ORDER = ['exoplanets', 'integer-multiplication', 'incentre-lattice', 'machine-mathematics', 'mobius-x1', 'gf2m-circuits'];
  var STATIONS = [['Agents propose', 'dig'], ['Checkers verify', 'chk'], ['People decide and sign', 'bio']];

  /* reviewed κ records (CrocSwap/integer-mult-bounds certificates/selected-result.json history and README) */
  var KAPPA = [['2026-09-23T00:00Z', -182], ['2026-10-07T02:22Z', Math.log2(5.8e-33)], ['2026-10-07T13:35Z', -78], ['2026-10-07T19:27Z', -59], ['2026-10-08T00:27Z', Math.log2(8.3e-11)],
    ['2026-10-08T01:10Z', -31], ['2026-10-08T13:10Z', -30], ['2026-10-08T15:18Z', Math.log2(3.886675852e-5)], ['2026-10-08T18:24Z', Math.log2(5.1016920170078e-5)],
    ['2026-10-09T04:53Z', Math.log2(0.0004609169)], ['2026-10-09T05:55Z', Math.log2(0.000472143085)], ['2026-10-09T06:01Z', Math.log2(0.000472154791)], ['2026-10-09T12:32Z', Math.log2(0.000661885549259598)],
    ['2026-10-10T14:08Z', Math.log2(0.000723571590007464)], ['2026-10-12T01:55Z', Math.log2(0.001517760977820331)], ['2026-10-12T13:10Z', Math.log2(0.001584931111785787)],
    ['2026-10-12T14:41Z', Math.log2(0.001602278921983212)], ['2026-10-12T16:59Z', Math.log2(0.0016127213726553)], ['2026-10-12T21:01Z', Math.log2(0.001635183729255778)],
    ['2026-10-12T22:36Z', Math.log2(0.001635527380375392)], ['2026-10-13T05:57Z', Math.log2(0.001661202643272239)], ['2026-10-13T06:44Z', Math.log2(0.001661634653669567)],
    ['2026-10-13T13:30Z', Math.log2(0.001661957774647029)], ['2026-10-13T15:06Z', Math.log2(0.001661960547713947)], ['2026-10-13T18:05Z', Math.log2(0.001672188119205421)],
    ['2026-10-13T18:45Z', Math.log2(0.001672660197076918)]].map(function (d) { return [Date.parse(d[0]), d[1]]; });
  /* the six refinements on the After-the-722 page: log10 of "times better" (before -> after, both from that page's sources) */
  var SLACK = [['C', 'matroid', 78.909], ['κ', 'integer mult.', 52.011], ['δ', 'Fourier', 10.091], ['c', 'van der Waerden', 4.046], ['R', 'Sidorenko', 0.939], ['N', 'unit distances', 0.495]];
  var GATES = { rec: [6, 117], pareto: [[6, 112], [7, 110], [12, 108], [13, 107]] };

  /* ---------- glyphs: small canvases drawn from exact formulas or data ---------- */
  function ring(x, cx, cy, r, fill, bg) { x.fillStyle = bg; x.beginPath(); x.arc(cx, cy, r + 2, 0, Math.PI * 2); x.fill(); x.fillStyle = fill; x.beginPath(); x.arc(cx, cy, r, 0, Math.PI * 2); x.fill(); }
  function gauss(i) { var a = Math.sin(i * 12.9898 + 78.233) * 43758.5453, b = Math.sin(i * 39.3468 + 11.135) * 24634.6345; var u = Math.max(1e-6, a - Math.floor(a)), v = b - Math.floor(b); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
    function top(w) { return w < 400 ? 44 : 28; } // narrow cards: the readout moves under the key, so the drawing starts lower
var G = {
    doodle: { still: null, period: 3600, once: true, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-incentre'), line = tk('--line-ui'), T = top(w), B = h - 8, s = Math.min(46, (B - T) / 2), rows = Math.max(1, Math.floor((B - T) / s)), cols = Math.max(1, Math.floor((w - 20) / s));
      var ox = (w - cols * s) / 2, oy = T + (B - T - rows * s) / 2, r = (Math.SQRT2 - 1) / 2, n = rows * cols, shown = ph == null ? n : Math.max(1, Math.ceil(Math.min(1, ph) * n));
      var cells = [];
      for (var i = 0; i < rows; i++) for (var j = 0; j < cols; j++) cells.push([i, j, Math.abs(j - (cols - 1) / 2) + Math.abs(i - (rows - 1) / 2) * 0.6]);
      cells.sort(function (a, b) { return a[2] - b[2]; });
      x.lineWidth = 1;
      cells.slice(0, shown).forEach(function (c, k) {
        var x0 = ox + c[1] * s, y0 = oy + c[0] * s;
        x.strokeStyle = line; x.globalAlpha = 0.9;
        x.strokeRect(x0 + 0.5, y0 + 0.5, s - 1, s - 1);
        x.globalAlpha = 0.45; x.beginPath(); x.moveTo(x0, y0); x.lineTo(x0 + s, y0 + s); x.moveTo(x0 + s, y0); x.lineTo(x0, y0 + s); x.stroke();
        x.globalAlpha = 1; x.fillStyle = acc;
        [[0.5, r], [1 - r, 0.5], [0.5, 1 - r], [r, 0.5]].forEach(function (p) { x.beginPath(); x.arc(x0 + p[0] * s, y0 + p[1] * s, Math.max(1.8, s * 0.055), 0, Math.PI * 2); x.fill(); });
        if (k === 0) { x.strokeStyle = acc; x.lineWidth = 1.2; x.beginPath(); x.arc(x0 + 0.5 * s, y0 + r * s, r * s, 0, Math.PI * 2); x.stroke(); x.lineWidth = 1; }
      });
      out('r = (√2−1)/2 ≈ 0.2071');
    } },
    stack: { still: null, period: 4200, once: true, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-exoplanets'), L0 = 12, R0 = w - 12, T = top(w), B = h - 10, mid = (T + B) / 2 - 6, sc = (B - T) / 2600; // ppm to px
      var N = ph == null ? 64 : Math.max(1, Math.round(1 + 63 * Math.min(1, ph) * Math.min(1, ph))), sig = 1300 / Math.sqrt(N), bins = Math.max(24, Math.min(64, Math.floor((R0 - L0) / 6)));
      function model(t) { var a = Math.abs(t), half = 0.85, ing = 0.15; if (a >= half) return 0; if (a <= half - ing) return 398; return 398 * (half - a) / ing; } // hours from mid-transit
      x.strokeStyle = tk('--grid'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, mid); x.lineTo(R0, mid); x.stroke();
      x.strokeStyle = tk('--ink-3'); x.lineWidth = 1.5; x.beginPath();
      for (var i = 0; i <= 120; i++) { var t = -6 + 12 * i / 120, xx = L0 + (R0 - L0) * i / 120, yy = mid + model(t) * sc; i ? x.lineTo(xx, yy) : x.moveTo(xx, yy); }
      x.stroke();
      x.fillStyle = acc;
      for (var b = 0; b < bins; b++) { var tb = -6 + 12 * (b + 0.5) / bins, v = model(tb) + gauss(b + 1) * sig, yb = Math.max(T, Math.min(B, mid + v * sc)); x.beginPath(); x.arc(L0 + (R0 - L0) * (b + 0.5) / bins, yb, 2.1, 0, Math.PI * 2); x.fill(); }
      out(N + ' pass' + (N > 1 ? 'es' : '') + ' stacked');
    } },
    kappa: { period: 2400, once: true, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-intmult'), L0 = 12, R0 = w - 14, T = top(w) + 2, B = h - 14;
      var t0 = KAPPA[0][0], t1 = KAPPA[KAPPA.length - 1][0] + 6 * 3600e3, X = function (t) { return L0 + (R0 - L0) * (t - t0) / (t1 - t0); }, Y = function (v) { return B - (B - T) * (v + 190) / 190; };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B); x.lineTo(R0, B); x.stroke();
      var prog = ph == null ? 1 : Math.min(1, ph), upto = t0 + (t1 - t0) * prog;
      x.strokeStyle = acc; x.lineWidth = 2; x.beginPath();
      var last = KAPPA[0];
      KAPPA.forEach(function (k, i) { if (k[0] > upto) return; if (!i) x.moveTo(X(k[0]), Y(k[1])); else { x.lineTo(X(k[0]), Y(last[1])); x.lineTo(X(k[0]), Y(k[1])); } last = k; });
      x.lineTo(X(Math.min(upto, t1 - 6 * 3600e3)), Y(last[1])); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'left'; x.fillText('−182 · machine-written paper', L0 + 2, Y(-182) - 7);
      ring(x, X(Math.min(upto, t1 - 6 * 3600e3)), Y(last[1]), 3.5, acc, tk('--bg-1'));
      out('log₂κ ' + last[1].toFixed(2).replace('-', '−'));
    } },
    slack: { period: 2000, once: true, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-mm'), L0 = 30, R0 = w - 46, T = top(w), B = h - 8, rowH = (B - T) / SLACK.length, prog = ph == null ? 1 : Math.min(1, ph);
      var X = function (d) { return L0 + (R0 - L0) * d / 80; };
      x.strokeStyle = tk('--grid'); x.lineWidth = 1;
      [0, 20, 40, 60, 80].forEach(function (d) { x.beginPath(); x.moveTo(X(d) + 0.5, T - 2); x.lineTo(X(d) + 0.5, B); x.stroke(); });
      x.font = mono(11); x.textBaseline = 'middle';
      SLACK.forEach(function (r, i) {
        var cy = T + rowH * (i + 0.5), bw = Math.max(2, (X(r[2]) - L0) * prog), th = Math.min(6, rowH * 0.5);
        x.fillStyle = tk('--ink-2'); x.textAlign = 'right'; x.fillText(r[0], L0 - 8, cy);
        x.fillStyle = acc; x.beginPath(); x.moveTo(L0, cy - th / 2); x.lineTo(L0 + bw - th / 2, cy - th / 2); x.arc(L0 + bw - th / 2, cy, th / 2, -Math.PI / 2, Math.PI / 2); x.lineTo(L0, cy + th / 2); x.closePath(); x.fill();
        if (prog >= 1) { x.fillStyle = tk('--ink-3'); x.textAlign = 'left'; if (r[2] >= 3) fillSup(x, '×10', String(Math.round(r[2])), L0 + bw + 6, cy, 11); else x.fillText('×' + Math.pow(10, r[2]).toFixed(1), L0 + bw + 6, cy); }
      });
      x.textBaseline = 'alphabetic';
      out(prog >= 1 ? '6 results' : '');
    } },
    pascal: { still: 31 / 32, period: 6400, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-mobius'), N = 32, size = Math.min(h - top(w) - 4, w - 24), cell = size / N, ox = (w - size) / 2, oy = h - size - 8;
      var row = ph == null ? 31 : Math.floor(ph * N) % N;
      for (var i = 0; i < N; i++) for (var j = 0; j <= i; j++) {
        if ((j & i) !== j) continue;
        x.fillStyle = i === row ? acc : tk('--ink-3'); x.globalAlpha = i === row ? 1 : 0.5;
        x.fillRect(ox + j * cell, oy + i * cell, Math.max(1, cell - 0.6), Math.max(1, cell - 0.6));
      }
      x.globalAlpha = 1;
      var ones = 0; for (var jj = 0; jj <= row; jj++) if ((jj & row) === jj) ones++;
      out('row ' + row + ' · ' + ones + ' odd');
    } },
    gates: { period: 1800, once: true, draw: function (x, w, h, ph, out) {
      var acc = tk('--acc-gf2m'), L0 = 34, R0 = w - 14, T = top(w) + 2, B = h - 22;
      var X = function (d) { return L0 + (R0 - L0) * (d - 5) / 9; }, Y = function (g) { return B - (B - T) * (g - 105) / 14; };
      x.strokeStyle = tk('--line-ui'); x.lineWidth = 1; x.beginPath(); x.moveTo(L0, B); x.lineTo(R0, B); x.stroke();
      x.fillStyle = tk('--ink-3'); x.font = mono(11); x.textAlign = 'center';
      [6, 9, 12].forEach(function (d) { x.fillText(d, X(d), B + 14); });
      x.textAlign = 'right'; x.fillText('DEPTH', R0, B + 14);
      [107, 112, 117].forEach(function (g) { x.fillText(g, L0 - 6, Y(g) + 4); });
      var prog = ph == null ? 1 : Math.min(1, ph);
      x.strokeStyle = tk('--ink-2'); x.lineWidth = 1.5; x.beginPath(); x.arc(X(6), Y(117), 4, 0, Math.PI * 2); x.stroke();
      x.fillStyle = tk('--ink-3'); x.textAlign = 'left'; x.fillText('2010', X(6) + 9, Y(117) + 4);
      var pts = GATES.pareto, n = Math.max(1, Math.round(prog * pts.length));
      x.strokeStyle = acc; x.lineWidth = 2; x.beginPath();
      for (var i = 0; i < n; i++) { var p = pts[i]; if (!i) x.moveTo(X(p[0]), Y(p[1])); else { x.lineTo(X(p[0]), Y(pts[i - 1][1])); x.lineTo(X(p[0]), Y(p[1])); } }
      if (n === pts.length) x.lineTo(X(14), Y(pts[n - 1][1]));
      x.stroke();
      for (var k = 0; k < n; k++) ring(x, X(pts[k][0]), Y(pts[k][1]), 4, acc, tk('--bg-1'));
      out('−5 gates at depth 6');
    } }
  };
  var GL = {};
  function glyphs(root) {
    $$('canvas[data-glyph]', root).forEach(function (cv) {
      if (cv._f0) return; cv._f0 = true;
      var key = cv.getAttribute('data-glyph'), spec = G[key]; if (!spec) return;
      var c = F0.canvas(cv), box = cv.parentNode, card = cv.closest('.card') || box, ro = box.querySelector('[data-readout]');
      var out = function (s) { if (ro && ro.textContent !== s) ro.textContent = s; };
      var t0 = 0, want = false, visible = false;
      function paint(ph) { var x = c.ctx; x.setTransform(c.dpr, 0, 0, c.dpr, 0, 0); x.clearRect(0, 0, c.w, c.h); spec.draw(x, c.w, c.h, ph, out); }
      function still() { paint(spec.once ? null : spec.still); }
      var loop = F0.loop(function (now) {
        if (!t0) t0 = now;
        var ph = (now - t0) / spec.period;
        if (spec.once) { if (ph >= 1) { paint(null); loop.stop(); return; } paint(ph); }
        else paint(ph % 1);
      });
      function sync() { if (want && visible && F0.motion()) { if (!loop.running) { t0 = 0; loop.start(); } } else { loop.stop(); still(); } }
      card.addEventListener('pointerenter', function () { if (!want) { want = true; sync(); } });
      card.addEventListener('pointerleave', function () { want = false; sync(); });
      card.addEventListener('focusin', function () { if (!want) { want = true; sync(); } });
      card.addEventListener('focusout', function (e) { if (card.contains(e.relatedTarget)) return; want = false; sync(); });
      still();
      GL[key] = function () { if (!loop.running) still(); };
      c.resize(function () { if (!loop.running) still(); });
      F0.onTheme(function () { if (!loop.running) still(); });
      F0.whenVisible(box, function () { visible = true; sync(); }, function () { visible = false; sync(); });
      F0.onMotion(sync);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (!loop.running) still(); });
    });
  }

  /* ---------- the hero figure: propose, check, decide ---------- */
  function loopFig(PJ) {
    var stage = $('#loop-stage'), pick = $('#loop-pick'), play = $('#loop-play'), table = $('#loop-table'), say = $('#loop-say');
    if (!stage || !pick) return;
    stage.removeAttribute('aria-live');
    var by = {}; (PJ.projects || []).forEach(function (p) { by[p.slug] = p; });
    var list = LOOP_ORDER.filter(function (s) { return by[s] && P[s]; }), cur = 0;
    var SHORT = { 'integer-multiplication': 'Integer multiplication' };
    pick.innerHTML = list.map(function (s, i) { return '<button type="button" data-i="' + i + '" aria-pressed="' + (i === cur ? 'true' : 'false') + '" style="--acc:var(' + P[s].acc + ')"><i aria-hidden="true"></i>' + esc(SHORT[s] || by[s].title) + '</button>'; }).join('');
    stage.innerHTML = '<ol class="ri-st-list">' + STATIONS.map(function (st, i) {
      return '<li class="ri-st st-' + st[1] + '"><p class="k"><span class="mk" aria-hidden="true"></span>' + esc(st[0]) + '</p><p class="v" data-v="' + i + '"></p><p class="d" data-d="' + i + '"></p><p class="s" data-s="' + i + '"></p></li>';
    }).join('') + '</ol><p class="ri-loop-who"><span data-who></span><span class="badges" data-st></span><a data-go>Open the project</a></p>';
    function show(i, fromPlay) {
      cur = (i + list.length) % list.length;
      var s = list[cur], p = by[s], c = P[s];
      $$('button', pick).forEach(function (b, k) { b.setAttribute('aria-pressed', k === cur ? 'true' : 'false'); });
      stage.style.setProperty('--acc', 'var(' + c.acc + ')');
      stage.classList.remove('swap'); void stage.offsetWidth; if (F0.motion()) stage.classList.add('swap');
      c.loop.forEach(function (row, k) {
        $('[data-v="' + k + '"]', stage).textContent = row[0];
        $('[data-d="' + k + '"]', stage).textContent = row[1];
        $('[data-s="' + k + '"]', stage).textContent = 'src: ' + row[2];
      });
      $('[data-who]', stage).textContent = p.title + ' · ' + c.who;
      $('[data-st]', stage).innerHTML = F0.statusBadges(p.status, { ladder: 1 });
      var go = $('[data-go]', stage); go.href = rel(p.page); go.textContent = 'Open ' + p.title;
      if (!fromPlay) { stopPlay(); announce(); }
    }
    function announce(pre) {
      if (!say) return;
      var c = P[list[cur]];
      say.textContent = (pre || '') + by[list[cur]].title + ': ' + c.loop.map(function (r, k) { return STATIONS[k][0].toLowerCase() + ', ' + r[0] + ' ' + r[1]; }).join('; ') + '.';
    }
    pick.addEventListener('click', function (e) { var b = e.target.closest('button[data-i]'); if (b) show(+b.getAttribute('data-i')); });
    pick.addEventListener('keydown', function (e) {
      var b = e.target.closest('button[data-i]'); if (!b) return;
      var k = +b.getAttribute('data-i'), n = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (k + 1) % list.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (k - 1 + list.length) % list.length;
      if (n == null) return;
      e.preventDefault(); show(n); $$('button', pick)[n].focus();
    });
    var t0 = 0, steps = 0, loop = F0.loop(function (now) {
      if (!t0) t0 = now;
      if (now - t0 > 4200) { t0 = now; steps++; if (steps >= list.length) { stopPlay(); announce('Stopped on '); return; } show(cur + 1, true); }
    });
    function stopPlay() { loop.stop(); play.setAttribute('aria-pressed', 'false'); play.setAttribute('aria-label', 'Play through the six projects'); }
    play.addEventListener('click', function () {
      if (loop.running) { stopPlay(); announce('Paused on '); return; }
      if (!F0.motion()) { show(cur + 1); return; } // motion off: one step per press
      steps = 0; t0 = 0; show(cur + 1, true); loop.start();
      play.setAttribute('aria-pressed', 'true'); play.setAttribute('aria-label', 'Pause');
    });
    F0.onMotion(function (on) { if (!on && loop.running) { stopPlay(); announce('Paused on '); } });
    F0.onIdle(function (idle) { if (idle && loop.running) { stopPlay(); announce('Paused on '); } });
    show(0, true);
    if (table) {
      table.innerHTML = '<table class="tbl"><caption>Each project at the three steps</caption><thead><tr><th scope="col">Project</th>' + STATIONS.map(function (s) { return '<th scope="col">' + esc(s[0]) + '</th>'; }).join('') + '</tr></thead><tbody>' +
        list.map(function (s) { return '<tr><th scope="row">' + esc(by[s].title) + '</th>' + P[s].loop.map(function (r) { return '<td><b>' + esc(r[0]) + '</b> ' + esc(r[1]) + ' <span class="ri-src">(' + esc(r[2]) + ')</span></td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>';
    }
  }

  /* ---------- evidence ladder: each project on the rung its status gives it ---------- */
  /* a project sits on the rung of its headline claim: the weakest rung any part of its status line names
     (a Lean check of one part never lifts the whole), or the rung set above where the status line alone would overstate it */
  function rungOf(p) {
    if (P[p.slug] && P[p.slug].rung) return P[p.slug].rung;
    var r = 0;
    String(p.status || '').split(/\s+·\s+/).forEach(function (seg) { var c = F0.classifyStatus(seg); if (c.rung && (!r || c.rung < r)) r = c.rung; });
    return r || 1;
  }
  function ladder(PJ) {
    $$('.ri-rung').forEach(function (h) { h.innerHTML = ''; });
    var list = (PJ.projects || []).filter(function (p) { return p.kind === 'research' || p.kind === 'contribution'; });
    list.forEach(function (p) {
      var host = $('.ri-rung[data-rung="' + rungOf(p) + '"]'); if (!host) return;
      var note = P[p.slug] && P[p.slug].rungNote;
      var a = document.createElement('a');
      a.className = 'ri-chip'; a.href = '#card-' + p.slug; a.style.setProperty('--acc', 'var(' + ((P[p.slug] && P[p.slug].acc) || '--ink-3') + ')');
      a.textContent = p.title;
      a.setAttribute('aria-label', p.title + ': ' + p.status + (note ? '. ' + note : ''));
      var tip = '<div class="tip-k">' + esc(p.kind === 'contribution' ? 'Aska contributed' : 'Founding member’s research') + '</div><div class="tip-t">' + esc(p.title) + '</div><div class="tip-rows"><div class="tip-row">' + F0.statusBadges(p.status, { ladder: 1 }) + '</div></div>' + (note ? '<div class="tip-note">' + esc(note) + '</div>' : '');
      a.addEventListener('pointerenter', function (e) { F0.tip.show(tip, e.clientX, e.clientY); });
      a.addEventListener('pointermove', function (e) { F0.tip.show(tip, e.clientX, e.clientY); });
      a.addEventListener('pointerleave', function () { F0.tip.hide(); });
      a.addEventListener('focus', function () { var b = a.getBoundingClientRect(); F0.tip.show(tip, b.left + b.width / 2, b.bottom); });
      a.addEventListener('blur', function () { F0.tip.hide(); });
      host.appendChild(a);
    });
    $$('.ri-rung').forEach(function (h) { if (!h.children.length) { h.innerHTML = '<span class="ri-none">none of our projects yet</span>'; } });
  }

  /* ---------- project cards ---------- */
  function mmStats(FD) {
    var s = (FD && FD.summary) || {};
    return [
      { value: (s.manuscripts_day1 || 722) + ' → ' + (s.manuscripts_oct7 || 719), label: 'machine-written manuscripts on 6 Oct, then 7 Oct after three were withdrawn', source: 'openai/math README @ adc7f12 and fd4aeeb', href: R + 'data/openai-math-families.json' },
      { value: String(s.families || 372), label: 'families of results; ' + (s.families_with_lean_doc_oct7 || 242) + ' link a Lean scope document (a plan for checking, not a finished check)', source: 'data/openai-math-families.json', href: R + 'data/openai-math-families.json' },
      { value: '7', label: 'families founding members built on within a week', source: 'data/members.json builds_on', href: R + 'data/members.json' },
      { value: '52', label: 'public steps that tightened six results, 7 to 13 Oct', source: 'After the 722, section 03', href: 'machine-mathematics/#slack' }
    ];
  }
  function cardHTML(p, M, FD) {
    var c = P[p.slug]; if (!c) return '';
    var stats = p.slug === 'machine-mathematics' ? mmStats(FD) : (c.stats || p.stats || []);
    var links = '<a href="' + esc(rel(p.page)) + '">On Foundation0</a>' + (p.links || []).map(function (l) { return '<a href="' + esc(rel(l.url)) + '">' + esc(l.label) + '</a>'; }).join('');
    var st = stats.slice(0, 4).map(function (s, i) {
      var live = s.live || (!c.stats && p.slug === 'integer-multiplication' && i === 0);
      return '<li' + (live ? ' data-kappa' : '') + '><span class="v"' + (live ? ' data-k-v' : '') + '>' + supHTML(s.value) + '</span><span class="k"' + (live ? ' data-k-k' : '') + '>' + supHTML(s.label) + '</span>' +
        '<span class="s">' + (live ? '<a data-k-src href="https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json"><span class="dot stale" aria-hidden="true"></span><span data-k-when>snapshot · selected-result.json @ 0a31ad884</span></a>' : s.href ? '<a href="' + esc(s.href) + '">' + esc(s.source) + '</a>' : 'src: ' + esc(s.source)) + '</span></li>';
    }).join('');
    return '<article class="card ri-card" id="card-' + esc(p.slug) + '" data-slug="' + esc(p.slug) + '" style="--acc:var(' + c.acc + ')">' +
      '<p class="kick"><span>' + esc(c.field) + '</span><span>' + esc(c.who) + '</span></p>' +
      '<h3><a href="' + esc(rel(p.page)) + '">' + esc(p.title) + '</a></h3><p class="dek">' + esc(p.dek || '') + '</p>' +
      '<div class="badges">' + F0.statusBadges(p.status, { ladder: 1 }) + '</div>' +
      '<p class="credit">' + c.credit + '</p>' +
      '<div class="glyph"><canvas data-glyph="' + c.glyph + '" role="img" aria-label="' + esc(c.aria) + '"></canvas><span class="gk">' + esc(c.gk) + '</span><span class="gr" data-readout>' + esc(c.gr) + '</span></div>' +
      '<p class="gcap">' + supHTML(c.cap) + '</p>' +
      '<ul class="ri-stats" aria-label="' + esc(p.title) + ' in numbers">' + st + '</ul>' +
      '<p class="links">' + links + '</p></article>';
  }
  function cards(PJ, MB, FD) {
    var by = {}; (PJ.projects || []).forEach(function (p) { by[p.slug] = p; });
    var M = {}; ((MB && MB.members) || []).forEach(function (m) { M[m.login] = m; });
    var a = $('#cards-research'), b = $('#cards-contrib');
    if (a) a.innerHTML = ORDER_RESEARCH.filter(function (s) { return by[s]; }).map(function (s) { return cardHTML(by[s], M, FD); }).join('');
    if (b) b.innerHTML = ORDER_CONTRIB.filter(function (s) { return by[s]; }).map(function (s) { return cardHTML(by[s], M, FD); }).join('');
    glyphs(document);
    // live reviewed κ on the integer-multiplication card
    var box = $('[data-kappa]');
    var SNAP = { decimal: '0.001672660197076918', pr: 1094, at: '2026-10-13T18:45:23Z', source: 'snapshot' }; // projects.json stats[0]: selected-result.json @ 0a31ad884
    if (box && F0.kappa) F0.kappa().then(function (k) {
      if (!k || !/^0\.\d+$/.test(String(k.decimal))) return;
      if (k.source !== 'live' && !(Date.parse(k.at) > Date.parse(SNAP.at))) k = SNAP; // the local feed is older than our snapshot
      var live = k.source === 'live';
      $('[data-k-v]', box).textContent = k.decimal;
      $('[data-k-k]', box).textContent = 'reviewed κ, conditional' + (k.pr ? ', PR #' + k.pr + (k.pr === 1094 ? ' by founding member rohanarun' : '') : '') + (live ? ', fetched just now' : '');
      $('[data-k-when]', box).textContent = live ? 'live · ' + utc(k.at) : k.source === 'snapshot' ? 'snapshot · ' + utc(k.at) + ' (live file unreachable)' : 'feed.json · ' + (k.at ? utc(k.at) : '');
      $('.dot', box).className = 'dot ' + (live ? 'live' : 'stale');
      if (k.source === 'feed') $('[data-k-src]', box).href = R + 'feed.json';
      var lg = Math.log2(parseFloat(k.decimal)), last = KAPPA[KAPPA.length - 1];
      if (lg > last[1] + 1e-9) { KAPPA.push([Math.max(Date.parse(k.at) || Date.now(), last[0] + 3600e3), lg]); if (GL.kappa) GL.kappa(); }
    }).catch(function () {});
  }

  /* ---------- every repository, by member ---------- */
  function members(MB, FD) {
    var host = $('#member-cards'), count = $('#repo-count');
    if (!host || !MB) return;
    var fam = {}; ((FD && FD.families) || []).forEach(function (f) { fam[f.id] = f; });
    function famTitle(id) { var f = fam[id]; return f ? String(f.title).replace(/\\log\s*/g, ' log ').replace(/<[^>]+>/g, '').replace(/\s{2,}/g, ' ') : ''; }
    var list = MB.members || [];
    var PAGE_LBL = { 'research/incentre-lattice/': 'Incentre lattice', 'research/exoplanets/': 'Exoplanets', 'research/integer-multiplication/': 'Integer multiplication', 'research/mobius-x1/': 'mobius-x1', 'research/gf2m-circuits/': 'gf2m-circuits', 'instruments/#auto-research': 'Instruments: Auto-research-agent', 'instruments/#autofoundry': 'Instruments: autofoundry' };
    host.innerHTML = list.map(function (m, i) {
      var work = (m.work || []).map(function (w) {
        var bo = /#(\d+)/.exec(w.builds_on || ''), id = bo ? ('00' + bo[1]).slice(-3) : null;
        return '<li data-722="' + (id ? '1' : '0') + '"><a href="' + esc(w.url) + '">' + esc(w.name) + '</a>' +
          '<div class="badges">' + F0.statusBadges(w.status, { ladder: 1 }) + '</div>' +
          '<p>' + supHTML(w.note || '') + '</p>' +
          (w.page ? '<p class="ri-bo"><span>On Foundation0</span><a href="' + esc(rel(w.page)) + '">' + esc(PAGE_LBL[w.page] || w.name) + '</a></p>' : '') +
          (id ? '<p class="ri-bo"><span>Builds on</span><a href="machine-mathematics/#f-' + id + '">OpenAI family ' + id + (famTitle(id) ? ': ' + esc(famTitle(id)) : '') + '</a></p>' : '') + '</li>';
      }).join('');
      var mp = m.main_project || {};
      return '<article class="mcard" id="m-' + esc(m.login) + '"><p class="idx">M·' + ('0' + (i + 1)).slice(-2) + '</p><h3>' + esc(m.name) + '</h3><a class="gh" href="' + esc(m.github) + '">@' + esc(m.login) + '</a>' +
        '<p class="sum">' + supHTML(m.summary || '') + '</p>' +
        '<p class="ri-mp"><span>Main project</span><a href="' + esc(mp.page ? rel(mp.page) : mp.url) + '">' + esc(mp.name || '') + '</a></p>' +
        '<ul class="worklist" id="wl-' + esc(m.login) + '">' + work + '</ul>' +
        '<button type="button" class="ri-more" aria-expanded="false" aria-controls="wl-' + esc(m.login) + '" hidden></button></article>';
    }).join('');
    var CAP = 4;
    /* each card shows its first CAP entries in the current view; a button reveals the rest */
    function clip(card) {
      var vis = $$('.worklist li', card).filter(function (li) { return !li.hidden; }), b = $('.ri-more', card), open = b && b.getAttribute('aria-expanded') === 'true';
      vis.forEach(function (li, k) { li.classList.toggle('ri-clip', !open && k >= CAP); });
      $$('.worklist li[hidden]', card).forEach(function (li) { li.classList.remove('ri-clip'); });
      if (!b) return;
      var extra = vis.length - CAP;
      b.hidden = extra <= 0;
      if (extra <= 0) { b.textContent = ''; b.removeAttribute('aria-label'); return; }
      b.textContent = open ? 'Show fewer' : '+' + extra + ' more';
      b.setAttribute('aria-label', open ? 'Show fewer of ' + $('h3', card).textContent + '’s entries' : 'Show ' + extra + ' more of ' + $('h3', card).textContent + '’s entries');
    }
    function filt(mode) {
      var n = 0, all = 0;
      $$('.worklist li', host).forEach(function (li) { var on = mode === 'all' || (mode === '722') === (li.getAttribute('data-722') === '1'); li.hidden = !on; all++; if (on) n++; });
      $$('.mcard', host).forEach(function (c) { var any = $$('.worklist li', c).some(function (li) { return !li.hidden; }); c.classList.toggle('ri-empty', !any); clip(c); });
      if (count) count.textContent = n + ' of ' + all + ' entries';
    }
    host.addEventListener('click', function (e) {
      var b = e.target.closest('.ri-more'); if (!b) return;
      var card = b.closest('.mcard'), opening = b.getAttribute('aria-expanded') !== 'true';
      var first = $$('.worklist li.ri-clip', card)[0];
      b.setAttribute('aria-expanded', opening ? 'true' : 'false');
      clip(card);
      if (opening && first) { var a = $('a', first); if (a) a.focus(); }
    });
    $$('[data-rf]').forEach(function (b) {
      b.addEventListener('click', function () { $$('[data-rf]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }); filt(b.getAttribute('data-rf')); });
    });
    filt('all');
    $$('[data-count-mem]').forEach(function (e) { e.textContent = list.length; });
  }

  /* ---------- wire up ---------- */
  function boot() {
    Promise.all([
      F0.json(R + 'data/projects.json'),
      F0.json(R + 'data/members.json').catch(function () { return null; }),
      F0.json(R + 'data/openai-math-families.json').catch(function () { return null; })
    ]).then(function (d) {
      var PJ = d[0], MB = d[1], FD = d[2];
      var n = (PJ.projects || []).filter(function (p) { return p.kind === 'research' || p.kind === 'contribution'; }).length;
      $$('[data-count-proj]').forEach(function (e) { e.textContent = n; });
      if (PJ.updated) $$('[data-updated]').forEach(function (e) { e.textContent = F0.fmtDate(PJ.updated); });
      loopFig(PJ);
      ladder(PJ);
      cards(PJ, MB, FD);
      members(MB, FD);
    }).catch(function (e) { console.warn('research data:', e); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
