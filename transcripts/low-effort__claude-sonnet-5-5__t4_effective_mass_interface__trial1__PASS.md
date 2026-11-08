# claude-sonnet-5-5 | t4_effective_mass_interface | trial 1 | low-effort

- grade: **pass** (correct), parsed value: 0.058
- run date: 2026-11-08 21:35:04, seconds: 12.8, usage: output_tokens=1487

## Prompt sent

```
This is a closed-book numerical physics problem. No code execution or other tools are available: use your own reasoning and arithmetic. Use hbar^2/(2 m0) = 0.0380998 eV nm^2, where m0 is the free-electron mass. Electron energies are measured from the band edge of the contacts, where the potential is 0 unless stated otherwise.

A GaAs / AlGaAs / GaAs heterostructure. The electron effective mass is 0.067 m0 in the GaAs contacts and 0.092 m0 in the AlGaAs barrier. The barrier height is V0 = 0.30 eV above the GaAs band edge and the barrier width is a = 3.0 nm. An electron with energy E = 0.10 eV above the GaAs band edge is incident from the left GaAs contact. Use the envelope-function matching conditions that are appropriate at a heterointerface with position-dependent effective mass. Find the exact transmission probability T, as a dimensionless number between 0 and 1 (key "T").

Reply with brief reasoning, then finish with one final line of exactly this form (JSON, a plain number, no units inside the braces): ANSWER: {"<key>": <number>}
```

## Model output (visible text; hidden reasoning is not stored)

The structure is a single rectangular barrier with a position-dependent effective mass. I used the BenDaniel–Duke matching conditions, which require ψ and (1/m*)dψ/dx to be continuous at each interface.

**Wavevectors**

- In the GaAs contacts, k² = m_w E/(ħ²/2m0) = 0.067·0.10/0.0380998 = 0.17585 nm⁻², so k = 0.41935 nm⁻¹.
- In the AlGaAs barrier, κ² = m_b (V0 − E)/(ħ²/2m0) = 0.092·0.20/0.0380998 = 0.48294 nm⁻², so κ = 0.69494 nm⁻¹.
- The barrier exponent is κa = 0.69494·3.0 = 2.0848.

**Transmission formula**

With the mass-corrected matching conditions, the standard rectangular-barrier result becomes

T = 1 / [cosh²(κa) + (ε²/4) sinh²(κa)], where ε = r − 1/r and r = (κ m_w)/(k m_b).

- r = (0.69494/0.41935)·(0.067/0.092) = 1.65719·0.72826 = 1.2069.
- ε = 1.2069 − 0.8286 = 0.3783, so ε²/4 = 0.03577.
- cosh(2.0848) = 4.0837, so cosh² = 16.677.
- sinh(2.0848) = 3.9594, so sinh² = 15.677.

**Result**

The denominator is 16.677 + 0.03577·15.677 = 16.677 + 0.561 = 17.237, so T = 1/17.237 ≈ 0.0580.

ANSWER: {"T": 0.0580}
