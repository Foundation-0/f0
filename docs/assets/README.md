# Foundation0 design system: a one-page guide

Everything a page needs lives in this folder. There is no build step: plain HTML, one stylesheet, one runtime script, served by GitHub Pages from `docs/`.

| File | What it is | Who edits it |
|---|---|---|
| `f0.css` | Tokens (both themes), base, layout and every shared component | foundation builder only |
| `f0.js` | The runtime, `window.F0` (theme, motion, data, tooltip, canvas, loop, badges, live κ) | foundation builder only |
| `radiant.js` | The Radiant: the ledger drawn as one radial figure (`F0.Radiant`) | foundation builder only |
| `home.js` | Home page wiring (data rendering, card figures) | foundation builder only |
| `favicon.svg`, `og.png` | The zero-octagon mark; the 1200×630 share image | foundation builder only |

Your page's own CSS and JS go in your page's folder (`<page-dir>/page.css`, `<page-dir>/page.js`). If you need something shared, ask for it rather than editing these files.

## 1. Page skeleton

Copy from `docs/index.html`, verbatim, and fix every relative prefix for your depth (`../` one level down, `../../` two):

1. the whole `<head>`: fonts link, the inline theme and motion bootstrap script (it must run before paint), the theme-color metas, `<link rel="icon" href="{rel}assets/favicon.svg">`, `og:image` = `{rel}assets/og.png`, `<link rel="stylesheet" href="{rel}assets/f0.css">`, `<script defer src="{rel}assets/f0.js">`;
2. the hidden `<svg>` with the `#zero` symbol (the header and footer marks use it);
3. the skip link, the header (mark `aria-current="page"` on your nav link in both `.nav` and `.menu-panel`), the HUD `<nav class="hud" data-hud>`;
4. the footer.

Give `<body>` a `data-page` key and the `<main id="main">` your sections. Sections follow one pattern, and the HUD index on wide screens builds itself from them:

```html
<section class="sec" id="method" data-index="Method" data-num="02" aria-labelledby="method-h">
  <div class="wrap">
    <div class="sec-head"><p class="sec-label"><b>02</b><i>//</i>Method</p><span class="chip">source chip</span></div>
    <h2 class="h2" id="method-h">One plain sentence.</h2>
    <p class="lede">Two lines of context, in the serif.</p>
  </div>
</section>
```

Alternate `.sec` and `.sec.alt` for banding. Inner pages open with a `.page-hero` (below) instead of the home hero.

## 2. Tokens

Use tokens only; never hard-code a colour. Light ("Encyclopedia paper") is the default; dark ("Terminus night") applies from the OS preference or `data-theme="dark"`. Every pair below passes WCAG AA in both themes.

- **Ground and ink:** `--bg` page, `--bg-1` alt band and figure stages, `--bg-2` panels and cards, `--bg-3` wells; `--line` decorative hairline, `--line-ui` anything clickable (≥ 3:1), `--grid` chart gridlines; `--ink`, `--ink-2` body, `--ink-3` muted (keep small text off `--bg-3` in light).
- **Symbiosis:** `--bio` gold = the human strand, `--dig` cyan = the digital strand (`-hi` variants for hover). Chart marks use `--mark-bio`, `--mark-mid`, `--mark-dig`. Never add a third "joint" colour; show joint work with a split glyph.
- **Red hairline:** `--hair` marks founding members' own work (Asimov's Radiant drew later additions in red).
- **Evidence status:** `--st-verified`, `--st-reviewed`, `--st-preprint`, `--st-claimed`, `--st-contested`, `--st-retracted`, `--st-deployed`. Never colour alone: always with a text label and the ladder glyph.
- **Project accents** (2px card bar, figure line): `--acc-incentre`, `--acc-exoplanets`, `--acc-intmult`, `--acc-mm` (After the 722), `--acc-mobius`, `--acc-gf2m`, `--acc-rohan`, `--acc-shea`, `--acc-exo`, `--acc-medcode`, `--acc-nutrak`. Set `style="--acc:var(--acc-…)"` on the component.
- **Type:** `--f-sans` Geist (headings, UI), `--f-serif` Newsreader (explanations), `--f-mono` Geist Mono (labels, data; uppercase with `--tr-label`). Sizes: `--fs-label` 11.5 (never below 11px), `--fs-xs` 13, `--fs-sm` 15, `--fs-ui` 16, `--fs-base` 18, `--fs-lede`, `--fs-h3`, `--fs-h2`, `--fs-h1`, `--fs-display`, `--fs-stat`.
- **Space:** `--s-1`…`--s-10` (4, 8, 12, 16, 24, 32, 48, 64, 96, 128), `--sec-pad`, `--max` 1320, `--gutter`, `--read` 760 (text column), `--wide` 1040 (figure breakout), `--measure` 68ch.
- **Hidden:** `[hidden]` always wins (`display: none !important`), so toggling `el.hidden` works on any component without page CSS.
- **Tool buttons:** below 760px the header's `.tbtn` collapse to icons; buttons inside `.fig` / `.fig-ctrl` keep their visible text.
- **Motion:** `--t-micro` 120ms, `--t-ui` 220ms, `--t-reveal`, `--t-draw`; `--ease-out`, `--ease-io`. `html[data-motion="off"]` kills every CSS animation and transition.

