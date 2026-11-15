# Exact Taylor expansion of V = sum 1/|x-a_i| at the centre of the regular tetrahedron
# a_i = (1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1), equal unit charges. Order 6.
import sympy as sp
x,y,z,t=sp.symbols('x y z t')
A=[(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)]
N=7
V=0
for a in A:
    d2=sum((t*v-c)**2 for v,c in zip((x,y,z),a))
    V+=sp.series(d2**sp.Rational(-1,2),t,0,N).removeO()
V=sp.expand(V)
parts={k:sp.factor(sp.expand(V.coeff(t,k))) for k in range(N)}
for k in range(N): print(k, parts[k])
K4=x**4+y**4+z**4-3*(x**2*y**2+y**2*z**2+z**2*x**2)
lap=lambda f: sp.diff(f,x,2)+sp.diff(f,y,2)+sp.diff(f,z,2)
for k in range(N): print('harmonic',k, sp.simplify(lap(parts[k]))==0)
print('cubic/xyz', sp.simplify(parts[3]/(x*y*z)))
print('quartic/K4', sp.simplify(parts[4]/K4))
import pickle; pickle.dump({k:str(parts[k]) for k in parts}, open('taylor_tet.pkl','wb'))
