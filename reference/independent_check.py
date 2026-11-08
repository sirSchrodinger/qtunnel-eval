"""Independent cross-checks of the reference answers (different method from the transfer-matrix solver).
1. Rectangle / thick-barrier / threshold: closed forms.
2. Symmetric double barrier, equal mass everywhere: lowest resonance from the analytic phase condition
   k L = pi - arctan[ 2 k kappa / ((kappa^2 - k^2) tanh(kappa b)) ]  (transmission is exactly 1 there).
3. Asymmetric double barrier: peak T = 4 TL TR / (TL + TR)^2 evaluated with the single-barrier transmissions at the
   resonance energy is NOT exact for finite barriers, so the exact value is checked by a direct wave-amplitude
   linear solve with explicit interface equations.
Run: python reference/independent_check.py"""
import json, os, sys
import numpy as np
from scipy.optimize import brentq, minimize_scalar

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qsolver as q

HB = q.HB2M0
EXP = json.load(open(os.path.join(os.path.dirname(__file__), "expected.json")))


def amp_T(E, V, mu, d, muL, muR):
    """T by explicit plane-wave amplitudes (psi and psi'/mu continuous at each interface), complex linear solve."""
    n = len(V)
    kk = lambda Vj, m: np.sqrt(complex(m * (E - Vj) / HB))
    ks = [kk(0.0, muL)] + [kk(Vj, m) for Vj, m in zip(V, mu)] + [kk(0.0, muR)]
    ms = [muL] + list(mu) + [muR]
    x = np.concatenate([[0.0], np.cumsum(d)])  # interface positions
    # unknowns: A_j (forward), B_j (backward) for regions 0..n+1 ; A_0 = 1, B_{n+1} = 0
    N = 2 * (n + 2)
    M = np.zeros((N, N), complex); rhs = np.zeros(N, complex)
    row = 0
    for j in range(n + 1):          # interface between region j and j+1 at x[j]
        xj = x[j]
        kj, kj1, mj, mj1 = ks[j], ks[j + 1], ms[j], ms[j + 1]
        # psi
        M[row, 2 * j] = np.exp(1j * kj * xj); M[row, 2 * j + 1] = np.exp(-1j * kj * xj)
        M[row, 2 * j + 2] = -np.exp(1j * kj1 * xj); M[row, 2 * j + 3] = -np.exp(-1j * kj1 * xj); row += 1
        # psi'/m
        M[row, 2 * j] = 1j * kj * np.exp(1j * kj * xj) / mj; M[row, 2 * j + 1] = -1j * kj * np.exp(-1j * kj * xj) / mj
        M[row, 2 * j + 2] = -1j * kj1 * np.exp(1j * kj1 * xj) / mj1; M[row, 2 * j + 3] = 1j * kj1 * np.exp(-1j * kj1 * xj) / mj1; row += 1
    M[row, 0] = 1; rhs[row] = 1; row += 1
    M[row, N - 1] = 1; rhs[row] = 0
    sol = np.linalg.solve(M, rhs)
    A_out = sol[N - 2]
    return float((abs(A_out) ** 2) * (ks[-1].real / muR) / (ks[0].real / muL))


def check(name, got, want, tol=1e-6):
    ok = abs(got - want) <= tol * abs(want)
    print(("PASS " if ok else "FAIL ") + f"{name}: independent={got:.8g} reference={want:.8g}")
    return ok


ok = True
# rectangle thin, above-barrier, threshold, effective mass
ok &= check("t1", amp_T(0.40, [1.0], [1.0], [0.25], 1.0, 1.0), EXP["t1_thin_barrier_exact"]["ref"])
ok &= check("t2", amp_T(0.70, [0.5], [1.0], [1.2], 1.0, 1.0), EXP["t2_above_barrier"]["ref"])
ok &= check("t3 (E just below/above V0 average)", 0.5 * (amp_T(0.5 - 1e-9, [0.5], [1.0], [1.0], 1.0, 1.0) +
            amp_T(0.5 + 1e-9, [0.5], [1.0], [1.0], 1.0, 1.0)), EXP["t3_threshold_E_equals_V0"]["ref"], 1e-5)
ok &= check("t4", amp_T(0.10, [0.30], [0.092], [3.0], 0.067, 0.067), EXP["t4_effective_mass_interface"]["ref"])
# t5: analytic phase condition, equal mass everywhere
m = 0.067; V0 = 0.30; b = 2.0; L = 5.0
def f(E):
    k = np.sqrt(m * E / HB); kap = np.sqrt(m * (V0 - E) / HB)
    return k * L - np.pi + np.arctan(2 * k * kap / ((kap ** 2 - k ** 2) / 1.0 * np.tanh(kap * b)))
