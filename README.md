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

## Deliverables
- Log Files:
  - `mining_fuzz_bug_report.log` - Report of bugs found from fuzzing
  - `mining_log_forensics.log` - Shows logs produced from integrating forensics
- Code:
  - `fuzz.py` - Main file where the code functions responsible for fuzzing and execution reside.
  - `fuzz_cases.py` - File to cleanly define all the fuzzing inputs to use in our fuzzing functions.
- Location of continuous integration (CI) build:
  - NOTE: a new CI build is executed after every commit. It is EXPECTED to FAIL since our fuzzing finds bugs in the methods we chose!
  - Specific build: https://github.com/jmurrah/FuzzOps-FALL2025-SQA/actions/runs/19848730308/job/56871043924
  - All builds: https://github.com/jmurrah/FuzzOps-FALL2025-SQA/actions/workflows/continuous-integration.yml
- `screenshots/` - Folder that contains all screenshots that showing execution of forensics, fuzzing, and continuous integration
- `SQA-REPO.md` - Report describing what activities we performed and what we have learned

NOTE: When errors/bugs are found during fuzzing, our CI pipeline will FAIL (this is expected).

## Project Overview

Rubric: https://github.com/paser-group/continuous-secsoft/tree/master/fall25-sqa/project

This project implements **whitebox fuzz testing** for the `mining.py` file within the `MLForensics.zip` file. The fuzz testing script `fuzz.py` automatically fuzz tests 5 methods in order to detect crashes, logical errors, or unexpected behavior. We then log the fuzzing results to the `mining_fuzz_bug_report.log` file for further analysis.

**Key Features:**

- Automated fuzz testing for 5 methods for the `mining.py` within the `MLForensics.zip` file:
  - `makeChunks`
  - `days_between`
  - `dumpContentIntoFile`
  - `getPythonFileCount`
  - `checkPythonFile`
- Logs errors with full tracebacks for debugging.
- Generates detailed log reports every run:
  - `mining_fuzz_bug_report.log` – contains run start, errors found, and a "No errors found" note on clean runs
  - `mining_log_forensics.log` - contains comprhensive logs for the 5 methods in mining.py. This includes entry/exit points, debug info, type checks, and workflow details.
- Integrated with GitHub Actions for automated testing on all commits.

## Execution Instructions
Pre-requisites: Install python3.10+
1. Clone the repository

```bash
git clone https://github.com/jmurrah/FuzzOps-FALL2025-SQA.git
cd FuzzOps-FALL2025-SQA
```

2. Create virtual env
```bash
python3 -m venv fuzzops-venv
```

3. Activate virtual env
```bash
source fuzzops-venv/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Run fuzzing locally
```bash
python3 fuzz.py 
```

5. GitHub Actions Integration
The project is configured to automatically run fuzz testing on `mining.py` using GitHub Actions.
```
Workflow: .github/workflows/continuous-integration.yml
- Trigger: On push or pull request to feature or main branches.
- Steps:
  - Checkout repository 
  - Set up Python 
  - Install dependencies 
  - Run fuzz.py 
  - Upload artifact `mining_fuzz_bug_report.log` for review 
  - Artifacts allow team members and instructors to inspect errors directly from GitHub.
```
NOTE: When errors/bugs are found during fuzzing, our CI pipeline will FAIL (this is expected).
