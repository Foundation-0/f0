"""Export the thread's octahedron model (family octahedron:crot:3) as coefficients on an exact rational basis.
The thread's own modules are used only to rebuild its polynomial. The lower terms are then fitted to five harmonic
polynomials with rational coefficients that are invariant under the cyclic permutation x -> y -> z:
  degree 1: x + y + z;  degree 2: xy + yz + zx;
  degree 3: xyz;  x^3 + y^3 + z^3 - (3/2)(x^2 y + x^2 z + y^2 x + y^2 z + z^2 x + z^2 y);  x^2 y + y^2 z + z^2 x - x y^2 - y z^2 - z x^2.
The leading form is K4 / 3 with K4 = x^4 + y^4 + z^4 - 3(x^2 y^2 + y^2 z^2 + z^2 x^2).
Usage: export_c3_model.py <thread folder> <result.json> <out.json>"""
import sys, json, numpy as np
sys.path.insert(0, sys.argv[1])
import hmodel as hm
solid, d, F, thetas = hm.load_model(sys.argv[2]); C = hm.model(F, d, thetas)
rng = np.random.default_rng(0); X = rng.normal(size=(400, 3)); x, y, z = X.T
def val(C, X):
    out = np.zeros(len(X))
    for a in range(d + 1):
        for b in range(d + 1):
            for c in range(d + 1):
                if C[a, b, c] != 0: out += C[a, b, c] * X[:, 0] ** a * X[:, 1] ** b * X[:, 2] ** c
    return out
K4 = x**4 + y**4 + z**4 - 3 * (x*x*y*y + y*y*z*z + z*z*x*x)
B = np.stack([x + y + z, x*y + y*z + z*x, x*y*z, x**3 + y**3 + z**3 - 1.5 * (x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y), x*x*y + y*y*z + z*z*x - x*y*y - y*z*z - z*x*x], axis=1)
rhs = val(C, X) - C[0, 0, 0] - K4 / 3
coef, res, rk, sv = np.linalg.lstsq(B, rhs, rcond=None)
print("fit coefficients:", coef); print("largest fit error: %.2e" % np.abs(B @ coef - rhs).max(), " (relative to values of size %.2e)" % np.abs(rhs).max())
json.dump({"leading": "K4/3", "basis": ["x+y+z", "xy+yz+zx", "xyz", "x^3+y^3+z^3-(3/2)(x^2y+x^2z+y^2x+y^2z+z^2x+z^2y)", "x^2y+y^2z+z^2x-xy^2-yz^2-zx^2"], "coefficients": [float(c) for c in coef]}, open(sys.argv[3], "w"), indent=1)
