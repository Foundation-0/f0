import json, glob, os
S0='../oeis/certs/'
os.makedirs('proofs',exist_ok=True)
inp=json.load(open('skipped_inputs.json'))
n=0
for src,kind in (('certs','first'),('certs_skipped','skipped')):
    for f in sorted(glob.glob(src+'/A*.json')):
        r=json.load(open(f))
        if r['status']!='proved': print('not proved',f,r['status']); continue
        a=r['oeis_id']
        if kind=='first':
            c=json.load(open(S0+a+'.json')); name=c['name']; co=c['recurrence']['coefficients']; data=c['data_terms']
        else:
            name=inp[a]['name']; co=inp[a]['coeffs']; data=inp[a]['data']
        out=dict({'format':'square-law-cert/1','oeis_id':a,'group':kind,'name':name,'coefficients':co,'data_terms':data,
          'sqrt_poly':r['sqrt_poly'],'extra_x_plus_1':r['extra_x_plus_1'],'nilpotency_s':r['nilp_s'],
          'primes_hypothesis':r['primes_hyp'],'primes_window':r['primes_win'],'theorem_index':r['theorem_index'],
          'start':r['start'],'omega0':r['omega0'],'omega1':r['omega1'],'rho_rows':r['rho_rows'],'rho_cols':r['rho_cols']})
        json.dump(out,open('proofs/%s.json'%a,'w')); n+=1
print(n,'certificates written')
