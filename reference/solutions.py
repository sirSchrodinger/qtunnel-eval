"""Reference solutions: exact answers from the verified transfer-matrix solver (qsolver.py), plus
the answers that common *wrong methods* give. Never shown to the models."""
import json, os, sys
import numpy as np
from scipy.optimize import brentq, minimize_scalar

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import qsolver as q

HB = q.HB2M0  # hbar^2/(2 m0) in eV nm^2


def rect_T(E, V0, a, mu_b=1.0, mu_c=1.0):
    return float(q.transmission(np.array([E]), np.array([[V0]]), np.array([[mu_b]]), np.array([[a]]),
                                mu_L=mu_c, mu_R=mu_c)[0])


def dbl_T(E, b1, b2, w, V0=0.30, mu=0.067):
    # the prompt puts the same effective mass in the contacts, barriers and well -> mu_L = mu_R = mu as well
    return float(q.transmission(np.array([E]), np.array([[V0, 0.0, V0]]), np.array([[mu] * 3]),
                                np.array([[b1, w, b2]]), mu_L=mu, mu_R=mu)[0])


def first_peak(b1, b2, w=5.0, V0=0.30, mu=0.067):
    Es = np.linspace(0.005, 0.295, 6000)
    T = np.array([dbl_T(e, b1, b2, w, V0, mu) for e in Es])
    j = next(i for i in range(1, len(Es) - 1) if T[i] > T[i - 1] and T[i] > T[i + 1])
    r = minimize_scalar(lambda e: -dbl_T(e, b1, b2, w, V0, mu), bounds=(Es[j - 3], Es[j + 3]),
                        method="bounded", options={"xatol": 1e-11})
    return float(r.x), float(-r.fun)


