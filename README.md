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

Rubric: https://github.com/paser-group/continuous-secsoft/tree/master/fall25-sqa/project

This project implements **whitebox fuzz testing** for the `mining.py` file within the `MLForensics.zip` file. The fuzz testing script `fuzz.py` automatically fuzz tests 5 methods in order to detect crashes, logical errors, or unexpected behavior. We then log the fuzzing results to the `fuzz_forensics.log` file for further analysis.

**Key Features:**

- Automated fuzz testing for 5 methods for the `mining.py` within the `MLForensics.zip` file:
  - `makeChunks`
  - `days_between`
  - `dumpContentIntoFile`
  - `getPythonFileCount`
  - `checkPythonFile`
- Logs errors with full tracebacks for debugging.
- Generates a detailed log report every run:
  - `fuzz_forensics.log` – contains run start, errors found, and a "No errors found" note on clean runs
- Integrated with GitHub Actions for automated testing on all commits.
---


## Execution Instructions
**Pre-requisites: Install python3.10+**
1. **Clone the repository**

```bash
git clone https://github.com/jmurrah/FuzzOps-FALL2025-SQA.git
cd FuzzOps-FALL2025-SQA

```
2. Create virtual env
```python3 -m venv fuzzops-venv```

3. Activate virtual env
```
source fuzzops-venv/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Run fuzzing locally
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
  - Upload artifact `fuzz_forensics.log` for review 
  - Artifacts allow team members and instructors to inspect errors directly from GitHub.
```
