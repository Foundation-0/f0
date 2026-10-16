/* The Radiant: a radial projection of the Foundation0 ledger (Canvas 2D, no dependencies).
   angle    = field (domain), one sector each, in a fixed order
   distance = date: the rim is the ledger's update date; each ring inward reaches
              1 + sqrt(2) (the silver ratio) times further back in time
   size     = significance (area proportional to 1..5, an editorial judgement)
   dial     = AI role: share of the disc filled cyan (digital) vs gold (human): 1/4, 1/2, 3/4
   ring     = evidence: the thin outer ring closes as evidence firms up (claimed 1/5 ... formally verified 5/5)
   hairline = founding members' work, or work Aska contributed to (Asimov's red hairlines: contributions added later)
   Motion, two modes:
   - opts.time = {range, play, output}: the figure starts paused on the full record ("now"); the range scrubs
     through time (marks newer than the chosen date fade) and the play button runs the record from the centre
     to the rim once (stepped ring by ring when motion is off). Used on the home page.
   - no opts.time (legacy): a slow ambient sweep from the centre to the rim, paused off-screen, in a hidden tab,
     after 60 s idle, with the motion toggle off, and under prefers-reduced-motion (a still frame).
   Two more kinds of motion, both only while F0.motion() is on (README §5):
   - entrance: when the figure first comes into view, the marks rise from the centre to their rings, oldest first,
     in 1.2 s (F0.enter), and stop on the full record. Any pointer, key or control use finishes it at once.
   - pointer: marks within 40 px of the cursor brighten and show their year; pointing at a founding member's mark
     draws red hairlines to the other marks of the same members (ledger field foundation0_members).
   opts.members = [{name, login}] (data/members.json) names founding members in the hairline notes.
   opts.counts = false leaves the counts off the sector labels (the share image, which must not go stale).
   Credit lines for founding members' items come from the ledger's own foundation0_note field. */
