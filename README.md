# Resource-aware adaptive GUI model — simulation code

Code and results for the simulation study in the paper:

> Ні Я. Формальна модель проєктування адаптивного графічного інтерфейсу комп'ютерних систем з урахуванням ресурсної вартості адаптації. [журнал, рік — додати після публікації]

## What it does

Monte Carlo comparison of four GUI adaptation policies on three device classes
(desktop on mains power, mid-range laptop on battery, low-end laptop on battery), 10 000 sessions each:

| Policy | Decision rule |
|---|---|
| `never` | no adaptation |
| `always` | apply the candidate with the largest positive expected gain G |
| `user` | user-cost-only criterion G − C_U > θ |
| `proposed` | V = G − C_U − β·C_R > θ, plus response-time (τ_max = 200 ms) and energy-budget constraints |

Simulated users have an unknown pattern (novice / expert) inferred online with a Bayesian update.
Three adaptation candidates of increasing cost are modelled (enlarge primary action,
simplify navigation, generative page rebuild). A sweep over β ∈ {0, 1, 2, 5, 10, 20} is included.

**All parameters are assumptions of the simulation study** (listed at the top of `sim.py`).
The results describe the relative behaviour of the decision rules, not measured values of real systems.

## Reproduce

```bash
pip install -r requirements.txt
python sim.py    # writes results/policies.json and results/beta_sweep.json (seed 2026, deterministic)
python plot.py   # writes figures/fig5_policies.png and figures/fig6_beta.png
```

Tested with Python 3.13, NumPy 2.x, Matplotlib 3.x. A full run takes a few minutes on a laptop.

## Files

- `sim.py` — model, policies and simulation (Table 6, Fig. 5–6 of the paper)
- `plot.py` — figures
- `results/` — simulation outputs used in the paper
- `figures/` — figures used in the paper

## License

MIT, see `LICENSE`.
