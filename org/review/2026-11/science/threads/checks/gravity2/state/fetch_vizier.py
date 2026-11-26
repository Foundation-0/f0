"""Fetch full VizieR catalogs as TSV into sources/. One request per 1.5 s."""
import sys, time, urllib.request, urllib.parse, pathlib
out = pathlib.Path(__file__).parent / "sources"
for cat in sys.argv[1:]:
    fn = out / ("vz_" + cat.replace("/", "_").replace("+", "") + ".tsv")
    if fn.exists() and fn.stat().st_size > 2000:
        print("cached", fn.name); continue
    url = "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?" + urllib.parse.urlencode(
        {"-source": cat, "-out.all": "", "-out.max": "unlimited"})
    try:
        t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60).read()
        fn.write_bytes(t); print(cat, len(t), "bytes")
    except Exception as e:
        print(cat, "ERR", e)
    time.sleep(1.5)
