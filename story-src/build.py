"""Build index.html from data.json. Standard library only: python3 -I build.py"""
import json, os, datetime, html

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'data.json')))


def ts(s):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').timestamp()


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


def line_chart(points, w=760, h=320, pad=(28, 18, 34, 64)):
    """Single-series time/value line. pad = top,right,bottom,left."""
    pt, pr, pb, pl = pad
    xs = [ts(p['t']) for p in points]
    ys = [p['k'] for p in points]
    ticks = nice_ticks(max(ys))
    y0, y1 = 0.0, ticks[-1]
    # start the x domain at midnight of the first day so every day gets a label
    x0 = datetime.datetime.utcfromtimestamp(min(xs)).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()
    x1 = max(xs)
    px = lambda x: pl + (x - x0) / (x1 - x0) * (w - pl - pr)
    py = lambda y: h - pb - (y - y0) / (y1 - y0) * (h - pt - pb)
    out = [f'<svg class="chart" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="Verified kappa over time, {points[0]["k"]} to {points[-1]["k"]}">']
    # y gridlines + ticks
    for v in ticks:
        y = py(v)
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{pl-10}" y="{y+4:.1f}" class="tick tick-y">{v:.4f}</text>')
    # x ticks, one per day
    day = datetime.datetime.utcfromtimestamp(x0).replace(hour=0, minute=0, second=0)
    while day.timestamp() <= x1:
        if day.timestamp() >= x0:
            x = px(day.timestamp())
            out.append(f'<line x1="{x:.1f}" y1="{pt}" x2="{x:.1f}" y2="{h-pb}" class="grid"/>')
            out.append(f'<text x="{x:.1f}" y="{h-pb+20}" class="tick tick-x">{day.strftime("%b %-d")}</text>')
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
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="dot" '
                   f'data-t="{p["t"][:16].replace("T"," ")}Z" data-k="{p["k"]:.18g}"/>')
    # last value, direct-labelled
    lx, ly = px(ts(points[-1]['t'])), py(points[-1]['k'])
    out.append(f'<text x="{lx-8:.1f}" y="{ly-14:.1f}" class="lastlabel">{points[-1]["k"]:.6f}</text>')
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
    out = [f'<svg class="chart small" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">']
    for v in ticks:
        y = py(v)
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w-pr}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{pl-7}" y="{y+4:.1f}" class="tick tick-y">{int(v)}</text>')
    for i, r in enumerate(rows):
        x = pl + gap * i + (gap - bw) / 2
        y = py(r[key])
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h-pb-y:.1f}" '
                   f'rx="3" class="bar" data-t="{r["d"]}" data-k="{r[key]} {label.lower()}"/>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" class="barval">{r[key]}</text>')
        out.append(f'<text x="{x+bw/2:.1f}" y="{h-pb+18}" class="tick tick-x">{r["d"][-2:]}</text>')
    out.append(f'<line x1="{pl}" y1="{h-pb}" x2="{w-pr}" y2="{h-pb}" class="axis"/>')
    out.append('</svg>')
    return '\n'.join(out)


k = D['kappa']
r = D['repo']
grow = k[-1]['k'] / k[0]['k']

