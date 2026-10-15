"""Build the story page from data.json. Standard library only: python3 -I story-src/build.py

Writes docs/research/integer-multiplication/story/index.html plus its page.css and page.js.
The page uses the Foundation0 site chrome and tokens (docs/assets/f0.css, f0.js); the text and every
number come from BODY below and data.json, unchanged since the essay was published on 13 Oct 2026.
Corrections are added in their own section, never by editing the essay's words."""
import json, os, datetime, html

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'data.json')))
OUTDIR = os.path.join(HERE, '..', 'docs', 'research', 'integer-multiplication', 'story')
UTC = datetime.timezone.utc


def ts(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC).timestamp()


def nice_ticks(vmax, want=4):
    """Round tick step at or above vmax/want, from the 1-2-5 ladder."""
    import math
    raw = vmax / want
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 5, 10) if m * mag >= raw)
    out, v = [], 0.0
    while True:                      # always close above vmax so no mark overflows
        out.append(round(v, 12))
        if v >= vmax:
            return out
        v += step


def kdec(x):
    """A kappa as the decimal it was recorded as: the shortest string that reads back as the same float
    (0.0004609169, not 0.000460916899999999998)."""
    t = repr(float(x))
    return t if 'e' not in t else format(x, '.20f').rstrip('0')


def utc_label(s):
    d = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return f'{d.day} {d.strftime("%b")} {d.year}, {d.strftime("%H:%M")} UTC'


