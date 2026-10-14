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
        lab = f'{utc_label(p["t"])}: kappa {p["k"]:.18g}'
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="dot" tabindex="0" role="img" aria-label="{lab}" '
                   f'data-t="{p["t"][:16].replace("T"," ")}Z" data-k="&#954; = {p["k"]:.18g}"/>')
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
    rows = ''.join(f'<tr><td>{utc_label(p["t"])}</td><td class="n">{p["k"]:.18g}</td></tr>' for p in points)
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

# Page CSS (written to story/page.css). Tokens only; one page token for the series colour, validated
# with the dataviz palette script beside the site's chart surfaces (light #2a5fb0, dark #4f90e3).
CSS = """/* The story page (research/integer-multiplication/story). Generated by story-src/build.py: edit there.
   f0.css tokens only, plus --mark-im for the series (validated: light #2a5fb0, dark #4f90e3). */
:root { --mark-im: #2a5fb0; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --mark-im: #4f90e3; } }
:root[data-theme="dark"] { --mark-im: #4f90e3; }

.st-hero .wrap { align-items: center; }
.st-hero .ph-text { min-width: 0; }
.st-hero .h1 { max-width: 16ch; }
.st-hero .dek { max-width: 54ch; }
.st-hero .dek strong { color: var(--ink); font-weight: 600; }
.st-num { padding: clamp(20px, 3vw, 36px); width: 100%; max-width: 460px; justify-self: end; }
@media (max-width: 960px) { .st-num { justify-self: stretch; max-width: none; } }
.st-num .n { font: 600 clamp(64px, 7vw + 20px, 128px)/.95 var(--f-sans); letter-spacing: -.05em; color: var(--ink); }
.st-num .c { font: 400 var(--fs-sm)/1.5 var(--f-sans); color: var(--ink-2); margin-top: 12px; max-width: 30ch; }
.st-num .k { font: 500 var(--fs-label)/1.4 var(--f-mono); letter-spacing: var(--tr-label); text-transform: uppercase; color: var(--ink-3); margin-bottom: 12px; }

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
JS = """/* The story page. Generated by story-src/build.py: edit there. Shows the shared tooltip (F0.tip)
   for every chart mark on hover, tap and keyboard focus; the tables under each chart hold the same values. */
(function () {
  'use strict';
  function boot() {
    var F0 = window.F0; if (!F0) return;
    document.querySelectorAll('[data-t]').forEach(function (el) {
      function show(x, y) { F0.tip.show('<p class="tip-k">' + F0.esc(el.getAttribute('data-t')) + '</p><p class="tip-t">' + F0.esc(el.getAttribute('data-k')) + '</p>', x, y); }
      el.addEventListener('pointermove', function (e) { show(e.clientX, e.clientY); });
      el.addEventListener('pointerleave', function () { F0.tip.hide(); });
      el.addEventListener('focus', function () { var b = el.getBoundingClientRect(); show(b.right, b.top); });
      el.addEventListener('blur', function () { F0.tip.hide(); });
    });
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
<aside class="callout caveat"><p class="c-k">Read with care</p><p>This essay was written on 13 October 2026, and its figures are as of {AS_OF}. The race has moved since: the <a href="../">project page</a> shows the current reviewed &kappa;, read live from the race&rsquo;s own record file. Three lines below have <a href="#corrections">corrections</a>, kept separate so the essay&rsquo;s words stay as published.</p></aside>
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

S_FIX = sec('06', 'corrections', 'Corrections', 'Corrections, 14 October 2026', """<p class="lede">Foundation0 checked this essay against the sources before republishing it. Three lines say more than the evidence does; the essay above is unchanged, and here is what the record supports.</p>
<ol class="st-fix">
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
      <p class="dek">{LEDE}</p>
      <div class="meta-row">
        <span class="chip">Snapshot &middot; {AS_OF}</span>
        <span class="badge n">Essay &middot; not peer reviewed</span>
        <a class="chip" href="../">Current record on the project page &rarr;</a>
      </div>
    </div>
    <div class="ph-fig st-num frame">
      <p class="k">Reviewed constant, 9 to 13 Oct</p>
      <div class="n">{grow:.1f}&times;</div>
      <div class="c">improvement in the reviewed constant, 9 to 13 October 2026</div>
    </div>
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
  <a class="next" href="../live/"><span>Next &rarr;</span>The live race tracker</a>
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
