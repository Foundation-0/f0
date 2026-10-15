/* The Ledger explorer (docs/ledger/). Vanilla JS on the shared runtime window.F0.
   One state object drives everything: the filter bar scopes the wall (canvas swimlanes with a
   keyboard twin), the Encyclopedia entry, the sortable table and the two charts. Filter state and the
   selected entry live in the URL hash (#<id>, or #field=…&role=…&entry=<id>), so any view can be shared.
   Every string from the data is escaped (F0.esc) before it reaches innerHTML. */
(function () {
  'use strict';
  var DATA = '../data/ledger.json';
  var SVGNS = 'http://www.w3.org/2000/svg';
  var D = document;
  function $(s, r) { return (r || D).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || D).querySelectorAll(s)); }
  function esc(s) { return F0.esc(s); }
  function pct(a, b) { return b ? Math.round(100 * a / b) : 0; }
  function pad3(n) { return String(n).padStart(3, '0'); }

  /* ---------------- vocabulary ---------------- */
  var ORDER = ['mathematics', 'computing', 'physics', 'astronomy-space', 'earth-climate', 'energy',
    'chemistry-materials', 'biology', 'medicine', 'engineering-robotics', 'science-of-science'];
  var FIELD = { 'mathematics': 'Mathematics', 'computing': 'Computing', 'physics': 'Physics', 'astronomy-space': 'Astronomy & space',
    'earth-climate': 'Earth & climate', 'energy': 'Energy', 'chemistry-materials': 'Chemistry & materials', 'biology': 'Biology',
    'medicine': 'Medicine', 'engineering-robotics': 'Engineering & robotics', 'science-of-science': 'Science of science' };
  var FIELD_SHORT = { 'mathematics': 'Mathematics', 'computing': 'Computing', 'physics': 'Physics', 'astronomy-space': 'Astronomy',
    'earth-climate': 'Earth, climate', 'energy': 'Energy', 'chemistry-materials': 'Chemistry', 'biology': 'Biology', 'medicine': 'Medicine',
    'engineering-robotics': 'Engineering', 'science-of-science': 'Sci. of science' };
  var FIELD_UP = { 'mathematics': ['MATHEMATICS', 'MATHS'], 'computing': ['COMPUTING'], 'physics': ['PHYSICS'],
    'astronomy-space': ['ASTRONOMY · SPACE', 'ASTRONOMY', 'ASTRO'], 'earth-climate': ['EARTH · CLIMATE', 'CLIMATE'], 'energy': ['ENERGY'],
    'chemistry-materials': ['CHEMISTRY · MATERIALS', 'CHEMISTRY', 'CHEM'], 'biology': ['BIOLOGY'], 'medicine': ['MEDICINE'],
    'engineering-robotics': ['ENGINEERING · ROBOTS', 'ROBOTICS'], 'science-of-science': ['SCIENCE OF SCIENCE', 'META-SCIENCE'] };
  function fieldName(d) { return FIELD[d] || d; }
  var ROLES = ['instrument', 'collaborator', 'originator'];
  var ROLE_F = { instrument: 0.25, collaborator: 0.5, originator: 0.75 };
  var ROLE_NAME = { instrument: 'Instrument', collaborator: 'Collaborator', originator: 'Originator' };
  var ROLE_TXT = {
    instrument: 'AI was a tool inside a study people designed.',
    collaborator: 'AI proposed key ideas or constructions; people selected, proved or tested them.',
    originator: 'AI produced the result itself; people checked it.'
  };
  var EVS = ['formally-verified', 'independently-replicated', 'peer-reviewed', 'deployed', 'preprint', 'claimed'];
  var RUNG = { 'claimed': 1, 'preprint': 2, 'peer-reviewed': 3, 'deployed': 3, 'independently-replicated': 4, 'formally-verified': 5 };
  var EV_NAME = { 'formally-verified': 'Formally verified', 'independently-replicated': 'Independently replicated', 'peer-reviewed': 'Peer reviewed',
    'deployed': 'Deployed', 'preprint': 'Preprint', 'claimed': 'Claimed' };
  var EV_SHORT = { 'formally-verified': 'Verified', 'independently-replicated': 'Replicated', 'peer-reviewed': 'Reviewed', 'deployed': 'Deployed', 'preprint': 'Preprint', 'claimed': 'Claimed' };
  var EV_CLS = { 'formally-verified': 'v', 'independently-replicated': 'v', 'peer-reviewed': 'r', 'deployed': 'd', 'preprint': 'p', 'claimed': 'c' };
  var EV_TOK = { 'formally-verified': '--st-verified', 'independently-replicated': '--st-verified', 'peer-reviewed': '--st-reviewed', 'deployed': '--st-deployed', 'preprint': '--st-preprint', 'claimed': '--st-claimed' };
  var BASIS = { publication: 'published', preprint: 'preprint posted', announcement: 'announced', competition: 'competition result', deployment: 'went into use' };
  var MON = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
  var CUT = 2016;
  /* Who did what on Foundation0's own entries (credit per docs/data/projects.json, members.json and the project dossiers). */
  var CREDIT = {
    'aska-cab-to-fcc-exact-fold': 'Founding member Ahraz Arifuddin’s own work at Aska Digital, done with a team of AI agents.',
    'eumemic-tess-faint-transit-candidates': 'Founding member eumemic’s search. Aska Digital built the first version of the project’s website and sent ten pull requests, four of them pipeline fixes; the authors merged all ten.',
    'integer-mult-bounds-community': 'Founding member Doug Colkitt (GitHub: Mister-Meeseeks) runs this open race in the CrocSwap repository. Founding member rohanarun holds the current reviewed κ record (PR #1094); eumemic and Ryan Shea also contribute. Aska built the live tracker that grew into this site.',
    'vdw-coefficient-community-refinement': 'Started by founding member rohanarun with Codex and Claude; the last steps came from contributors DaysSky and artuskg.',
    'exact-dft-lean-record-shea-kothe': 'Founding member Ryan Shea’s record, built on Jeremy Kothe’s community circuit.',
    'gf2m-aes-field-multiplier-112': 'Swapnil Jain’s repository and result. Aska Digital contributed verified multipliers for four more fields, GF(2^9), GF(2^10), GF(2^11) and GF(2^128) (PR #1, merged; not records).',
    'mobius-x1-gf2-mobius-below-nlogn': 'Swapnil Jain’s repository and claim. Aska Digital wrote and ran the full-network check behind Theorem 2 (PR #1, merged).'
  };
  var CREDIT_DEFAULT = 'Foundation0 work: by a founding member, or with a contribution from Aska Digital.';

  /* ---------------- glyphs ---------------- */
  function dialPath(f, r) {
    var a = -Math.PI / 2 + f * Math.PI * 2, x = (r * Math.cos(a)).toFixed(2), y = (r * Math.sin(a)).toFixed(2);
    return 'M0 0L0 -' + r + 'A' + r + ' ' + r + ' 0 ' + (f > 0.5 ? 1 : 0) + ' 1 ' + x + ' ' + y + 'Z';
  }
  function dialSVG(f) {
    return '<svg class="dial" viewBox="-9 -9 18 18" aria-hidden="true"><circle r="7" style="fill:var(--mark-bio)"/><path d="' + dialPath(f, 7) + '" style="fill:var(--mark-dig)"/></svg>';
  }
  function ladderHTML(r) { return '<span class="ladder" data-r="' + r + '" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>'; }
  function sigDots(n) { var s = '<span class="sigdots" aria-hidden="true">'; for (var k = 1; k <= 5; k++) s += '<i' + (k <= n ? ' class="on"' : '') + '></i>'; return s + '</span>'; }
  function norm(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  /* ---------------- state ---------------- */
  var S = { all: [], byId: {}, rows: [], byRow: [], sel: -1, selSrc: 'default', selUser: false, shown: [], updated: '', yMin: 1965, yMax: 2026, tNow: 2026.8, nowYear: 2026 };
  var F = null;
  function defaults() { return { q: '', qt: [], fields: [], roles: [], ev: [], c: false, m: false, y0: S.yMin, y1: S.yMax }; }
  function filtersActive() { var d = defaults(); return !!(F.q || F.fields.length || F.roles.length || F.ev.length || F.c || F.m || F.y0 !== d.y0 || F.y1 !== d.y1); }
  function pass(m, skip) {
    if (skip !== 'fields' && F.fields.length && F.fields.indexOf(m.domain) < 0) return false;
    if (skip !== 'roles' && F.roles.length && F.roles.indexOf(m.ai_role) < 0) return false;
    if (skip !== 'ev' && F.ev.length && F.ev.indexOf(m.evidence) < 0) return false;
    if (skip !== 'c' && F.c && !m.contested) return false;
    if (skip !== 'm' && F.m && !m.foundation0) return false;
    if (skip !== 'y' && (m.y < F.y0 || m.y > F.y1)) return false;
    if (skip !== 'q') for (var k = 0; k < F.qt.length; k++) if (m.hay.indexOf(F.qt[k]) < 0) return false;
    return true;
  }

  function prep(L) {
    S.updated = L.updated;
    S.tNow = F0.decYear(L.updated);
    S.nowYear = +String(L.updated).slice(0, 4);
    var M = L.milestones.slice();
    M.forEach(function (m) {
      m.t = F0.decYear(m.date); m.y = +String(m.date).slice(0, 4);
      m.rung = RUNG[m.evidence] || 1; m.f = ROLE_F[m.ai_role] || 0.5;
      var ba = m.before_after || {};
      m.hay = norm([m.id, m.title, m.summary, m.subfield, fieldName(m.domain), m.why_it_matters, (m.ai_systems || []).join(' '),
        (m.organizations || []).join(' '), m.contested_note, ba.metric, ba.before, ba.after, m.ai_role, EV_NAME[m.evidence], m.date].join(' \u0001 '));
    });
    M.sort(function (a, b) { return a.t - b.t || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0); });
    M.forEach(function (m, i) { m.i = i; S.byId[m.id] = m; });
    S.all = M;
    var present = {}; M.forEach(function (m) { present[m.domain] = (present[m.domain] || 0) + 1; });
    S.counts = present;
    S.rows = ORDER.filter(function (d) { return present[d]; }).concat(Object.keys(present).filter(function (d) { return ORDER.indexOf(d) < 0; }).sort());
    S.byRow = S.rows.map(function (d) { return M.filter(function (m) { return m.domain === d; }); });
    M.forEach(function (m) { m.row = S.rows.indexOf(m.domain); });
    S.yMin = Math.min.apply(null, M.map(function (m) { return m.y; }));
    S.yMax = Math.max(S.nowYear, Math.max.apply(null, M.map(function (m) { return m.y; })));
  }

  /* ---------------- hero numbers ---------------- */
  function stats() {
    var M = S.all, c = function (fn) { return M.filter(fn).length; };
    var map = {
      count: M.length, span: S.yMin + '–' + Math.max.apply(null, M.map(function (m) { return m.y; })), fields: S.rows.length,
      verified: c(function (m) { return m.evidence === 'formally-verified'; }), contested: c(function (m) { return m.contested; }),
      members: c(function (m) { return m.foundation0; }), updated: 'Updated ' + S.updated,
      srcline: M.length + ' milestones, updated ' + S.updated,
      stamp: 'Ledger updated ' + S.updated + ' · ' + M.length + ' milestones'
    };
    ROLES.forEach(function (r) { map['r-' + r] = c(function (m) { return m.ai_role === r; }); });
    EVS.forEach(function (e) { map['e-' + e] = c(function (m) { return m.evidence === e; }); });
    $$('[data-stat]').forEach(function (el) { var k = el.getAttribute('data-stat'); if (map[k] != null) el.textContent = map[k]; });
  }

  /* ================= filter bar ================= */
  var FACETS = {
    fields: function () { return S.rows.map(function (d) { return { v: d, label: fieldName(d), short: FIELD_SHORT[d] || d, g: '' }; }); },
    roles: function () { return ROLES.map(function (r) { return { v: r, label: ROLE_NAME[r], short: ROLE_NAME[r], g: dialSVG(ROLE_F[r]) }; }); },
    ev: function () { return EVS.map(function (e) { return { v: e, label: EV_NAME[e], short: EV_SHORT[e], g: '<span style="color:var(' + EV_TOK[e] + ')">' + ladderHTML(RUNG[e]) + '</span>' }; }); }
  };
  var KEYOF = { fields: 'domain', roles: 'ai_role', ev: 'evidence' };
  function buildFacets() {
    Object.keys(FACETS).forEach(function (f) {
      var host = $('[data-opts="' + f + '"]');
      host.innerHTML = FACETS[f]().map(function (o) {
        return '<label class="fopt"><input type="checkbox" name="' + f + '" value="' + esc(o.v) + '"><span class="g">' + o.g + '</span><span class="ol">' + esc(o.label) + '</span><span class="oc" data-oc="' + esc(o.v) + '">0</span></label>';
      }).join('');
      host.addEventListener('change', function () {
        F[f] = $$('input:checked', host).map(function (i) { return i.value; });
        update();
      });
    });
    $$('[data-clear]').forEach(function (b) { b.addEventListener('click', function () { F[b.getAttribute('data-clear')] = []; syncControls(); update(); }); });
    var y0 = $('#f-y0'), y1 = $('#f-y1'), opts = '';
    for (var y = S.yMin; y <= S.yMax; y++) opts += '<option value="' + y + '">' + y + '</option>';
    y0.innerHTML = opts; y1.innerHTML = opts;
    function years() {
      var a = +y0.value, b = +y1.value; if (a > b) { var t = a; a = b; b = t; }
      F.y0 = a; F.y1 = b; W.view = null; syncControls(); update();
    }
    y0.addEventListener('change', years); y1.addEventListener('change', years);
    $('#f-c').addEventListener('change', function (e) { F.c = e.target.checked; update(); });
    $('#f-m').addEventListener('change', function (e) { F.m = e.target.checked; update(); });
    var q = $('#f-q'), qt = 0;
    q.addEventListener('input', function () { clearTimeout(qt); qt = setTimeout(function () { setQuery(q.value); update(); }, 120); });
    q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); clearTimeout(qt); setQuery(q.value); update(); } });
    $('#fbar').addEventListener('submit', function (e) { e.preventDefault(); });
    $('#f-reset').addEventListener('click', function () { if (this.getAttribute('aria-disabled') !== 'true') resetFilters(); });
    /* "Clear the filters" sits in a note that hides once the table has rows again: keep focus on the table */
    $$('[data-reset]').forEach(function (b) { b.addEventListener('click', function () { resetFilters(); var tw = $('.ltbl-wrap'); if (tw) tw.focus({ preventScroll: true }); }); });
    /* phones: the facets fold behind one Filters button */
    var fm = $('#f-more'), fb = $('#fbar');
    fm.addEventListener('click', function () { var o = !fb.classList.contains('open'); fb.classList.toggle('open', o); fm.setAttribute('aria-expanded', o ? 'true' : 'false'); });
    $$('#zoom [data-zoom]').forEach(function (b) {
      b.addEventListener('click', function () {
        var z = b.getAttribute('data-zoom');
        W.view = null;
        if (z === 'fit') { var fr = fitRange(); F.y0 = fr[0]; F.y1 = fr[1]; }
        else { F.y0 = z === 'all' ? S.yMin : Math.max(S.yMin, +z); F.y1 = S.yMax; }
        syncControls(); update();
      });
    });
    /* popovers (filter panels and the "?" notes): one open at a time; Escape or an outside click closes */
    var pops = $$('.fpop, .qpop');
    pops.forEach(function (p) {
      p.addEventListener('toggle', function () {
        if (!p.open) return;
        pops.forEach(function (o) { if (o !== p) o.open = false; });
        /* keep the panel inside the viewport */
        var pn = p.querySelector('.fpanel, .qpanel'); pn.style.transform = '';
        var r = pn.getBoundingClientRect(), vw = D.documentElement.clientWidth, dx = 0;
        if (r.right > vw - 12) dx = vw - 12 - r.right;
        if (r.left + dx < 12) dx = 12 - r.left;
        if (dx) pn.style.transform = 'translateX(' + Math.round(dx) + 'px)';
      });
      p.addEventListener('keydown', function (e) { if (e.key === 'Escape' && p.open) { p.open = false; p.querySelector('summary').focus(); } });
    });
    D.addEventListener('click', function (e) { pops.forEach(function (p) { if (p.open && !p.contains(e.target)) p.open = false; }); });
    /* "/" focuses the search */
    D.addEventListener('keydown', function (e) {
      if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
      var t = e.target, tag = t && t.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (t && t.isContentEditable)) return;
      e.preventDefault(); q.focus();
    });
  }
  /* the years spanned by the milestones that pass every filter except the year range */
  function fitRange() {
    var lo = Infinity, hi = -Infinity;
    S.all.forEach(function (m) { if (pass(m, 'y')) { if (m.y < lo) lo = m.y; if (m.y > hi) hi = m.y; } });
    return isFinite(lo) ? [lo, hi] : [S.yMin, S.yMax];
  }
  function setQuery(v) { F.q = String(v || '').trim(); F.qt = norm(F.q).split(/\s+/).filter(Boolean); }
  function resetFilters() { F = defaults(); W.view = null; syncControls(); update(); }
  function syncControls() {
    Object.keys(FACETS).forEach(function (f) {
      $$('[data-opts="' + f + '"] input').forEach(function (i) { i.checked = F[f].indexOf(i.value) >= 0; });
      var opts = FACETS[f](), on = F[f], txt = 'All';
      if (on.length === 1) { var o = opts.filter(function (x) { return x.v === on[0]; })[0]; txt = o ? o.short : on[0]; }
      else if (on.length > 1) txt = on.length + ' chosen';
      $('[data-fv="' + f + '"]').textContent = txt;
      $('.fpop[data-facet="' + f + '"]').classList.toggle('on', on.length > 0);
    });
    $('#f-y0').value = String(F.y0); $('#f-y1').value = String(F.y1);
    $('.fyears').classList.toggle('on', F.y0 !== S.yMin || F.y1 !== S.yMax);
    $('#f-c').checked = F.c; $('#f-m').checked = F.m;
    var q = $('#f-q'); if (q.value.trim() !== F.q) q.value = F.q;
    var anyPreset = false, wr = wRange();
    $$('#zoom [data-zoom]').forEach(function (b) {
      var z = b.getAttribute('data-zoom'); if (z === 'fit') return;
      var y0 = z === 'all' ? S.yMin : Math.max(S.yMin, +z), on = wr[0] === y0 && wr[1] === S.yMax;
      anyPreset = anyPreset || on;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    var fr = fitRange(), fb = $('#zoom [data-zoom="fit"]');
    if (fb) fb.setAttribute('aria-pressed', !W.view && !anyPreset && F.y0 === fr[0] && F.y1 === fr[1] ? 'true' : 'false');
    $('#f-reset').setAttribute('aria-disabled', filtersActive() ? 'false' : 'true');
    var nf = F.fields.length + F.roles.length + F.ev.length + (F.c ? 1 : 0) + (F.m ? 1 : 0) + (F.y0 !== S.yMin || F.y1 !== S.yMax ? 1 : 0), fn = $('.fmore-n');
    fn.textContent = nf; fn.hidden = !nf;
    $('.wall-cap-mob').hidden = !W.view;
  }
  function facetCounts() {
    Object.keys(FACETS).forEach(function (f) {
      var key = KEYOF[f], c = {};
      S.all.forEach(function (m) { if (pass(m, f)) c[m[key]] = (c[m[key]] || 0) + 1; });
      $$('[data-opts="' + f + '"] [data-oc]').forEach(function (el) {
        var n = c[el.getAttribute('data-oc')] || 0; el.textContent = n;
        el.parentNode.classList.toggle('zero', n === 0);
      });
    });
  }

  /* ================= the update cycle ================= */
  var pending = 0;
  function update() {
    if (pending) return;
    pending = requestAnimationFrame(function () {
      pending = 0;
      S.shown = S.all.filter(function (m) { var ok = pass(m); m.on = ok; return ok; });
      viewKeepsSel();
      var n = S.shown.length, N = S.all.length;
      $('#f-count').innerHTML = '<b>' + n + '</b> of ' + N;
      syncControls(); facetCounts();
      wLayout(); wBuildList(); wDraw(); wCount();
      if (S.sel >= 0) showEntry(S.sel, S.selSrc, true);
      tRender(); chartsRender();
      writeHash();
    });
  }

  /* ================= URL hash: #<id> or #field=a,b&role=…&entry=<id> ================= */
  var lastHash = null;
  function stateHash() {
    var p = [], d = defaults();
    if (F.q) p.push('q=' + encodeURIComponent(F.q));
    if (F.fields.length) p.push('field=' + F.fields.join(','));
    if (F.roles.length) p.push('role=' + F.roles.join(','));
    if (F.ev.length) p.push('evidence=' + F.ev.join(','));
    if (F.c) p.push('contested=1');
    if (F.m) p.push('members=1');
    if (F.y0 !== d.y0 || F.y1 !== d.y1) p.push('years=' + F.y0 + '-' + F.y1);
    var sel = S.selUser && S.sel >= 0 ? S.all[S.sel].id : '';
    if (!p.length) return sel ? '#' + sel : '';
    if (sel) p.push('entry=' + sel);
    return '#' + p.join('&');
  }
  function writeHash() {
    var h = stateHash();
    if (h === lastHash) return;
    var cur = location.hash, raw = decodeURIComponent(cur.slice(1));
    // leave a plain section anchor (#the-list) alone until something worth sharing changes
    if (!h && cur && D.getElementById(raw) && lastHash === null) { lastHash = h; return; }
    lastHash = h;
    try { history.replaceState(null, '', location.pathname + location.search + (h || '')); } catch (e) { /* file:// or sandboxed */ }
  }
  /* returns 'entry' when the hash names an entry, 'filters' when it sets filters, '' otherwise */
  function readHash(hash) {
    var raw = String(hash || '').replace(/^#/, '');
    if (!raw) return '';
    var dec; try { dec = decodeURIComponent(raw); } catch (e) { dec = raw; }
    if (raw.indexOf('=') < 0) {
      if (S.byId[dec]) { setSel(S.byId[dec].i, 'link', true); return 'entry'; }
      return '';
    }
    var q = new URLSearchParams(raw), nf = defaults();
    var list = function (k, allowed) { var v = q.get(k); return v ? v.split(',').filter(function (x) { return allowed.indexOf(x) >= 0; }) : []; };
    nf.fields = list('field', S.rows); nf.roles = list('role', ROLES); nf.ev = list('evidence', EVS);
    nf.c = q.get('contested') === '1'; nf.m = q.get('members') === '1';
    var yr = /^(\d{4})-(\d{4})$/.exec(q.get('years') || '');
    if (yr) W.view = null;
    if (yr) { var a = Math.max(S.yMin, Math.min(+yr[1], +yr[2])), b = Math.min(S.yMax, Math.max(+yr[1], +yr[2])); if (a <= b) { nf.y0 = a; nf.y1 = b; } }
    F = nf; setQuery(q.get('q') || '');
    var e = q.get('entry');
    if (e && S.byId[e]) setSel(S.byId[e].i, 'link', true);
    return e && S.byId[e] ? 'entry' : 'filters';
  }

  /* ================= selection ================= */
  function setSel(i, src, user) {
    S.sel = i; S.selSrc = src; if (user) S.selUser = true;
  }
  function select(i, src, user) {
    if (i < 0) return;
    setSel(i, src, user);
    if (viewKeepsSel()) { wLayout(); wBuildList(); wCount(); syncControls(); }
    if (user) arStop();
    showEntry(i, src);
    wSyncRoving(); wDraw(); tMarkSel();
    if (user) writeHash();
  }
  function goToEntry(i, how) {
    select(i, 'select', true);
    var single = getComputedStyle($('.wall-grid')).gridTemplateColumns.split(' ').length < 2;
    var target = single ? $('#entry') : $('#wall-fig');
    target.scrollIntoView({ behavior: F0.motion() ? 'smooth' : 'auto', block: 'start' });
    if (how === 'kbd') $('#entry').focus({ preventScroll: true });
  }

  /* ================= the wall ================= */
  var W = { cv: null, C: null, ctx: null, L: null, T: {}, hover: -1, kbd: false, glideX: null, vis: [], pos: {}, links: {}, ptr: 'mouse', view: null };
  /* The wall's time window. It is the year filter, except on a phone's first view, where the wall alone opens on
     2023 onward (W.view) so the lanes are legible; any zoom, year choice or reset hands it back to the filter. */
  function wRange() { return W.view ? [W.view.y0, W.view.y1] : [F.y0, F.y1]; }
  /* an entry chosen outside the phone view widens the wall to the filter's years; true when it did */
  function viewKeepsSel() {
    if (!W.view || S.sel < 0 || !S.selUser || S.all[S.sel].y >= W.view.y0) return false;
    W.view = null; return true;
  }
  function wCount() {
    var N = S.all.length, n = S.shown.filter(function (m) { return m.vx != null; }).length;
    $$('[data-live="shown"]').forEach(function (el) { el.textContent = n + ' of ' + N; });
  }
  function readTok() {
    var g = function (n) { return F0.css(n); };
    W.T = { bg1: g('--bg-1'), bg2: g('--bg-2'), bg3: g('--bg-3'), grid: g('--grid'), line: g('--line'), lineUi: g('--line-ui'),
      ink: g('--ink'), ink2: g('--ink-2'), ink3: g('--ink-3'), bio: g('--mark-bio'), dig: g('--mark-dig'), digLine: g('--dig'),
      hair: g('--hair'), focus: g('--focus'), x: g('--st-contested'), mono: g('--f-mono') || 'monospace', serif: g('--f-serif') || 'serif', dark: F0.theme() === 'dark' };
  }
  function wInit() {
    W.cv = $('#wall-canvas'); W.C = F0.canvas(W.cv); W.ctx = W.C.ctx;
    readTok();
    W.C.resize(function () { wLayout(); wDraw(); });
    F0.onTheme(function () { readTok(); wDraw(); });
    if (D.fonts && D.fonts.ready) D.fonts.ready.then(function () { readTok(); wDraw(); });
    var cv = W.cv;
    cv.addEventListener('pointerdown', function (e) { W.ptr = e.pointerType || 'mouse'; });
    cv.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'touch') return;
      W.ptr = e.pointerType || 'mouse';
      var i = wPick(e.clientX, e.clientY);
      if (i !== W.hover) {
        W.hover = i;
        cv.style.cursor = i >= 0 ? 'pointer' : 'crosshair';
        showEntry(i >= 0 ? i : S.sel, i >= 0 ? 'hover' : S.selSrc);
        wDraw();
      }
    });
    cv.addEventListener('pointerleave', function () {
      if (W.hover >= 0) { W.hover = -1; cv.style.cursor = 'crosshair'; showEntry(S.sel, S.selSrc); wDraw(); }
    });
    cv.addEventListener('click', function (e) {
      var i = wPick(e.clientX, e.clientY, W.ptr === 'touch' || W.ptr === 'pen');
      if (i < 0) return;
      W.hover = -1; select(i, 'select', true);
    });
    /* keyboard twin: a list of links behind the canvas, one tab stop, arrows move the cursor */
    var list = $('#wall-list');
    list.addEventListener('focusin', function (e) {
      var a = e.target.closest('a'); if (!a) return;
      W.kbd = true;
      var i = +a.getAttribute('data-i');
      if (i !== S.sel || S.selSrc !== 'select') select(i, 'select', true); else wDraw();
    });
    list.addEventListener('focusout', function (e) { if (!list.contains(e.relatedTarget)) { W.kbd = false; wDraw(); } });
    list.addEventListener('click', function (e) { var a = e.target.closest('a'); if (a) e.preventDefault(); });
    list.addEventListener('keydown', function (e) {
      var a = e.target.closest('a'); if (!a) return;
      var i = +a.getAttribute('data-i'), p = W.pos[i], vis = W.vis, j = -1, m = S.all[i];
      if (p == null) return;
      switch (e.key) {
        case 'ArrowRight': j = vis[Math.min(vis.length - 1, p + 1)].i; break;
        case 'ArrowLeft': j = vis[Math.max(0, p - 1)].i; break;
        case 'PageDown': j = vis[Math.min(vis.length - 1, p + 10)].i; break;
        case 'PageUp': j = vis[Math.max(0, p - 10)].i; break;
        case 'Home': j = vis[0].i; break;
        case 'End': j = vis[vis.length - 1].i; break;
        case 'ArrowDown': case 'ArrowUp':
          var dir = e.key === 'ArrowDown' ? 1 : -1;
          for (var r = m.row + dir; r >= 0 && r < S.rows.length; r += dir) {
            var best = null, bd = Infinity;
            S.byRow[r].forEach(function (q) { if (W.pos[q.i] != null) { var d = Math.abs(q.t - m.t); if (d < bd) { bd = d; best = q; } } });
            if (best) { j = best.i; break; }
          }
          if (j < 0) j = i;
          break;
        case 'Enter': case ' ':
          e.preventDefault(); $('#entry').focus(); return;
        case 'Escape': a.blur(); return;
        default: return;
      }
      e.preventDefault();
      if (j >= 0 && W.links[j]) W.links[j].focus();
    });
    $('#entry').addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && S.sel >= 0 && W.links[S.sel]) { e.preventDefault(); W.links[S.sel].focus(); }
    });
  }
  function wLayout() {
    if (!W.C) return;
    var C = W.C, w = C.w, h = C.h, mob = w < 640, L = { w: w, h: h, mob: mob };
    L.top = mob ? 30 : 58; L.axis = 30; /* wide screens: a two-line band above the rows, era and now labels, then the caption */
    L.gutter = mob ? 0 : (w < 900 ? 148 : 178);
    L.x0 = L.gutter + (mob ? 12 : 14); L.x1 = w - (mob ? 16 : 26); L.pw = L.x1 - L.x0;
    L.R = Math.max(1, S.rows.length);
    L.rowH = (h - L.top - L.axis) / L.R;
    L.maxLen = mob ? Math.max(10, L.rowH - 24) : Math.min(L.rowH * 0.74, L.rowH - 14);
    var yr = wRange(), t0 = yr[0], t1 = yr[1] >= S.nowYear ? S.tNow + 1 / 18 : yr[1] + 1;
    if (t1 <= t0) t1 = t0 + 1;
    L.t0 = t0; L.t1 = t1;
    L.comp = t0 < CUT - 1 && t1 > CUT + 1;
    L.pre = L.comp ? Math.round(L.pw * (mob ? 0.12 : 0.09)) : 0; L.gap = L.comp ? 14 : 0;
    W.L = L;
    var sigR = mob ? [0, 2.3, 2.8, 3.4, 4.1, 4.9] : [0, 2.6, 3.2, 3.9, 4.7, 5.6], sigLen = [0, 0.36, 0.52, 0.68, 0.84, 1];
    S.byRow.forEach(function (list, r) {
      var yb = L.top + (r + 1) * L.rowH - (mob ? 5 : 7), last = -1e9;
      list.forEach(function (m) {
        if (m.y < yr[0] || m.y > yr[1]) { m.vx = null; return; }
        var x = xOf(m.t); if (x - last < 1.6) x = last + 1.6; last = x;
        m.vx = x; m.yb = yb; m.len = L.maxLen * sigLen[m.significance || 1]; m.r = sigR[m.significance || 1];
      });
    });
    L.ticks = wTicks();
  }
  function xOf(t) {
    var L = W.L;
    if (L.comp) {
      if (t < CUT) return L.x0 + Math.max(0, (t - L.t0) / (CUT - L.t0)) * L.pre;
      return L.x0 + L.pre + L.gap + (t - CUT) / (L.t1 - CUT) * (L.pw - L.pre - L.gap);
    }
    return L.x0 + (t - L.t0) / (L.t1 - L.t0) * L.pw;
  }
  function wTicks() {
    var L = W.L, out = [], a = L.comp ? CUT : L.t0, b = L.t1;
    var pxY = (xOf(b) - xOf(a)) / Math.max(0.01, b - a), minGap = L.mob ? 34 : 46;
    if (pxY >= 210) { // quarters
      for (var y = Math.floor(a); y < b; y++) for (var q = 0; q < 4; q++) {
        var t = y + q / 4, te = Math.min(b, t + 0.25);
        if (t < a - 1e-6 || t >= b) continue;
        var lab = MON[q * 3] + (q === 0 || t === a ? ' ’' + String(y).slice(2) : '');
        out.push({ x: xOf(t), mid: (xOf(t) + xOf(te)) / 2, w: xOf(te) - xOf(t), label: lab });
      }
      return out;
    }
    var step = [1, 2, 5, 10, 20].filter(function (s) { return s * pxY >= minGap; })[0] || 25;
    if (L.mob && step === 1 && pxY < 46) step = 2;
    for (var yy = Math.ceil(a / step) * step; yy < b; yy += step) {
      var e2 = Math.min(b, yy + step);
      out.push({ x: xOf(yy), mid: step === 1 ? (xOf(yy) + xOf(e2)) / 2 : xOf(yy), w: xOf(e2) - xOf(yy),
        label: L.mob && step === 1 ? '’' + String(yy).slice(2) : String(yy) });
    }
    // single-year grid lines between labelled steps
    if (step > 1 && pxY >= 8) for (var g = Math.ceil(a); g < b; g++) if (g % step) out.push({ x: xOf(g), minor: true });
    return out;
  }
  function wPick(cx, cy, touch) {
    if (!W.L) return -1;
    var r = W.cv.getBoundingClientRect(), px = cx - r.left, py = cy - r.top, L = W.L;
    var row = Math.floor((py - L.top) / L.rowH);
    if (row < 0 || row >= L.R) return -1;
    var tol = touch ? 18 : 10, best = -1, bd = Infinity;
    S.byRow[row].forEach(function (m) {
      if (!m.on || m.vx == null) return;
      var top = m.yb - m.len - m.r, dx = Math.abs(m.vx - px), dy = py < top ? top - py : (py > m.yb ? py - m.yb : 0);
      var d = Math.sqrt(dx * dx + dy * dy * 0.5);
      if (d < bd && dx <= tol + m.r) { bd = d; best = m.i; }
    });
    return bd <= tol + 6 ? best : -1;
  }
  function wBuildList() {
    var vis = S.all.filter(function (m) { return m.on && m.vx != null; });
    W.vis = vis; W.pos = {}; W.links = {};
    vis.forEach(function (m, k) { W.pos[m.i] = k; });
    var ol = $('#wall-list');
    ol.innerHTML = vis.map(function (m) {
      return '<li><a href="#' + encodeURIComponent(m.id) + '" data-i="' + m.i + '" tabindex="-1">' + esc(F0.fmtDate(m.date) + ': ' + m.title + '. ' +
        fieldName(m.domain) + '. AI ' + m.ai_role + '. ' + EV_NAME[m.evidence] + '. Significance ' + m.significance + ' of 5.' +
        (m.contested ? ' Contested.' : '') + (m.foundation0 ? ' Members’ work.' : '')) + '</a></li>';
    }).join('');
    $$('a', ol).forEach(function (a) { W.links[+a.getAttribute('data-i')] = a; });
    wSyncRoving();
  }
  function wSyncRoving() {
    var ks = Object.keys(W.links); if (!ks.length) return;
    var target = W.links[S.sel] || W.links[W.vis[W.vis.length - 1].i];
    ks.forEach(function (k) { W.links[k].tabIndex = -1; });
    target.tabIndex = 0;
  }

  /* drawing */
  function circle(x, cx, cy, r) { x.beginPath(); x.arc(cx, cy, r, 0, Math.PI * 2); x.fill(); }
  function octagon(x, cx, cy, r) {
    x.beginPath();
    for (var k = 0; k < 8; k++) { var a = (22.5 + 45 * k) * Math.PI / 180, px = cx + r * Math.cos(a), py = cy + r * Math.sin(a); if (k) x.lineTo(px, py); else x.moveTo(px, py); }
    x.closePath(); x.stroke();
  }
  function drawMark(x, m, mode) { /* mode 0 ghost (outside filters), 1 normal, 2 active */
    var T = W.T, X = m.vx, yb = m.yb, top = yb - m.len, r = m.r * (mode === 2 ? 1.3 : 1);
    if (mode === 0) {
      x.globalAlpha = T.dark ? 0.26 : 0.22;
      x.strokeStyle = T.ink3; x.lineWidth = 1; x.setLineDash([]);
      x.beginPath(); x.moveTo(X, yb); x.lineTo(X, top + r); x.stroke();
      x.fillStyle = T.ink3; circle(x, X, top, r * 0.8);
      x.globalAlpha = 1; return;
    }
    x.globalAlpha = 1;
    x.strokeStyle = m.foundation0 ? T.hair : T.ink3;
    x.lineWidth = mode === 2 ? 1.8 : (m.foundation0 ? 1.4 : 1.15);
    x.setLineDash(m.rung >= 3 ? [] : (m.rung === 2 ? [3, 2] : [1, 2.2]));
    x.beginPath(); x.moveTo(X, yb); x.lineTo(X, top + r + 1); x.stroke();
    x.setLineDash([]);
    x.fillStyle = T.bg2; circle(x, X, top, r + 1.7);
    x.fillStyle = T.bio; circle(x, X, top, r);
    x.fillStyle = T.dig; x.beginPath(); x.moveTo(X, top); x.arc(X, top, r, -Math.PI / 2, -Math.PI / 2 + m.f * Math.PI * 2); x.closePath(); x.fill();
    if (m.foundation0) { x.strokeStyle = T.hair; x.lineWidth = 1.25; octagon(x, X, top, r + 3.6); }
    if (m.contested) {
      var s = mode === 2 ? 3.2 : 2.6, cy = top - r - (m.foundation0 ? 9 : 6.5);
      x.strokeStyle = T.x; x.lineWidth = 1.5;
      x.beginPath(); x.moveTo(X - s, cy - s); x.lineTo(X + s, cy + s); x.moveTo(X + s, cy - s); x.lineTo(X - s, cy + s); x.stroke();
    }
  }
  function fitText(x, s, max) {
    if (x.measureText(s).width <= max) return s;
    var lo = 0, hi = s.length;
    while (lo < hi) { var mid = (lo + hi + 1) >> 1; if (x.measureText(s.slice(0, mid) + '…').width <= max) lo = mid; else hi = mid - 1; }
    return s.slice(0, lo).replace(/[\s,;:·-]+$/, '') + '…';
  }
  function spacing(x, v) { if ('letterSpacing' in x) x.letterSpacing = v; }
  function wDraw() {
    var L = W.L; if (!L || !W.ctx) return;
    var x = W.ctx, T = W.T, h = L.h, w = L.w;
    x.clearRect(0, 0, w, h);
    var act = W.hover >= 0 ? W.hover : S.sel, am = act >= 0 ? S.all[act] : null;
    if (am && am.vx == null) am = null;
    var gridTop = L.top - 8, gridBot = h - L.axis + 3;
    /* compressed era band */
    if (L.comp) { x.fillStyle = T.bg3; x.globalAlpha = 0.6; x.fillRect(L.x0 - 6, gridTop, L.pre + 12, gridBot - gridTop); x.globalAlpha = 1; }
    /* active row */
    if (am) { x.fillStyle = T.bg3; x.globalAlpha = T.dark ? 0.55 : 0.6; x.fillRect(0, L.top + am.row * L.rowH, w, L.rowH); x.globalAlpha = 1; }
    /* grid */
    x.lineWidth = 1;
    L.ticks.forEach(function (t) {
      x.strokeStyle = T.grid; x.globalAlpha = t.minor ? 0.55 : 1;
      var gx = Math.round(t.x) + 0.5; x.beginPath(); x.moveTo(gx, gridTop); x.lineTo(gx, gridBot); x.stroke();
    });
    x.globalAlpha = 1;
    /* rows: baselines and labels */
    x.font = '500 11px ' + T.mono; spacing(x, '0.9px');
    S.rows.forEach(function (d, r) {
      var yb = Math.round(L.top + (r + 1) * L.rowH - (L.mob ? 5 : 7)) + 0.5;
      x.strokeStyle = T.lineUi; x.globalAlpha = 0.55;
      x.beginPath(); x.moveTo(L.mob ? L.x0 - 8 : 12, yb); x.lineTo(L.x1 + 8, yb); x.stroke(); x.globalAlpha = 1;
      if (!L.mob) {
        var on = 0; S.byRow[r].forEach(function (m) { if (m.on) on++; });
        var tot = S.byRow[r].length, cnt = on === tot ? String(tot) : on + '/' + tot;
        x.textAlign = 'right'; x.textBaseline = 'alphabetic'; x.fillStyle = T.ink3;
        var cw = x.measureText(cnt).width; x.fillText(cnt, L.gutter - 4, yb - 6);
        var room = L.gutter - 18 - cw - 10, labs = FIELD_UP[d] || [String(d).toUpperCase()], lab = labs[labs.length - 1];
        for (var k = 0; k < labs.length; k++) if (x.measureText(labs[k]).width <= room) { lab = labs[k]; break; }
        x.textAlign = 'left'; x.fillStyle = on ? T.ink2 : T.ink3; x.fillText(fitText(x, lab, room), 14, yb - 6);
      }
    });
    spacing(x, '0px');
    /* axis */
    x.font = '400 11px ' + T.mono; x.fillStyle = T.ink3; x.textBaseline = 'alphabetic';
    var ay = h - L.axis + 19;
    if (L.comp) {
      x.textAlign = 'left'; x.fillText(String(L.t0), L.x0 - 2, ay);
      var bx = L.x0 + L.pre + L.gap / 2; x.strokeStyle = T.ink3;
      x.beginPath(); x.moveTo(bx - 4, h - L.axis + 8); x.lineTo(bx - 1, h - L.axis - 2); x.moveTo(bx + 1, h - L.axis + 8); x.lineTo(bx + 4, h - L.axis - 2); x.stroke();
    }
    x.textAlign = 'center';
    var lastR = -1e9, pill = null;
    if (am) { var pw0 = x.measureText(F0.fmtDate(am.date).toUpperCase()).width + 12, px0 = Math.min(w - 4 - pw0, Math.max(4, am.vx - pw0 / 2)); pill = [px0 - 4, px0 + pw0 + 4]; }
    L.ticks.forEach(function (t) {
      if (t.minor || !t.label) return;
      var tw = x.measureText(t.label).width;
      if (t.mid - tw / 2 < lastR + 6 || t.mid + tw / 2 > w - 2) return;
      if (pill && t.mid + tw / 2 > pill[0] && t.mid - tw / 2 < pill[1]) return;
      x.fillText(t.label, t.mid, ay); lastR = t.mid + tw / 2;
    });
    /* top line: compressed era and now (on wide screens the active entry's caption sits on the line below) */
    x.textAlign = 'left';
    var lay = L.mob ? L.top - 16 : 17;
    if (L.comp && !L.mob) x.fillText(L.t0 + '–' + (CUT - 1) + ', COMPRESSED', L.x0 - 2, lay);
    if (S.tNow <= L.t1 && S.tNow >= L.t0) {
      var nx = Math.round(xOf(S.tNow)) + 0.5;
      x.strokeStyle = T.ink3; x.globalAlpha = 0.8; x.beginPath(); x.moveTo(nx, lay + 6); x.lineTo(nx, gridBot); x.stroke(); x.globalAlpha = 1;
      x.textAlign = 'right'; x.fillStyle = T.ink2;
      x.fillText(L.mob ? 'NOW' : 'NOW · ' + F0.fmtDate(S.updated).toUpperCase(), nx + 4, lay);
    }
    /* the reading line of the auto-reader */
    if (W.glideX != null) {
      x.strokeStyle = T.digLine; x.globalAlpha = 0.7; x.lineWidth = 1.5;
      x.beginPath(); x.moveTo(Math.round(W.glideX) + 0.5, L.top - 8); x.lineTo(Math.round(W.glideX) + 0.5, gridBot); x.stroke(); x.globalAlpha = 1;
    }
    /* marks: outside the filters first, then the rest, then founding members' */
    var E = S.all, k2, m;
    for (k2 = 0; k2 < E.length; k2++) { m = E[k2]; if (m.vx != null && !m.on && m !== am) drawMark(x, m, 0); }
    for (k2 = 0; k2 < E.length; k2++) { m = E[k2]; if (m.vx != null && m.on && !m.foundation0 && m !== am) drawMark(x, m, 1); }
    for (k2 = 0; k2 < E.length; k2++) { m = E[k2]; if (m.vx != null && m.on && m.foundation0 && m !== am) drawMark(x, m, 1); }
    if (L.mob) wMobLabels(x);
    if (am) wDrawActive(x, am);
    x.globalAlpha = 1;
  }
  function wMobLabels(x) {
    var L = W.L, T = W.T;
    x.font = '500 11px ' + T.mono; spacing(x, '0.6px'); x.textAlign = 'left'; x.textBaseline = 'alphabetic';
    S.rows.forEach(function (d, r) {
      var y = L.top + r * L.rowH + 13, labs = FIELD_UP[d] || [String(d).toUpperCase()], lab = labs[0];
      var on = 0; S.byRow[r].forEach(function (m) { if (m.on) on++; });
      var tot = S.byRow[r].length, cnt = on === tot ? String(tot) : on + '/' + tot;
      var lw = x.measureText(lab).width, cw = x.measureText(cnt).width;
      x.fillStyle = T.bg2; x.globalAlpha = 0.9; x.fillRect(L.x0 - 6, y - 11, lw + cw + 20, 15); x.globalAlpha = 1;
      x.fillStyle = on ? T.ink2 : T.ink3; x.fillText(lab, L.x0, y);
      x.fillStyle = T.ink3; x.fillText(cnt, L.x0 + lw + 8, y);
    });
    spacing(x, '0px');
  }
  function wDrawActive(x, m) {
    var L = W.L, T = W.T, h = L.h, X = m.vx;
    x.strokeStyle = T.ink; x.globalAlpha = 0.38; x.lineWidth = 1;
    x.beginPath(); x.moveTo(Math.round(X) + 0.5, L.top - 8); x.lineTo(Math.round(X) + 0.5, h - L.axis + 3); x.stroke(); x.globalAlpha = 1;
    drawMark(x, m, m.on ? 2 : 2);
    var top = m.yb - m.len, rr = m.r * 1.3 + (m.foundation0 ? 6.8 : 4.6);
    x.strokeStyle = T.focus; x.lineWidth = W.kbd ? 2.4 : 1.8;
    x.beginPath(); x.arc(X, top, rr, 0, Math.PI * 2); x.stroke();
    /* date pill on the axis */
    x.font = '500 11px ' + T.mono;
    var ds = F0.fmtDate(m.date).toUpperCase(), dw = x.measureText(ds).width + 12;
    var dx = Math.min(L.w - 4 - dw, Math.max(4, X - dw / 2));
    x.fillStyle = T.ink; x.fillRect(dx, h - L.axis + 5, dw, 19);
    x.fillStyle = T.bg2; x.textAlign = 'left'; x.textBaseline = 'alphabetic'; x.fillText(ds, dx + 6, h - L.axis + 18.5);
    /* the title, printed in the band above the rows and joined to its mark by a leader, so no mark is
       covered (wide screens only; on phones the entry sits right below the wall) */
    if (L.mob) return;
    var fs = 15, ty = L.top - 15, ly = ty - 5, gapX = 9, lo = 12, hi = L.w - 10;
    x.font = 'italic 400 ' + fs + 'px ' + T.serif;
    var full = x.measureText(m.title).width, roomR = hi - (X + gapX), roomL = (X - gapX) - lo;
    var right = full <= roomR || (full > roomL && roomR >= roomL);
    var s = fitText(x, m.title, Math.min(620, right ? roomR : roomL)), tw = x.measureText(s).width;
    var tx = right ? X + gapX : X - gapX - tw;
    /* the leader: from the caption down to the top of the mark's focus ring */
    x.strokeStyle = T.ink; x.globalAlpha = 0.55; x.lineWidth = 1;
    var lx = Math.round(X) + 0.5;
    x.beginPath(); x.moveTo(right ? tx - 3 : tx + tw + 3, ly + 0.5); x.lineTo(lx, ly + 0.5); x.lineTo(lx, top - rr); x.stroke(); x.globalAlpha = 1;
    /* a thin halo in the stage colour lets the now line pass behind the words */
    x.textAlign = 'left'; x.textBaseline = 'alphabetic';
    x.lineJoin = 'round'; x.lineWidth = 5; x.strokeStyle = T.bg2; x.strokeText(s, tx, ty);
    x.fillStyle = T.ink; x.fillText(s, tx, ty);
  }

  /* ================= the Encyclopedia entry ================= */
  var shownKey = '';
  var SRC_LABEL = { default: 'Highest significance', select: 'Selected', hover: 'Preview', auto: 'Auto-reading', link: 'From your link' };
  function host(u) { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } }
  function showEntry(i, src, force) {
    var el = $('#entry'); if (i < 0 || !S.all[i]) return;
    var key = i + '|' + src + '|' + (S.all[i].on ? 1 : 0);
    if (!force && key === shownKey) return;
    var same = shownKey.split('|')[0] === String(i);
    shownKey = key;
    var m = S.all[i], N = S.all.length, h = '';
    h += '<div class="e-top"><span class="e-k">Encyclopedia <i>//</i> ' + pad3(i + 1) + ' of ' + N + '</span><span class="e-src' + (src === 'auto' ? ' auto' : '') + '">' + esc(SRC_LABEL[src] || '') + '</span></div>';
    h += '<p class="e-field">' + esc(fieldName(m.domain)) + (m.subfield ? ' · ' + esc(m.subfield) : '') + '</p>';
    h += '<h3 class="e-title" id="entry-title">' + esc(m.title) + '</h3>';
    h += '<p class="e-date"><time datetime="' + esc(m.date) + '">' + esc(F0.fmtDate(m.date)) + '</time> · ' + esc(BASIS[m.date_basis] || m.date_basis) + '</p>';
    h += '<div class="badges">' +
      '<span class="badge n">' + dialSVG(m.f) + 'AI ' + esc(ROLE_NAME[m.ai_role] || m.ai_role) + '</span>' +
      '<span class="badge ' + (EV_CLS[m.evidence] || 'n') + '">' + ladderHTML(m.rung) + esc(EV_NAME[m.evidence] || m.evidence) + '</span>' +
      '<span class="badge n" title="Significance is an editorial judgement">' + sigDots(m.significance) + 'Significance ' + m.significance + '/5</span>' +
      (m.contested ? '<span class="badge x"><span class="xm" aria-hidden="true">×</span>Contested</span>' : '') +
      (m.foundation0 ? '<span class="badge hb"><i class="hl" aria-hidden="true"></i>Members’ work</span>' : '') + '</div>';
    h += '<p class="e-role"><b>What the AI did:</b> ' + esc(ROLE_TXT[m.ai_role] || '') + '</p>';
    h += '<p class="e-sum">' + esc(m.summary) + '</p>';
    if (m.before_after) {
      var ba = m.before_after;
      h += '<div class="e-ba"><p class="e-h">Before → after</p><p class="e-metric">' + esc(ba.metric) + '</p><div class="e-ba-row"><div class="b"><span>Before</span>' + esc(ba.before) + '</div><span class="arr" aria-hidden="true">→</span><div class="a"><span>After</span>' + esc(ba.after) + '</div></div></div>';
    }
    h += '<p class="e-h">Why it matters</p><p class="e-why">' + esc(m.why_it_matters) + '</p>';
    var li = function (a) { return a && a.length ? '<ul>' + a.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul>' : '<span>Not stated</span>'; };
    h += '<dl class="e-dl"><dt>AI systems</dt><dd>' + li(m.ai_systems) + '</dd><dt>People and organisations</dt><dd>' + li(m.organizations) + '</dd></dl>';
    if (m.contested) h += '<div class="e-note x"><p class="e-h"><span aria-hidden="true">×</span> Contested</p><p>' + esc(m.contested_note) + '</p></div>';
    else if (m.contested_note) h += '<div class="e-note"><p class="e-h">Caveats</p><p>' + esc(m.contested_note) + '</p></div>';
    if (m.foundation0) h += '<div class="e-note mem"><p class="e-h"><i class="hl" aria-hidden="true"></i>Who did what</p><p>' + esc(m.foundation0_note || CREDIT[m.id] || CREDIT_DEFAULT) + '</p></div>';
    h += '<p class="e-h">Sources</p><ol class="e-srcs">' + (m.sources || []).map(function (s) {
      return '<li><a href="' + esc(s.url) + '" rel="noopener">' + esc(s.label) + '</a><span class="dom">' + esc(host(s.url)) + '</span></li>';
    }).join('') + '</ol>';
    var p = W.pos[i], prev = p != null && p > 0 ? W.vis[p - 1] : null, next = p != null && p < W.vis.length - 1 ? W.vis[p + 1] : null;
    h += '<div class="e-foot">' + (m.page ? '<a class="more" href="../' + esc(String(m.page).replace(/^\/+/, '')) + '">Read our page on this</a>' : '') +
      '<button type="button" class="tbtn" data-copy="' + esc(m.id) + '">Copy link</button>' +
      '<button type="button" class="tbtn" data-step="' + (prev ? prev.i : '') + '"' + (prev ? '' : ' disabled') + ' aria-label="Earlier entry">← Earlier</button>' +
      '<button type="button" class="tbtn" data-step="' + (next ? next.i : '') + '"' + (next ? '' : ' disabled') + ' aria-label="Later entry">Later →</button></div>';
    if (!m.on) h += '<p class="e-out">This entry is outside your current filters.</p>';
    el.innerHTML = h;
    if (!same) el.scrollTop = 0;
    entryMore();
  }
  /* the entry scrolls inside a fixed-height panel beside the wall: fade its foot and show a hint while more is below */
  function entryMore() {
    var el = $('#entry'), more = el.scrollHeight - el.scrollTop - el.clientHeight > 8;
    if (more !== el.classList.contains('has-more')) el.classList.toggle('has-more', more);
  }
  function entryInit() {
    var el = $('#entry');
    el.addEventListener('scroll', entryMore, { passive: true });
    window.addEventListener('resize', entryMore);
    $('#e-more').addEventListener('click', function () { el.scrollBy({ top: Math.round(el.clientHeight * 0.7), behavior: F0.motion() ? 'smooth' : 'auto' }); });
    el.addEventListener('click', function (e) {
      var c = e.target.closest('[data-copy]'), st = e.target.closest('[data-step]');
      if (c) {
        var url = location.origin + location.pathname + '#' + c.getAttribute('data-copy'), done = function (ok) { c.textContent = ok ? 'Copied' : 'Copy failed'; setTimeout(function () { c.textContent = 'Copy link'; }, 1800); };
        try { navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); }); } catch (err) { done(false); }
      }
      if (st && !st.disabled && st.getAttribute('data-step') !== '') {
        var lab = st.getAttribute('aria-label');
        select(+st.getAttribute('data-step'), 'select', true);
        var again = $$('#entry [data-step]').filter(function (x) { return x.getAttribute('aria-label') === lab; })[0];
        (again && !again.disabled ? again : el).focus({ preventScroll: true });
      }
    });
  }

  /* ================= auto-read (off by default; user starts it) ================= */
  var AR = { on: false, timer: 0, g: null, job: null, vis: false };
  function arInit() {
    var btn = $('#auto-btn');
    AR.job = F0.loop(function (now) {
      var g = AR.g; if (!g) { AR.job.stop(); return; }
      var q = Math.min(1, (now - g.t0) / g.dur), e = q < 0.5 ? 4 * q * q * q : 1 - Math.pow(-2 * q + 2, 3) / 2;
      W.glideX = g.x0 + (g.x1 - g.x0) * e; wDraw();
      if (q >= 1) arLand();
    });
    btn.addEventListener('click', function () { if (AR.on) arStop(); else { AR.on = true; btn.setAttribute('aria-pressed', 'true'); arSchedule(250); } });
    F0.onMotion(function (on) { if (!on && AR.g) arLand(); });
    F0.whenVisible($('#wall-stage'), function () { AR.vis = true; }, function () { AR.vis = false; });
  }
  function arLand() { var g = AR.g; AR.g = null; W.glideX = null; AR.job.stop(); if (g) select(g.to, 'auto', false); arSchedule(3600); }
  function arSchedule(ms) { clearTimeout(AR.timer); AR.timer = setTimeout(arStep, ms); }
  function arStop() {
    if (!AR.on && !AR.g) return;
    AR.on = false; clearTimeout(AR.timer); AR.g = null; W.glideX = null; if (AR.job) AR.job.stop();
    $('#auto-btn').setAttribute('aria-pressed', 'false'); wDraw();
  }
  function arStep() {
    if (!AR.on) return;
    if (!AR.vis || D.hidden || F0.idle() || W.hover >= 0 || W.kbd || !W.vis.length) { arSchedule(1500); return; }
    var p = W.pos[S.sel], to = W.vis[p == null ? 0 : (p + 1) % W.vis.length], from = S.all[S.sel];
    if (F0.motion() && from && from.vx != null && to.vx != null) {
      AR.g = { to: to.i, t0: performance.now(), dur: Math.min(1100, 420 + Math.abs(to.vx - from.vx) * 1.2), x0: from.vx, x1: to.vx };
      AR.job.start();
    } else { select(to.i, 'auto', false); arSchedule(3600); }
  }

  /* ================= the table ================= */
  var TB = { k: 'date', dir: -1 };
  var FIRST_DIR = { date: -1, title: 1, field: 1, role: -1, ev: -1, sig: -1 };
  function cmp(a, b) {
    var d = 0, k = TB.k;
    if (k === 'date') d = a.t - b.t;
    else if (k === 'title') d = a.title.localeCompare(b.title);
    else if (k === 'field') d = a.row - b.row;
    else if (k === 'role') d = ROLES.indexOf(a.ai_role) - ROLES.indexOf(b.ai_role);
    else if (k === 'ev') d = (a.rung - b.rung) || (EVS.indexOf(b.evidence) - EVS.indexOf(a.evidence));
    else if (k === 'sig') d = a.significance - b.significance;
    d *= TB.dir;
    return d || (b.t - a.t) || (a.id < b.id ? -1 : 1);
  }
  function tInit() {
    $$('#ltbl thead [data-sort]').forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-sort');
        if (TB.k === k) TB.dir = -TB.dir; else { TB.k = k; TB.dir = FIRST_DIR[k]; }
        tRender();
      });
    });
    $('#ltbody').addEventListener('click', function (e) {
      var a = e.target.closest('a[data-pick]'); if (!a) return;
      e.preventDefault();
      var m = S.byId[a.getAttribute('data-pick')]; if (m) goToEntry(m.i, e.detail === 0 ? 'kbd' : 'ptr');
    });
  }
  function tRender() {
    var rows = S.shown.slice().sort(cmp), n = rows.length;
    var ORDERTXT = { date: ['oldest first', 'newest first'], title: ['A to Z', 'Z to A'], field: ['by field', 'by field, reversed'], role: ['instrument first', 'originator first'], ev: ['weakest evidence first', 'strongest evidence first'], sig: ['least significant first', 'most significant first'] };
    var ot = ORDERTXT[TB.k][TB.dir > 0 ? 0 : 1];
    $('#l-count').innerHTML = '<b>' + n + '</b> ' + (n === 1 ? 'milestone' : 'milestones') + ', ' + esc(ot);
    $('#l-cap').textContent = n + ' ledger milestones, ' + ot;
    $$('#ltbl thead th').forEach(function (th) {
      var b = th.querySelector('[data-sort]');
      if (b && b.getAttribute('data-sort') === TB.k) th.setAttribute('aria-sort', TB.dir > 0 ? 'ascending' : 'descending'); else th.removeAttribute('aria-sort');
    });
    $('#l-empty').hidden = n > 0;
    var html = rows.map(function (m) {
      var role = '<span class="gl"><i class="cdial" style="--f:' + (m.f * 100) + '%" aria-hidden="true"></i>' + esc(ROLE_NAME[m.ai_role]) + '</span>';
      var ev = '<span class="gl"><span style="color:var(' + EV_TOK[m.evidence] + ')">' + ladderHTML(m.rung) + '</span>' + esc(EV_SHORT[m.evidence]) + '</span>';
      var flags = (m.contested ? '<span class="xmark" aria-hidden="true" title="Contested">×</span><span class="sr-only">(contested)</span>' : '') +
        (m.foundation0 ? '<i class="hl" aria-hidden="true" title="Members’ work"></i><span class="sr-only">(members’ work)</span>' : '');
      return '<tr data-i="' + m.i + '"' + (m.i === S.sel ? ' class="sel"' : '') + '>' +
        '<td class="c-date"><time datetime="' + esc(m.date) + '">' + esc(F0.fmtDate(m.date)) + '</time></td>' +
        '<td class="c-title"><a href="./#' + encodeURIComponent(m.id) + '" data-pick="' + esc(m.id) + '">' + esc(m.title) + '</a>' + (flags ? '<span class="t-flags">' + flags + '</span>' : '') +
        '<span class="t-sub">' + esc(m.subfield || '') + '</span>' +
        '<span class="m-meta"><span>' + esc(FIELD_SHORT[m.domain] || m.domain) + '</span>' + role + ev + '</span></td>' +
        '<td class="c-field">' + esc(FIELD_SHORT[m.domain] || m.domain) + '</td>' +
        '<td class="c-role">' + role + '</td><td class="c-ev">' + ev + '</td>' +
        '<td class="c-sig">' + m.significance + '</td></tr>';
    });
    /* first rows now, the rest on the next frame: filtering stays responsive with hundreds of entries */
    var tb = $('#ltbody'), FIRST = 60, token = ++tRender.token;
    tb.innerHTML = html.slice(0, FIRST).join('');
    if (html.length > FIRST) requestAnimationFrame(function () { if (token === tRender.token) { tb.insertAdjacentHTML('beforeend', html.slice(FIRST).join('')); tMarkSel(); } });
  }
  tRender.token = 0;
  function tMarkSel() {
    $$('#ltbody tr.sel').forEach(function (tr) { tr.classList.remove('sel'); });
    var tr = $('#ltbody tr[data-i="' + S.sel + '"]'); if (tr) tr.classList.add('sel');
  }

  /* ================= CSV, made in the browser ================= */
  function csvCell(v) {
    var s = v == null ? '' : String(v);
    if (typeof v === 'string' && /^[=+\-@\t\r]/.test(s)) s = "'" + s;
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function downloadCSV(list, name) {
    var base = location.origin + location.pathname;
    var cols = ['id', 'date', 'date_basis', 'title', 'domain', 'subfield', 'ai_role', 'evidence', 'contested', 'significance', 'foundation0', 'summary',
      'why_it_matters', 'before_after_metric', 'before', 'after', 'ai_systems', 'organizations', 'contested_note', 'sources', 'page', 'ledger_link'];
    var lines = [cols.join(',')];
    list.forEach(function (m) {
      var ba = m.before_after || {};
      lines.push([m.id, m.date, m.date_basis, m.title, m.domain, m.subfield, m.ai_role, m.evidence, m.contested, m.significance, m.foundation0, m.summary,
        m.why_it_matters, ba.metric || '', ba.before || '', ba.after || '', (m.ai_systems || []).join('; '), (m.organizations || []).join('; '), m.contested_note || '',
        (m.sources || []).map(function (s) { return s.label + ' <' + s.url + '>'; }).join('; '), m.page || '', base + '#' + m.id].map(csvCell).join(','));
    });
    var blob = new Blob(['﻿' + lines.join('\r\n') + '\r\n'], { type: 'text/csv;charset=utf-8' });
    var a = D.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    D.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
  }
  function csvInit() {
    $$('[data-csv]').forEach(function (b) {
      b.addEventListener('click', function () {
        var view = b.getAttribute('data-csv') === 'view';
        var list = view ? S.shown.slice().sort(cmp) : S.all.slice();
        downloadCSV(list, 'foundation0-ledger-' + S.updated + (view ? '-view-' + list.length : '') + '.csv');
      });
    });
  }

  /* ================= charts (100% stacked bars, one axis, SVG) ================= */
  function svgEl(tag, attrs, parent) {
    var e = D.createElementNS(SVGNS, tag);
    for (var k in attrs) { if (k === 'text') e.textContent = attrs[k]; else e.setAttribute(k, attrs[k]); }
    if (parent) parent.appendChild(e); return e;
  }
  /* the shared periods (F0.rolePeriods), so Home and the Ledger group the years the same way */
  function periods(list) {
    return F0.rolePeriods(list, { yMin: S.yMin, yMax: S.yMax, nowYear: S.nowYear });
  }
  var ROLE_FILL = { instrument: 'var(--mark-bio)', collaborator: 'var(--mark-mid)', originator: 'var(--mark-dig)' };
  var EVK = [5, 4, 3, 2, 1], EV_FILL = { 5: 'var(--ev-5)', 4: 'var(--ev-4)', 3: 'var(--ev-3)', 2: 'var(--ev-2)', 1: 'var(--ev-1)' };
  var EV_RN = { 5: 'Formally verified', 4: 'Independently replicated', 3: 'Peer reviewed or deployed', 2: 'Preprint', 1: 'Claimed' };
  var evBy = 'period';

  var CW = {};
  function stackChart(hostEl, spec) {
    hostEl.innerHTML = '';
    var cw = CW[hostEl.id] || (CW[hostEl.id] = Math.round(hostEl.getBoundingClientRect().width)); /* cached: no forced layout per update */
    var Wd = Math.max(260, cw), small = Wd < 520;
    var labW = small ? spec.labW[1] : spec.labW[0], colW = small ? 50 : 82, nW = small ? 30 : 40, rowH = small ? 18 : 20, gap = small ? 12 : 14, top = 24;
    var x0 = labW, x1 = Wd - (2 * colW + nW + (small ? 6 : 12));
    var H = top + spec.rows.length * (rowH + gap) - gap + 26;
    var svg = svgEl('svg', { viewBox: '0 0 ' + Wd + ' ' + H, width: Wd, height: H, class: 'ch-svg', role: 'group', 'aria-label': spec.aria }, hostEl);
    var X = function (f) { return x0 + (x1 - x0) * f; };
    var c1 = x1 + (small ? 6 : 12) + colW, c2 = c1 + colW, cn = c2 + nW;
    var head = function (x, t) { svgEl('text', { x: x, y: 12, 'text-anchor': 'end', 'font-size': small ? 10.5 : 11, style: 'fill:var(--ink-3);letter-spacing:.06em', text: t }, svg); };
    head(c1, small ? spec.cols[0].s : spec.cols[0].l); head(c2, small ? spec.cols[1].s : spec.cols[1].l); head(cn, 'N');
    [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
      svgEl('line', { x1: X(f), x2: X(f), y1: top - 6, y2: H - 20, style: 'stroke:var(--grid)', 'stroke-width': 1 }, svg);
      if (!small || f % 0.5 === 0) svgEl('text', { x: X(f), y: H - 5, 'text-anchor': f === 0 ? 'start' : f === 1 ? 'end' : 'middle', 'font-size': 11, style: 'fill:var(--ink-3)', text: Math.round(f * 100) + '%' }, svg);
    });
    var groups = [];
    spec.rows.forEach(function (row, r) {
      var y = top + r * (rowH + gap), few = row.n > 0 && row.n < 10;
      var g = svgEl('g', { class: 'row', tabindex: r === 0 ? 0 : -1, role: 'img', 'aria-label': spec.rowAria(row) }, svg);
      groups.push(g);
      svgEl('rect', { class: 'rowbg', x: 0, y: y - 5, width: Wd, height: rowH + 10, fill: 'transparent', rx: 2 }, g);
      svgEl('text', { x: 0, y: y + rowH / 2 + 4, 'font-size': small ? 11 : 12, style: 'fill:' + (row.n ? 'var(--ink-2)' : 'var(--ink-3)'), text: row.label + (few ? '*' : '') }, g);
      if (!row.n) {
        svgEl('rect', { x: X(0), y: y + rowH / 2 - 0.5, width: X(1) - X(0), height: 1, style: 'fill:var(--line-ui)' }, g);
      } else {
        var acc = 0;
        spec.keys.forEach(function (k) {
          var s = (row.c[k] || 0) / row.n; if (s <= 0) return;
          var a = X(acc) + (acc > 0 ? 1 : 0), e = X(acc + s) - (acc + s < 0.9999 ? 1 : 0), w = Math.max(0.6, e - a), isEnd = acc + s >= 0.9999, rr = Math.min(4, w / 2);
          var d = isEnd ? 'M' + a + ' ' + y + 'H' + (a + w - rr) + 'Q' + (a + w) + ' ' + y + ' ' + (a + w) + ' ' + (y + rr) + 'V' + (y + rowH - rr) + 'Q' + (a + w) + ' ' + (y + rowH) + ' ' + (a + w - rr) + ' ' + (y + rowH) + 'H' + a + 'Z'
            : 'M' + a + ' ' + y + 'H' + (a + w) + 'V' + (y + rowH) + 'H' + a + 'Z';
          var seg = svgEl('path', { d: d, class: 'seg-r', style: 'fill:' + spec.fill[k] + (few ? ';opacity:.45' : '') }, g);
          seg.addEventListener('pointermove', function (ev) { seg.style.opacity = few ? '.6' : '.82'; F0.tip.show(spec.tip(row, k), ev.clientX, ev.clientY); });
          seg.addEventListener('pointerleave', function () { seg.style.opacity = few ? '.45' : ''; F0.tip.hide(); });
          acc += s;
        });
      }
      var v1 = row.n ? pct(spec.cols[0].v(row), row.n) + '%' : '–', v2 = row.n ? pct(spec.cols[1].v(row), row.n) + '%' : '–';
      svgEl('text', { x: c1, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12.5, style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: v1 }, g);
      svgEl('text', { x: c2, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12.5, style: 'fill:var(--ink);font-variant-numeric:tabular-nums', text: v2 }, g);
      svgEl('text', { x: cn, y: y + rowH / 2 + 4, 'text-anchor': 'end', 'font-size': 12, style: 'fill:var(--ink-3);font-variant-numeric:tabular-nums', text: row.n }, g);
      g.addEventListener('focus', function () { var bb = g.getBoundingClientRect(); F0.tip.show(spec.tip(row, null), bb.left + bb.width * 0.45, bb.bottom); });
      g.addEventListener('blur', function () { F0.tip.hide(); });
      g.addEventListener('keydown', function (e) {
        var j = e.key === 'ArrowDown' ? r + 1 : e.key === 'ArrowUp' ? r - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? groups.length - 1 : -2;
        if (j === -2) return; e.preventDefault();
        j = Math.max(0, Math.min(groups.length - 1, j));
        groups.forEach(function (q, qi) { q.setAttribute('tabindex', qi === j ? 0 : -1); });
        groups[j].focus();
      });
    });
  }
  function tipRows(row, keys, fill, name, focus) {
    return keys.map(function (k) {
      var strong = !focus || focus === k;
      return '<div class="tip-row" style="opacity:' + (strong ? 1 : 0.62) + '"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="6.5" width="14" height="3" rx="1" style="fill:' + fill[k] + '"/></svg><span class="tip-v">' + pct(row.c[k] || 0, row.n) + '%</span><span>' + esc(name[k].toUpperCase()) + ' · ' + (row.c[k] || 0) + ' of ' + row.n + '</span></div>';
    }).join('');
  }
  function tableHTML(caption, heads, rows) {
    return '<table class="tbl"><caption>' + esc(caption) + '</caption><thead><tr>' + heads.map(function (h, i) { return '<th scope="col"' + (i ? ' class="n"' : '') + '>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr>' + r.map(function (v, i) { return i ? '<td class="n">' + esc(v) + '</td>' : '<th scope="row">' + esc(v) + '</th>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>';
  }
  function setInsight(key, t, p) { $('[data-insight="' + key + '-t"]').textContent = t; $('[data-insight="' + key + '-p"]').textContent = p; }
  function viewNote() { return filtersActive() ? ' in this filtered view' : ''; }

  function roleChart() {
    var P = periods(S.shown);
    P.forEach(function (p) { p.c = {}; ROLES.forEach(function (k) { p.c[k] = 0; }); p.items.forEach(function (m) { p.c[m.ai_role]++; }); });
    var rowsLab = function (p) { return p.label + (p.now ? ' (to ' + F0.fmtDate(S.updated) + ')' : ''); };
    stackChart($('#ch-role-host'), {
      rows: P, keys: ROLES, fill: ROLE_FILL, labW: [86, 66],
      cols: [{ l: 'INSTRUMENT', s: 'INSTR', v: function (r) { return r.c.instrument; } }, { l: 'ORIGINATOR', s: 'ORIG', v: function (r) { return r.c.originator; } }],
      aria: 'Share of milestones by AI role, per period. Focus a row and use the up and down arrows to read each period.',
      rowAria: function (p) { return p.n ? rowsLab(p) + ': instrument ' + pct(p.c.instrument, p.n) + '%, collaborator ' + pct(p.c.collaborator, p.n) + '%, originator ' + pct(p.c.originator, p.n) + '%, of ' + p.n + ' milestones' : rowsLab(p) + ': no milestones in this view'; },
      tip: function (p, k) { return '<div class="tip-k">' + esc(rowsLab(p)) + ' · ' + p.n + (p.n === 1 ? ' milestone' : ' milestones') + '</div><div class="tip-rows">' + (p.n ? tipRows(p, ROLES.slice().reverse(), ROLE_FILL, ROLE_NAME, k) : '<div class="tip-row">No milestones in this view</div>') + '</div>'; }
    });
    var ins = F0.roleInsight(P, { note: viewNote() });   /* one headline and sentence, shared with Home */
    setInsight('role', ins.h, ins.p);
    var foot = $('#ch-role-foot'), faint = P.some(function (p) { return p.n > 0 && p.n < 10; });
    foot.innerHTML = 'Source: <a href="../data/ledger.json">data/ledger.json</a>, ' + S.shown.length + ' of ' + S.all.length + ' milestones' + (filtersActive() ? ' (filtered)' : '') + '.' + (faint ? ' * fewer than 10 milestones: drawn faint.' : '');
    $('#ch-role-table').innerHTML = tableHTML('Milestones by AI role and period' + viewNote(), ['Period', 'Milestones', 'Instrument', 'Collaborator', 'Originator'],
      P.map(function (p) { return [rowsLab(p), String(p.n)].concat(ROLES.map(function (k) { return p.c[k] + ' (' + pct(p.c[k], p.n) + '%)'; })); }));
  }
  function evChart() {
    var groups;
    if (evBy === 'period') groups = periods(S.shown).map(function (p) { return { label: p.label, full: p.label + (p.now ? ' (to ' + F0.fmtDate(S.updated) + ')' : ''), items: p.items, n: p.n, now: p.now, a: p.a, b: p.b }; });
    else groups = S.rows.map(function (d, r) { var it = S.shown.filter(function (m) { return m.domain === d; }); return { label: FIELD_SHORT[d] || d, full: fieldName(d), items: it, n: it.length, d: d }; });
    groups.forEach(function (g) { g.c = {}; EVK.forEach(function (k) { g.c[k] = 0; }); g.x = 0; g.items.forEach(function (m) { g.c[m.rung]++; if (m.contested) g.x++; }); });
    if (evBy === 'field') groups.sort(function (a, b) { return (b.n ? (b.c[5] + b.c[4] + b.c[3]) / b.n : -1) - (a.n ? (a.c[5] + a.c[4] + a.c[3]) / a.n : -1) || b.n - a.n; });
    var low = function (g) { return g.c[1] + g.c[2]; };
    stackChart($('#ch-ev-host'), {
      rows: groups, keys: EVK, fill: EV_FILL, labW: evBy === 'field' ? [118, 92] : [86, 66],
      cols: [{ l: 'VERIFIED', s: 'VERIF', v: function (g) { return g.c[5]; } }, { l: 'UNREVIEWED', s: 'UNREV', v: low }],
      aria: 'Share of milestones at each rung of the evidence ladder, ' + (evBy === 'field' ? 'per field' : 'per period') + '. Focus a row and use the up and down arrows to read each one.',
      rowAria: function (g) { return g.n ? g.full + ': ' + EVK.map(function (k) { return EV_RN[k].toLowerCase() + ' ' + pct(g.c[k], g.n) + '%'; }).join(', ') + ', of ' + g.n + ' milestones' : g.full + ': no milestones in this view'; },
      tip: function (g, k) { return '<div class="tip-k">' + esc(g.full) + ' · ' + g.n + (g.n === 1 ? ' milestone' : ' milestones') + (g.x ? ' · ' + g.x + ' contested' : '') + '</div><div class="tip-rows">' + (g.n ? tipRows(g, EVK, EV_FILL, EV_RN, k) : '<div class="tip-row">No milestones in this view</div>') + '</div>'; }
    });
    var ok = groups.filter(function (g) { return g.n >= 10; });
    if (evBy === 'period' && ok.length >= 2) {
      var last = ok[ok.length - 1], prior = ok.slice(0, -1), pn = 0, p3 = 0, p5 = 0, plo = 0;
      prior.forEach(function (g) { pn += g.n; p3 += g.c[3] + g.c[4]; p5 += g.c[5]; plo += low(g); });
      var v5 = pct(last.c[5], last.n), lo = pct(low(last), last.n), mid = pct(p3, pn), mid1 = pct(last.c[3] + last.c[4], last.n);
      var v5p = pct(p5, pn), lop = pct(plo, pn), ll = last.now ? last.label + ' so far' : last.label;
      var from = isFinite(prior[0].a) ? prior[0].a : S.yMin, to = prior[prior.length - 1].b;
      var span = from === to ? String(from) : from + '–' + to;
      /* both ends grew at the expense of the middle: say so; otherwise a plain title */
      var t = v5 > v5p && lo > lop ? 'In ' + ll + ', more results are machine-checked, and more are not yet checked at all.' : 'How sure the record is, period by period.';
      setInsight('ev', t, 'In ' + ll + ', ' + v5 + '% of milestones' + viewNote() + ' were formally verified (' + v5p + '% across ' + span + ') and ' + lo + '% were still only preprints or claims (' + lop + '% before). The share peer reviewed, deployed or replicated went from ' + mid + '% to ' + mid1 + '%.');
    } else if (evBy === 'field' && ok.length >= 2) {
      var tot5 = 0; groups.forEach(function (g) { tot5 += g.c[5]; });
      var top5 = groups.slice().sort(function (a, b) { return b.c[5] - a.c[5]; })[0];
      var lowF = ok.slice().sort(function (a, b) { return low(b) / b.n - low(a) / a.n; })[0];
      if (tot5 >= 3 && top5.c[5] * 2 > tot5) setInsight('ev', top5.full + ' holds most of the machine-checked proofs.', top5.full + ' has ' + top5.c[5] + ' of the ' + tot5 + ' formally verified milestones' + viewNote() + '. ' + (lowF === top5 ? 'It also has' : lowF.full + ' has') + ' the largest share still unreviewed: ' + pct(low(lowF), lowF.n) + '% are preprints or claims.');
      else setInsight('ev', 'How sure the record is, field by field.', 'Fields sorted by the share of milestones that are peer reviewed, deployed, replicated or formally verified' + viewNote() + '.');
    } else setInsight('ev', 'How sure the record is.', 'Too few milestones' + viewNote() + ' to compare; the numbers are in the table below the chart.');
    var cont = S.shown.filter(function (m) { return m.contested; }).length;
    var faintEv = groups.some(function (g) { return g.n > 0 && g.n < 10; });
    $('#ch-ev-foot').innerHTML = 'Source: <a href="../data/ledger.json">data/ledger.json</a>, ' + S.shown.length + ' of ' + S.all.length + ' milestones' + (filtersActive() ? ' (filtered)' : '') +
      '. Unreviewed = preprint or claimed. ' + cont + ' contested ' + (cont === 1 ? 'milestone is' : 'milestones are') + ' counted at their rung.' + (faintEv ? ' * fewer than 10: drawn faint.' : '');
    $('#ch-ev-table').innerHTML = tableHTML('Milestones by evidence rung, ' + (evBy === 'field' ? 'per field' : 'per period') + viewNote(), [evBy === 'field' ? 'Field' : 'Period', 'Milestones'].concat(EVK.map(function (k) { return k + ' ' + EV_RN[k]; })).concat(['Contested']),
      groups.map(function (g) { return [g.full, String(g.n)].concat(EVK.map(function (k) { return g.c[k] + ' (' + pct(g.c[k], g.n) + '%)'; })).concat([String(g.x)]); }));
  }
  function chartsRender() { roleChart(); evChart(); }
  function chartsInit() {
    $$('#ev-by [data-by]').forEach(function (b) {
      b.addEventListener('click', function () {
        evBy = b.getAttribute('data-by');
        $$('#ev-by [data-by]').forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        evChart();
      });
    });
    if ('ResizeObserver' in window) {
      var ro = new ResizeObserver(function (es) {
        var changed = false;
        es.forEach(function (e) { var w = Math.round(e.contentRect.width); if (w && w !== CW[e.target.id]) { CW[e.target.id] = w; changed = true; } });
        if (changed && S.all.length && F) chartsRender();
      });
      ro.observe($('#ch-role-host')); ro.observe($('#ch-ev-host'));
    }
  }

  /* ================= how to read it: a closable panel, open on a first visit ================= */
  var HOWTO_KEY = 'f0-ledger-howto';
  function inHowto(id) { var d = $('#reading'), t = id && D.getElementById(id); return d && t && d.contains(t) ? t : null; }
  function howtoInit() {
    var d = $('#reading'); if (!d) return;
    var st = null; try { st = localStorage.getItem(HOWTO_KEY); } catch (e) { /* storage blocked: stay open */ }
    var h = ''; try { h = decodeURIComponent(location.hash.slice(1)); } catch (e) { h = ''; }
    if (st === 'closed' && !inHowto(h)) d.open = false;
    d.addEventListener('toggle', function () { try { localStorage.setItem(HOWTO_KEY, d.open ? 'open' : 'closed'); } catch (e) { /* ignore */ } });
    /* links to a card ("?" notes, filter panels, the jump row) open the panel first */
    D.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#read"]'); if (!a) return;
      var t = inHowto(a.getAttribute('href').slice(1)); if (!t) return;
      e.preventDefault();
      var pop = a.closest('details.fpop, details.qpop'); if (pop) pop.open = false;
      d.open = true;
      t.scrollIntoView({ behavior: F0.motion() ? 'smooth' : 'auto', block: 'start' });
      if (t === d) { d.querySelector('summary').focus({ preventScroll: true }); return; }
      t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });
      t.classList.add('flash'); setTimeout(function () { t.classList.remove('flash'); }, 1800);
    });
  }

  /* ================= boot ================= */
  function start() {
    howtoInit();
    F0.json(DATA).then(function (L) {
      prep(L); F = defaults(); stats();
      buildFacets(); wInit(); entryInit(); tInit(); csvInit(); chartsInit(); arInit();
      var how = readHash(location.hash);
      if (S.sel < 0) {
        var best = S.all.reduce(function (a, m) { return (m.significance > a.significance || (m.significance === a.significance && m.t > a.t)) ? m : a; }, S.all[0]);
        setSel(best.i, 'default', false);
      }
      /* phones open the wall on 2023 onward, unless a link chose the years or an older entry */
      var y23 = Math.max(S.yMin, 2023);
      if (W.C && W.C.w > 0 && W.C.w < 640 && F.y0 === S.yMin && F.y1 === S.yMax && S.all[S.sel].y >= y23) W.view = { y0: y23, y1: S.yMax };
      syncControls();
      S.shown = S.all.filter(function (m) { var ok = pass(m); m.on = ok; return ok; });
      update();
      if (how === 'entry') requestAnimationFrame(function () { requestAnimationFrame(function () { $('#wall-fig').scrollIntoView({ block: 'start' }); }); });
      /* in-page links that name an entry (role examples) */
      D.addEventListener('click', function (e) {
        var a = e.target.closest('a[data-pick]'); if (!a || a.closest('#ltbody')) return;
        var m = S.byId[a.getAttribute('data-pick')]; if (!m) return;
        e.preventDefault(); goToEntry(m.i, e.detail === 0 ? 'kbd' : 'ptr');
      });
      window.addEventListener('hashchange', function () {
        var raw = location.hash.slice(1), dec; try { dec = decodeURIComponent(raw); } catch (er) { dec = raw; }
        if (inHowto(dec)) $('#reading').open = true;
        if (!raw || (D.getElementById(dec) && !S.byId[dec])) return; // a section anchor
        if ('#' + raw === lastHash) return;
        var r = readHash(location.hash);
        if (!r) return;
        lastHash = null; syncControls(); update();
        if (r === 'entry') { showEntry(S.sel, S.selSrc, true); $('#wall-fig').scrollIntoView({ behavior: F0.motion() ? 'smooth' : 'auto', block: 'start' }); }
      });
    }).catch(function (err) {
      console.error(err);
      var t = $('#entry-title'); if (t) t.textContent = 'The Ledger could not be loaded. The raw file is at data/ledger.json.';
    });
  }
  if (D.readyState === 'loading') D.addEventListener('DOMContentLoaded', start); else start();
})();