## 3. Components

Existing (home): `.site-head`, `.nav`, `.menu`, `.hud`, `.sec`/`.sec-head`/`.sec-label`, `.h2`, `.lede`, `.prose`, `.more` (arrow link), `.frame` (corner ticks: gold top-left, cyan bottom-right) with `.corner.tl|tr|bl|br`, `.chip` (with `.dot.live`), `.badge` + `.ladder`, `.btn`/`.btn.primary`, `.tbtn` (small tool button), `.stats`/`.stat`, `.chart` + `.chart-head`/`.chart-title`/`.chart-how`/`.chart-foot`, `.vlegend`, `.tbl` + `.table-wrap`, `.card`/`.cards` (+ `.card.feature`, `.glyph`), `.ccard`, `.two`, `.vault`, `.member`/`.members` (compact strip), `.posts`/`.post`, `.law`, `.aside-note`, `.principles`, `.f0-tip` (shared tooltip, use `F0.tip`).

Added for inner pages (section 19 of `f0.css`; each has a commented snippet there):

| Class | Use |
|---|---|
| `.page-hero` (+ `.has-fig`, `.ph-fig`), `.crumbs`, `.h1`, `.dek`, `.meta-row` | Inner-page hero: breadcrumb, kicker, title, dek, badges row; optional figure on the right; `--acc` sets its top bar |
| `.read`, `.wide` (alias `.breakout`) | 760px reading column; figures break out to 1040px, centred (also on a `.fig`). `.wide` is global: give page-specific variants another name (`.wide-fig`) |
| `.prose h3, ul, ol, blockquote, code` | Long-form text inside `.prose` |
| `.split` (+ `.rev`, `> .sticky`) | Prose beside a figure that sticks while you read |
| `.fig` (+ `.frame`), `.fig-head`, `.fig-title`, `.fig-how`, `.fig-stage` (`--ratio`), `.fig-out`, `.fig-ctrl`, `.ctrl-label`, `.ctrl`, `.fig-foot`, `.fig-src`, `details.twin` | The explainer frame: title, how to read, stage, controls row, source line, and the "show the numbers" twin |
| `input.range`, `.seg` (buttons with `aria-pressed`), `.tbtn.play` (`.i-play`/`.i-pause` inside) | Controls |
| `.callout` (`.def`, `.note`, `.caveat`, `.c-k`), `dfn.term` | Plain-words definitions, asides, honesty caveats |
| `.fnref`, `ol.notes` (`li id="fn-1"`, `.back`), `.src-list` | Footnotes and sources |
| `.badge.d` (deployed), `.badge.rt` (retracted), `.badge .xm` (× for contested) | Extra evidence states |
| `.statrow` (`.v`, `.k`, `.src`) | Auto-fitting row of sourced numbers |
| `.mcards`/`.mcard`, `.worklist` | Full member card (no pictures, ever) with their work and status badges |
| `.doors`/`.door` | Navigation tiles for index pages |
| `.kv`, `.toc`, `.prevnext` | Key/value facts, contents list, previous/next footer |
| `.live-val`, `.chip .dot.stale` | A value fetched at view time, labelled with what it is and when |

## 4. Runtime: `window.F0` (load `f0.js` with `defer`; it is stable, changes are additive)

