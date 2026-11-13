/* Witness Map physics: order-of-magnitude, first-principles estimates. No dependencies.
 * Copy of witness-map/model.js in https://github.com/Foundation-0/fractals (c44283e); change it there first.
 *
 * For an object of mass m asked to be in two places a gap dx apart:
 *   wave clock     t_wave = m dx^2 / hbar   (time for its wave to spread across the gap)
 *   witness rate   Gamma  = sum over witnesses of (hits per second) x (information per hit)
 *   witness number W      = Gamma x t_wave  (W < 1: the wave wins; W > 1: witnesses win)
 * Information per hit with wavenumber k: 1 - exp(-(k dx)^2 / 3) (Joos & Zeh 1985 long- and short-wavelength limits).
 * Black hole horizon (Danielson, Satishchandran & Wald 2022, eqs. 15 and 19), valid for dx << b:
 *   gravity  Gamma = G^6 M^5 m^2 dx^4 / (hbar c^10 b^10);  electric  Gamma = G^3 M^3 q^2 dx^2 / (eps0 hbar c^6 b^6)
 */
(function (root) {
  'use strict';
  const C = {
    h: 6.62607015e-34, hbar: 1.054571817e-34, c: 2.99792458e8, kB: 1.380649e-23,
    G: 6.674e-11, eps0: 8.8541878128e-12, e: 1.602176634e-19, Msun: 1.989e30,
    sigmaT: 6.6524587e-29, amu: 1.66054e-27, rGas: 1.5e-10, ly: 9.4607e15, au: 1.496e11, kpc: 3.086e19,
  };
  // Witness populations. dil = photon density relative to a full black body at T (sunlight at 1 AU is 5.4e-6).
  const ENVS = {
    uhv: { name: 'Lab vacuum, room temperature', Tamb: 300, pops: [
      { type: 'photon', label: 'Glow of room-temperature walls', T: 300, dil: 1 },
      { type: 'gas', label: 'Leftover gas molecules', n: 2.4e12, m: 2 * 1.008 * C.amu, T: 300 } ] },
    cryo: { name: 'Cold vacuum box, 4 K', Tamb: 4, pops: [
      { type: 'photon', label: 'Faint glow of 4 K walls', T: 4, dil: 1 },
      { type: 'gas', label: 'Leftover helium atoms', n: 1e8, m: 4.0026 * C.amu, T: 4 } ] },
    air: { name: 'Room air', Tamb: 300, pops: [
      { type: 'photon', label: 'Room-temperature glow', T: 300, dil: 1 },
      { type: 'gas', label: 'Air molecules', n: 2.5e25, m: 28 * C.amu, T: 300 } ] },
    sunlit: { name: 'Open space near Earth, in sunlight', Tamb: 280, pops: [
      { type: 'photon', label: 'Sunlight', T: 5778, dil: 5.4e-6 },
      { type: 'photon', label: 'Big Bang afterglow', T: 2.725, dil: 1 },
      { type: 'beam', label: 'Solar wind protons', n: 5e6, m: 1.6726e-27, v: 4e5 } ] },
    interstellar: { name: 'Interstellar space', Tamb: 20, pops: [
      { type: 'photon', label: 'Starlight', T: 5000, dil: 1e-13 },
      { type: 'photon', label: 'Big Bang afterglow', T: 2.725, dil: 1 },
      { type: 'gas', label: 'Hydrogen atoms', n: 1e6, m: 1.6735e-27, T: 8000 } ] },
    intergalactic: { name: 'Intergalactic void', Tamb: 3, pops: [
      { type: 'photon', label: 'Big Bang afterglow', T: 2.725, dil: 1 },
      { type: 'gas', label: 'Hydrogen atoms', n: 1, m: 1.6735e-27, T: 1e4 } ] },
  };
  // a = radius (m). selfHeat keeps the object's own temperature T; others take the surroundings' temperature.
  // eps scales thermal emission (molecules glow about 100x more weakly than solid grains; calibrated so a
  // buckyball loses its wave behaviour near 2,500-3,000 K, as in Hackermueller et al. 2004).
  const OBJECTS = [
    { id: 'electron', name: 'Electron', m: 9.109e-31, a: 0, charged: true, home: 'uhv', seen: 'two-slit experiments' },
    { id: 'rb', name: 'Rubidium atom', m: 1.443e-25, a: 2.5e-10, noGlow: true, home: 'uhv', seen: 'atom interferometers' },
    { id: 'c60', name: 'Buckyball (60 carbon atoms)', m: 1.197e-24, a: 3.5e-10, T: 900, selfHeat: true, eps: 0.01, home: 'uhv', seen: 'Vienna, 1999' },
    { id: 'bigmol', name: 'Giant molecule (~2,000 atoms)', m: 4.15e-23, a: 2e-9, T: 500, selfHeat: true, eps: 0.01, home: 'uhv', seen: 'Vienna, 2019' },
    { id: 'virus', name: 'Virus', m: 6e-19, a: 5e-8, home: 'air' },
    { id: 'dust', name: 'Interstellar dust grain', m: 1e-15, a: 5e-7, home: 'interstellar' },
    { id: 'sand', name: 'Grain of sand', m: 1.4e-6, a: 5e-4, home: 'air' },
    { id: 'cat', name: 'Cat (alive, 38 °C)', m: 4, a: 0.15, T: 310, selfHeat: true, home: 'air' },
    { id: 'moon', name: 'Moon', m: 7.35e22, a: 1.737e6, T: 250, selfHeat: true, home: 'sunlit' },
    { id: 'earth', name: 'Earth', m: 5.97e24, a: 6.371e6, T: 255, selfHeat: true, home: 'sunlit' },
    { id: 'sun', name: 'Sun', m: 1.989e30, a: 6.96e8, T: 5778, selfHeat: true, home: 'interstellar' },
    { id: 'galaxy', name: 'Milky Way (whole galaxy)', m: 3e42, a: 4.6e20, noScatter: true, glowL: 1e37, glowLambda: 6e-7, home: 'intergalactic' },
    { id: 'fdm', name: 'Wave dark matter particle', m: 1.78e-58, a: 0, dark: true, home: 'intergalactic' },
    { id: 'wimp', name: 'Heavy dark matter particle', m: 1.78e-25, a: 0, dark: true, home: 'intergalactic' },
  ];
  const XS = (function () { const N = 360, a = Math.log(1e-4), b = Math.log(60), out = [];
    for (let i = 0; i < N; i++) { const lx = a + (b - a) * (i + 0.5) / N; out.push([Math.exp(lx), (b - a) / N]); } return out; })();
  function planckIntegral(T, dil, f) { // sum over a thermal photon spectrum of n(k) f(k) dk
    const k0 = C.kB * T / (C.hbar * C.c); let s = 0;
    for (const [x, dlx] of XS) { const k = x * k0; const nk = dil * k * k / (Math.PI * Math.PI) / Math.expm1(x); s += nk * f(k) * k * dlx; }
    return s;
  }
  const info = (k, dx) => -Math.expm1(-k * k * dx * dx / 3);
  function sigmaScatter(o, k) {
    if (o.dark || o.noScatter) return 0;
    if (o.charged) return C.sigmaT;
    const s = (8 / 3) * Math.pow(k * o.a, 4); return Math.PI * o.a * o.a * s / (1 + s);
  }
  function sigmaAbs(o, k) { const q = k * o.a; return (o.eps || 1) * Math.PI * o.a * o.a * q / (1 + q); }
  function rates(o, env, dx, bh) {
    const parts = [];
    if (!o.dark) {
      for (const p of env.pops) {
        let g = 0;
        if (p.type === 'photon') g = planckIntegral(p.T, p.dil, k => C.c * sigmaScatter(o, k) * info(k, dx));
        else if (!o.noScatter) {
          const vbar = p.type === 'gas' ? Math.sqrt(8 * C.kB * p.T / (Math.PI * p.m)) : p.v;
          const k2 = p.type === 'gas' ? 3 * p.m * C.kB * p.T / (C.hbar * C.hbar) : Math.pow(p.m * p.v / C.hbar, 2);
          const R = p.n * vbar * Math.PI * Math.pow(o.a + C.rGas, 2);
          const L = R * (4 * Math.PI / 9) * k2; g = R * -Math.expm1(-L * dx * dx / R);
        }
        if (g > 0) parts.push({ label: p.label, rate: g });
      }
      const Tobj = o.noGlow ? 0 : (o.selfHeat ? o.T : (o.a > 0 && !o.charged ? env.Tamb : 0));
      if (Tobj) { const g = planckIntegral(Tobj, 1, k => C.c * sigmaAbs(o, k) * info(k, dx)); if (g > 0) parts.push({ label: 'Its own heat glow', rate: g }); }
      if (o.glowL) { const N = o.glowL * o.glowLambda / (C.h * C.c); parts.push({ label: 'Its own starlight', rate: N * info(2 * Math.PI / o.glowLambda, dx) }); }
    }
    let bhNote = null;
    if (bh) {
      if (dx < bh.b / 10) {
        parts.push({ label: 'Black hole horizon (gravity)', rate: Math.pow(C.G, 6) * Math.pow(bh.M, 5) * o.m * o.m * Math.pow(dx, 4) / (C.hbar * Math.pow(C.c, 10) * Math.pow(bh.b, 10)), bh: true });
        if (o.charged) parts.push({ label: 'Black hole horizon (electric)', rate: Math.pow(C.G, 3) * Math.pow(bh.M, 3) * C.e * C.e * dx * dx / (C.eps0 * C.hbar * Math.pow(C.c, 6) * Math.pow(bh.b, 6)), bh: true });
      } else bhNote = 'The gap is too large compared with the distance to the black hole for the horizon formula to apply.';
    }
    const gamma = parts.reduce((s, p) => s + p.rate, 0);
    const tWave = o.m * dx * dx / C.hbar;
    return { parts, gamma, tWave, tau: 1 / gamma, W: gamma * tWave, bhNote };
  }
  const BH_M = 4.3e6 * C.Msun, RS = 2 * C.G * BH_M / (C.c * C.c);
  const api = { C, ENVS, OBJECTS, rates, planckIntegral, BH_M, RS, DEFAULT_LOG_GAP: Math.log10(2.5e-7) };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.WM = api;
})(typeof window !== 'undefined' ? window : globalThis);
