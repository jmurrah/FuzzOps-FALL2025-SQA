# SQA Report

Report your activities and lessons learned.

## Activities

1. Unzip the `MLForensics.zip` folder into the root of the project directory in order to interact with the python files.
2. We began by looking at all the Python files in the unzipped `MLForensics.zip` folder and decided to chose the `mining.py` file to fuzz and log since it had multiple self-contained methods with clear inputs and outputs.
3. The 5 methods in the `mining.py` that we chose to fuzz and log are listed below:
    - `makeChunks(the_list, size_)`: splits data into evenly sized chunks.
    - `days_between(d1_, d2_)`: computes absolute day difference between dates.
    - `dumpContentIntoFile(strP, fileP)`: writes repository summaries to disk.
    - `getPythonFileCount(path2dir)`: counts Python files in a tree.
    - `checkPythonFile(path2dir)`: scans files for ML keywords.

## Lessons Learned

1. Fuzz Testing: Learned automated input generation for edge cases.
2. Error Logging: Implemented comprehensive error handling and tracebacks.
3. CI/CD: Automated regression testing with GitHub Actions.
4. Python Exception Handling: Logged multiple types of runtime errors (IndexError, ValueError, OSError, etc.).
5. SQA Best Practices: Demonstrated reproducibility, traceability, and code robustness.