- `F0.root`: relative path from this page to `docs/` (`''`, `'../'`, `'../../'`). Build data URLs with it: `F0.json(F0.root + 'data/ledger.json')`.
- `F0.json(path)` → memoised Promise of parsed JSON. `F0.esc(s)` HTML-escapes; escape every data string you put in `innerHTML` (or use `textContent`).
- `F0.theme()` → `'dark'|'light'`; `F0.onTheme(fn)`; `F0.css('--token')` reads a token (cached per theme). Canvases read colours through `F0.css` and redraw in `onTheme`.
- `F0.motion()` → is motion allowed (the header toggle, else `prefers-reduced-motion`); `F0.onMotion(fn)`; `F0.reduced`.
- `F0.loop(fn)` → `{start, stop, running}`: one shared 30 fps animation loop, paused in hidden tabs and when motion is off. `F0.whenVisible(el, onEnter, onLeave)` pauses off-screen. `F0.onIdle(fn)` / `F0.idle()` for ambient loops (pause after 60 s without input).
- `F0.canvas(el)` → `{ctx, w, h, dpr, resize(fn)}`: DPR-aware (capped at 2), resize-observed.
- `F0.tip.show(html, x, y)`, `F0.tip.hide()`: the one tooltip, clamped to the viewport. Classes for its content: `.tip-k`, `.tip-t`, `.tip-rows`, `.tip-row`, `.tip-v`, `.tip-note`, `.tip-foot`.
- `F0.fmtDate('2026-10-13')` → `13 Oct 2026` (also `YYYY-MM`, `YYYY`); `F0.decYear(s)` → decimal year.
- `F0.statusBadges(status, {ladder})` → badge HTML from a status string such as `projects.json`'s `"Conditional · maintainer-reviewed · not peer reviewed"`. `F0.ladderHTML(rung)` draws the 5-rung evidence ladder (claimed 1, preprint 2, peer reviewed or deployed 3, replicated 4, formally verified 5). `radiant.js` adds `F0.EVID`, `F0.RUNG`, `F0.PLAIN` (field names), `F0.ROLE_TXT`, `F0.dialSVG`.
- `F0.kappa(opts)` → Promise `{decimal, kappa, pr, prs, status, source, at, url, feedAt}`: the maintainer-reviewed κ from `CrocSwap/integer-mult-bounds` `certificates/selected-result.json` (`source: 'live'`, `at` = fetch time, `status` = the file's own status field); if that cannot be reached, the newer of the local `feed.json` (`source: 'feed'`, `at` = its `generated_at`) and `F0.KAPPA_SNAPSHOT` (`source: 'snapshot'`, the record as last read by hand, 13 Oct 2026 18:45 UTC; pass `opts.snapshot` to use your page's own). The upstream file is fetched once per page. Always print which and when.
- `F0.Radiant(stage, ledger, opts)`: the ledger figure. `opts.time = {range, play, output}` gives it a time slider and a play button and starts it paused on the full record; without it you get the legacy ambient sweep. `opts.list` (an `<ol>` for keyboard access), `opts.readout`, `opts.base` (link prefix), `opts.members`.

## 5. Every figure

Title, a one-line "how to read", a source line linking the data file, a text or table twin, keyboard operation (real buttons and inputs; arrow keys where natural; visible focus), colours from tokens in both themes, and no horizontal scroll at 360px. Anything that moves starts paused on an informative frame, runs only on a visible ▶ or on hover/focus, respects `F0.motion()`, and pauses off-screen. Follow the dataviz rules: one y-axis, thin marks, fixed colour order, a legend for two or more series, text in ink tokens (never in series colour), a tooltip on every mark.

## 6. Words

First principles and plain words; define any technical term the first time. No hype words. Credit precisely, state evidence exactly as the data files and dossiers do, never show "claimed" as "verified", no pictures of people, they/them unless a person's own page says otherwise, and never link private repositories.

## 7. Home page notes

`index.html` carries a pre-rendered copy of the numbers, members strip, research cards and writing list so the page reads without JavaScript; `home.js` re-renders each from `data/ledger.json`, `data/members.json`, `data/projects.json`, `data/openai-math-families.json` and `data/writing.json` on load. Every pre-rendered copy, on every page, sits between `<!--prerender:NAME-->` and `<!--/prerender:NAME-->` markers inside the element its script writes into; after changing `docs/data`, run `node scripts/prerender.mjs` to refresh them (rules at the top of that script). A new research or contribution project in `projects.json` appears as a card automatically (add a glyph to `CARD` in `home.js` for a figure). The share image `og.png` (1200×630) is rendered from `data/ledger.json` by `scripts/og/` (`node scripts/og/shoot.mjs`).
