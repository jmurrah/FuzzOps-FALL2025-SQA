# FuzzOps-FALL2025-SQA

COMP-5710/COMP-6710 Course Project – Fall 2025

## Team Name
FuzzOps

## Group Members

| Name           | Email              |
|----------------|--------------------|
| Cooper Jackson | cej0054@auburn.edu |
| Jacob Murrah   | jhm0068@auburn.edu |
| JD Wilks       | jdw0143@auburn.edu |
| Kritika Vyas   | kzv0032@auburn.edu |

---

## Project Overview

This project implements **fuzz testing** for the `MLForensics.mining.mining` Python module.  
The fuzz testing script (`fuzz.py`) automatically generates random inputs to test core functions, detect crashes, logical errors, or unexpected behavior, and logs detailed reports for analysis.

**Key Features:**

- Automated fuzz testing for critical functions:
  - `makeChunks`
  - `days_between`
  - `dumpContentIntoFile`
  - `getPythonFileCount`
  - `checkPythonFile`
- Logs errors with full tracebacks for debugging.
- Generates a detailed log report every run:
  - `fuzz_forensics.log` – contains run start, errors found, and a "No errors found" note on clean runs
- Integrated with **GitHub Actions** for automated testing on push and pull request events.
---


## Setup Instructions
**Pre-requisites: Install python3.10+**
1. **Clone the repository**

```bash
git clone git@github.com:jmurrah/FuzzOps-FALL2025-SQA.git
cd FuzzOps-FALL2025-SQA

```
2. Create virtual env
```python3 -m venv venv```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run fuzz  locally**
```bash
python fuzz.py 
```

5. **GitHub Actions Integration**
The project is configured to automatically run fuzz testing using GitHub Actions.
```
Workflow: .github/workflows/continuous-integration.yml
- Trigger: On push or pull request to feature or main branches.
- Steps:
  - Checkout repository 
  - Set up Python 
  - Install dependencies 
  - Run fuzz.py 
  - Upload artifact (fuzz_forensics.log) for review 
  - Artifacts allow team members and instructors to inspect errors directly from GitHub.
```
