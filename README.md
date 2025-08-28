# FPL-Optimisation-Project - Project Overview
A project built to optimise FPL points with input budget constraints and given player constraints. Data is sourced from open-source GitHub repositories as well as the official FPL API. 

# Acknowledgements
- This code follow the structure and guidance provided in [FPL-Optimization-Tools](https://github.com/otheruser/their-repo). Full credit to the original author.
- Data is found at - [FPL-Elo-Insights](https://github.com/olbauday/FPL-Elo-Insights)


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

[Single-Period Optimisation](Single_Period.md) → Optimisation model for selecting the best squad in a single gameweek.



## 🚀 Features
- Single-period FPL optimisation model.  
- Multi-period optimisation (**Still in progress** planning ahead for multiple weeks).  
- Integration of external expected points data.  
- Example outputs and solutions for validation.  
- Jupyter notebook tutorials explaining the approach.  

---

## ⚙️ How to Run  

### 1. Clone the repository  
```bash
git clone https://github.com/yourusername/FPL-Optimisation-Project.git
cd FPL-Optimisation-Project

