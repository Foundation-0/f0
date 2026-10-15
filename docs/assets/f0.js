/* Foundation0 runtime (window.F0). Plain script, no modules, no dependencies.
   API per SPEC §4: reduced, theme(), onTheme(), css(), json(), tip, whenVisible(), canvas(), fmtDate(), esc().
   Additions: motion(), onMotion(), loop(), enter() (one-shot entrance), idle-pause, section index (rail + compact bar),
   root (relative path to docs/), statusBadges(), kappa() (live reviewed κ), kappaWhen(), rolePeriods() and roleInsight()
   (the Ledger's role-over-time numbers, shared by Home and the Ledger), titleHTML()/titleText() (OpenAI family titles),
   prerendering (true while scripts/prerender.mjs bakes the no-JS copy). Guide: assets/README.md */
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
  /* The header toggle is a toggle button with a fixed name, "Motion"; aria-pressed (and the icon: waves, or waves
     struck through) says whether motion is on. Its name never changes, so a screen reader never hears "Pause, pressed". */
  function applyMotion() {
    root.setAttribute('data-motion', F0.motion() ? 'on' : 'off');
    document.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      var on = F0.motion();
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', 'Motion');
      b.title = on ? 'Motion is on: press to stop it' : 'Motion is off: press to allow it';
      var t = b.querySelector('.t-txt'); if (t) t.textContent = 'Motion';
      var i = b.querySelector('.ico'); if (i) i.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">' +
        '<path d="M2 6c2-2.2 4 2.2 6 0s4-2.2 6 0M2 10.5c2-2.2 4 2.2 6 0s4-2.2 6 0"/>' + (on ? '' : '<path d="M3 14L13 2"/>') + '</g></svg>';
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
      b.setAttribute('aria-label', dark ? 'Dark theme: switch to light' : 'Light theme: switch to dark');
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

  /* ---- shared tooltip: one element, clamped to the viewport. It can be hovered (it stays while the pointer is on
     it), Escape dismisses it, and hide() waits a moment so the pointer can travel from the mark to the tip. ---- */
  var tipEl = null, tipT = 0, onTip = false;
  F0.tip = {
    show: function (html, x, y) {
      clearTimeout(tipT);
      if (!tipEl) {
        tipEl = document.createElement('div'); tipEl.className = 'f0-tip'; tipEl.setAttribute('aria-hidden', 'true');
        tipEl.addEventListener('pointerenter', function () { onTip = true; clearTimeout(tipT); });
        tipEl.addEventListener('pointerleave', function () { onTip = false; F0.tip.hide(); });
        document.body.appendChild(tipEl);
      }
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
    hide: function (now) {
      if (!tipEl) return;
      clearTimeout(tipT);
      if (now === true) { onTip = false; tipEl.classList.remove('on'); return; }
      tipT = setTimeout(function () { if (!onTip) tipEl.classList.remove('on'); }, 220);
    }
  };
  window.addEventListener('scroll', function () { F0.tip.hide(true); }, { passive: true });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') F0.tip.hide(true); });

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
      api.ready = r.width >= 2 && r.height >= 2; // false until the canvas is laid out: skip drawing, resize() fires later
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

  /* ---- one-shot entrance: F0.enter(el, fn, {duration, threshold}) ----
     The figure first paints its final, informative frame (the caller does that). When el first scrolls into view
     with motion on, fn(t) is called for t from 0 to 1 over the duration (default --t-reveal, never above 1200 ms),
     and it ends on fn(1). Just before el comes into view it is drawn at fn(0), so it never flashes full, then empty;
     if it leaves again without playing, it is put back to fn(1). With motion off, while prerendering, or without
     IntersectionObserver, nothing moves and the final frame stays. Returns {finish(), running, done}. */
  F0.enter = function (el, fn, opts) {
    opts = opts || {};
    var dur = Math.min(1200, opts.duration || parseFloat(F0.css('--t-reveal')) || 650), thr = opts.threshold || 0.3;
    var state = 'idle', raf = 0, near = null, vis = null;
    var api = { finish: finish, get running() { return state === 'running'; }, get done() { return state === 'done'; } };
    function stopObs() { if (near) near.disconnect(); if (vis) vis.disconnect(); }
    function finish() { if (state === 'done') return; var was = state; state = 'done'; cancelAnimationFrame(raf); stopObs(); if (was !== 'idle') fn(1); }
    function run() {
      if (state === 'running' || state === 'done') return;
      if (!F0.motion() || document.hidden) { finish(); return; }
      state = 'running'; stopObs();
      var t0 = 0;
      fn(0);
      raf = requestAnimationFrame(function step(now) {
        if (state !== 'running') return;
        if (!t0) t0 = now;
        var t = Math.min(1, (now - t0) / dur);
        if (t >= 1 || !F0.motion()) { state = 'done'; fn(1); return; }
        fn(t); raf = requestAnimationFrame(step);
      });
    }
    if (!F0.motion() || F0.prerendering || !('IntersectionObserver' in window)) { state = 'done'; return api; }
    near = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && state === 'idle') { state = 'armed'; fn(0); }
        else if (!e.isIntersecting && state === 'armed') { state = 'idle'; fn(1); }
      });
    }, { rootMargin: '30% 0px 30% 0px' });
    vis = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting && e.intersectionRatio >= thr) run(); }); }, { threshold: [thr] });
    near.observe(el); vis.observe(el);
    F0.onMotion(function (on) { if (!on) finish(); });
    return api;
  };

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

  /* ---- true while scripts/prerender.mjs bakes the no-JavaScript copy: say nothing about this visit's network ---- */
  F0.prerendering = !!window.__f0prerender;

  /* ---- AI's role over time, the Ledger's periods (shared by Home and the Ledger so both show the same numbers).
     F0.rolePeriods(milestones, {yMin, yMax, nowYear}) -> [{label, a, b, now, items, n, c: {instrument, collaborator,
     originator}}]: the first year to 2015, 2016-19, 2020-21, 2022-23, then one row per year from 2024.
     F0.roleInsight(periods, {note}) -> {h, p}: headline and sentence comparing the first and last period with at
     least 10 milestones. ---- */
  var ROLE_KEYS = ['instrument', 'collaborator', 'originator'];
  function yearOf(m) { return m.y != null ? m.y : +String(m.date).slice(0, 4); }
  F0.rolePeriods = function (list, opts) {
    opts = opts || {};
    var ys = list.map(yearOf), CUT = 2016;
    var yMin = opts.yMin != null ? opts.yMin : Math.min.apply(null, ys), yMax = opts.yMax != null ? opts.yMax : Math.max.apply(null, ys);
    var nowYear = opts.nowYear != null ? opts.nowYear : yMax;
    var P = [{ label: yMin + '–' + (CUT - 1), a: -Infinity, b: CUT - 1 }, { label: '2016–19', a: 2016, b: 2019 },
      { label: '2020–21', a: 2020, b: 2021 }, { label: '2022–23', a: 2022, b: 2023 }];
    for (var y = 2024; y <= yMax; y++) P.push({ label: String(y), a: y, b: y, now: y === nowYear });
    P.forEach(function (p) {
      p.items = list.filter(function (m) { var v = yearOf(m); return v >= p.a && v <= p.b; });
      p.n = p.items.length; p.c = {};
      ROLE_KEYS.forEach(function (k) { p.c[k] = 0; });
      p.items.forEach(function (m) { if (p.c[m.ai_role] != null) p.c[m.ai_role]++; });
    });
    return P;
  };
  F0.roleInsight = function (P, opts) {
    var note = (opts && opts.note) || '';
    var pc = function (a, b) { return b ? Math.round(100 * a / b) : 0; };
    var ok = P.filter(function (p) { return p.n >= 10; });
    if (ok.length < 2) return { h: 'What AI did, period by period.', p: 'Too few milestones' + note + ' to compare periods; the numbers are in the table below the chart.' };
    var a = ok[0], b = ok[ok.length - 1], i0 = pc(a.c.instrument, a.n), o0 = pc(a.c.originator, a.n), i1 = pc(b.c.instrument, b.n), o1 = pc(b.c.originator, b.n);
    var bl = b.now ? b.label + ' so far' : b.label;
    var h = (o1 > o0 && i1 < i0) ? 'AI is doing more of the work itself.' : (o1 > o0 ? 'AI produces more of the results itself.' : (i1 < i0 ? 'AI is less often only a tool.' : 'What AI did, period by period.'));
    return { h: h, a: a, b: b, p: 'In ' + a.label + ', AI was only a tool (instrument) in ' + i0 + '% of the milestones we record' + note + ', and produced the result itself (originator) in ' + o0 + '%. In ' + bl + ', those shares are ' + i1 + '% and ' + o1 + '%.' };
  };

  /* ---- OpenAI family titles carry a little HTML (<i>, <sub>, <sup>) and some TeX: render both safely.
     F0.titleHTML(t) for innerHTML (everything else escaped), F0.titleText(t) for aria-labels and plain text. ---- */
  F0.titleHTML = function (t) {
    var s = F0.esc(t).replace(/&lt;(\/?)(i|sub|sup)&gt;/g, '<$1$2>');
    return s.replace(/\$/g, '').replace(/\\log\s*/g, ' log ').replace(/\\mathsf\{([^}]*)\}/g, '$1').replace(/\\mathsf\s*/g, '').replace(/\\mathcal\s*/g, '')
      .replace(/\\alpha/g, 'α').replace(/\^\{([^}]*)\}/g, '<sup>$1</sup>').replace(/_(\d)/g, '<sub>$1</sub>').replace(/\s{2,}/g, ' ').trim();
  };
  F0.titleText = function (t) {
    return F0.titleHTML(t).replace(/<sup>(.*?)<\/sup>/g, function (m, x) { x = x.replace(/<[^>]+>/g, ''); return x.length > 1 ? '^(' + x + ')' : '^' + x; }).replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&#39;/g, '’').replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
  };

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
    [/tested on every input|exhaustively tested/i, 'v', 0],
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
  /* The snapshot is the last reviewed record in research/integer-multiplication/kappa-history.json (the file the
     pages cite), read only when the live file cannot be reached; F0.KAPPA_SNAPSHOT above is the last resort and is
     updated in place from that file. F0.kappaHistory() resolves the file's records (or [] if it cannot be read). */
  F0.KAPPA_HISTORY = 'research/integer-multiplication/kappa-history.json';
  var histP = null;
  F0.kappaHistory = function () {
    if (!histP) histP = F0.json(F0.root + F0.KAPPA_HISTORY).then(function (d) { return (d && d.records) || []; }, function () { return []; });
    return histP;
  };
  function histSnapshot() {
    return F0.kappaHistory().then(function (recs) {
      var r = recs.filter(function (x) { return x.status === 'reviewed' && /^0\.\d+$/.test(String(x.decimal)); }).pop();
      if (!r || !(Date.parse(r.t) >= Date.parse(F0.KAPPA_SNAPSHOT.at))) return F0.KAPPA_SNAPSHOT;
      var pr = /#(\d+)/.exec(r.what || ''), S = F0.KAPPA_SNAPSHOT;
      S.decimal = String(r.decimal); S.kappa = r.kappa; S.pr = pr ? +pr[1] : null; S.prs = pr ? [+pr[1]] : []; S.at = r.t;
      S.url = r.commit ? 'https://github.com/CrocSwap/integer-mult-bounds/blob/' + r.commit + '/certificates/selected-result.json' : S.url;
      S.note = 'kappa-history.json, last reviewed record' + (r.commit ? ' (selected-result.json @ ' + r.commit + ')' : '');
      return S;
    });
  }
  F0.kappa = function (opts) {
    return kappaBase().then(function (k) {
      if (k && k.source === 'live') return k;
      return ((opts && opts.snapshot) ? Promise.resolve(opts.snapshot) : histSnapshot()).then(function (snap) {
        if (k && snap && !(Date.parse(k.at) > Date.parse(snap.at))) { var o = {}; for (var x in snap) o[x] = snap[x]; o.source = 'snapshot'; o.feedAt = k.at; return o; }
        if (k) return k;
        var c = {}; for (var y in snap) c[y] = snap[y]; c.source = 'snapshot'; return c;
      });
    });
  };
  /* what to print beside a κ value: which copy it is and when. The reason a live fetch failed is said only to a
     visitor whose fetch did fail, never baked into the no-JS copy by the prerender run. */
  F0.kappaWhen = function (k, utc) {
    utc = utc || function (iso) { var d = new Date(iso); return isNaN(d) ? String(iso || '') : F0.fmtDate(d.toISOString().slice(0, 10)) + ', ' + d.toISOString().slice(11, 16) + ' UTC'; };
    if (k.source === 'live') return 'live · fetched ' + utc(k.at);
    if (k.source === 'feed') return 'feed.json snapshot · ' + utc(k.at);
    return 'snapshot · ' + utc(k.at) + (F0.prerendering ? '' : ' (live file unreachable)');
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
    var secs = [].slice.call(document.querySelectorAll('section[data-index]')).filter(function (s) { return s.id; });
    var hud = document.querySelector('[data-hud]');
    if (hud && secs.length) {
      var num = function (s, i) { return s.getAttribute('data-num') || String(i).padStart(2, '0'); };
      var item = function (s, i, rail) {
        var li = document.createElement('li'), a = document.createElement('a'), n = num(s, i), t = s.getAttribute('data-index');
        a.href = '#' + s.id;
        a.innerHTML = rail ? '<span class="bar" aria-hidden="true"></span><span class="n">' + F0.esc(n) + '</span><span class="t">' + F0.esc(t) + '</span>'
          : '<span>' + F0.esc(n) + '</span>' + F0.esc(t);
        if (rail) a.setAttribute('aria-label', n + ' ' + t);
        li.appendChild(a); return li;
      };
      /* the rail (960px and up) */
      var ol = document.createElement('ol');
      secs.forEach(function (s, i) { ol.appendChild(item(s, i, true)); });
      hud.appendChild(ol);
      var links = [].slice.call(ol.querySelectorAll('a'));
      /* the compact bar under the header (below 960px), for pages with three or more sections */
      var bar = null, sum = null, prog = null, blinks = [], det = null;
      if (secs.length >= 3) {
        bar = document.createElement('nav'); bar.className = 'secbar'; bar.setAttribute('aria-label', 'On this page (compact)');
        bar.innerHTML = '<div class="wrap"><details><summary><span class="sb-cur"></span><svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5L6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></summary><ol></ol></details></div><span class="prog" aria-hidden="true"></span>';
        var bol = bar.querySelector('ol');
        secs.forEach(function (s, i) { bol.appendChild(item(s, i, false)); });
        blinks = [].slice.call(bol.querySelectorAll('a'));
        det = bar.querySelector('details'); sum = bar.querySelector('.sb-cur'); prog = bar.querySelector('.prog');
        blinks.forEach(function (a) { a.addEventListener('click', function () { det.open = false; }); });
        hud.parentNode.insertBefore(bar, hud);
        root.classList.add('has-secbar');
        closeOnLeave(det);
      }
      var lastCur = -2;
      var spy = function () {
        var y = 140, cur = -1;
        secs.forEach(function (s, i) { if (s.getBoundingClientRect().top <= y) cur = i; });
        if (cur !== lastCur) {
          lastCur = cur;
          links.concat(blinks).forEach(function (a) { a.setAttribute('aria-current', 'false'); });
          if (cur >= 0) { links[cur].setAttribute('aria-current', 'true'); if (blinks[cur]) blinks[cur].setAttribute('aria-current', 'true'); }
          if (sum && cur >= 0) sum.innerHTML = '<b>' + F0.esc(num(secs[cur], cur)) + '</b> // <span class="t">' + F0.esc(secs[cur].getAttribute('data-index')) + '</span> <span aria-hidden="true">·</span> ' + (cur + 1) + ' of ' + secs.length;
        }
        if (bar) {
          var doc = document.documentElement, max = Math.max(1, doc.scrollHeight - window.innerHeight), f = Math.min(1, Math.max(0, window.scrollY / max));
          prog.style.transform = 'scaleX(' + f.toFixed(4) + ')';
          var show = cur >= 0 && window.scrollY > window.innerHeight * 0.5;
          if (show !== bar.classList.contains('on')) { bar.classList.toggle('on', show); if (!show) det.open = false; }
        }
      };
      var pending = false;
      window.addEventListener('scroll', function () { if (!pending) { pending = true; requestAnimationFrame(function () { pending = false; spy(); }); } }, { passive: true });
      window.addEventListener('resize', spy, { passive: true });
      spy();
    }
    /* close the mobile menu (and the compact section list) with Escape, an outside click, or when focus leaves it */
    var menu = document.querySelector('.menu');
    if (menu) closeOnLeave(menu);
    themeChanged(); applyMotion(); wake();
  }
  function closeOnLeave(d) {
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.open) { d.open = false; d.querySelector('summary').focus(); } });
    document.addEventListener('click', function (e) { if (d.open && !d.contains(e.target)) d.open = false; });
    d.addEventListener('focusout', function (e) { if (d.open && e.relatedTarget && !d.contains(e.relatedTarget)) d.open = false; });
  }
  /* ---- quiet readouts while a figure plays: when any .tbtn.play reports playing (aria-pressed="true" or
     data-state="playing"), the live regions and <output>s of its figure are set to aria-live="off", so a screen
     reader does not hear every frame; when it stops they are restored and one summary is announced. ---- */
  (function () {
    if (typeof MutationObserver === 'undefined') return;
    function isOn(b) { return b.getAttribute('aria-pressed') === 'true' || b.getAttribute('data-state') === 'playing'; }
    function figOf(b) { return b.closest('figure, .fig') || b.closest('section') || document.body; }
    function quiet(fig) {
      if (fig._f0q) return;
      fig._f0q = Array.prototype.filter.call(fig.querySelectorAll('[aria-live], output, [role="status"]'), function (r) {
        return !r.hasAttribute('data-f0-sum') && r.getAttribute('aria-live') !== 'off';
      });
      fig._f0q.forEach(function (r) { r.setAttribute('data-f0-live', r.getAttribute('aria-live') || ''); r.setAttribute('aria-live', 'off'); });
    }
    function wake(fig) {
      var q = fig._f0q; if (!q) return; fig._f0q = null;
      q.forEach(function (r) { var v = r.getAttribute('data-f0-live'); r.removeAttribute('data-f0-live'); if (v) r.setAttribute('aria-live', v); else r.removeAttribute('aria-live'); });
      if (F0.prerendering) return;
      setTimeout(function () {
        if (fig._f0q) return;
        var sum = fig.querySelector('[data-f0-sum]'), seen = {};
        if (!sum) { sum = document.createElement('p'); sum.className = 'sr-only'; sum.setAttribute('aria-live', 'polite'); sum.setAttribute('data-f0-sum', ''); fig.appendChild(sum); }
        sum.textContent = q.map(function (r) { return (r.textContent || '').replace(/\s+/g, ' ').trim(); })
          .filter(function (t) { if (!t || seen[t]) return false; seen[t] = 1; return true; }).join(' ').slice(0, 400);
      }, 300);
    }
    new MutationObserver(function (ms) {
      ms.forEach(function (m) { var b = m.target; if (b.classList && b.classList.contains('play') && b.classList.contains('tbtn')) (isOn(b) ? quiet : wake)(figOf(b)); });
    }).observe(document.documentElement, { subtree: true, attributes: true, attributeFilter: ['aria-pressed', 'data-state'] });
  })();

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();
})();