CSS = """
:root{color-scheme:light;--plane:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;
--muted:#898781;--grid:#e1e0d9;--axis:#c3c2b7;--series:#2a78d6;--border:rgba(11,11,11,.10)}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme=light])){color-scheme:dark;
--plane:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--series:#3987e5;--border:rgba(255,255,255,.10)}}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);
font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased}
main{max-width:800px;margin:0 auto;padding:72px 24px 96px}
h1{font-size:40px;line-height:1.15;letter-spacing:-.02em;margin:0 0 20px;font-weight:650}
h2{font-size:21px;letter-spacing:-.01em;margin:56px 0 14px;font-weight:620}
p{margin:0 0 18px;color:var(--ink2);max-width:66ch}
p.lede{font-size:19px;color:var(--ink)}
strong{color:var(--ink);font-weight:600}
a{color:var(--series);text-decoration:none;border-bottom:1px solid var(--border)}
a:hover{border-bottom-color:var(--series)}
.hero{margin:40px 0 8px}
.hero .n{font-size:64px;line-height:1;font-weight:650;letter-spacing:-.03em}
.hero .c{color:var(--ink2);margin-top:8px;font-size:15px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
background:var(--border);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin:32px 0}
.tile{background:var(--surface);padding:16px 18px}
.tile .v{font-size:26px;font-weight:620;letter-spacing:-.02em}
.tile .l{font-size:13px;color:var(--muted);margin-top:3px}
figure{margin:28px 0;background:var(--surface);border:1px solid var(--border);
border-radius:10px;padding:18px 18px 10px}
figcaption{font-size:13px;color:var(--muted);margin-top:6px}
.fig-title{font-size:14px;font-weight:600;margin-bottom:10px}
.chart{width:100%;height:auto;display:block;overflow:visible}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:640px){.pair{grid-template-columns:1fr}h1{font-size:31px}.hero .n{font-size:46px}}
.grid{stroke:var(--grid);stroke-width:1}
.axis{stroke:var(--axis);stroke-width:1}
.series{fill:none;stroke:var(--series);stroke-width:2;stroke-linejoin:round}
.dot{fill:var(--series);stroke:var(--surface);stroke-width:2}
.bar{fill:var(--series)}
.tick{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
.tick-y{text-anchor:end}.tick-x{text-anchor:middle}
.barval{fill:var(--ink2);font-size:11px;text-anchor:middle;font-weight:600}
.lastlabel{fill:var(--ink);font-size:13px;font-weight:620;text-anchor:end}
#tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .1s;background:var(--ink);
color:var(--plane);font-size:12px;padding:6px 9px;border-radius:6px;white-space:nowrap;z-index:9;
font-variant-numeric:tabular-nums}
table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td.num{font-variant-numeric:tabular-nums;text-align:right}
footer{margin-top:72px;padding-top:24px;border-top:1px solid var(--border);
font-size:13px;color:var(--muted)}
"""

JS = """
const tip=document.getElementById('tip');
for(const el of document.querySelectorAll('[data-t]')){
 el.addEventListener('pointerenter',e=>{tip.textContent=el.dataset.t+'  ·  '+el.dataset.k;
  tip.style.opacity=1;});
 el.addEventListener('pointermove',e=>{tip.style.left=(e.clientX+14)+'px';
  tip.style.top=(e.clientY-34)+'px';});
 el.addEventListener('pointerleave',()=>tip.style.opacity=0);
}
"""

