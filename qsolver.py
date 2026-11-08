"""Transfer-matrix transmission for a 1D layered potential with position-dependent
effective mass (BenDaniel-Duke matching), batched with numpy.

Units: energies in eV, lengths in nm, masses as ratios mu = m*/m0.
HB2M0 = hbar^2 / (2 m0) = 0.0380998212 eV nm^2, so k^2 = mu (E - V) / HB2M0.

Formulation. In a layer with potential V, mass mu and thickness d the vector
(psi, p = psi'/mu) obeys psi'' = -w psi with w = mu (E - V) / HB2M0, and
    (psi, p)(d) = P (psi, p)(0),   P = [[C, mu S], [-w S / mu, C]],
    C = cos(kd) or cosh(kappa d),  S = sin(kd)/k or sinh(kappa d)/kappa  (S = d at w = 0).
BenDaniel-Duke makes psi and p continuous at every interface, so the product
M = P_N ... P_1 (det M = 1, real) relates the two leads. With incoming amplitude 1,
lead wave numbers q = k / mu, and M = [[a, b], [c, d]]:
    T = 4 q_L q_R / |(q_L q_R b - c) + i (q_R a + q_L d)|^2 ,
a sum of squares (no cancellation in the evanescent regime). M is rescaled after
every layer and the scale is carried in a log, so ln T survives ln T < -700.

Public functions: transmission(), ln_transmission(), trapezoid_layers(), rect_layers().
"""
import numpy as np

HB2M0 = 0.0380998212  # eV nm^2


def _layer_cs(w, d):
    """C and S for w = k^2 (any sign) and thickness d; arrays broadcast."""
    w = np.asarray(w, dtype=float)
    d = np.asarray(d, dtype=float)
    aw = np.abs(w)
    k = np.sqrt(aw)
    kd = k * d
    with np.errstate(divide="ignore", invalid="ignore"):
        osc = w > 0
        C = np.where(osc, np.cos(kd), np.cosh(np.where(osc, 0.0, kd)))
        sk = np.where(osc, np.sin(kd), np.sinh(np.where(osc, 0.0, kd)))
        S = np.where(k > 1e-12, sk / np.where(k > 1e-12, k, 1.0), d)
    return C, S


def ln_transmission(E, V, mu, d, mu_L=1.0, mu_R=1.0, V_L=0.0, V_R=0.0):
    """ln T for energies E (B,), layer potentials V (B,N) or (N,), masses mu, thicknesses d.

    Returns -inf where a lead is not propagating (E <= V_L or E <= V_R).
    """
    E = np.atleast_1d(np.asarray(E, dtype=float))
    B = E.shape[0]
    V = np.broadcast_to(np.asarray(V, dtype=float), (B, np.shape(V)[-1])).copy()
    N = V.shape[1]
    mu = np.broadcast_to(np.asarray(mu, dtype=float), (B, N))
    d = np.broadcast_to(np.asarray(d, dtype=float), (B, N))
    mu_L = np.broadcast_to(np.asarray(mu_L, dtype=float), (B,))
    mu_R = np.broadcast_to(np.asarray(mu_R, dtype=float), (B,))
    V_L = np.broadcast_to(np.asarray(V_L, dtype=float), (B,))
    V_R = np.broadcast_to(np.asarray(V_R, dtype=float), (B,))

    a = np.ones(B); b = np.zeros(B); c = np.zeros(B); dd = np.ones(B)
    lns = np.zeros(B)
    for j in range(N):
        w = mu[:, j] * (E - V[:, j]) / HB2M0
        C, S = _layer_cs(w, d[:, j])
        p11, p12, p21, p22 = C, mu[:, j] * S, -w * S / mu[:, j], C
        a, b, c, dd = p11 * a + p12 * c, p11 * b + p12 * dd, p21 * a + p22 * c, p21 * b + p22 * dd
        s = np.maximum.reduce([np.abs(a), np.abs(b), np.abs(c), np.abs(dd)])
        a, b, c, dd = a / s, b / s, c / s, dd / s
        lns += np.log(s)

    wL = mu_L * (E - V_L) / HB2M0
    wR = mu_R * (E - V_R) / HB2M0
    prop = (wL > 0) & (wR > 0)
    qL = np.sqrt(np.where(prop, wL, 1.0)) / mu_L
    qR = np.sqrt(np.where(prop, wR, 1.0)) / mu_R
    re = qL * qR * b - c
    im = qR * a + qL * dd
    lnT = np.log(4 * qL * qR) - np.log(re * re + im * im) - 2 * lns
    return np.where(prop, lnT, -np.inf)


def transmission(E, V, mu, d, **kw):
    return np.exp(ln_transmission(E, V, mu, d, **kw))


def rect_layers(V0, a, mu_b=1.0):
    """One rectangular barrier: arrays of shape (B,1)."""
    V0 = np.atleast_1d(np.asarray(V0, dtype=float))
    return V0[:, None], np.broadcast_to(np.asarray(mu_b, dtype=float), V0.shape)[:, None], \
        np.broadcast_to(np.asarray(a, dtype=float), V0.shape)[:, None]


def trapezoid_layers(phi, F, a, n=200, mu_b=1.0):
    """Barrier V(x) = phi - F x on [0, a], sliced into n midpoint-sampled layers.

    phi: barrier height at the cathode side (eV, above the lead band edge for E measured from it),
    F: field in eV/nm (q * E-field). Returns V, mu, d of shape (B, n). The right lead should
    sit at V_R = -F * a for a lead biased by qV = F a (caller passes V_R).
    """
    phi = np.atleast_1d(np.asarray(phi, dtype=float))
    F = np.broadcast_to(np.asarray(F, dtype=float), phi.shape)
    a = np.broadcast_to(np.asarray(a, dtype=float), phi.shape)
    x = (np.arange(n) + 0.5) / n
    V = phi[:, None] - F[:, None] * a[:, None] * x[None, :]
    d = np.repeat((a / n)[:, None], n, axis=1)
    mu = np.broadcast_to(np.asarray(mu_b, dtype=float), phi.shape)[:, None] * np.ones((1, n))
    return V, mu, d
