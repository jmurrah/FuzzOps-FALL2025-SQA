# SQA Report

Report your activities and lessons learned.

## Activities

1. Unzipped the `MLForensics.zip` folder into the root of the project directory in order to interact with the python files.
2. We began by looking at all the Python files in the unzipped `MLForensics.zip` folder and decided to chose the `mining.py` file to fuzz and log since it had multiple self-contained methods with clear inputs and outputs.
3. The 5 methods in the `mining.py` that we chose to fuzz and log are listed below:
    - `makeChunks(the_list, size_)`: splits a list into evenly sized chunks.
    - `days_between(d1_, d2_)`: returns the absolute difference in days between two dates.
    - `dumpContentIntoFile(strP, fileP)`: writes provided text to disk and reports the byte length.
    - `getPythonFileCount(path2dir)`: counts how many `.py` files exist under a directory tree.
    - `checkPythonFile(path2dir)`: scans Python files for ML keywords (e.g., sklearn, tensorflow).
4. Before fuzzing, we looked at each method and implemented logging forensics. This enabled us to better understand the data structures and formats used within the methods.
5. After adding logging, for each method we performed whitebox fuzzing by looking at the logging results, inputs, and code to generate fuzzing inputs to detect crashes, logical errors, or unexpected behavior.
6. Finally, we created the `continuous-integration.yml` GitHub Action to execute the `fuzz.py` on every commit to execute fuzzing on the `mining.py file.

## Lessons Learned

1. Thoroughly understanding the inputs and code for methods makes generating fuzzing inputs much easier. With a strong understanding of python you can deduce which inputs will cause crashes given the source code for a method.
2. Implementing logging for methods allow you to see the exact data format and flow of data within 


<!-- 1. Fuzz Testing: Learned automated input generation for edge cases.
2. Error Logging: Implemented comprehensive error handling and tracebacks.
3. CI/CD: Automated regression testing with GitHub Actions.
4. Python Exception Handling: Logged multiple types of runtime errors (IndexError, ValueError, OSError, etc.).
5. SQA Best Practices: Demonstrated reproducibility, traceability, and code robustness. -->