BODY = f"""
<main>
<h1>When the crowd gets a frontier model</h1>

<p class="lede">On 7 October someone opened a public repository holding one question: how much
faster than <em>n</em>&#8201;log&#8201;<em>n</em> can you <strong>prove</strong> that two large
numbers can be multiplied? Five days later it has {r['prs']} pull requests from
{r['authors']} people, and the reviewed answer has moved {grow:.1f}&times;.</p>

<div class="hero">
  <div class="n">{grow:.1f}&times;</div>
  <div class="c">improvement in the reviewed constant, 9 to 13 October 2026</div>
</div>

<figure>
  <div class="fig-title">The reviewed constant &kappa;, as recorded in the repository's own certificate</div>
  {line_chart(k)}
  <figcaption>Each step is a new result the maintainer reviewed and selected. Bigger is better:
  the proven running time is <em>n</em>&#8201;(log&#8201;<em>n</em>)<sup>1&#8722;&kappa;</sup>.</figcaption>
</figure>

<div class="tiles">
  <div class="tile"><div class="v">{r['prs']}</div><div class="l">pull requests</div></div>
  <div class="tile"><div class="v">{r['authors']}</div><div class="l">people</div></div>
  <div class="tile"><div class="v">{r['merged']}</div><div class="l">merged</div></div>
  <div class="tile"><div class="v">6</div><div class="l">days old</div></div>
</div>

<h2>Why it moved</h2>
<p>Two things were different. The first is obvious: a model will read a long technical argument
with you and draft the next step. That gets you a candidate.</p>
<p>The second matters more. <strong>Every result that moves the number arrives with a script that
checks it.</strong> Nobody has to trust the person who sent it. You run their verifier on your own
machine and it passes or it fails. A wrong answer costs its author some time and costs everyone
else nothing.</p>
<p>That is what makes a crowd usable on a problem like this. Without the check, {r['prs']} pull
requests is just noise nobody can afford to read. With it, the work composes: pull requests
name the exact constructions they build on, and those belong to other people.</p>

<figure>
  <div class="fig-title">Daily activity</div>
  <div class="pair">
    <div>{bar_chart(D['per_day'], 'prs', 'Pull requests opened')}
      <figcaption>Pull requests opened, by day of October.</figcaption></div>
    <div>{bar_chart(D['per_day'], 'new', 'First-time contributors')}
      <figcaption>People contributing for the first time.</figcaption></div>
  </div>
</figure>

<h2>Most of it is not the answer</h2>
<p>Look at what the pull requests actually contain and the shape of a working research community
shows up. Alongside the improvements there are independent re-verifications, speedups to other
people's checking scripts, formal proofs in Lean, and a steady stream of honest negative results:
<em>this route is closed, here is the obstruction</em>. Of {r['prs']} pull requests,
{r['merged']} are merged. The rest are not waste. A closed route nobody has to try again is worth
something, and the crowd is cheap enough to afford them.</p>

<h2>What this is not</h2>
<p>The result is conditional. It inherits a framework from an earlier paper, and the repository
says plainly that its finite checks are not a complete machine-checked theorem, and that none of
this is a claim about how fast your computer multiplies numbers today. The honesty is part of why
it works: the scope of every claim is written down, so the next person knows exactly what they are
standing on.</p>

<h2>Our part</h2>
<p>We have been working in two of these.</p>
<p><strong>Circuit constructions.</strong> A separate repository collects the smallest known
circuits for arithmetic in binary fields, measured in AND and XOR gates. Smaller circuits mean
cheaper encryption work, particularly in secure multi-party computation and zero-knowledge proofs.
We contributed multipliers for four fields it did not cover. Two of them came in below the
published baseline. All five were re-checked by the author against the pack's own verifier,
and merged.</p>
<table>
<tr><th>Field</th><th class="num">Baseline</th><th class="num">Ours</th><th class="num">Saved</th></tr>
<tr><td>GF(2<sup>9</sup>)</td><td class="num">142</td><td class="num">136</td><td class="num">6</td></tr>
<tr><td>GF(2<sup>10</sup>)</td><td class="num">172</td><td class="num">172</td><td class="num">0</td></tr>
<tr><td>GF(2<sup>11</sup>)</td><td class="num">206</td><td class="num">199</td><td class="num">7</td></tr>
<tr><td>GF(2<sup>128</sup>), the GHASH field</td><td class="num">11,972</td><td class="num">11,972</td><td class="num">0</td></tr>
</table>
<p><strong>The exponent race.</strong> We held the top open claim for several hours on 11 October,
at &kappa; = 0.00135058, by re-timing an existing construction. The race has since moved a long way
past it, on a different line of work. That is the honest state of it: a real contribution, briefly
in front, now behind.</p>

<h2>Why it matters</h2>
<p>The interesting part is not the constant. It is that a machine-checkable problem statement turns
a crowd with good tools into something that functions like a laboratory, in days, at almost no
coordination cost. The number of problems that can be posed this way is much larger than the number
that have been.</p>

<footer>
Figures read from the repository's own certificate file and the GitHub API,
as of {D['as_of']}. The race is
<a href="https://github.com/CrocSwap/integer-mult-bounds">CrocSwap/integer-mult-bounds</a>,
maintained by Douglas Colkitt. The circuit pack is
<a href="https://github.com/Swapnil-jain/gf2m-circuits">Swapnil-jain/gf2m-circuits</a>.
Numbers change by the hour; rebuild to refresh.
</footer>
</main>
<div id="tip"></div>
"""

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Crowd Research Frontier</title>
<meta name="description" content="A public repository moved a research constant 3.6x in four days, with {r['prs']} pull requests from {r['authors']} people. What made it work.">
<style>{CSS}</style></head>
<body>{BODY}<script>{JS}</script></body></html>
"""

out = os.path.join(HERE, '..', 'docs', 'story', 'index.html')
open(out, 'w').write(page)
print('wrote docs/story/index.html', len(page), 'bytes;', len(k), 'kappa points; growth %.2fx' % grow)
