# claude-opus-5-5 | t11_resonance_width | trial 1 | low-effort

- grade: **fail** (wrong: other), parsed value: 0.0142
- run date: 2026-11-08 21:42:02, seconds: 21.6, usage: output_tokens=1980

## Prompt sent

```
This is a closed-book numerical physics problem. No code execution or other tools are available: use your own reasoning and arithmetic. Use hbar^2/(2 m0) = 0.0380998 eV nm^2, where m0 is the free-electron mass. Electron energies are measured from the band edge of the contacts, where the potential is 0 unless stated otherwise.

A symmetric double-barrier resonant-tunnelling structure. The effective mass is 0.067 m0 in every region (contacts, barriers and well). Both barriers have height V0 = 0.30 eV and width 2.0 nm. They are separated by a quantum well of width 5.0 nm. The potential is 0 in the well and in the contacts. The transmission probability T(E) has its first (lowest-energy) resonance peak with maximum value 1. Find the full width at half maximum of that peak, i.e. the difference between the two energies, one on each side of the peak, at which T(E) = 0.5. Give it in eV (key "FWHM_eV").

Reply with brief reasoning, then finish with one final line of exactly this form (JSON, a plain number, no units inside the braces): ANSWER: {"<key>": <number>}
```

## Model output (visible text; hidden reasoning is not stored)

**Approach.** Locate the first quasi-bound level of the well. Then estimate the peak width as the tunnelling escape rate through the two barriers. This is a Lorentzian approximation, not an exact evaluation of T(E) = 0.5.

**1. Resonance energy.**
- ħ²/(2m*) = 0.0380998/0.067 = 0.56865 eV nm².
- Treat the well as a finite square well of depth 0.30 eV and width 5.0 nm.
- The well strength is z₀ = (L/2)·√(V₀/c) = 2.5 × √(0.30/0.56865) = 1.8158.
- Solve the even-state condition z·tan z = √(z₀² − z²). This gives z ≈ 0.9925.
- So k = 2z/L ≈ 0.397 nm⁻¹ and E_r = c·k² ≈ 0.0896 eV.
- This neglects the small shift from the barriers being only 2 nm thick.

**2. Single-barrier transmission at E_r.**
- κ = √((0.30 − 0.0896)/0.56865) ≈ 0.608 nm⁻¹, so κb ≈ 1.217 and sinh(κb) ≈ 1.540.
- The exact rectangular-barrier formula is T_b = [1 + (k² + κ²)² sinh²(κb)/(4k²κ²)]⁻¹.
- This gives T_b ≈ 0.261.

**3. Width.**
- The electron velocity term is ħv = 2ck ≈ 0.4515 eV nm.
- The effective well length includes the penetration depth on both sides: L_eff = L + 2/κ ≈ 8.29 nm.
- Each barrier gives an escape rate of ħv·T_b/(2L_eff). Two barriers give Γ = ħv·T_b/L_eff ≈ 0.4515 × 0.261 / 8.29 ≈ 0.0142 eV.
- For a symmetric structure, the FWHM equals Γ.

**Caveat.** The single-barrier transmission (≈0.26) is fairly large, so the Lorentzian estimate is crude. An exact evaluation of T(E) = 0.5 could differ by some percent.

ANSWER: {"FWHM_eV": 0.0142}