(function () {
  'use strict';
  var DELTA = 1 + Math.SQRT2, TAU = 0.5, TWO_PI = Math.PI * 2;
  var ORDER = ['mathematics', 'computing', 'physics', 'astronomy-space', 'earth-climate', 'energy',
    'chemistry-materials', 'biology', 'medicine', 'engineering-robotics', 'science-of-science'];
  var LABELS = {
    'mathematics': ['MATHEMATICS', 'MATHS'], 'computing': ['COMPUTING', 'COMPUTE'], 'physics': ['PHYSICS'],
    'astronomy-space': ['ASTRONOMY · SPACE', 'ASTRONOMY', 'ASTRO'], 'earth-climate': ['EARTH · CLIMATE', 'CLIMATE'],
    'energy': ['ENERGY'], 'chemistry-materials': ['CHEMISTRY · MATERIALS', 'CHEMISTRY', 'CHEM'],
    'biology': ['BIOLOGY'], 'medicine': ['MEDICINE'], 'engineering-robotics': ['ENGINEERING · ROBOTICS', 'ROBOTICS', 'ROBOTS'],
    'science-of-science': ['SCIENCE OF SCIENCE', 'META-SCIENCE', 'META']
  };
  var PLAIN = {
    'mathematics': 'mathematics', 'computing': 'computing', 'physics': 'physics', 'astronomy-space': 'astronomy and space',
    'earth-climate': 'earth and climate', 'energy': 'energy', 'chemistry-materials': 'chemistry and materials', 'biology': 'biology',
    'medicine': 'medicine', 'engineering-robotics': 'engineering and robotics', 'science-of-science': 'science of science'
  };
  var ROLE_F = { instrument: 0.25, collaborator: 0.5, originator: 0.75 };
  var ROLE_TXT = {
    instrument: 'a tool inside a study people designed',
    collaborator: 'proposed key ideas; people selected, proved or tested them',
    originator: 'produced the result; people checked it'
  };
  var RUNG = { 'claimed': 1, 'preprint': 2, 'peer-reviewed': 3, 'deployed': 3, 'independently-replicated': 4, 'formally-verified': 5 };
  var EVID = { 'formally-verified': 'Formally verified', 'independently-replicated': 'Independently replicated', 'peer-reviewed': 'Peer reviewed', 'deployed': 'Deployed', 'preprint': 'Preprint', 'claimed': 'Claimed' };
  /* Founding members' work in the ledger: items with foundation0 true. Their credit line is the item's own
     foundation0_note (docs/data/ledger.json); memberNote() below is only a fallback for an item without one. */
  var MEMBER_NAMES = [{ name: 'Ahraz Arifuddin', login: 'ahrazzle' }, { name: 'eumemic', login: 'eumemic' }, { name: 'Doug Colkitt', login: 'Mister-Meeseeks' },
    { name: 'rohanarun', login: 'rohanarun' }, { name: 'Ryan Shea', login: 'shea256' }];
  /* a credit line for a ledger item flagged foundation0 that has no hand-written note above */
  function memberNote(m, people) {
    var orgs = (m.organizations || []).join(' | ');
    var hit = people.filter(function (p) { return orgs.indexOf(p.name) >= 0 || orgs.indexOf(p.login) >= 0; }).map(function (p) { return p.name; });
    if (hit.length === 1) return 'Founding member ' + hit[0] + '’s work.';
    if (hit.length > 1) return 'Work by founding members ' + hit.slice(0, -1).join(', ') + ' and ' + hit[hit.length - 1] + '.';
    if (/Aska/.test(orgs)) return 'Aska Digital did or contributed to this work.';
    return 'Work by Foundation0’s founding members.';
  }
  var MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

  function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 100000) / 100000; }
  function yearLabel(y, now, short) {
    var yr = Math.floor(y), m = Math.min(11, Math.floor((y - yr) * 12));
    if (short) return String(yr);
    return (now - y) < 9 ? MON[m] + ' ' + yr : String(Math.round(y));
  }

  /* inline SVG glyphs shared with the legend and the tooltip */
  function dialSVG(f, size) {
    var a = -Math.PI / 2 + f * TWO_PI, r = 7, x = (r * Math.cos(a)).toFixed(2), y = (r * Math.sin(a)).toFixed(2);
    return '<svg viewBox="-9 -9 18 18" width="' + size + '" height="' + size + '" aria-hidden="true"><circle r="7" style="fill:var(--mark-bio)"/>' +
      '<path d="M0 0L0 -7A7 7 0 ' + (f > 0.5 ? 1 : 0) + ' 1 ' + x + ' ' + y + 'Z" style="fill:var(--mark-dig)"/></svg>';
  }
  function ladderHTML(r) { return '<span class="ladder" data-r="' + r + '" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>'; }
  F0.dialSVG = dialSVG; F0.ladderHTML = ladderHTML; F0.ROLE_F = ROLE_F; F0.ROLE_TXT = ROLE_TXT; F0.RUNG = RUNG; F0.EVID = EVID; F0.PLAIN = PLAIN;

  F0.Radiant = function (stage, ledger, opts) {
    opts = opts || {};
    var canvas = stage.querySelector('canvas');
    var listEl = opts.list, readout = opts.readout;
    var C = F0.canvas(canvas), ctx = C.ctx;
    var nowY = F0.decYear(ledger.updated);
    var items = ledger.milestones.slice().sort(function (a, b) { return F0.decYear(a.date) - F0.decYear(b.date) || (a.id < b.id ? -1 : 1); });
    var counts = {}; items.forEach(function (m) { counts[m.domain] = (counts[m.domain] || 0) + 1; });
    var domains = ORDER.filter(function (d) { return counts[d]; });
    var maxK = 0;
    var nodes = items.map(function (m, i) {
      var age = Math.max(0, nowY - F0.decYear(m.date));
      var k = Math.log(1 + age / TAU) / Math.log(DELTA);
      maxK = Math.max(maxK, k);
      return { m: m, i: i, k: k, f: ROLE_F[m.ai_role] || 0.5, rung: RUNG[m.evidence] || 1, d: domains.indexOf(m.domain),
        member: m.foundation0 ? (m.foundation0_note || memberNote(m, opts.members || MEMBER_NAMES)) : '',
        logins: m.foundation0 && Array.isArray(m.foundation0_members) ? m.foundation0_members : [],
        x: 0, y: 0, r: 0, rho: 0, dx: 0, dy: 0, da: 1 };
    });
    var K = Math.max(4, Math.ceil(maxK));
    var G = {}, staticCv = document.createElement('canvas'), sctx = staticCv.getContext('2d');
    var hover = -1, kbd = false, filter = null, sweep = 0, t0 = 0, loop, lastTap = -1;
    var T = opts.time || null, tw = 1, playing = false, lastNow = 0, stepTimer = 0, DUR = 12000;
    var rise = 1, entr = null, ptr = null, ptrRaf = 0; // entrance progress (1 = settled); pointer for the ambient highlight
    var showCounts = opts.counts !== false; // sector labels carry their counts (the share image leaves them out)
    var tok = {}, sprites = {};

    function readTokens() {
      ['--bg-1', '--bg-2', '--line', '--line-ui', '--grid', '--ink', '--ink-2', '--ink-3', '--bio', '--dig', '--mark-bio', '--mark-dig', '--hair', '--focus']
        .forEach(function (n) { tok[n] = F0.css(n); });
      tok.dark = F0.theme() === 'dark';
      sprites = { bio: sprite(tok['--bio']), dig: sprite(tok['--dig']) };
    }
    function sprite(col) {
      var c = document.createElement('canvas'), s = 64; c.width = c.height = s;
      var x = c.getContext('2d'), g = x.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
      g.addColorStop(0, col); g.addColorStop(0.35, col); g.addColorStop(1, 'rgba(0,0,0,0)');
      x.globalAlpha = 0.55; x.fillStyle = g; x.fillRect(0, 0, s, s);
      return c;
    }

    /* ---- geometry ---- */
    function layout() {
      var S = Math.min(C.w, C.h), small = S < 560;
      G.ok = C.ready !== false && S >= 160; // not laid out yet (or far too small): draw nothing until resize() fires
      if (!G.ok) return;
      G.S = S; G.cx = C.w / 2; G.cy = C.h / 2; G.small = small;
      G.band = small ? 20 : 28; G.ext = small ? 9 : 14;
      G.R = Math.max(40, S / 2 - G.band - G.ext - (small ? 4 : 8));
      G.r0 = G.R * 0.12;
      G.gap = small ? 0.42 : 0.27;
      G.w = (TWO_PI - G.gap) / domains.length;
      G.s0 = G.R * (small ? 0.0175 : 0.0124);
      G.font = 11; // never below the 11px label floor
      var groups = domains.map(function () { return []; });
      nodes.forEach(function (n) {
        n.rho = 1 - n.k / K;
        n.rt = G.r0 + (G.R - G.r0) * n.rho;
        n.r = Math.max(small ? 1.9 : 2.4, G.s0 * Math.sqrt(n.m.significance));
        groups[n.d].push(n);
      });
      groups.forEach(function (g, d) {
        var a0 = G.gap / 2 + d * G.w, a1 = a0 + G.w;
        g.forEach(function (n, j) {
          var pad = (n.r + 2.5) / Math.max(n.rt, 1);
          n.lo = a0 + pad; n.hi = a1 - pad;
          if (n.lo > n.hi) n.lo = n.hi = (a0 + a1) / 2;
          var u = (0.5 + j * 0.381966 + hash(n.m.id) * 0.15) % 1;
          n.th = n.lo + (n.hi - n.lo) * u;
          place(n, n.rt);
        });
        for (var it = 0; it < 260; it++) { // push overlapping marks apart (squared distances first: this runs ~10^6 times)
          var moved = false, hit = [];
          for (var a = 0; a < g.length; a++) {
            var p = g[a];
            for (var b = a + 1; b < g.length; b++) {
              var q = g[b], dx = q.x - p.x, dy = q.y - p.y, min = p.r + q.r + 3.2, d2 = dx * dx + dy * dy;
              if (d2 >= min * min) continue;
              var dd = Math.sqrt(d2) || 0.01, push = (min - dd) / 2 + 0.05, ux = dx / dd, uy = dy / dd;
              p.x -= ux * push; p.y -= uy * push; q.x += ux * push; q.y += uy * push; moved = true;
              if (!p._h) { p._h = 1; hit.push(p); } if (!q._h) { q._h = 1; hit.push(q); }
            }
          }
          hit.forEach(function (n) { n._h = 0; unplace(n); });
          if (!moved) break;
        }
      });
      drawStatic();
    }
    function place(n, r) { n.cr = r; n.x = G.cx + r * Math.sin(n.th); n.y = G.cy - r * Math.cos(n.th); }
    function unplace(n) {
      var dx = n.x - G.cx, dy = G.cy - n.y, r = Math.hypot(dx, dy), th = Math.atan2(dx, dy);
      if (th < 0) th += TWO_PI;
      var dev = Math.max(-3, Math.min(3, r - n.rt));
      n.th = Math.max(n.lo, Math.min(n.hi, th));
      place(n, n.rt + dev);
    }
    function ringR(k) { return G.r0 + (G.R - G.r0) * (1 - k / K); }
    function ageAtK(k) { return TAU * (Math.pow(DELTA, k) - 1); }

    /* ---- static layer: rings, sectors, labels, the zero mark ---- */
    function drawStatic() {
      if (!G.ok) return;
      staticCv.width = canvas.width; staticCv.height = canvas.height;
      var x = sctx; x.setTransform(C.dpr, 0, 0, C.dpr, 0, 0); x.clearRect(0, 0, C.w, C.h);
      var cx = G.cx, cy = G.cy;
      if (tok.dark) { // faint pearl wash inside the rim: the Radiant's "wall"
        var bg = x.createRadialGradient(cx, cy, G.r0, cx, cy, G.R + G.ext);
        bg.addColorStop(0, 'rgba(92,207,236,0.035)'); bg.addColorStop(0.8, 'rgba(230,184,116,0.025)'); bg.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = bg; x.beginPath(); x.arc(cx, cy, G.R + G.ext, 0, TWO_PI); x.fill();
      }
      x.lineWidth = 1;
      for (var k = 1; k < K; k++) { x.strokeStyle = tok['--grid']; x.beginPath(); x.arc(cx, cy, ringR(k), 0, TWO_PI); x.stroke(); }
      x.strokeStyle = tok['--line-ui']; x.beginPath(); x.arc(cx, cy, G.R, 0, TWO_PI); x.stroke();
      x.strokeStyle = tok['--grid']; x.beginPath(); x.arc(cx, cy, G.r0, 0, TWO_PI); x.stroke();
      // sector dividers
      x.strokeStyle = tok['--grid'];
      for (var d = 0; d <= domains.length; d++) {
        var a = G.gap / 2 + d * G.w;
        x.beginPath(); x.moveTo(cx + G.r0 * Math.sin(a), cy - G.r0 * Math.cos(a)); x.lineTo(cx + (G.R + G.ext) * Math.sin(a), cy - (G.R + G.ext) * Math.cos(a)); x.stroke();
      }
      // sector labels, set along the rim
      x.font = '500 ' + G.font + 'px ' + F0.css('--f-mono');
      x.fillStyle = tok['--ink-3']; x.textAlign = 'center'; x.textBaseline = 'middle';
      var lr = G.R + G.ext + G.band / 2 + 1;
      domains.forEach(function (dm, d) {
        var mid = G.gap / 2 + (d + 0.5) * G.w, room = G.w * lr * 0.92, opts = [];
        LABELS[dm].forEach(function (l) { if (showCounts) opts.push(l + '  ' + counts[dm]); opts.push(l); });
        var pick = null;
        for (var i = 0; i < opts.length; i++) if (arcWidth(x, opts[i]) <= room) { pick = opts[i]; break; }
        if (pick) arcText(x, pick, cx, cy, lr, mid);
      });
      // ring dates in the gap at twelve o'clock
      x.font = '500 ' + G.font + 'px ' + F0.css('--f-mono');
      var labs = [{ r: G.R, t: yearLabel(nowY, nowY, G.small) }];
      for (var j = 1; j < K; j++) labs.push({ r: ringR(j), t: yearLabel(nowY - ageAtK(j), nowY, G.small) });
      var lastR = Infinity, lastT = '';
      labs.forEach(function (L, j) {
        if (lastR - L.r < G.font + 4 || L.t === lastT) return;
        lastR = L.r; lastT = L.t;
        var w = x.measureText(L.t).width + 10;
        x.fillStyle = F0.css('--bg-1'); x.fillRect(cx - w / 2, cy - L.r - G.font / 2 - 3, w, G.font + 6);
        x.fillStyle = j === 0 ? tok['--ink-2'] : tok['--ink-3']; x.fillText(L.t, cx, cy - L.r);
      });
      zeroMark(x, cx, cy, G.r0 * 0.78);
    }
    function arcWidth(x, s) { var w = 0; for (var i = 0; i < s.length; i++) w += x.measureText(s[i]).width + 1.4; return w - 1.4; }
    function arcText(x, s, cx, cy, r, mid) {
      var total = arcWidth(x, s), bottom = mid > Math.PI / 2 && mid < Math.PI * 1.5;
      var a = bottom ? mid + total / 2 / r : mid - total / 2 / r;
      for (var i = 0; i < s.length; i++) {
        var cw = x.measureText(s[i]).width, ac = bottom ? a - cw / 2 / r : a + cw / 2 / r;
        x.save(); x.translate(cx + r * Math.sin(ac), cy - r * Math.cos(ac)); x.rotate(bottom ? ac + Math.PI : ac); x.fillText(s[i], 0, 0); x.restore();
        a += (bottom ? -1 : 1) * (cw + 1.4) / r;
      }
    }
    /* the incentre mark (the logo, as #zero): the four incircles of a square's diagonal triangles, radius
       (sqrt2 - 1) x half-side, and the middle circle touching all four, each with its centre marked. Weights are
       #zero's in units of half-side / 40; rings are inked inside their circle, so gold and cyan touch edge to edge */
    function zeroMark(x, cx, cy, r) {
      var h = r * 0.72, u = h / 40, rr = (Math.SQRT2 - 1) * h, d = h - rr, m = d - rr, w = 2.2 * u, lw = 1.1 * u;
      x.save();
      x.lineWidth = w;
      [[0, -d, '--bio'], [0, d, '--bio'], [-d, 0, '--dig'], [d, 0, '--dig']].forEach(function (c) {
        x.strokeStyle = tok[c[2]]; x.beginPath(); x.arc(cx + c[0], cy + c[1], rr - w / 2, 0, TWO_PI); x.stroke();
        x.fillStyle = tok[c[2]]; x.beginPath(); x.arc(cx + c[0], cy + c[1], 1.8 * u, 0, TWO_PI); x.fill();
      });
      x.strokeStyle = x.fillStyle = tok['--ink-2']; x.lineWidth = lw;
      x.beginPath(); x.arc(cx, cy, m - lw / 2, 0, TWO_PI); x.stroke();
      x.beginPath(); x.arc(cx, cy, 1.8 * u, 0, TWO_PI); x.fill();
      x.restore();
    }

    /* ---- one frame ---- */
    function inTime(n) { return !T || n.rho <= tw + 1e-6; }
    function match(n) {
      if (!inTime(n)) return false;
      if (!filter) return true;
      if (filter === 'members') return !!n.member;
      return n.m.ai_role === filter;
    }
    /* where a mark is drawn: its place, or on its way out from the centre during the entrance (oldest first) */
    function disp(n) {
      if (rise >= 1) { n.dx = n.x; n.dy = n.y; n.da = 1; return; }
      var p = Math.max(0, Math.min(1, (rise - n.rho * 0.45) / 0.55)), e = 1 - Math.pow(1 - p, 3), r0 = G.r0 * 0.6, rr = r0 + (n.cr - r0) * e;
      n.dx = G.cx + rr * Math.sin(n.th); n.dy = G.cy - rr * Math.cos(n.th); n.da = Math.min(1, p * 2.5);
    }
    function shares(a, b) { for (var i = 0; i < a.length; i++) if (b.indexOf(a[i]) >= 0) return true; return false; }
    function draw(now) {
      var x = ctx, animating = !T && !!(loop && loop.running && !F0.idle());
      x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, canvas.width, canvas.height);
      if (!G.ok) return;
      nodes.forEach(disp);
      x.drawImage(staticCv, 0, 0);
      x.setTransform(C.dpr, 0, 0, C.dpr, 0, 0);
      var w = T && tw < 0.9995 ? tw : -1;
      if (w >= 0) {
        var rt = G.r0 + (G.R - G.r0) * w;
        x.strokeStyle = tok['--dig']; x.globalAlpha = tok.dark ? 0.5 : 0.55; x.lineWidth = 1.2;
        x.beginPath(); x.arc(G.cx, G.cy, rt, 0, TWO_PI); x.stroke(); x.globalAlpha = 1;
      }
      if (animating) {
        var P = 11000, ph = ((now - t0) % P) / P;
        sweep = ph < 0.82 ? 0.5 - 0.5 * Math.cos(Math.PI * ph / 0.82) : 1;
        w = ph < 0.82 ? sweep : -1;
        if (w >= 0) {
          var rw = G.r0 + (G.R - G.r0) * w;
          x.strokeStyle = tok['--dig']; x.globalAlpha = tok.dark ? 0.28 : 0.35; x.lineWidth = 1;
          x.beginPath(); x.arc(G.cx, G.cy, rw, 0, TWO_PI); x.stroke(); x.globalAlpha = 1;
        }
      }
      // glow belongs to data (dark theme only)
      if (tok.dark) {
        x.globalCompositeOperation = 'lighter';
        nodes.forEach(function (n) {
          var I = w >= 0 ? Math.exp(-Math.pow((n.rho - w) / 0.05, 2)) : 0, on = match(n);
          var s = n.r * (3.2 + 2.2 * I);
          x.globalAlpha = (on ? 0.22 + 0.6 * I : 0.04) * n.da;
          x.drawImage(n.f > 0.5 ? sprites.dig : sprites.bio, n.dx - s, n.dy - s, 2 * s, 2 * s);
        });
        x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1;
      }
      // red hairlines: founding members' work, run out past the rim (they appear as the entrance settles)
      var hairA = rise >= 1 ? 1 : Math.max(0, (rise - 0.7) / 0.3);
      if (hairA > 0) nodes.forEach(function (n) {
        if (!n.member) return;
        var on = match(n); x.globalAlpha = (on ? 1 : 0.25) * hairA;
        var a = n.th, r1 = n.cr + n.r + 4, r2 = G.R + G.ext;
        x.strokeStyle = tok['--hair']; x.lineWidth = 1;
        x.beginPath(); x.moveTo(G.cx + r1 * Math.sin(a), G.cy - r1 * Math.cos(a)); x.lineTo(G.cx + r2 * Math.sin(a), G.cy - r2 * Math.cos(a)); x.stroke();
        octagon(x, G.cx + (r2 + 3) * Math.sin(a), G.cy - (r2 + 3) * Math.cos(a), 3, true);
        octagon(x, n.x, n.y, n.r + 4.2, false);
        x.globalAlpha = 1;
      });
      nodes.forEach(function (n) { drawNode(x, n, match(n), w); });
      if (rise >= 1 && F0.motion()) ambient(x);
      if (hover >= 0) {
        var h = nodes[hover];
        x.strokeStyle = tok['--focus']; x.lineWidth = 2;
        x.beginPath(); x.arc(h.x, h.y, h.r + 6, 0, TWO_PI); x.stroke();
        x.lineWidth = 1; x.globalAlpha = 0.7;
        x.beginPath(); x.moveTo(G.cx + (h.cr + h.r + 7) * Math.sin(h.th), G.cy - (h.cr + h.r + 7) * Math.cos(h.th));
        x.lineTo(G.cx + G.R * Math.sin(h.th), G.cy - G.R * Math.cos(h.th)); x.stroke(); x.globalAlpha = 1;
      }
      if (readout) {
        var txt;
        if (T && w >= 0) {
          var seenT = 0; nodes.forEach(function (n) { if (n.rho <= w + 1e-6) seenT++; });
          txt = 'TO ' + timeLabel(w).toUpperCase() + ' · ' + seenT + '/' + nodes.length;
        } else if (animating && w >= 0) {
          var yr = nowY - ageAtK(K * (1 - w)), seen = 0;
          nodes.forEach(function (n) { if (n.rho <= w) seen++; });
          txt = 'SWEEP ' + Math.max(Math.floor(yr), 1928) + ' · ' + seen + ' OF ' + nodes.length;
        } else txt = nodes.length + ' MARKS · ' + items[0].date.slice(0, 4) + '–' + items[items.length - 1].date.slice(0, 4);
        if (readout.textContent !== txt) readout.textContent = txt;
      }
    }
    /* pointer layer (motion on): marks near the cursor brighten and show their year; a founding member's mark under
       the pointer is joined by red hairlines to the other marks of the same members */
    function ambient(x) {
      if (hover >= 0 && nodes[hover].logins.length) {
        var h = nodes[hover];
        x.strokeStyle = tok['--hair']; x.lineWidth = 1; x.globalAlpha = 0.85;
        nodes.forEach(function (q) {
          if (q === h || !q.logins.length || !shares(h.logins, q.logins) || !match(q)) return;
          var mx = (h.x + q.x) / 2, my = (h.y + q.y) / 2, cx = G.cx + (mx - G.cx) * 0.35, cy = G.cy + (my - G.cy) * 0.35;
          x.beginPath(); x.moveTo(h.x, h.y); x.quadraticCurveTo(cx, cy, q.x, q.y); x.stroke();
        });
        x.globalAlpha = 1;
      }
      if (!ptr) return;
      var near = [];
      nodes.forEach(function (n) { if (!match(n)) return; var d = Math.hypot(n.x - ptr.x, n.y - ptr.y); if (d < 40) near.push([d, n]); });
      near.sort(function (a, b) { return a[0] - b[0]; });
      x.font = '500 11px ' + F0.css('--f-mono'); x.textAlign = 'left'; x.textBaseline = 'middle';
      near.slice(0, 6).forEach(function (e) {
        var n = e[1], k = 1 - e[0] / 40;
        x.globalAlpha = 0.35 + 0.55 * k; x.strokeStyle = n.f > 0.5 ? tok['--dig'] : tok['--bio']; x.lineWidth = 1.4;
        x.beginPath(); x.arc(n.x, n.y, n.r + 4, 0, TWO_PI); x.stroke();
        if (n.i === hover) return;
        var t = n.m.date.slice(0, 4), tw2 = x.measureText(t).width, lx = n.x + n.r + 6, ly = n.y;
        if (lx + tw2 + 4 > C.w) lx = n.x - n.r - 6 - tw2;
        x.globalAlpha = 0.9; x.fillStyle = tok['--bg-1']; x.fillRect(lx - 2, ly - 7, tw2 + 4, 14);
        x.globalAlpha = 0.5 + 0.5 * k; x.fillStyle = tok['--ink-2']; x.fillText(t, lx, ly + 0.5);
      });
      x.globalAlpha = 1;
    }
    function octagon(x, cx, cy, r, fill) {
      x.beginPath();
      for (var i = 0; i < 8; i++) { var a = (22.5 + 45 * i) * Math.PI / 180, px = cx + r * Math.cos(a), py = cy + r * Math.sin(a); i ? x.lineTo(px, py) : x.moveTo(px, py); }
      x.closePath();
      if (fill) { x.fillStyle = tok['--hair']; x.fill(); } else { x.strokeStyle = tok['--hair']; x.lineWidth = 1.2; x.stroke(); }
    }
    function drawNode(x, n, on, w) {
      var A = n.da, px = n.dx, py = n.dy;
      x.globalAlpha = (on ? 1 : 0.16) * A;
      var I = (w >= 0) ? Math.exp(-Math.pow((n.rho - w) / 0.05, 2)) : 0, r = n.r * (1 + 0.18 * I);
      x.fillStyle = tok['--bg-1']; x.beginPath(); x.arc(px, py, r + 1.6, 0, TWO_PI); x.fill();
      x.fillStyle = tok['--mark-bio']; x.beginPath(); x.arc(px, py, r, 0, TWO_PI); x.fill();
      x.fillStyle = tok['--mark-dig']; x.beginPath(); x.moveTo(px, py); x.arc(px, py, r, -Math.PI / 2, -Math.PI / 2 + n.f * TWO_PI); x.closePath(); x.fill();
      if (r >= 2) { // evidence ring: closes as evidence firms up
        x.strokeStyle = tok['--ink-2']; x.lineWidth = G.small ? 0.9 : 1.1; x.globalAlpha = (on ? 0.9 : 0.15) * A;
        x.beginPath(); x.arc(px, py, r + 2.4, -Math.PI / 2, -Math.PI / 2 + TWO_PI * n.rung / 5); x.stroke();
      }
      if (n.m.contested) { // contested: a small cross at two o'clock
        var cxx = px + (r + 3.6) * 0.8, cyy = py - (r + 3.6) * 0.6, s = G.small ? 2 : 2.6;
        x.strokeStyle = tok['--ink']; x.lineWidth = 1.2; x.globalAlpha = (on ? 1 : 0.2) * A;
        x.beginPath(); x.moveTo(cxx - s, cyy - s); x.lineTo(cxx + s, cyy + s); x.moveTo(cxx + s, cyy - s); x.lineTo(cxx - s, cyy + s); x.stroke();
      }
      x.globalAlpha = 1;
    }

    /* ---- entry card ---- */
    function tipHTML(n) {
      var m = n.m, e = F0.esc;
      var h = '<div class="tip-k">Entry ' + String(n.i + 1).padStart(3, '0') + ' · ' + e(PLAIN[m.domain]) + ' · ' + e(F0.fmtDate(m.date)) + '</div>' +
        '<div class="tip-t">' + e(m.title) + '</div><div class="tip-rows">' +
        '<div class="tip-row">' + dialSVG(n.f, 16) + '<span>AI ' + e(m.ai_role.toUpperCase()) + ': ' + e(ROLE_TXT[m.ai_role]) + '</span></div>' +
        '<div class="tip-row">' + ladderHTML(n.rung) + '<span>' + e(EVID[m.evidence].toUpperCase()) + '</span></div>' +
        '<div class="tip-row"><span style="width:16px;text-align:center">' + '●'.repeat(1) + '</span><span>SIGNIFICANCE ' + m.significance + ' OF 5 (EDITORIAL)</span></div>' +
        (m.contested ? '<div class="tip-row"><span class="badge x" style="padding:2px 6px">× Contested</span></div>' : '') +
        '</div>';
      if (n.member) h += '<div class="tip-note"><span class="h"></span>' + e(n.member) + '</div>';
      h += '<div class="tip-foot">' + (kbd ? 'Enter opens the Ledger entry' : 'Click to open the Ledger entry') + '</div>';
      return h;
    }
    function showTip(i, cx, cy) {
      if (i < 0) { F0.tip.hide(); return; }
      if (cx == null) { var b = canvas.getBoundingClientRect(); cx = b.left + nodes[i].x; cy = b.top + nodes[i].y; }
      F0.tip.show(tipHTML(nodes[i]), cx, cy);
    }
    function nearest(px, py) {
      if (!G.ok) return -1;
      var best = -1, bd = Infinity;
      nodes.forEach(function (n, i) {
        if (!match(n)) return;
        var d = Math.hypot(n.x - px, n.y - py), lim = Math.max(G.small ? 14 : 12, n.r + 7);
        if (d < lim && d < bd) { bd = d; best = i; }
      });
      return best;
    }
    function setHover(i, viaKbd, cx, cy) {
      kbd = !!viaKbd;
      if (i !== hover) { hover = i; if (!running()) draw(performance.now()); }
      canvas.style.cursor = i >= 0 ? 'pointer' : 'crosshair';
      showTip(i, cx, cy);
    }
    function running() { return T ? playing && loop && loop.running : loop && loop.running && !F0.idle(); }

    function settle() { if (entr && !entr.done) entr.finish(); }
    function redrawSoon() { if (!ptrRaf) ptrRaf = requestAnimationFrame(function () { ptrRaf = 0; if (!running()) draw(performance.now()); }); }
    canvas.addEventListener('pointermove', function (e) {
      settle();
      var b = canvas.getBoundingClientRect(), px = e.clientX - b.left, py = e.clientY - b.top;
      ptr = F0.motion() && e.pointerType !== 'touch' ? { x: px, y: py } : null;
      setHover(nearest(px, py), false, e.clientX, e.clientY);
      if (ptr) redrawSoon();
    });
    canvas.addEventListener('pointerleave', function () { var had = !!ptr; ptr = null; if (!kbd) setHover(-1); if (had) redrawSoon(); });
    canvas.addEventListener('pointerdown', settle);
    canvas.addEventListener('click', function (e) {
      var b = canvas.getBoundingClientRect(), i = nearest(e.clientX - b.left, e.clientY - b.top);
      if (i < 0) { setHover(-1); return; }
      if (e.pointerType === 'touch' && lastTap !== i) { lastTap = i; setHover(i, false, e.clientX, e.clientY); return; }
      location.href = (opts.base || 'ledger/') + '#' + encodeURIComponent(nodes[i].m.id);
    });

    /* ---- time control (opts.time) ---- */
    var MONL = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    function yearAt(w) { return nowY - ageAtK(K * (1 - w)); }
    function timeLabel(w) {
      var y = yearAt(w), yr = Math.floor(y), mo = Math.min(11, Math.floor((y - yr) * 12));
      return (nowY - y) < 9 ? MONL[mo] + ' ' + yr : String(yr);
    }
    function countAt(w) { var c = 0; nodes.forEach(function (n) { if (n.rho <= w + 1e-6) c++; }); return c; }
    function syncTime() {
      if (!T) return;
      var full = tw >= 0.9995, txt = (full ? 'Now, ' + F0.fmtDate(ledger.updated) : 'Up to ' + timeLabel(tw)) + ' · ' + countAt(tw) + ' of ' + nodes.length;
      if (T.range) { T.range.value = String(Math.round(tw * 1000)); T.range.setAttribute('aria-valuetext', txt + ' milestones'); }
      if (T.output && T.output.textContent !== txt) T.output.textContent = txt;
      if (T.play) { // a button whose label swaps (Play / Pause) and carries no aria-pressed; CSS swaps the icon on data-state
        T.play.removeAttribute('aria-pressed'); T.play.setAttribute('data-state', playing ? 'playing' : 'paused');
        T.play.setAttribute('aria-label', playing ? 'Pause' : (full ? 'Play the record from the oldest milestone' : 'Play on from this date'));
      }
    }
    function stopPlay() {
      playing = false; if (loop) loop.stop(); clearInterval(stepTimer); stepTimer = 0; syncTime(); draw(performance.now());
    }
    function startPlay() {
      if (tw >= 0.9995) tw = 0;
      playing = true; setHover(-1);
      if (F0.motion()) { lastNow = 0; loop.start(); }
      else stepTimer = setInterval(function () { // motion off: step ring by ring
        tw = Math.min(1, (Math.floor(tw * K + 1e-6) + 1) / K); syncTime(); draw(performance.now());
        if (tw >= 1) stopPlay();
      }, 700);
      syncTime(); draw(performance.now());
    }
    this.setTime = function (w) { if (playing) stopPlay(); tw = Math.max(0, Math.min(1, w)); syncTime(); draw(performance.now()); };
    if (T) {
      if (T.range) T.range.addEventListener('input', function () { settle(); if (playing) stopPlay(); tw = (+T.range.value) / 1000; if (hover >= 0 && !match(nodes[hover])) setHover(-1); syncTime(); draw(performance.now()); });
      if (T.play) T.play.addEventListener('click', function () { settle(); if (playing) stopPlay(); else startPlay(); });
    }

    /* ---- keyboard: a real list of links behind the canvas, with roving focus ---- */
    var links = [];
    if (listEl) {
      var frag = document.createDocumentFragment();
      nodes.forEach(function (n) {
        var li = document.createElement('li'), a = document.createElement('a'), m = n.m;
        a.href = (opts.base || 'ledger/') + '#' + encodeURIComponent(m.id);
        a.tabIndex = -1; a.dataset.i = n.i;
        a.textContent = F0.fmtDate(m.date) + ': ' + m.title + '. Field: ' + PLAIN[m.domain] + '. AI role: ' + m.ai_role + '. Evidence: ' + EVID[m.evidence].toLowerCase() + '.' +
          (m.contested ? ' Contested.' : '') + (n.member ? ' Founding members’ work.' : '');
        li.appendChild(a); frag.appendChild(li); links.push(a);
      });
      listEl.appendChild(frag);
      links[links.length - 1].tabIndex = 0;
      listEl.addEventListener('focusin', function (e) {
        var i = +e.target.dataset.i; if (isNaN(i)) return;
        settle();
        links.forEach(function (a, j) { a.tabIndex = j === i ? 0 : -1; });
        var cb = canvas.getBoundingClientRect(), my = cb.top + nodes[i].y, vh = window.innerHeight;
        if (my < 90 || my > vh - 60) window.scrollBy({ top: my - vh / 2, behavior: 'auto' }); // keep the focused mark in view
        setHover(i, true);
      });
      listEl.addEventListener('focusout', function (e) { if (!listEl.contains(e.relatedTarget)) { kbd = false; setHover(-1); } });
      listEl.addEventListener('keydown', function (e) {
        var i = +document.activeElement.dataset.i; if (isNaN(i)) return;
        var j = i, n = nodes[i];
        if (e.key === 'ArrowRight') j = Math.min(nodes.length - 1, i + 1);
        else if (e.key === 'ArrowLeft') j = Math.max(0, i - 1);
        else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          var dir = e.key === 'ArrowDown' ? 1 : -1, d = n.d;
          for (var step = 1; step <= domains.length; step++) {
            var dd = (n.d + dir * step + domains.length) % domains.length, best = -1, bd = Infinity;
            nodes.forEach(function (q, qi) { if (q.d === dd) { var g = Math.abs(q.rho - n.rho); if (g < bd) { bd = g; best = qi; } } });
            if (best >= 0) { j = best; break; }
          }
        }
        else if (e.key === 'Home') j = 0;
        else if (e.key === 'End') j = nodes.length - 1;
        else if (e.key === 'PageUp') j = Math.max(0, i - 10);
        else if (e.key === 'PageDown') j = Math.min(nodes.length - 1, i + 10);
        else if (e.key === 'Escape') { links[i].blur(); return; }
        else return;
        e.preventDefault(); links[j].focus({ preventScroll: true });
      });
    }

    /* ---- filters from the legend ---- */
    this.setFilter = function (f) { settle(); filter = f; if (hover >= 0 && !match(nodes[hover])) setHover(-1); if (!running()) draw(performance.now()); };

    /* ---- lifecycle ---- */
    readTokens(); layout(); draw(performance.now());
    C.resize(function () { layout(); draw(performance.now()); });
    F0.onTheme(function () { readTokens(); drawStatic(); draw(performance.now()); });
    var visible = false;
    if (T) {
      loop = F0.loop(function (now) {
        if (!lastNow) lastNow = now;
        tw = Math.min(1, tw + (now - lastNow) / DUR); lastNow = now;
        draw(now); syncTime();
        if (tw >= 1) stopPlay();
      });
      F0.whenVisible(stage, function () { visible = true; if (playing && stepTimer === 0) { lastNow = 0; loop.start(); } }, function () { visible = false; loop.stop(); });
      F0.onMotion(function () { if (playing) stopPlay(); });
      syncTime();
    } else {
      loop = F0.loop(draw);
      var sync = function () { if (visible && F0.motion() && !F0.idle()) { if (!loop.running) t0 = performance.now(); loop.start(); } else { loop.stop(); draw(performance.now()); } };
      F0.whenVisible(stage, function () { visible = true; sync(); }, function () { visible = false; sync(); });
      F0.onMotion(sync); F0.onIdle(sync);
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { drawStatic(); draw(performance.now()); });
    entr = F0.enter ? F0.enter(stage, function (t) { rise = t; if (!running()) draw(performance.now()); }, { duration: 1200, threshold: 0.2 }) : null;
    /* two short lines: where the rim is, and how far back the inner edge reaches (the oldest mark is in the readout) */
    if (opts.centre) opts.centre.innerHTML = '<span class="ln">Rim: ' + F0.esc(F0.fmtDate(ledger.updated)) + '</span><span class="ln">Inner edge: ' + Math.round(nowY - ageAtK(K)) + '</span>';
    this.nodes = nodes; this.domains = domains;
  };
})();
