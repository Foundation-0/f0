"""Per-system profiles and form-B extra mass with every correction switch."""
import math, numpy as np
from m_lib import *
import m_data
DEF = dict(b2500=0.0, b500=0.0, sqrtC=1.0, ge=0.0, a0=1.2e-10, nu="exp (RAR)", kstar=1.5)
class System:
    def __init__(self, r):
        self.r = r; self.name = r["name"]; self.sample = r["sample"]; self.kT = r["kT"]; self.sig = sigma_T(r["kT"])
        self.two = "M2500" in r
        self.r5, self.M5 = r["r500"], r["M500"]; self.fs5 = r["fstar500_used"]
        if self.two:
            self.r25, self.M25 = r["r2500"], r["M2500"]
            self.nfw = nfw_two_point(self.r25, self.M25, self.r5, self.M5)
        else:
            self.r25 = None; self.nfw = None
    def Mgas(self, rr, o):
        r = self.r
        g5 = r["fg500"] * self.M5
        if not self.two: return g5
        g25 = r["fg2500"] * self.M25
        al = math.log(g5 / g25) / math.log(self.r5 / self.r25)
        gr = g25 * (rr / self.r25) ** al
        if rr > self.r25: gr = g25 + (gr - g25) / o["sqrtC"]          # clumping inflates the shell gas only
        return gr
    def Mstar(self, rr, o):
        s5 = self.fs5 * self.M5
        if not self.two: return s5
        s25 = min(o["kstar"] * self.fs5 * self.M25, s5)
        al = math.log(s5 / s25) / math.log(self.r5 / self.r25) if s5 > s25 else 0.0
        return s25 * (rr / self.r25) ** al
    def b(self, rr, o):
        if not self.two: return o["b500"]
        t = min(max(math.log(rr / self.r25) / math.log(self.r5 / self.r25), 0), 1)
        return o["b2500"] + (o["b500"] - o["b2500"]) * t
    def Mtot(self, rr, o):
        M = float(nfw_M(rr, *self.nfw)) if self.two else self.M5
        return M / (1 - self.b(rr, o))
    def extra(self, rr, o=DEF):
        Mb = self.Mgas(rr, o) + self.Mstar(rr, o); Mt = self.Mtot(rr, o)
        gt = G * Mt * MSUN / (rr * KPC) ** 2
        gN = solve_gN(gt, o["a0"], NU[o["nu"]], o["ge"] * o["a0"])
        MN = gN * (rr * KPC) ** 2 / G / MSUN
        return MN - Mb, Mb, Mt
def load(): return [System(r) for r in m_data.systems()]
def opts(**kw): o = dict(DEF); o.update(kw); return o
