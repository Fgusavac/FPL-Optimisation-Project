# FPL-Optimisation-Project
A project built to optimise FPL points with a input budget constraints and given player constraints. Data is found from open source GitHub repositories as well as the offical FPL API


📌 Project Overview

This project explores Fantasy Premier League (FPL) optimisation using machine learning and mathematical programming. The aim is to create algorithms that maximise expected points across single and multi-gameweek scenarios, given constraints such as budget, squad size, and position requirements.

The project combines:

Linear programming (LP) / Mixed-integer programming (MIP) for optimisation.

Python (pandas, numpy, etc.) for data handling.

Solver integration (CBC, etc.) for finding optimal squads.

FPL Review & API data for realistic inputs.

FPL-Optimisation-Project/
│── FPL Machine learning/       # Jupyter notebooks and experiments
│   ├── code/                   # Main optimisation notebooks and outputs
│   │   ├── FPL.ipynb
│   │   ├── Tutorial 1 - GK problem with method.ipynb
│   │   ├── Tutorial 2 - Single Period FPL.ipynb
│   │   ├── single_period.mps   # MPS formulation for single-period optimisation
│   │   ├── solution.txt        # Example solution outputs
│   │   ├── ...
│   ├── data/                   # Input datasets
│   │   ├── fplreview.csv       # Expected points from FPL Review
│   │   ├── players.csv         # Player metadata
│   │   ├── teams.csv           # Team information
│   ├── solver/                 # Optimisation solver experiments
│   │   └── src/                # Python implementations of solvers
│   │       ├── multi_period.py # Multi-period optimisation model
│   │       ├── single_period.py# Single-period optimisation model
│   │       └── single_period.mps
│
│── README.md                   # Project documentation (this file)



---

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