def compute():
    out = {}
    # t1: thin barrier
    E, V0, a = 0.40, 1.00, 0.25
    kap = np.sqrt((V0 - E) / HB)
    out["t1_thin_barrier_exact"] = dict(
        ref=rect_T(E, V0, a),
        wrong={"thick_barrier_approximation": 16 * (E / V0) * (1 - E / V0) * np.exp(-2 * kap * a),
               "exp_only_no_prefactor": float(np.exp(-2 * kap * a))})
    # t2: above the barrier
    out["t2_above_barrier"] = dict(ref=rect_T(0.70, 0.50, 1.20), wrong={"classical_full_transmission": 1.0})
    # t3: E == V0 (limit kappa -> 0): T = 1 / (1 + k0^2 a^2 / 4) with k0^2 = V0 / HB
    k0sq = 1.00 / 1.00 * 0.50 / HB
    out["t3_threshold_E_equals_V0"] = dict(
        ref=rect_T(0.50, 0.50, 1.00),
        wrong={"missing_factor_4": 1 / (1 + k0sq * 1.0 ** 2), "missing_factor_2": 1 / (1 + k0sq * 1.0 ** 2 / 2)})
    # t4: effective-mass interface
    E, V0, a, muw, mub = 0.10, 0.30, 3.0, 0.067, 0.092
    k = np.sqrt(muw * E / HB); kb = np.sqrt(mub * (V0 - E) / HB)
    naive = 1 / (1 + ((k ** 2 + kb ** 2) ** 2 * np.sinh(kb * a) ** 2) / (4 * k ** 2 * kb ** 2))  # psi' continuous
    out["t4_effective_mass_interface"] = dict(
        ref=rect_T(E, V0, a, mub, muw),
        wrong={"psi_prime_continuous_instead_of_psi_prime_over_m": float(naive),
               "same_mass_everywhere": rect_T(E, V0, a, muw, muw)})
    # t5, t6: double barrier
    e1, _ = first_peak(2.0, 2.0)
    out["t5_resonance_energy"] = dict(ref=e1, wrong={"infinite_well_E1": HB * np.pi ** 2 / (0.067 * 5.0 ** 2)})
    e2, t2 = first_peak(2.0, 3.0)
    out["t6_asymmetric_resonance_peak"] = dict(ref=t2, wrong={"unit_peak_symmetric_rule": 1.0})
    # t7: decades
    def lnT(a):
        return np.log(rect_T(0.10, 3.20, a, 0.42, 1.0))
    ref7 = (lnT(1.0) - lnT(1.2)) / np.log(10)
    kap_free = np.sqrt((3.20 - 0.10) / HB)
    out["t7_thickness_sensitivity_decades"] = dict(
        ref=float(ref7), wrong={"ignores_barrier_effective_mass": 2 * kap_free * 0.2 / np.log(10),
                                "effective_mass_in_denominator_of_kappa": 2 * np.sqrt((3.20 - 0.10) / (HB * 0.42)) * 0.2 / np.log(10)})
    # t8: STM
    k1, k2 = np.sqrt(4.5 / HB), np.sqrt(4.8 / HB)
    r8 = float(np.exp(-2 * (k2 - k1) * 1.0))
    out["t8_stm_barrier_error_factor"] = dict(ref=r8, wrong={"inverted_ratio": 1 / r8})
    # t9: validity of thick-barrier formula; T_approx/T = (1-u)^2 + 16 e (1-e) u, u = exp(-2 kappa a)
    eps = 0.25
    f = lambda x: ((1 - np.exp(-2 * x)) ** 2 + 16 * eps * (1 - eps) * np.exp(-2 * x)) - 1.10
    x = brentq(f, 0.1, 6.0)
    kap9 = np.sqrt((2.0 - 0.5) / HB)
    a9 = float(x / kap9)
    # cross-check against the transfer-matrix solver
    Ta = 16 * eps * (1 - eps) * np.exp(-2 * kap9 * a9)
    assert abs(Ta / rect_T(0.5, 2.0, a9) - 1.10) < 1e-6
    out["t9_thick_barrier_validity"] = dict(ref=a9, wrong={"kappa_a_equals_1": 1 / kap9, "kappa_a_equals_2": 2 / kap9})
    # t10: sloped barrier, sliced exactly (converged, checked against n = 1000 and n = 4000)
    def sloped(n):
        x = (np.arange(n) + 0.5) / n * 3.0
        V = (0.80 - 0.20 * x)[None, :]
        return float(q.transmission(np.array([0.15]), V, np.full((1, n), 0.067), np.full((1, n), 3.0 / n),
                                    mu_L=0.067, mu_R=0.067)[0])
    t10 = sloped(4000)
    assert abs(sloped(1000) / t10 - 1) < 1e-4, "slice convergence"
    k = lambda E, V: np.sqrt(0.067 * (V - E) / HB)
    wkb = np.exp(-2 * np.trapezoid(k(0.15, 0.80 - 0.20 * np.linspace(0, 3, 4001)), np.linspace(0, 3, 4001)))
    out["t10_sloped_barrier"] = dict(ref=t10, wrong={"wkb_no_prefactor": float(wkb)})
    # t11: FWHM of the first resonance of the symmetric double barrier
    Er, _ = first_peak(2.0, 2.0)
    Tpk = dbl_T(Er, 2.0, 2.0, 5.0)
    lo = brentq(lambda e: dbl_T(e, 2.0, 2.0, 5.0) - 0.5 * Tpk, Er - 0.02, Er)
    hi = brentq(lambda e: dbl_T(e, 2.0, 2.0, 5.0) - 0.5 * Tpk, Er, Er + 0.02)
    out["t11_resonance_width"] = dict(ref=hi - lo, wrong={"asymmetric_halfwidth_only": (hi - lo) / 2})
    # t12: five-layer stack with layer-dependent mass (BenDaniel-Duke), leads m = 0.067
    Vs = np.array([[0.30, 0.00, 0.35, 0.05, 0.30]]); mus = np.array([[0.092, 0.067, 0.100, 0.070, 0.092]])
    ds = np.array([[1.5, 4.0, 2.5, 3.0, 1.5]])
    out["t12_five_layer_stack"] = dict(
        ref=float(q.transmission(np.array([0.12]), Vs, mus, ds, mu_L=0.067, mu_R=0.067)[0]),
        wrong={})
    # t13: splitting of the two lowest resonances of a symmetric triple barrier
    def tri_T(E):
        return float(q.transmission(np.array([E]), np.array([[0.30, 0.0, 0.30, 0.0, 0.30]]),
                                    np.array([[0.067] * 5]), np.array([[1.5, 4.0, 1.5, 4.0, 1.5]]), mu_L=0.067, mu_R=0.067)[0])
    Es = np.linspace(0.01, 0.20, 3800); T = np.array([tri_T(e) for e in Es])
    pk = [j for j in range(1, len(Es) - 1) if T[j] > T[j - 1] and T[j] > T[j + 1]]
    pe = []
    for j in pk[:2]:
        r = minimize_scalar(lambda e: -tri_T(e), bounds=(Es[j - 2], Es[j + 2]), method="bounded", options={"xatol": 1e-12})
        pe.append(float(r.x))
    assert len(pk) == 2, f"expected exactly two peaks below 0.20 eV, found {len(pk)}"
    out["t13_triple_barrier_splitting"] = dict(ref=(pe[1] - pe[0]) * 1000.0,
                                               wrong={})
    for v in out.values():
        v["ref"] = float(v["ref"]); v["wrong"] = {n: float(x) for n, x in v["wrong"].items()}
    return out


if __name__ == "__main__":
    res = compute()
    json.dump(res, open(os.path.join(os.path.dirname(__file__), "expected.json"), "w"), indent=2)
    for k, v in res.items():
        print(f"{k:38s} ref={v['ref']:.6g}  wrong={ {n: round(x, 5) for n, x in v['wrong'].items()} }")
