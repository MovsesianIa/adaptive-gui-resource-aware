"""Monte Carlo simulation of adaptation policies for the resource-aware adaptive GUI model.

Reproduces Table 6 and Fig. 5-6 of the paper
"Формальна модель проєктування адаптивного графічного інтерфейсу комп'ютерних систем
з урахуванням ресурсної вартості адаптації".

Policies:
  never    - no adaptation
  always   - apply the candidate with the largest positive expected gain G
  user     - user-cost-only criterion: G - C_U > theta  (cf. SUPPLE, Todi et al.)
  proposed - full model: V = G - C_U - beta*C_R > theta, with response-time and energy-budget constraints

All parameters below are assumptions of the simulation study (see Section "Імітаційне моделювання").
Run:  python sim.py   (writes results/*.json; seed is fixed, results are deterministic)
"""
import json
import os
import numpy as np

SEED = 2026
rng = np.random.default_rng(SEED)

# Mean task cost (s) for the initial configuration, per user pattern; habituation level xi per pattern
BASE = {'nov': 12.0, 'exp': 6.0}
XI = {'nov': 0.2, 'exp': 0.9}
# Adaptation candidates: (task-cost change novice, task-cost change expert, delta, dt_ms, dm_MB, dE_J)
#   A1 enlarge primary action, A2 simplify navigation, A3 generative page rebuild
ADS = [(-1.5, -0.2, 0.2, 40, 5, 1.5),
       (-2.0, 0.3, 0.4, 60, 8, 2.5),
       (-3.0, -0.5, 0.7, 150, 50, 8.0)]
# Device classes: dt multiplier, dE multiplier, energy budget per session (J), available memory (MB)
DEV = {'desk': dict(kt=1, kE=1, b=np.inf, m=4000),
       'mid': dict(kt=2, kE=1, b=40.0, m=1000),
       'weak': dict(kt=4, kE=1.5, b=15.0, m=300)}
# Model parameters
KAPPA = 10      # re-learning time scale, s
BETA = 10       # exchange rate between user time and resource cost, s
TH = 1          # hysteresis threshold theta, s
TMIN = 3        # minimal interval between adaptations, tasks
TAU = 200       # response-time limit tau_max, ms (INP "good" threshold)
DTMAX = 200     # normalisation for dt, ms
W = (0.4, 0.2, 0.4)  # weights w_t, w_m, w_E
SD = 2.0        # std of observed task time, s
EN = 20         # expected session length used for the horizon H_t


def run(policy, dev, rng):
    """Simulate one session; return (mean time per task, energy spent, #adaptations, #tau violations, budget exceeded)."""
    d = DEV[dev]
    true = 'nov' if rng.random() < 0.5 else 'exp'
    N = int(rng.integers(10, 31))
    jit = rng.uniform(0.8, 1.2, size=(3, 3))  # parameter uncertainty: gains, dt, dE
    ads = [(g1 * jit[i, 0], g2 * jit[i, 0], dl, dt * d['kt'] * jit[i, 1], dm, dE * d['kE'] * jit[i, 2])
           for i, (g1, g2, dl, dt, dm, dE) in enumerate(ADS)]
    applied = set(); pi = 0.5; spent = 0.0; last = -99; T = 0.0; nad = 0; inp = 0
    for t in range(N):
        mn = {'nov': BASE['nov'] + sum(ads[i][0] for i in applied),
              'exp': BASE['exp'] + sum(ads[i][1] for i in applied)}
        obs = rng.normal(mn[true], SD)
        T += max(obs, 0.5)
        # Bayesian update of pi_t(novice) with Gaussian likelihood
        ln = np.exp(-(obs - mn['nov']) ** 2 / (2 * SD ** 2))
        le = np.exp(-(obs - mn['exp']) ** 2 / (2 * SD ** 2))
        pi = pi * ln / (pi * ln + (1 - pi) * le + 1e-300)
        if policy == 'never' or t - last < TMIN:
            continue
        H = max(EN - t - 1, 1)
        xi = pi * XI['nov'] + (1 - pi) * XI['exp']
        brem = d['b'] - spent
        best = None; bv = -np.inf
        for i, (g1, g2, dl, dt, dm, dE) in enumerate(ads):
            if i in applied:
                continue
            G = -H * (pi * g1 + (1 - pi) * g2)
            CU = KAPPA * xi * dl
            CR = W[0] * dt / DTMAX + W[1] * dm / d['m'] + (
                W[2] * dE / brem if np.isfinite(brem) and brem > 0 else (0 if not np.isfinite(brem) else np.inf))
            if policy == 'always':
                v = G; ok = G > 0
            elif policy == 'user':
                v = G - CU; ok = v > TH
            else:
                v = G - CU - BETA * CR; ok = v > TH and dt <= TAU and (dE <= brem)
            if ok and v > bv:
                bv = v; best = i
        if best is not None:
            g1, g2, dl, dt, dm, dE = ads[best]
            applied.add(best); last = t; nad += 1
            T += KAPPA * XI[true] * dl  # actual re-learning cost
            spent += dE
            inp += dt > TAU
    over = spent > d['b']
    return T / N, spent, nad, inp, over


if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    res = {}
    for dev in DEV:
        for pol in ['never', 'always', 'user', 'proposed']:
            r = np.array([run(pol, dev, rng) for _ in range(10000)], dtype=float)
            m = r.mean(0); se = r.std(0, ddof=1) / np.sqrt(len(r))
            res[f'{dev}|{pol}'] = dict(time=m[0], time_ci=1.96 * se[0], E=m[1], nad=m[2], inp=m[3], over=m[4] * 100)
            print(dev, pol, {a: round(b, 3) for a, b in res[f'{dev}|{pol}'].items()})
    json.dump(res, open('results/policies.json', 'w'), indent=1)
    sweep = {}
    for dev in ['mid', 'weak']:
        for bval in [0, 1, 2, 5, 10, 20]:
            BETA = bval
            r = np.array([run('proposed', dev, rng) for _ in range(5000)], dtype=float)
            sweep[f'{dev}|{bval}'] = dict(time=r[:, 0].mean(), E=r[:, 1].mean(), nad=r[:, 2].mean(), inp=r[:, 3].mean())
            print('beta sweep', dev, bval, {a: round(b, 3) for a, b in sweep[f'{dev}|{bval}'].items()})
    json.dump(sweep, open('results/beta_sweep.json', 'w'), indent=1)
