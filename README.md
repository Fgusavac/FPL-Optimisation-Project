# FPL-Optimisation-Project
A project built to optimise FPL points with a input budget constraints and given player constraints. Data is found from open source GitHub repositories as well as the offical FPL API


# FPL-Optimisation-Project
A project built to optimise FPL points with input budget constraints and given player constraints. Data is sourced from open-source GitHub repositories as well as the official FPL API.  

## 📌 Project Overview
This project explores Fantasy Premier League (FPL) optimisation using machine learning and mathematical programming. The aim is to create algorithms that maximise expected points across single and multi-gameweek scenarios, given constraints such as budget, squad size, and position requirements.  

The project combines:  
- Linear programming (LP) / Mixed-integer programming (MIP) for optimisation.  
- Python (pandas, numpy, etc.) for data handling.  
- Solver integration (CBC, etc.) for finding optimal squads.  
- FPL Review & API data for realistic inputs.  

## 📂 Project Structure

```text
FPL-Optimisation-Project/
├── FPL Machine learning/        # Jupyter notebooks and experiments
│   ├── code/                    # Main optimisation notebooks and outputs
│   │   ├── FPL.ipynb
│   │   ├── Tutorial 1 - GK problem with method.ipynb
│   │   ├── Tutorial 2 - Single Period FPL.ipynb
│   │   ├── single_period.mps    # MPS formulation for single-period optimisation
│   │   ├── solution.txt         # Example solution outputs
│   │   └── …
│   ├── data/                    # Input datasets
│   │   ├── fplreview.csv        # Expected points from FPL Review
│   │   ├── players.csv          # Player metadata
│   │   └── teams.csv            # Team information
│   └── solver/                  # Optimisation solver experiments
│       └── src/                 # Python implementations of solvers
│           ├── multi_period.py  # Multi-period optimisation model
│           ├── single_period.py # Single-period optimisation model
│           └── single_period.mps
│
└── README.md                    # Project documentation (this file)
```

# ⚽ Single-Period FPL Optimisation

This module implements a **single-period Fantasy Premier League (FPL) optimisation model**.  
It fetches live FPL data, merges it with external datasets, and builds a mathematical programming model to select the best squad under budget and game rules.  

[Single-Period Optimisation](single_period.md) → Optimisation model for selecting the best squad in a single gameweek.

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



## 🚀 Features
- Single-period FPL optimisation model.  
- Multi-period optimisation (planning ahead for multiple weeks).  
- Integration of external expected points data.  
- Example outputs and solutions for validation.  
- Jupyter notebook tutorials explaining the approach.  

---

## ⚙️ How to Run  

### 1. Clone the repository  
```bash
git clone https://github.com/yourusername/FPL-Optimisation-Project.git
cd FPL-Optimisation-Project

