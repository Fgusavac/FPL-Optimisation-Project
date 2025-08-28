
---

## 🔑 Key Features
- Fetches **live player & team data** from the official [FPL API](https://fantasy.premierleague.com/api/bootstrap-static/).
- Integrates **FPL Review projections** and custom CSV datasets.
- Builds a **Mixed Integer Programming (MIP)** model using [`sasoptpy`](https://sassoftware.github.io/sasoptpy/).
- Enforces real FPL rules:
  - 15-player squad
  - 11-player lineup
  - Captain & Vice-Captain constraints
  - Position-specific formations
  - Maximum 3 players per team
  - Budget limit
- Exports model in `.mps` format and solves with [CBC solver](https://github.com/coin-or/Cbc).
- Runs across multiple budget values in **parallel** using `ProcessPoolExecutor`.

---

## 🛠️ How it Works

1. **Data Loading (`get_data`)**
   - Calls the FPL API (`bootstrap-static`).
   - Reads `fplreview.csv`, `players.csv`, and `teams.csv` from `../data/`.
   - Merges player stats, team info, and projected points into one dataset.

2. **Optimisation Model (`solve_single_period_fpl`)**
   - Defines binary decision variables for:
     - `squad` (15 players total)
     - `lineup` (11 starters)
     - `captain` (1 player)
     - `vicecap` (1 player)
   - Adds constraints for FPL rules (squad size, budget, formations, team limits).
   - Objective: **Maximise expected points**.

3. **Solver Execution**
   - Exports `.mps` model file.
   - Runs CBC solver via subprocess.
   - Reads solution file and reconstructs chosen squad.

4. **Results**
   - Returns a DataFrame of selected players with:
     - Name, position, price, expected points, lineup/captain/vicecap status.
   - Computes and prints **total expected points** for given budget.

5. **Parallel Execution (`__main__`)**
   - Runs optimisation for budgets from **£80m → £120m** in steps of £5m.
   - Uses `ProcessPoolExecutor` to solve in parallel.
   - Outputs a budget vs. expected points DataFrame.

---

## ▶️ Example Usage

```bash
# Run optimisation for budgets between £80m and £120m
python single_period.py
