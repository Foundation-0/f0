import re,json,sys
out={}
for q in (7,8,9):
    s=open(f'sources/t{q}.html').read()
    cells={}
    for m in re.finditer(r'title="n=(\d+), k=(\d+)"[^>]*HREF="[^"]*">([^<]*)</A>',s):
        n,k,t=int(m[1]),int(m[2]),m[3].strip()
        if re.fullmatch(r'\d+',t): lo=up=int(t)
        elif re.fullmatch(r'\d+-\d+',t): lo,up=map(int,t.split('-'))
        else: print('odd',q,n,k,t); continue
        cells[f'{n},{k}']=(lo,up)
    out[q]=cells
    print(q,len(cells),sum(1 for a,b in cells.values() if a<b),max(int(x.split(',')[0]) for x in cells))
json.dump(out,open('table.json','w'))
