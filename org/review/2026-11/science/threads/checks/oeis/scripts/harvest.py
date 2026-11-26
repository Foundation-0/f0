import sys; sys.path.insert(0,'.')
import oeisfetch as O, json
q = sys.argv[1]; maxp = int(sys.argv[2])
nums = []
for p in range(maxp):
    r = O.search(q, start=10*p)
    if not r: break
    for e in r: nums.append(e['number'])
    if len(r) < 10: break
print(q, 'pages', p+1, 'entries', len(nums), 'range', min(nums) if nums else None, max(nums) if nums else None)
