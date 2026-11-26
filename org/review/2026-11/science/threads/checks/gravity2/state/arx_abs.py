"""Fetch arXiv abstracts by id (one API call), cache to sources/abstracts.xml, print id | title | abstract."""
import sys, urllib.parse, urllib.request, re, pathlib
fn = pathlib.Path(__file__).parent / "sources" / ("abstracts_%s.xml" % sys.argv[1])
if not fn.exists():
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": ",".join(sys.argv[2:]), "max_results": 50})
    fn.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=60).read())
t = fn.read_text()
for e in t.split("<entry>")[1:]:
    g = lambda k: re.sub(r"\s+", " ", re.search(rf"<{k}>(.*?)</{k}>", e, re.S).group(1)).strip()
    print(g("id").split("/abs/")[-1], "|", g("title"), "|", g("summary")); print()
