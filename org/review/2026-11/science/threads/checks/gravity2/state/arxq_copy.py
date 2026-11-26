import sys, time, urllib.parse, urllib.request, re
for q in sys.argv[1:]:
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": q, "max_results": 8})
    txt = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=40).read().decode()
    for e in txt.split("<entry>")[1:]:
        g = lambda t: re.sub(r"\s+", " ", re.search(rf"<{t}>(.*?)</{t}>", e, re.S).group(1)).strip()
        print(g("id").split("/abs/")[-1], g("published")[:10], "|", g("title")[:150])
    print("--"); time.sleep(3)
