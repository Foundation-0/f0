/* Foundation0 runtime (window.F0). Plain script, no modules, no dependencies.
   API per SPEC §4: reduced, theme(), onTheme(), css(), json(), tip, whenVisible(), canvas(), fmtDate(), esc().
   Additions: motion(), onMotion(), loop(), idle-pause, section index,
   root (relative path to docs/), statusBadges(), kappa() (live reviewed κ). Guide: assets/README.md */
(function () {
  'use strict';
  var root = document.documentElement;
  var me = document.currentScript;
  var mqReduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mqDark = window.matchMedia('(prefers-color-scheme: dark)');
  var F0 = window.F0 = window.F0 || {};

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } return null; }

  /* ---- reduced motion + global motion toggle ---- */
  F0.reduced = mqReduce.matches;
  var motionPref = root.getAttribute('data-motion-pref'); // set by the inline bootstrap from ?motion= or storage
  var motionFns = [];
  F0.motion = function () { return motionPref ? motionPref === 'on' : !F0.reduced; };
  function applyMotion() {
    root.setAttribute('data-motion', F0.motion() ? 'on' : 'off');
    document.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      var on = F0.motion();
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', on ? 'Pause motion' : 'Play motion');
      var t = b.querySelector('.t-txt'); if (t) t.textContent = on ? 'Motion on' : 'Motion off';
      var i = b.querySelector('.ico'); if (i) i.innerHTML = on
        ? '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="4" y="3" width="2.6" height="10" fill="currentColor"/><rect x="9.4" y="3" width="2.6" height="10" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>';
    });
    motionFns.forEach(function (f) { try { f(F0.motion()); } catch (e) { console.error(e); } });
  }
  F0.onMotion = function (fn) { motionFns.push(fn); };
  mqReduce.addEventListener('change', function () { F0.reduced = mqReduce.matches; applyMotion(); });

  /* ---- theme ---- */
  var themeFns = [];
  F0.theme = function () { var t = root.getAttribute('data-theme'); return t === 'dark' || t === 'light' ? t : (mqDark.matches ? 'dark' : 'light'); };
  F0.onTheme = function (fn) { themeFns.push(fn); };
  function themeChanged() {
    cssCache = {};
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      var dark = F0.theme() === 'dark';
      b.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      var t = b.querySelector('.t-txt'); if (t) t.textContent = dark ? 'Dark' : 'Light';
      var i = b.querySelector('.ico'); if (i) i.innerHTML = dark
        ? '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.8 2.2a6 6 0 1 0 3 9.6A5.2 5.2 0 0 1 10.8 2.2z" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3.2" fill="currentColor"/><g stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M3 13l1.4-1.4M11.6 4.4L13 3"/></g></svg>';
    });
    themeFns.forEach(function (f) { try { f(F0.theme()); } catch (e) { console.error(e); } });
  }
  mqDark.addEventListener('change', themeChanged);

  /* ---- CSS custom properties (canvas colours come from tokens) ---- */
  var cssCache = {};
  F0.css = function (name) {
    if (cssCache[name] !== undefined) return cssCache[name];
    return (cssCache[name] = getComputedStyle(root).getPropertyValue(name).trim());
  };

  /* ---- JSON, memoised ---- */
  var jsonCache = {};
  F0.json = function (path) {
    if (!jsonCache[path]) jsonCache[path] = fetch(path, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(path + ': ' + r.status); return r.json(); });
    return jsonCache[path];
  };

  /* ---- escaping and dates ---- */
  F0.esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  F0.fmtDate = function (s) {
    if (!s) return '';
    var p = String(s).split('-');
    if (p.length === 1) return p[0];
    if (p.length === 2) return MON[+p[1] - 1] + ' ' + p[0];
    return (+p[2]) + ' ' + MON[+p[1] - 1] + ' ' + p[0];
  };
  /* decimal year; a year alone is read as mid-year, a month as mid-month */
  F0.decYear = function (s) {
    var p = String(s).split('-').map(Number);
    if (p.length === 1) return p[0] + 0.5;
    if (p.length === 2) return p[0] + (p[1] - 0.5) / 12;
    var start = Date.UTC(p[0], 0, 1), end = Date.UTC(p[0] + 1, 0, 1);
    return p[0] + (Date.UTC(p[0], p[1] - 1, p[2]) - start) / (end - start);
  };

  /* ---- shared tooltip: one element, clamped to the viewport ---- */
  var tipEl = null;
  F0.tip = {
    show: function (html, x, y) {
      if (!tipEl) { tipEl = document.createElement('div'); tipEl.className = 'f0-tip'; tipEl.setAttribute('aria-hidden', 'true'); document.body.appendChild(tipEl); }
      tipEl.innerHTML = html;
      tipEl.classList.add('on');
      var r = tipEl.getBoundingClientRect(), vw = window.innerWidth, vh = window.innerHeight, pad = 12;
      var left = x + 16, top = y + 16;
      if (left + r.width > vw - pad) left = x - r.width - 16;
      if (left < pad) left = Math.max(pad, Math.min(vw - r.width - pad, x - r.width / 2));
      if (top + r.height > vh - pad) top = y - r.height - 16;
      if (top < pad) top = pad;
      tipEl.style.transform = 'none';
      tipEl.style.left = Math.round(left) + 'px'; tipEl.style.top = Math.round(top) + 'px';
    },
    hide: function () { if (tipEl) tipEl.classList.remove('on'); }
  };
  window.addEventListener('scroll', function () { F0.tip.hide(); }, { passive: true });

  /* ---- visibility: pause animation off-screen ---- */
  F0.whenVisible = function (el, onEnter, onLeave) {
    if (!('IntersectionObserver' in window)) { onEnter && onEnter(); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) onEnter && onEnter(); else onLeave && onLeave(); }); }, { rootMargin: '80px 0px' });
    io.observe(el); return io;
  };

  /* ---- DPR-aware, resize-observed canvas (DPR capped at 2) ---- */
  F0.canvas = function (el) {
    var ctx = el.getContext('2d');
    var api = { el: el, ctx: ctx, w: 0, h: 0, dpr: 1, fns: [] };
    function fit() {
      var r = el.getBoundingClientRect();
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      var w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height));
      if (w === api.w && h === api.h && dpr === api.dpr) return false;
      api.w = w; api.h = h; api.dpr = dpr;
      el.width = Math.round(w * dpr); el.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return true;
    }
    api.fit = fit;
    api.resize = function (fn) { api.fns.push(fn); };
    fit();
    if ('ResizeObserver' in window) new ResizeObserver(function () { if (fit()) api.fns.forEach(function (f) { f(api); }); }).observe(el);
    else window.addEventListener('resize', function () { if (fit()) api.fns.forEach(function (f) { f(api); }); });
    return api;
  };

  /* ---- one shared animation loop, capped at 30 fps, paused when the tab is hidden ---- */
  var jobs = [], rafId = 0, last = 0, FRAME = 1000 / 30;
  function tick(now) {
    rafId = 0;
    var active = jobs.filter(function (j) { return j.active; });
    if (!active.length || document.hidden || !F0.motion()) return;
    if (now - last >= FRAME - 2) { last = now; active.forEach(function (j) { try { j.fn(now); } catch (e) { console.error(e); j.active = false; } }); }
    rafId = requestAnimationFrame(tick);
  }
  function kick() { if (!rafId && F0.motion() && !document.hidden && jobs.some(function (j) { return j.active; })) rafId = requestAnimationFrame(tick); }
  F0.loop = function (fn) {
    var job = { fn: fn, active: false };
    jobs.push(job);
    return { start: function () { job.active = true; kick(); }, stop: function () { job.active = false; }, get running() { return job.active && F0.motion(); } };
  };
  document.addEventListener('visibilitychange', kick);
  F0.onMotion(kick);

  /* ---- idle pause: ambient loops stop after 60 s without interaction ---- */
  var idleFns = [], idleTimer = 0, isIdle = false;
  F0.onIdle = function (fn) { idleFns.push(fn); };
  function wake() {
    if (isIdle) { isIdle = false; idleFns.forEach(function (f) { f(false); }); }
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () { isIdle = true; idleFns.forEach(function (f) { f(true); }); }, 60000);
  }
  ['pointermove', 'pointerdown', 'keydown', 'scroll', 'touchstart'].forEach(function (ev) { window.addEventListener(ev, wake, { passive: true }); });
  F0.idle = function () { return isIdle; };

  /* ---- relative path from this page to docs/ ('' on the home page, '../../' two levels down) ---- */
  F0.root = (function () {
    var src = me && me.getAttribute('src');
    return src ? src.replace(/assets\/f0\.js(?:[?#].*)?$/, '') : '';
  })();

  /* ---- status string -> badges. "Conditional · maintainer-reviewed · not peer reviewed" becomes two badges:
     an evidence badge with its ladder glyph (rungs: claimed 1, preprint 2, reviewed or deployed 3,
     replicated 4, formally verified 5) and a neutral one. Text is kept exactly as given (CSS sets caps). ---- */
  var BADGE_RULES = [
    [/retract/i, 'rt', 0], [/contested/i, 'x', 0],
    [/not confirmed|unreviewed|claim|candidate|superseded/i, 'c', 1],
    [/^(not|no) |refereed only|pending|not clinically/i, 'n', 0],
    [/partly/i, 'p', 2],
    [/lean|formally|machine-verified|machine-checked|proof checker/i, 'v', 5],
    [/replicated/i, 'v', 4],
    [/peer[- ]reviewed|published in/i, 'r', 3],
    [/deployed|released|live demo|daily use|software/i, 'd', 3],
    [/preprint|conditional|maintainer|certificate|proof/i, 'p', 2],
    [/private|in design|in progress|sealed/i, 'sealed', 0]
  ];
  F0.ladderHTML = F0.ladderHTML || function (r) { return '<span class="ladder" data-r="' + r + '" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>'; };
  F0.classifyStatus = function (seg) {
    for (var i = 0; i < BADGE_RULES.length; i++) if (BADGE_RULES[i][0].test(seg)) return { cls: BADGE_RULES[i][1], rung: BADGE_RULES[i][2] };
    return { cls: 'n', rung: 0 };
  };
  F0.statusBadges = function (status, opts) {
    opts = opts || {};
    var groups = [];
    String(status || '').split(/\s+·\s+/).filter(Boolean).forEach(function (seg) {
      var c = F0.classifyStatus(seg), g = groups[groups.length - 1];
      if (g && g.cls === c.cls && g.rung === c.rung) g.text.push(seg); else groups.push({ cls: c.cls, rung: c.rung, text: [seg] });
    });
    if (opts.ladder && groups.length && !groups.some(function (g) { return g.rung; })) { groups[0].rung = opts.ladder; if (groups[0].cls === 'n') groups[0].cls = 'c'; }
    return groups.map(function (g) {
      var t = g.text.join(' · ');
      return '<span class="badge ' + g.cls + '">' + (g.rung ? F0.ladderHTML(g.rung) : '') + (g.cls === 'x' ? '<span class="xm" aria-hidden="true">×</span>' : '') + F0.esc(t.charAt(0).toUpperCase() + t.slice(1)) + '</span>';
    }).join('');
  };

  /* ---- the live reviewed κ for integer multiplication (CrocSwap/integer-mult-bounds).
     F0.kappa(opts) resolves {decimal, kappa, pr, prs, status, source: 'live'|'feed'|'snapshot', at, url, feedAt}.
     'live'     the maintainer's certificates/selected-result.json fetched now (at = fetch time; status = its status field);
     'feed'     this site's feed.json selected result (at = its generated_at), used only when it is newer than the snapshot;
     'snapshot' F0.KAPPA_SNAPSHOT (or opts.snapshot): the record as last read by hand, with its own date.
     The upstream fetch is made once per page; opts only changes which fallback wins. Always show which one and when. ---- */
  var kappaP = null;
  F0.KAPPA_URL = 'https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/main/certificates/selected-result.json';
  F0.KAPPA_SNAPSHOT = { decimal: '0.001672660197076918', kappa: '836330098538459/500000000000000000', pr: 1094, prs: [1094], status: null,
    source: 'snapshot', at: '2026-10-13T18:45:23Z', url: 'https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json', note: 'selected-result.json @ 0a31ad884' };
  function kappaBase() {
    if (kappaP) return kappaP;
    var ctl = 'AbortController' in window ? new AbortController() : null, timer = ctl && setTimeout(function () { ctl.abort(); }, 8000);
    kappaP = fetch(F0.KAPPA_URL, { cache: 'no-cache', signal: ctl ? ctl.signal : undefined })
      .then(function (r) { if (!r.ok) throw new Error('selected-result.json: ' + r.status); return r.json(); })
      .then(function (d) {
        clearTimeout(timer);
        if (!d || !/^0\.\d+$/.test(String(d.decimal))) throw new Error('selected-result.json: no decimal');
        var prs = Array.isArray(d.source_prs) ? d.source_prs : [];
        return { decimal: String(d.decimal), kappa: d.kappa, pr: prs[0] || null, prs: prs, status: d.status || null, source: 'live', at: new Date().toISOString(), url: F0.KAPPA_URL };
      })
      .catch(function () {
        clearTimeout(timer);
        return F0.json(F0.root + 'feed.json').then(function (f) {
          var s = f.selected_result || {};
          if (!/^0\.\d+$/.test(String(s.decimal))) return null;
          return { decimal: String(s.decimal), kappa: s.kappa, pr: null, prs: [], status: null, source: 'feed', at: f.generated_at, url: F0.root + 'feed.json' };
        }, function () { return null; });
      });
    return kappaP;
  }
  F0.kappa = function (opts) {
    var snap = (opts && opts.snapshot) || F0.KAPPA_SNAPSHOT;
    return kappaBase().then(function (k) {
      if (k && k.source === 'live') return k;
      if (k && snap && !(Date.parse(k.at) > Date.parse(snap.at))) { var o = {}; for (var x in snap) o[x] = snap[x]; o.source = 'snapshot'; o.feedAt = k.at; return o; }
      if (k) return k;
      var c = {}; for (var y in snap) c[y] = snap[y]; c.source = 'snapshot'; return c;
    });
  };

  /* ---- toggles and section index ---- */
  function bind() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        var next = F0.theme() === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next); store('f0-theme', next); themeChanged();
      });
    });
    document.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        motionPref = F0.motion() ? 'off' : 'on'; store('f0-motion', motionPref); applyMotion();
      });
    });
    var secs = [].slice.call(document.querySelectorAll('section[data-index]'));
    var hud = document.querySelector('[data-hud]');
    if (hud && secs.length) {
      var ol = document.createElement('ol');
      secs.forEach(function (s, i) {
        var li = document.createElement('li'), a = document.createElement('a');
        a.href = '#' + s.id;
        var n = s.getAttribute('data-num') || String(i).padStart(2, '0');
        a.innerHTML = '<span class="t">' + F0.esc(s.getAttribute('data-index')) + '</span><span class="bar"></span><span class="n">' + F0.esc(n) + '</span>';
        a.setAttribute('aria-label', n + ' ' + s.getAttribute('data-index'));
        li.appendChild(a); ol.appendChild(li);
      });
      hud.appendChild(ol);
      var links = [].slice.call(ol.querySelectorAll('a'));
      var spy = function () {
        var y = 140, cur = -1;
        secs.forEach(function (s, i) { if (s.getBoundingClientRect().top <= y) cur = i; });
        links.forEach(function (a, i) { a.setAttribute('aria-current', i === cur ? 'true' : 'false'); });
      };
      var pending = false;
      window.addEventListener('scroll', function () { if (!pending) { pending = true; requestAnimationFrame(function () { pending = false; spy(); }); } }, { passive: true });
      spy();
    }
    /* close the mobile menu with Escape or an outside click */
    var menu = document.querySelector('.menu');
    if (menu) {
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); } });
      document.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    }
    themeChanged(); applyMotion(); wake();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();
})();