def line_chart(points, w=760, h=320, pad=(28, 18, 34, 64)):
    """Single-series time/value line. pad = top,right,bottom,left."""
    pt, pr, pb, pl = pad
    xs = [ts(p['t']) for p in points]
    ys = [p['k'] for p in points]
    ticks = nice_ticks(max(ys))
    y0, y1 = 0.0, ticks[-1]
    # start the x domain at midnight of the first day so every day gets a label
    x0 = datetime.datetime.fromtimestamp(min(xs), UTC).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()
    x1 = max(xs)
    px = lambda x: pl + (x - x0) / (x1 - x0) * (w - pl - pr)
    py = lambda y: h - pb - (y - y0) / (y1 - y0) * (h - pt - pb)
    out = [f'<svg class="chart st-line" viewBox="0 0 {w} {h}" role="group" '
           f'aria-label="Reviewed kappa over time, {points[0]["k"]} to {points[-1]["k"]}. Each point can be focused.">']
    # y gridlines + ticks
    for v in ticks:
        y = py(v)
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{pl-10}" y="{y+4:.1f}" class="tick tick-y" aria-hidden="true">{v:.4f}</text>')
    # x ticks, one per day
    day = datetime.datetime.fromtimestamp(x0, UTC).replace(hour=0, minute=0, second=0)
    while day.timestamp() <= x1:
        if day.timestamp() >= x0:
            x = px(day.timestamp())
            out.append(f'<line x1="{x:.1f}" y1="{pt}" x2="{x:.1f}" y2="{h-pb}" class="grid"/>')
            out.append(f'<text x="{x:.1f}" y="{h-pb+20}" class="tick tick-x" aria-hidden="true">{day.strftime("%b %-d")}</text>')
        day += datetime.timedelta(days=1)
    out.append(f'<line x1="{pl}" y1="{h-pb}" x2="{w-pr}" y2="{h-pb}" class="axis"/>')
    # step-and-rise path: the certificate holds a value until it is replaced
    d = []
    for i, p in enumerate(points):
        x, y = px(ts(p['t'])), py(p['k'])
        if i == 0:
            d.append(f'M {x:.1f} {y:.1f}')
        else:
            d.append(f'L {x:.1f} {py(points[i-1]["k"]):.1f} L {x:.1f} {y:.1f}')
    d.append(f'L {px(x1):.1f} {py(points[-1]["k"]):.1f}')
    out.append(f'<path d="{" ".join(d)}" class="series"/>')
    for p in points:
        x, y = px(ts(p['t'])), py(p['k'])
        lab = f'{utc_label(p["t"])}: kappa {kdec(p["k"])}'
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="dot" tabindex="0" role="img" aria-label="{lab}" '
                   f'data-t="{p["t"][:16].replace("T"," ")}Z" data-k="&#954; = {kdec(p["k"])}"/>')
    # last value, direct-labelled
    lx, ly = px(ts(points[-1]['t'])), py(points[-1]['k'])
    out.append(f'<text x="{lx-8:.1f}" y="{ly-14:.1f}" class="lastlabel" aria-hidden="true">{points[-1]["k"]:.6f}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def bar_chart(rows, key, label, w=360, h=190, pad=(14, 10, 30, 34)):
    pt, pr, pb, pl = pad
    vals = [r[key] for r in rows]
    ticks = nice_ticks(max(vals), want=3)
    y1 = ticks[-1]
    n = len(rows)
    bw = (w - pl - pr) / n * 0.62
    gap = (w - pl - pr) / n
    py = lambda v: h - pb - v / y1 * (h - pt - pb)
    out = [f'<svg class="chart small" viewBox="0 0 {w} {h}" role="group" aria-label="{label}, by day of October. Each bar can be focused.">']
    for v in ticks:
        y = py(v)
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{pl-7}" y="{y+4:.1f}" class="tick tick-y" aria-hidden="true">{int(v)}</text>')
    for i, r in enumerate(rows):
        x = pl + gap * i + (gap - bw) / 2
        y = py(r[key])
        bh = h - pb - y
        rr = min(3.0, bh / 2, bw / 2)
        # rounded at the data end, square at the baseline
        dpath = (f'M {x:.1f} {h-pb:.1f} V {y+rr:.1f} Q {x:.1f} {y:.1f} {x+rr:.1f} {y:.1f} '
                 f'H {x+bw-rr:.1f} Q {x+bw:.1f} {y:.1f} {x+bw:.1f} {y+rr:.1f} V {h-pb:.1f} Z')
        out.append(f'<path d="{dpath}" class="bar" tabindex="0" role="img" aria-label="{r["d"]}: {r[key]} {label.lower()}" '
                   f'data-t="{r["d"]}" data-k="{r[key]} {label.lower()}"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" class="barval" aria-hidden="true">{r[key]}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{h-pb+18}" class="tick tick-x" aria-hidden="true">{r["d"][-2:]}</text>')
    out.append(f'<line x1="{pl}" y1="{h-pb}" x2="{w-pr}" y2="{h-pb}" class="axis"/>')
    out.append('</svg>')
    return '\n'.join(out)


def kappa_table(points):
    rows = ''.join(f'<tr><td>{utc_label(p["t"])}</td><td class="n">{kdec(p["k"])}</td></tr>' for p in points)
    return ('<table class="tbl"><caption>The reviewed constant, each time the certificate changed</caption>'
            f'<thead><tr><th>Selected (UTC)</th><th class="n">&kappa;</th></tr></thead><tbody>{rows}</tbody></table>')


def day_table(rows):
    body = ''.join(f'<tr><td>{r["d"]}</td><td class="n">{r["prs"]}</td><td class="n">{r["new"]}</td></tr>' for r in rows)
    return ('<table class="tbl"><caption>Daily activity</caption><thead><tr><th>Day (UTC)</th>'
            f'<th class="n">Pull requests opened</th><th class="n">First-time contributors</th></tr></thead><tbody>{body}</tbody></table>')


k = D['kappa']
r = D['repo']
grow = k[-1]['k'] / k[0]['k']
AS_OF = utc_label(D['as_of'][:16] + ':00Z') if len(D['as_of']) == 17 else D['as_of']

# The site's own record file: its last reviewed record is the no-JavaScript end of the hero sparkline (the page
# replaces it with the live value). The essay's own numbers stay those of data.json.
HIST = json.load(open(os.path.join(HERE, '..', 'docs', 'research', 'integer-multiplication', 'kappa-history.json')))
SNAPREC = [x for x in HIST['records'] if x.get('status') == 'reviewed' and x.get('decimal')][-1]


def spark(points, snap, as_of):
    """The hero sparkline: the essay's reviewed steps (9 to 13 Oct), then a dashed step to the record now in a
    separate "now" column. No text inside the SVG, so it scales to any width; labels sit in the HTML."""
    T0, T1 = ts('2026-10-09T00:00:00Z'), ts('2026-10-14T00:00:00Z')
    X = lambda t: 6 + (t - T0) / (T1 - T0) * 334
    Y = lambda v: 112 - min(v, 0.0019) / 0.002 * 100
    out = [f'<svg id="sp-svg" class="st-sp" viewBox="0 0 400 120" role="img" data-first="{kdec(points[0]["k"])}" '
           f'aria-label="The reviewed constant rose step by step from {kdec(points[0]["k"])} on 9 October to '
           f'{kdec(points[-1]["k"])} by the essay&#8217;s snapshot, and reached {snap["decimal"]} by {utc_label(snap["t"])}.">']
    for v in (0.0005, 0.001, 0.0015):
        out.append(f'<line x1="0" y1="{Y(v):.1f}" x2="400" y2="{Y(v):.1f}" class="grid"/>')
    out.append('<line x1="0" y1="112" x2="400" y2="112" class="axis"/>')
    for d in range(9, 15):
        x = X(ts(f'2026-10-{d:02d}T00:00:00Z'))
        out.append(f'<line x1="{x:.1f}" y1="112" x2="{x:.1f}" y2="116" class="axis"/>')
    out.append('<path d="M343 118L347 106M348 118L352 106" class="axis"/>')
    d = []
    for i, p in enumerate(points):
        x, y = X(ts(p['t'])), Y(p['k'])
        d.append(f'M{x:.1f} {y:.1f}' if i == 0 else f'H{x:.1f}V{y:.1f}')
    xa, ya = X(ts(as_of)), Y(points[-1]['k'])
    d.append(f'H{xa:.1f}')
    out.append(f'<path d="{"".join(d)}" class="series"/>')
    yn = Y(float(snap['decimal']))
    out.append(f'<path id="sp-ext" class="ext" data-x0="{xa:.1f}" data-y0="{ya:.1f}" d="M{xa:.1f} {ya:.1f}H352V{yn:.1f}H378"/>')
    for p in points:
        out.append(f'<circle cx="{X(ts(p["t"])):.1f}" cy="{Y(p["k"]):.1f}" r="2.6" class="dot" '
                   f'data-t="{p["t"][:16].replace("T", " ")}Z" data-k="&#954; = {kdec(p["k"])}"/>')
    out.append(f'<circle id="sp-dot" cx="378" cy="{yn:.1f}" r="5" class="now" data-t="snapshot &#183; {utc_label(snap["t"])}" '
               f'data-k="&#954; = {snap["decimal"]}"/>')
    out.append('</svg>')
    return '\n'.join(out)


# "Break it": the block of Aska's PR #469 as claimed, and the one inequality at the heart of a kappa claim,
# bill(a) = sum_r n_r (r/m)^(1-a) / W + charge * E * m^(a-1) / W <= 1 with a = kappa/(1-kappa)
# (the race's autoresearch.md section 2; the same counts as the budget figure on the project page).
CK_M, CK_W = 78, 1200
CK_COUNTS = {1: 26411, 2: 11209, 3: 3201, 4: 3465, 5: 1089, 6: 660, 7: 55, 8: 99, 14: 1, 56: 184}
CK_KAPPA = '0.001350580884553120'


def bill_minus_one(counts, kstr):
    """bill - 1 at the claimed kappa, to 80 significant digits (the page re-does this with whole numbers)."""
    from decimal import Decimal, getcontext
    getcontext().prec = 80
    k = Decimal(kstr)
    a = k / (1 - k)
    m, W = Decimal(CK_M), Decimal(CK_W)
    bill = sum(Decimal(n) * (Decimal(rr) / m) ** (1 - a) for rr, n in counts.items()) / W
    bill += Decimal(194688) / Decimal(10) ** 16 * sum(counts.values()) * m ** (a - 1) / W
    return bill - 1


def sci_html(x):
    """1 - 1.073 x 10^-18, as HTML, for a small signed Decimal x = bill - 1."""
    sgn = '&minus;' if x < 0 else '+'
    t = f'{abs(x):.3e}'
    mant, ex = t.split('e')
    return f'1 {sgn} {mant} &times; 10<sup>{int(ex):d}</sup>'.replace('<sup>-', '<sup>&minus;')


CK_D = bill_minus_one(CK_COUNTS, CK_KAPPA)
CK_INPUTS = ''.join(
    f'<label class="st-ck-n"><span>size {rr}</span><input type="text" inputmode="numeric" pattern="[0-9]*" maxlength="8" spellcheck="false" autocomplete="off" '
    f'value="{n}" data-r="{rr}" aria-label="Jobs of size {rr}"></label>' for rr, n in CK_COUNTS.items())
CHECK = f"""<figure class="fig frame st-check" id="check" aria-labelledby="ck-title">
  <div class="fig-head">
    <p class="fig-title" id="ck-title">Check a claim yourself, then break it</p>
    <p class="fig-how"><b>How to read:</b> below is the block from Aska&rsquo;s PR #469 as it was claimed: how many child jobs of each size it hands down, and the &kappa; it says that gives. The checker recomputes the block&rsquo;s bill at that &kappa; and accepts only if the bill stays under 1. Press &ldquo;Break it&rdquo; to raise the claim by one unit in its last digit, or change any count.</p>
  </div>
  <div class="st-ck">
    <div class="st-ck-claim">
      <label class="st-ck-k" for="ck-k">Claimed &kappa;</label>
      <input id="ck-k" class="st-ck-in" type="text" inputmode="decimal" value="{CK_KAPPA}" spellcheck="false" autocomplete="off">
      <p class="st-ck-k st-ck-sub">Child jobs by size <i>r</i> (block width <i>m</i> = 78, <i>W</i> = 1,200 roles)</p>
      <div class="st-ck-grid">{CK_INPUTS}</div>
    </div>
    <div class="st-ck-out" id="ck-out" aria-live="polite">
      <p class="st-ck-verdict ok" id="ck-verdict">Accepted: the bill stays under 1.</p>
      <p class="st-ck-bill">Bill at the claimed &kappa;: <span id="ck-bill">{sci_html(CK_D)}</span></p>
      <p class="st-ck-time" id="ck-time">Checked when this page was built, to 80 digits.</p>
    </div>
  </div>
  <div class="fig-ctrl" role="group" aria-label="Checker controls">
    <span class="ctrl-label">Ctrl //</span>
    <button class="tbtn break" type="button" id="ck-break" aria-pressed="false">Break it</button>
    <button class="tbtn" type="button" id="ck-reset">Restore the claim</button>
  </div>
  <figcaption class="fig-foot"><span>Your browser recomputes bill(<i>a</i>) = &Sigma;<sub><i>r</i></sub> <i>n</i><sub><i>r</i></sub>&#8239;(<i>r</i>/<i>m</i>)<sup>1&minus;<i>a</i></sup>&#8239;/&#8239;<i>W</i> plus a tiny insurance charge, with <i>a</i> = &kappa;/(1&minus;&kappa;), in whole-number arithmetic to 60 decimal places, and gives a verdict only when the bill is further from 1 than any rounding could reach. This re-does the one inequality at the heart of a claim; it is not the race&rsquo;s own checker, and it does not check that the counts come from a real construction.</span><span class="fig-src">Source: PR #469 head <a href="https://github.com/CrocSwap/integer-mult-bounds/pull/469">a820816f</a>, <code>PROOF.md</code>; the bill as in the race&rsquo;s <a href="https://github.com/CrocSwap/integer-mult-bounds/blob/main/autoresearch.md">autoresearch.md</a>; the same block as the <a href="../#budget">budget figure</a> on the project page.</span></figcaption>
</figure>"""

# Page CSS (written to story/page.css). Tokens only; one page token for the series colour, validated
# with the dataviz palette script beside the site's chart surfaces (light #2a5fb0, dark #4f90e3).
CSS = """/* The story page (research/integer-multiplication/story). Generated by story-src/build.py: edit there.
   f0.css tokens only, plus --mark-im for the series (validated: light #2a5fb0, dark #4f90e3). */
:root { --mark-im: #2a5fb0; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --mark-im: #4f90e3; } }
:root[data-theme="dark"] { --mark-im: #4f90e3; }

.st-hero .wrap { align-items: center; }
.st-hero .dek a { white-space: nowrap; }
.st-hero .ph-text { min-width: 0; }
.st-hero .h1 { max-width: 16ch; }
.st-hero .dek { max-width: 54ch; }
.st-hero .dek strong { color: var(--ink); font-weight: 600; }
.st-spark { align-self: center; }
.st-sp-stage { position: relative; margin-top: 12px; background: var(--bg-1); border: 1px solid var(--line); padding: 12px 12px 26px; }
.st-sp { display: block; width: 100%; height: auto; overflow: visible; }
.st-sp .grid { stroke: var(--grid); stroke-width: 1; vector-effect: non-scaling-stroke; }
.st-sp .axis { stroke: var(--line-ui); stroke-width: 1; fill: none; vector-effect: non-scaling-stroke; }
.st-sp .series { fill: none; stroke: var(--mark-im); stroke-width: 2; stroke-linejoin: round; vector-effect: non-scaling-stroke; }
.st-sp .ext { fill: none; stroke: var(--mark-im); stroke-width: 1.6; stroke-dasharray: 4 3; vector-effect: non-scaling-stroke; }
.st-sp .dot { fill: var(--mark-im); stroke: var(--bg-1); stroke-width: 1.5; vector-effect: non-scaling-stroke; }
.st-sp .now { fill: var(--st-verified); stroke: var(--bg-1); stroke-width: 2; vector-effect: non-scaling-stroke; }
.st-sp-axis { position: absolute; left: 12px; right: 12px; bottom: 6px; height: 16px; }
.st-sp-axis span { position: absolute; transform: translateX(-50%); font: 400 11.5px/16px var(--f-mono); color: var(--ink-3); white-space: nowrap; }
.st-sp-axis span:first-child { transform: none; }
.st-sp-axis span:last-child { transform: translateX(-70%); }
.st-sp-facts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); margin: 12px 0 0; }
.st-sp-facts > div { background: var(--bg-2); padding: 9px 10px; min-width: 0; }
.st-sp-facts dt { font: 500 11px/1.35 var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--ink-3); }
.st-sp-facts dd { margin: 4px 0 0; font: 500 15px/1.3 var(--f-mono); color: var(--ink); overflow-wrap: anywhere; }
.st-sp-facts dd small { font: 400 12px var(--f-mono); color: var(--ink-2); margin-left: 4px; }
@media (max-width: 420px) { .st-sp-facts { grid-template-columns: minmax(0, 1fr); } }
.st-spark .fig-foot { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; }
.st-open { margin: var(--s-6) 0 0; }
.st-open-k { font: 500 11px/1.3 var(--f-mono); letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 8px; }
.st-open p + p { font: 400 var(--fs-lede)/1.5 var(--f-serif); color: var(--ink); max-width: 60ch; }
.st-open strong { font-weight: 600; }

/* "Break it": the exact checker */
.st-check { margin-top: var(--s-6); }
.st-ck { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: 14px 22px; margin-top: 14px; padding: 14px; background: var(--bg-1); border: 1px solid var(--line); }
@media (max-width: 720px) { .st-ck { grid-template-columns: minmax(0, 1fr); } }
.st-ck-k { display: block; font: 500 11px/1.35 var(--f-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--ink-3); }
.st-ck-sub { margin-top: 14px; text-transform: none; letter-spacing: .02em; font-size: 12px; }
.st-ck-in { display: block; width: 100%; margin-top: 6px; padding: 8px 10px; min-height: 44px; font: 500 clamp(15px, 1vw + 11px, 19px)/1.3 var(--f-mono); color: var(--ink); background: var(--bg-2); border: 1px solid var(--line-ui); border-radius: var(--r-btn); }
.st-ck-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 8px; margin-top: 8px; }
@media (max-width: 520px) { .st-ck-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.st-ck-n { display: grid; gap: 3px; font: 400 12px/1.3 var(--f-mono); color: var(--ink-2); min-width: 0; }
.st-ck-n input { width: 100%; min-width: 0; min-height: 40px; padding: 6px 8px; font: 500 14px var(--f-mono); color: var(--ink); background: var(--bg-2); border: 1px solid var(--line-ui); border-radius: var(--r-btn); }
.st-ck-in:focus-visible, .st-ck-n input:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.st-ck-n input.changed, .st-ck-in.changed { border-color: var(--hair); box-shadow: inset 0 0 0 1px var(--hair); }
.st-ck-out { display: grid; align-content: start; gap: 8px; padding: 12px 14px; background: var(--bg-2); border: 1px solid var(--line); border-left: 3px solid var(--st-verified); }
.st-ck-out.no { border-left-color: var(--st-contested); }
.st-ck-out.unsure { border-left-color: var(--st-preprint); }
.st-ck-verdict { font: 600 var(--fs-ui)/1.35 var(--f-sans); color: var(--ink); }
.st-ck-verdict::before { content: "✓ "; color: var(--st-verified); }
.st-ck-out.no .st-ck-verdict::before { content: "✕ "; color: var(--st-contested); }
.st-ck-out.unsure .st-ck-verdict::before { content: "? "; color: var(--ink-3); }
.st-ck-bill { font: 400 var(--fs-sm)/1.5 var(--f-sans); color: var(--ink-2); }
.st-ck-bill span { font: 500 15px var(--f-mono); color: var(--ink); white-space: nowrap; }
.st-ck-time { font: 400 12.5px/1.45 var(--f-mono); color: var(--ink-3); }
.st-check .fig-ctrl { margin-top: 12px; }
html:not(.js) .st-ck input { pointer-events: none; }

.st-sec { padding-block: clamp(40px, 6vw, 80px); }
.st-sec .sec-head { margin-bottom: var(--s-4); }
.st-h2 { font: 600 clamp(24px, 1.6vw + 16px, 36px)/1.12 var(--f-sans); letter-spacing: -.025em; max-width: 24ch; margin-bottom: var(--s-5); }
.st-read .prose { max-width: none; }
.st-read .prose em { font-style: italic; }
.st-read > .fig, .st-read > .statrow, .st-read > .callout { margin-top: var(--s-6); }
.st-read > .callout { max-width: none; }

.chart { width: 100%; height: auto; display: block; overflow: visible; margin-top: 10px; }
.chart .grid { stroke: var(--grid); stroke-width: 1; }
.chart .axis { stroke: var(--line-ui); stroke-width: 1; }
.chart .series { fill: none; stroke: var(--mark-im); stroke-width: 2; stroke-linejoin: round; }
.chart .dot { fill: var(--mark-im); stroke: var(--bg-1); stroke-width: 2; cursor: default; }
.chart .dot:focus { outline: none; }
.chart .dot:focus-visible, .chart .dot:hover { stroke: var(--ink); }
.chart .bar { fill: var(--mark-im); }
.chart .bar:focus { outline: none; }
.chart .bar:focus-visible, .chart .bar:hover { stroke: var(--ink); stroke-width: 1.5; }
.chart .tick { fill: var(--ink-3); font: 11px var(--f-mono); font-variant-numeric: tabular-nums; }
.chart .tick-y { text-anchor: end; } .chart .tick-x { text-anchor: middle; }
.chart .barval { fill: var(--ink-2); font: 600 11px var(--f-mono); text-anchor: middle; }
.chart .lastlabel { fill: var(--ink); font: 600 13px var(--f-mono); text-anchor: end; }
.st-pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 12px; }
@media (max-width: 640px) { .st-pair { grid-template-columns: minmax(0, 1fr); } }
.st-pair figcaption, .st-cap { font: 400 12.5px/1.5 var(--f-sans); color: var(--ink-3); margin-top: 6px; }
.st-stage { background: var(--bg-1); border: 1px solid var(--line); padding: 12px 12px 8px; margin-top: 14px; }
.st-gf { margin-top: var(--s-5); max-width: 560px; }
.st-gf td.n, .st-gf th.n { text-align: right; font-family: var(--f-mono); font-variant-numeric: tabular-nums; }
.st-colophon { margin-top: var(--s-7); padding-top: var(--s-4); border-top: 1px dashed var(--line-ui); font: 400 var(--fs-xs)/1.6 var(--f-sans); color: var(--ink-3); }
.st-fix { list-style: none; margin: var(--s-5) 0 0; padding: 0; display: grid; gap: 1px; background: var(--line); border: 1px solid var(--line); }
.st-fix li { background: var(--bg-2); padding: 14px 16px; display: grid; gap: 6px; }
.st-fix .q { font: italic 400 var(--fs-sm)/1.55 var(--f-serif); color: var(--ink); }
.st-fix .q::before { content: "The essay says: "; font: 500 11px/1.4 var(--f-mono); font-style: normal; letter-spacing: .1em; text-transform: uppercase; color: var(--st-contested); margin-right: 4px; }
.st-fix .a { font: 400 var(--fs-sm)/1.55 var(--f-sans); color: var(--ink-2); }
.st-fix .a b { color: var(--ink); font-weight: 600; }
.st-end { padding: 0 0 var(--sec-pad); }
.st-narrow { display: none; }
@media (max-width: 560px) { .st-wide { display: none; } .st-narrow { display: block; } }
.st-read .statrow { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 560px) { .st-read .statrow { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.chart.small .tick, .chart.small .barval { font-size: 13px; }
.chart.st-line .tick { font-size: 12px; }
.st-end .prevnext { margin-top: 0; }
"""

# Page JS (written to story/page.js): the shared tooltip on hover and keyboard focus.
JS = r"""/* The story page. Generated by story-src/build.py: edit there.
   1. The shared tooltip (F0.tip) for every chart mark on hover, tap and keyboard focus; the tables under each
      chart hold the same values.
   2. The hero sparkline's last step: the reviewed kappa now, through F0.kappa() (live, else this site's snapshot),
      always labelled with which and when.
   3. "Break it": the bill of a kappa claim recomputed in whole-number (BigInt) arithmetic, so one unit in the
      18th decimal place decides it. */
(function () {
  'use strict';
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function utc(iso) { var d = new Date(iso); if (isNaN(d)) return String(iso || '');
    return d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear() + ', ' + String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0') + ' UTC'; }

  function tips(F0) {
    document.querySelectorAll('[data-t]').forEach(function (el) {
      function show(x, y) { F0.tip.show('<p class="tip-k">' + F0.esc(el.getAttribute('data-t')) + '</p><p class="tip-t">' + F0.esc(el.getAttribute('data-k')) + '</p>', x, y); }
      el.addEventListener('pointermove', function (e) { show(e.clientX, e.clientY); });
      el.addEventListener('pointerleave', function () { F0.tip.hide(); });
      el.addEventListener('focus', function () { var b = el.getBoundingClientRect(); show(b.right, b.top); });
      el.addEventListener('blur', function () { F0.tip.hide(true); });
    });
  }

  function spark(F0) {
    var svg = document.getElementById('sp-svg'); if (!svg || !F0.kappa) return;
    F0.kappa().then(function (k) {
      var v = parseFloat(k.decimal); if (!(v > 0)) return;
      var ext = document.getElementById('sp-ext'), dot = document.getElementById('sp-dot');
      var y = (112 - Math.min(v, 0.0019) / 0.002 * 100).toFixed(1);
      ext.setAttribute('d', 'M' + ext.getAttribute('data-x0') + ' ' + ext.getAttribute('data-y0') + 'H352V' + y + 'H378');
      dot.setAttribute('cy', y);
      var when = F0.kappaWhen ? F0.kappaWhen(k, utc) : utc(k.at);
      dot.setAttribute('data-t', when); dot.setAttribute('data-k', 'κ = ' + k.decimal + (k.pr ? ' · PR #' + (+k.pr) : ''));
      var first = parseFloat(svg.getAttribute('data-first'));
      document.getElementById('sp-now').innerHTML = F0.esc(v.toFixed(6)) + ' <small>' + (v / first).toFixed(2) + '&times;</small>';
      document.getElementById('sp-now-k').textContent = k.source === 'live' ? 'Now, read live' : 'Last reviewed record';
      document.getElementById('sp-when').textContent = when;
      var d = document.querySelector('#sp-chip .dot'); if (d) d.className = 'dot ' + (k.source === 'live' ? 'live' : 'stale');
      svg.setAttribute('aria-label', svg.getAttribute('aria-label').replace(/, and reached .*$/, ', and ' + (k.source === 'live' ? 'is now ' : 'reached ') + k.decimal + ' (' + when + ').'));
    }).catch(function () {});
  }

  /* ---- the checker: bill(a) = sum n_r (r/m)^(1-a) / W + charge * E * m^(a-1) / W, a = k/(1-k) ---- */
  function checker() {
    var root = document.getElementById('check'); if (!root || typeof BigInt !== 'function') return;
    var B = BigInt, ZERO = B(0), ONE = B(1), TWO = B(2);
    function pow10(n) { var r = ONE; for (var i = 0; i < n; i++) r *= B(10); return r; }
    var S = pow10(60), G = pow10(72), GS = pow10(12), MARGIN = pow10(10); /* verdicts need |bill - 1| > 10^-50 */
    function atanhInv(q, scale) { var sum = ZERO, k = ZERO, qq = B(q), pw = qq; for (;;) { var t = scale / ((TWO * k + ONE) * pw); if (t === ZERO) break; sum += t; k += ONE; pw *= qq * qq; } return sum; }
    var ln2 = TWO * atanhInv(3, G), ln3 = ln2 + TWO * atanhInv(5, G), ln5 = TWO * ln2 + TWO * atanhInv(9, G);
    var LN = { 2: ln2, 3: ln3, 5: ln5, 7: ln5 + TWO * atanhInv(6, G), 13: TWO * ln2 + ln3 + TWO * atanhInv(25, G) };
    function lnInt(n) { var s = ZERO; [2, 3, 5, 7, 13].forEach(function (p) { while (n % p === 0) { s += LN[p]; n /= p; } }); return s; }
    function expS(x) { var sum = S, t = S, k = ONE; for (;;) { t = t * x / (k * S); if (t === ZERO) break; sum += t; k += ONE; } return sum; }
    var M_ = 78, W_ = 1200, MW = B(M_ * W_), LNM = lnInt(M_);
    function bill(counts, kstr) { /* bill - 1, in units of 10^-60 */
      var parts = kstr.split('.'), kn = B(parts[0] + parts[1]), kd = pow10(parts[1].length), an = kn, ad = kd - kn, total = ZERO, E = ZERO;
      counts.forEach(function (c) { var n = B(c.n); E += n; total += n * B(c.r) * expS((LNM - lnInt(c.r)) / GS * an / ad) / MW; });
      total += B(194688) * E * expS(LNM / GS * an / ad) / (pow10(16) * MW);
      return total - S;
    }
    function sci(d) {
      var neg = d < ZERO, s = (neg ? -d : d).toString(), e = s.length - 1 - 60;
      if (e > -3) return '&asymp; ' + (1 + (neg ? -1 : 1) * Number(s.slice(0, 15)) * Math.pow(10, e - Math.min(14, s.length - 1))).toPrecision(5);
      var mant = s.charAt(0) + (s.length > 1 ? '.' + (s.slice(1, 4) + '000').slice(0, 3) : '');
      return '1 ' + (neg ? '&minus;' : '+') + ' ' + mant + ' &times; 10<sup>' + (e < 0 ? '&minus;' + (-e) : e) + '</sup>';
    }
    var kin = document.getElementById('ck-k'), out = document.getElementById('ck-out'), verdict = document.getElementById('ck-verdict');
    var billEl = document.getElementById('ck-bill'), timeEl = document.getElementById('ck-time'), brk = document.getElementById('ck-break'), reset = document.getElementById('ck-reset');
    var ins = [].slice.call(root.querySelectorAll('.st-ck-n input'));
    var K0 = kin.value, N0 = ins.map(function (i) { return i.value; });
    function bump(k) { var p = k.split('.'), d = p[1].length, n = (B(p[0] + p[1]) + ONE).toString(); while (n.length < d + 1) n = '0' + n; return n.slice(0, n.length - d) + '.' + n.slice(n.length - d); }
    function run() {
      var kstr = kin.value.trim(), bad = '';
      kin.classList.toggle('changed', kstr !== K0);
      ins.forEach(function (i, j) { i.classList.toggle('changed', i.value !== N0[j]); });
      if (!/^0\.\d{1,40}$/.test(kstr) || /^0\.0+$/.test(kstr)) bad = 'κ must be a decimal between 0 and 1, such as 0.001350580884553120.';
      var counts = ins.map(function (i) { var v = i.value.trim(); if (!/^\d{1,8}$/.test(v)) bad = bad || 'Each count must be a whole number.'; return { r: +i.getAttribute('data-r'), n: v || '0' }; });
      if (bad) { out.className = 'st-ck-out no'; verdict.textContent = 'Rejected: not a valid claim.'; billEl.textContent = '—'; timeEl.textContent = bad; return; }
      var t0 = performance.now(), d = bill(counts, kstr), dt = performance.now() - t0;
      if (d <= -MARGIN) { out.className = 'st-ck-out'; verdict.textContent = 'Accepted: the bill stays under 1.'; }
      else if (d >= MARGIN) { out.className = 'st-ck-out no'; verdict.textContent = 'Rejected: the bill goes over 1.'; }
      else { out.className = 'st-ck-out unsure'; verdict.textContent = 'Too close to 1 to call at 60 decimal places.'; }
      billEl.innerHTML = sci(d);
      timeEl.textContent = 'Checked in ' + (dt < 0.1 ? 'under 0.1' : dt.toFixed(1)) + ' ms, in your browser.';
    }
    kin.addEventListener('input', function () { brk.setAttribute('aria-pressed', 'false'); run(); });
    ins.forEach(function (i) { i.addEventListener('input', run); });
    brk.addEventListener('click', function () {
      var on = brk.getAttribute('aria-pressed') !== 'true';
      brk.setAttribute('aria-pressed', on ? 'true' : 'false');
      kin.value = on ? bump(K0) : K0; run();
    });
    reset.addEventListener('click', function () { kin.value = K0; ins.forEach(function (i, j) { i.value = N0[j]; }); brk.setAttribute('aria-pressed', 'false'); run(); });
    run();
  }

  function boot() {
    var F0 = window.F0;
    try { checker(); } catch (e) { console.error(e); }
    if (!F0) return;
    tips(F0); spark(F0);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
"""

# The essay. Its words and numbers are as published on 13 Oct 2026; only the markup around them changed.
LEDE = (f"""On 7 October someone opened a public repository holding one question: how much
faster than <em>n</em>&#8239;log&#8239;<em>n</em> can you <strong>prove</strong> that two large
numbers can be multiplied? Five days later it has {r['prs']} pull requests from
{r['authors']} people, and the reviewed answer has moved {grow:.1f}&times;.""")


def sec(num, sid, label, title, inner, alt=False):
    return (f'<section class="sec st-sec{" alt" if alt else ""}" id="{sid}" data-index="{label}" data-num="{num}" aria-labelledby="{sid}-h">'
            f'<div class="read st-read"><div class="sec-head"><p class="sec-label"><b>{num}</b><i>//</i>{label}</p></div>'
            f'<h2 class="st-h2" id="{sid}-h">{title}</h2>{inner}</div></section>')


S_NUMBER = f"""<section class="sec st-sec" id="number" data-index="The constant" data-num="00" aria-labelledby="number-h">
<div class="read st-read">
<div class="sec-head"><p class="sec-label"><b>00</b><i>//</i>The constant</p><span class="chip">Snapshot &middot; {AS_OF}</span></div>
<h2 class="st-h2 sr-only" id="number-h">The reviewed constant</h2>
<aside class="callout caveat"><p class="c-k">Read with care</p><p>This essay was written on 13 October 2026, and its figures are as of {AS_OF}. The race has moved since: the <a href="../">project page</a> shows the current reviewed &kappa;, read live from the race&rsquo;s own record file. Six lines have <a href="#corrections">corrections</a>, kept separate so the essay&rsquo;s words stay as published.</p></aside>
<div class="st-open"><p class="st-open-k">The essay, as published</p><p>{LEDE}</p></div>
<figure class="fig frame">
  <div class="fig-head">
    <p class="fig-title">The reviewed constant &kappa;, as recorded in the repository's own certificate</p>
    <p class="fig-how"><b>How to read:</b> each step is a new value the maintainer selected; the line holds it until the next. Point at or Tab to a point for its time and value.</p>
  </div>
  <div class="st-stage"><div class="st-wide">{line_chart(k)}</div><div class="st-narrow">{line_chart(k, w=360, h=300, pad=(30, 14, 34, 58))}</div></div>
  <figcaption class="fig-foot"><span>Each step is a new result the maintainer reviewed and selected. Bigger is better:
  the proven running time is <em>n</em>&#8239;(log&#8239;<em>n</em>)<sup>1&#8722;&kappa;</sup>.</span><span class="fig-src">Source: <a href="https://github.com/CrocSwap/integer-mult-bounds/commits/main/certificates/selected-result.json">certificates/selected-result.json</a> history, in <a href="https://github.com/aska-digital/frontier-math/blob/main/story-src/data.json">story-src/data.json</a></span></figcaption>
  <details class="twin"><summary>Show the numbers</summary><div class="table-wrap">{kappa_table(k)}</div></details>
</figure>

<ul class="statrow" aria-label="The repository in numbers, {AS_OF}">
  <li><div class="v">{r['prs']}</div><div class="k">pull requests</div></li>
  <li><div class="v">{r['authors']}</div><div class="k">people</div></li>
  <li><div class="v">{r['merged']}</div><div class="k">merged</div></li>
  <li><div class="v">6</div><div class="k">days old</div></li>
</ul>
</div></section>"""

S_WHY = sec('01', 'why', 'Why it moved', 'Why it moved', f"""<div class="prose">
<p>Two things were different. The first is obvious: a model will read a long technical argument
with you and draft the next step. That gets you a candidate.</p>
<p>The second matters more. <strong>Every result that moves the number arrives with a script that
checks it.</strong> Nobody has to trust the person who sent it. You run their verifier on your own
machine and it passes or it fails. A wrong answer costs its author some time and costs everyone
else nothing.</p>
<p>That is what makes a crowd usable on a problem like this. Without the check, {r['prs']} pull
requests is just noise nobody can afford to read. With it, the work composes: pull requests
name the exact constructions they build on, and those belong to other people.</p>
</div>
{CHECK}
<figure class="fig frame">
  <div class="fig-head">
    <p class="fig-title">Daily activity</p>
    <p class="fig-how"><b>How to read:</b> one bar per day of October 2026, UTC. Point at or Tab to a bar for its value.</p>
  </div>
  <div class="st-pair">
    <div class="st-stage">{bar_chart(D['per_day'], 'prs', 'Pull requests opened')}
      <p class="st-cap">Pull requests opened, by day of October.</p></div>
    <div class="st-stage">{bar_chart(D['per_day'], 'new', 'First-time contributors')}
      <p class="st-cap">People contributing for the first time.</p></div>
  </div>
  <figcaption class="fig-foot"><span class="fig-src">Source: the GitHub API, as of {AS_OF}, in <a href="https://github.com/aska-digital/frontier-math/blob/main/story-src/data.json">story-src/data.json</a></span></figcaption>
  <details class="twin"><summary>Show the numbers</summary><div class="table-wrap">{day_table(D['per_day'])}</div></details>
</figure>""", alt=True)

S_NOT_ANSWER = sec('02', 'not-answer', 'Most of it is not the answer', 'Most of it is not the answer', f"""<div class="prose">
<p>Look at what the pull requests actually contain and the shape of a working research community
shows up. Alongside the improvements there are independent re-verifications, speedups to other
people's checking scripts, formal proofs in Lean, and a steady stream of honest negative results:
<em>this route is closed, here is the obstruction</em>. Of {r['prs']} pull requests,
{r['merged']} are merged. The rest are not waste. A closed route nobody has to try again is worth
something, and the crowd is cheap enough to afford them.</p>
</div>""")

S_NOT = sec('03', 'not', 'What this is not', 'What this is not', """<div class="prose">
<p>The result is conditional. It inherits a framework from an earlier paper, and the repository
says plainly that its finite checks are not a complete machine-checked theorem, and that none of
this is a claim about how fast your computer multiplies numbers today. The honesty is part of why
it works: the scope of every claim is written down, so the next person knows exactly what they are
standing on.</p>
</div>""", alt=True)

S_OURS = sec('04', 'ours', 'Our part', 'Our part', """<div class="prose">
<p>We have been working in two of these.</p>
<p><strong>Circuit constructions.</strong> A separate repository collects the smallest known
circuits for arithmetic in binary fields, measured in AND and XOR gates. Smaller circuits mean
cheaper encryption work, particularly in secure multi-party computation and zero-knowledge proofs.
We contributed multipliers for four fields it did not cover. Two of them came in below the
published baseline. All five were re-checked by the author against the pack's own verifier,
and merged.</p>
</div>
<div class="table-wrap st-gf">
<table class="tbl">
<tr><th>Field</th><th class="n">Baseline</th><th class="n">Ours</th><th class="n">Saved</th></tr>
<tr><td>GF(2<sup>9</sup>)</td><td class="n">142</td><td class="n">136</td><td class="n">6</td></tr>
<tr><td>GF(2<sup>10</sup>)</td><td class="n">172</td><td class="n">172</td><td class="n">0</td></tr>
<tr><td>GF(2<sup>11</sup>)</td><td class="n">206</td><td class="n">199</td><td class="n">7</td></tr>
<tr><td>GF(2<sup>128</sup>), the GHASH field</td><td class="n">11,972</td><td class="n">11,972</td><td class="n">0</td></tr>
</table>
</div>
<div class="prose" style="margin-top:var(--s-5)">
<p><strong>The exponent race.</strong> We held the top open claim for several hours on 11 October,
at &kappa; = 0.00135058, by re-timing an existing construction. The race has since moved a long way
past it, on a different line of work. That is the honest state of it: a real contribution, briefly
in front, now behind.</p>
</div>""")

S_MATTERS = sec('05', 'matters', 'Why it matters', 'Why it matters', f"""<div class="prose">
<p>The interesting part is not the constant. It is that a machine-checkable problem statement turns
a crowd with good tools into something that functions like a laboratory, in days, at almost no
coordination cost. The number of problems that can be posed this way is much larger than the number
that have been.</p>
</div>
<p class="st-colophon">
Figures read from the repository's own certificate file and the GitHub API,
as of {D['as_of']}. The race is
<a href="https://github.com/CrocSwap/integer-mult-bounds">CrocSwap/integer-mult-bounds</a>,
maintained by Douglas Colkitt. The circuit pack is
<a href="https://github.com/Swapnil-jain/gf2m-circuits">Swapnil-jain/gf2m-circuits</a>.
Numbers change by the hour; rebuild to refresh.
</p>""", alt=True)

S_FIX = sec('06', 'corrections', 'Corrections', 'Corrections, 14 and 15 October 2026', """<p class="lede">Foundation0 checked this essay against the sources before republishing it. Six lines need a note: one leaves out who opened the repository, two have slips, and three say more than the evidence does. The essay above is unchanged; here is what the record supports.</p>
<ol class="st-fix">
  <li><p class="q">On 7 October someone opened a public repository</p>
      <p class="a"><b>Named.</b> The repository was opened by founding member Doug Colkitt (<a href="https://github.com/Mister-Meeseeks">@Mister-Meeseeks</a>), who maintains it and selects every reviewed record.</p></li>
  <li><p class="q">Five days later it has 857 pull requests</p>
      <p class="a"><b>Six days.</b> The repository opened on 7 October and the counts are from 13 October, 08:10 UTC: six days, as the essay&rsquo;s own &ldquo;6 days old&rdquo; tile says.</p></li>
  <li><p class="q">We have been working in two of these.</p>
      <p class="a"><b>Two of what.</b> Two kinds of crowd-checkable problem: circuit constructions, and the exponent race.</p></li>
  <li><p class="q">We held the top open claim for several hours on 11 October.</p>
      <p class="a"><b>Not supported by our own data.</b> Our tracker saw PR #469 (&kappa; = 0.001350580884553120) only between its appearance at 17:32 UTC and the tracker&rsquo;s last snapshot at 17:41 UTC. In that window it was the top open claim, and it was still a draft; higher claims from other contributors (#480 and #505, for example) carry commits from later that day. It was never reviewed, and Aska closed it on 13 October. Read: briefly the top open claim on our tracker. The full account is on the <a href="../#ours">project page</a>.</p></li>
  <li><p class="q">All five were re-checked by the author against the pack's own verifier, and merged.</p>
      <p class="a"><b>Four, not five, and the re-check is ours.</b> The table lists four fields. The repository&rsquo;s history shows the maintainer merged the pull request and credited it in the README; it does not show a re-run by the maintainer. Foundation0 re-ran the pack&rsquo;s verifier on all four circuits on 13 October, and they pass. None of them is a record.</p></li>
  <li><p class="q">Smaller circuits mean cheaper encryption work, particularly in secure multi-party computation and zero-knowledge proofs.</p>
      <p class="a"><b>Too broad.</b> In those settings the cost is driven mostly by AND gates, while XOR gates are nearly free, and every gate these circuits save is an XOR; the AND counts are unchanged. Smaller XOR counts mean less hardware and fewer instructions in bit-sliced software.</p></li>
</ol>
<p class="st-colophon">Corrections compiled from the circuit pack&rsquo;s history (<a href="https://github.com/Swapnil-jain/gf2m-circuits/pull/1">PR #1</a>), this site&rsquo;s tracker feed (<a href="../../../chart-data.json">chart-data.json</a>, generated 11 Oct 2026, 17:41 UTC) and the race&rsquo;s pull requests <a href="https://github.com/CrocSwap/integer-mult-bounds/pull/469">#469</a> and <a href="https://github.com/CrocSwap/integer-mult-bounds/pull/464">#464</a>.</p>""")

HEAD = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>When the crowd gets a frontier model · Foundation0</title>
<meta name="description" content="A public repository moved a research constant 3.6x in four days, with {r['prs']} pull requests from {r['authors']} people. What made it work.">
<meta property="og:type" content="article">
<meta property="og:title" content="When the crowd gets a frontier model · Foundation0">
<meta property="og:description" content="A public repository moved a research constant 3.6x in four days, with {r['prs']} pull requests from {r['authors']} people. What made it work.">
<meta property="og:image" content="../../../assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Foundation0: the Radiant, every ledger milestone as a mark, beside the wordmark.">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#070b0e" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f5f0e6" media="(prefers-color-scheme: light)">
<link rel="icon" type="image/svg+xml" href="../../../assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
<link rel="stylesheet" href="../../../assets/f0.css">
<link rel="stylesheet" href="page.css">
<script>
/* theme + motion bootstrap, before paint: ?theme=dark|light and ?motion=on|off override the stored choice */
(function(){{var d=document.documentElement;d.classList.add('js');try{{var q=new URLSearchParams(location.search),t=q.get('theme')||localStorage.getItem('f0-theme'),m=q.get('motion')||localStorage.getItem('f0-motion');if(t==='dark'||t==='light')d.setAttribute('data-theme',t);if(m==='on'||m==='off')d.setAttribute('data-motion-pref',m);}}catch(e){{}}var r=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,p=d.getAttribute('data-motion-pref');d.setAttribute('data-motion',p?p:(r?'off':'on'));}})();
</script>
<script defer src="../../../assets/f0.js"></script>
<script defer src="page.js"></script>
</head>
<body data-page="research-integer-multiplication-story">
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <clipPath id="zl"><rect x="-50" y="-50" width="50" height="100"/></clipPath>
    <clipPath id="zr"><rect x="0" y="-50" width="50" height="100"/></clipPath>
    <g id="zgeo" fill="none">
      <polygon stroke-width="5" points="40.65,16.84 16.84,40.65 -16.84,40.65 -40.65,16.84 -40.65,-16.84 -16.84,-40.65 16.84,-40.65 40.65,-16.84"/>
      <polygon stroke-width="2.2" opacity=".6" points="40.65,16.84 -40.65,16.84 16.84,-40.65 16.84,40.65 -40.65,-16.84 40.65,-16.84 -16.84,40.65 -16.84,-40.65"/>
      <circle r="16.84" stroke-width="3.4"/>
      <circle r="6.97" stroke-width="3"/>
    </g>
    <symbol id="zero" viewBox="-50 -50 100 100">
      <use href="#zgeo" clip-path="url(#zl)" style="stroke:var(--bio)"/>
      <use href="#zgeo" clip-path="url(#zr)" style="stroke:var(--dig)"/>
    </symbol>
  </defs>
</svg>
<a class="skip" href="#main">Skip to content</a>

<header class="site-head">
  <div class="wrap">
    <a class="brand" href="../../../" aria-label="Foundation0 home"><svg aria-hidden="true"><use href="#zero"/></svg>Foundation0</a>
    <nav class="nav" aria-label="Main">
      <a href="../../../ledger/">Ledger</a><a href="../../../research/" aria-current="page">Research</a><a href="../../../instruments/">Instruments</a><a href="../../../commons/">Commons</a><a href="../../../writing/">Writing</a><a href="../../../charter/">Charter</a>
    </nav>
    <div class="tools">
      <button class="tbtn" type="button" data-motion-toggle aria-pressed="true" aria-label="Pause motion"><span class="ico"></span><span class="t-txt">Motion on</span></button>
      <button class="tbtn" type="button" data-theme-toggle aria-label="Switch theme"><span class="ico"></span><span class="t-txt">Theme</span></button>
    </div>
    <details class="menu">
      <summary class="tbtn" aria-label="Menu"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.4"/></svg><span class="t-txt">Menu</span></summary>
      <nav class="menu-panel" aria-label="Main (compact)">
        <a href="../../../ledger/">Ledger <span>01</span></a><a href="../../../research/" aria-current="page">Research <span>03</span></a><a href="../../../instruments/">Instruments <span>04</span></a><a href="../../../commons/">Commons <span>05</span></a><a href="../../../writing/">Writing <span>06</span></a><a href="../../../charter/">Charter <span>00</span></a>
      </nav>
    </details>
  </div>
</header>
<nav class="hud" data-hud aria-label="On this page"></nav>
"""

HERO = f"""<header class="page-hero has-fig st-hero" style="--acc:var(--acc-intmult)">
  <div class="wrap">
    <div class="ph-text">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="../../../">Home</a></li><li><a href="../../">Research</a></li><li><a href="../">Integer multiplication</a></li><li aria-current="page">The story</li></ol></nav>
      <p class="kicker"><span class="pair" aria-hidden="true"><i></i><i></i></span>Essay &middot; Aska Digital &middot; 13 Oct 2026</p>
      <h1 class="h1">When the crowd gets a frontier model</h1>
      <p class="dek">On 7 October founding member <a href="../../../charter/#m-Mister-Meeseeks">Doug Colkitt</a> opened a public repository around one question: how much faster than <em>n</em>&#8239;log&#8239;<em>n</em> can two large numbers <strong>provably</strong> be multiplied? Within days a crowd of people and their AI agents was moving the answer. Aska Digital&rsquo;s essay of 13 October 2026, kept as published, asks why that worked.</p>
      <div class="meta-row">
        <span class="chip">Snapshot &middot; {AS_OF}</span>
        <span class="badge n">Essay &middot; not peer reviewed</span>
        <a class="chip" href="../">Current record on the project page &rarr;</a>
      </div>
    </div>
    <figure class="ph-fig fig frame st-spark" aria-labelledby="sp-title">
      <div class="fig-head">
        <p class="fig-title" id="sp-title">The reviewed constant &kappa;, 9 October to now</p>
        <p class="fig-how"><b>How to read:</b> each step is a value the race&rsquo;s maintainer selected. The solid line is the essay&rsquo;s data, to {AS_OF}; the dashed step ends at the record now. Point at a dot for its value.</p>
      </div>
      <div class="st-sp-stage">{spark(k, SNAPREC, D['as_of'][:16] + ':00Z')}
        <div class="st-sp-axis" aria-hidden="true"><span style="left:1.5%">9 Oct</span><span style="left:34.9%">11 Oct</span><span style="left:68.3%">13 Oct</span><span style="left:94.5%">now</span></div>
      </div>
      <dl class="st-sp-facts">
        <div><dt>9 Oct, first record</dt><dd>{kdec(k[0]['k'])}</dd></div>
        <div><dt>Essay, 13 Oct</dt><dd>{k[-1]['k']:.6f} <small>{grow:.1f}&times;</small></dd></div>
        <div><dt id="sp-now-k">Last reviewed record</dt><dd id="sp-now">{float(SNAPREC['decimal']):.6f} <small>{float(SNAPREC['decimal']) / k[0]['k']:.2f}&times;</small></dd></div>
      </dl>
      <figcaption class="fig-foot"><a class="chip" id="sp-chip" href="https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json"><span class="dot stale" aria-hidden="true"></span><span id="sp-when">snapshot &middot; {utc_label(SNAPREC['t'])}</span></a><span class="fig-src">Source: <a href="https://github.com/aska-digital/frontier-math/blob/main/story-src/data.json">story-src/data.json</a>; the end point from <a href="https://github.com/CrocSwap/integer-mult-bounds/blob/main/certificates/selected-result.json">selected-result.json</a>, read live, else <a href="../kappa-history.json">kappa-history.json</a>.</span></figcaption>
    </figure>
  </div>
</header>
"""

FOOT = """<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-brand"><svg aria-hidden="true"><use href="#zero"/></svg>Foundation0</div>
        <p>Foundation0 is an independent project, not affiliated with the Asimov estate, his publishers, or Apple TV+. Quotations from Asimov are one sentence each, for commentary.</p>
        <p>Source code under the <a href="https://github.com/aska-digital/frontier-math/blob/main/LICENSE">Apache License 2.0</a>. Every number on this page links to a data file or a source.</p>
      </div>
      <div class="foot-cols">
        <div><h4>Record</h4><ul><li><a href="../../../ledger/">The Ledger</a></li><li><a href="../../../data/ledger.json">Ledger data (JSON)</a></li><li><a href="../../../charter/">Charter</a></li></ul></div>
        <div><h4>Work</h4><ul><li><a href="../../../research/">Research</a></li><li><a href="../../../instruments/">Instruments</a></li><li><a href="../../../commons/">Commons</a></li><li><a href="../../../writing/">Writing</a></li></ul></div>
        <div><h4>Source</h4><ul><li><a href="https://github.com/aska-digital/frontier-math">Repository</a></li><li><a href="https://github.com/aska-digital/frontier-math/issues">Report an error</a></li><li><a href="https://digital.askaconsult.com/">Aska Digital</a></li></ul></div>
      </div>
    </div>
    <div class="stamp">
      <span>Terminus colophon</span>
      <span>Built from <a href="https://github.com/aska-digital/frontier-math/blob/main/story-src/data.json">story-src/data.json</a> by story-src/build.py</span>
      <span class="who"><i style="background:var(--bio)" aria-hidden="true"></i>Human: Ahraz Arifuddin &middot; Aska Digital</span>
      <span class="who"><i style="background:var(--dig)" aria-hidden="true"></i>Digital: Claude (Anthropic)</span>
    </div>
  </div>
</footer>
"""

NAV = """<div class="wrap"><nav class="prevnext" aria-label="More on this race">
  <a href="../"><span>&larr; Back to</span>Integer multiplication below n log n</a>
  <a class="next" href="../live/"><span>Next &rarr;</span>The race tracker (claims feed of 11 Oct)</a>
</nav></div>
"""

page = (HEAD + '<main id="main">\n' + HERO + S_NUMBER + S_WHY + S_NOT_ANSWER + S_NOT + S_OURS + S_MATTERS + S_FIX +
        '<section class="st-end" aria-label="More">' + NAV + '</section>\n</main>\n' + FOOT + '</body>\n</html>\n')

os.makedirs(OUTDIR, exist_ok=True)
for name, text in (('index.html', page), ('page.css', CSS), ('page.js', JS)):
    with open(os.path.join(OUTDIR, name), 'w') as fh:
        fh.write(text)
print('wrote docs/research/integer-multiplication/story/{index.html,page.css,page.js}', len(page), 'bytes;',
      len(k), 'kappa points; growth %.2fx' % grow)