E_res = brentq(f, 0.05, 0.12)
ok &= check("t5 analytic resonance condition", E_res, EXP["t5_resonance_energy"]["ref"], 1e-5)
ok &= check("t5 T(E_res) = 1 (amplitude solver)", amp_T(E_res, [V0, 0, V0], [m] * 3, [b, L, b], m, m), 1.0, 1e-6)
# t6: amplitude solver peak
Tf = lambda E: amp_T(E, [V0, 0, V0], [m] * 3, [2.0, L, 3.0], m, m)
r = minimize_scalar(lambda E: -Tf(E), bounds=(0.07, 0.10), method="bounded", options={"xatol": 1e-11})
ok &= check("t6 peak T (amplitude solver)", -r.fun, EXP["t6_asymmetric_resonance_peak"]["ref"], 1e-5)
# t7
lnT = lambda a: np.log(amp_T(0.10, [3.20], [0.42], [a], 1.0, 1.0))
ok &= check("t7", (lnT(1.0) - lnT(1.2)) / np.log(10), EXP["t7_thickness_sensitivity_decades"]["ref"], 1e-6)
# t8 closed form
ok &= check("t8", float(np.exp(-2 * (np.sqrt(4.8 / HB) - np.sqrt(4.5 / HB)))), EXP["t8_stm_barrier_error_factor"]["ref"], 1e-9)
# t9: ratio approx/exact at the reference width must be 1.10 with the independent solver
a9 = EXP["t9_thick_barrier_validity"]["ref"]; kap = np.sqrt(1.5 / HB)
ratio = 16 * 0.25 * 0.75 * np.exp(-2 * kap * a9) / amp_T(0.5, [2.0], [1.0], [a9], 1.0, 1.0)
ok &= check("t9 ratio at reference width", ratio, 1.10, 1e-6)
# t10: sloped barrier, explicit-amplitude solve with 500 slices (converges to ~1e-3; the reference uses 4000)
n = 500; xs = (np.arange(n) + 0.5) / n * 3.0
ok &= check("t10 sloped barrier (500 slices)", amp_T(0.15, list(0.80 - 0.20 * xs), [0.067] * n, [3.0 / n] * n, 0.067, 0.067),
            EXP["t10_sloped_barrier"]["ref"], 3e-3)
# t11: FWHM with the amplitude solver
Tdb = lambda E: amp_T(E, [V0, 0, V0], [m] * 3, [b, L, b], m, m)
Er = E_res; Tp = Tdb(Er)
lo = brentq(lambda e: Tdb(e) - 0.5 * Tp, Er - 0.02, Er); hi = brentq(lambda e: Tdb(e) - 0.5 * Tp, Er, Er + 0.02)
ok &= check("t11 FWHM (amplitude solver)", hi - lo, EXP["t11_resonance_width"]["ref"], 1e-5)
# t12: five-layer stack
ok &= check("t12 five-layer stack", amp_T(0.12, [0.30, 0.0, 0.35, 0.05, 0.30], [0.092, 0.067, 0.100, 0.070, 0.092],
            [1.5, 4.0, 2.5, 3.0, 1.5], 0.067, 0.067), EXP["t12_five_layer_stack"]["ref"])
# t13: triple barrier peaks with the amplitude solver
Vt = [0.30, 0, 0.30, 0, 0.30]; dt = [1.5, 4.0, 1.5, 4.0, 1.5]
Tt = lambda E: amp_T(E, Vt, [m] * 5, dt, m, m)
Eg = np.linspace(0.01, 0.20, 1900); Tg = np.array([Tt(e) for e in Eg])
pk = [j for j in range(1, len(Eg) - 1) if Tg[j] > Tg[j - 1] and Tg[j] > Tg[j + 1]]
pe = [minimize_scalar(lambda e: -Tt(e), bounds=(Eg[j - 2], Eg[j + 2]), method="bounded", options={"xatol": 1e-12}).x for j in pk]
ok &= check("t13 splitting (amplitude solver), exactly two peaks", (pe[1] - pe[0]) * 1000 if len(pe) == 2 else float("nan"),
            EXP["t13_triple_barrier_splitting"]["ref"], 1e-5)
print("ALL INDEPENDENT CHECKS PASS" if ok else "SOME CHECKS FAILED"); sys.exit(0 if ok else 1)
