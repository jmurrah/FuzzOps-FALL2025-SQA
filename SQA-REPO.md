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
2. Implementing logging for methods allows you to see the exact data flow and format within a method. Understanding the inputs and outputs of additional calls within a method allows you to create inputs that will break those internal calls.
3. Setting up GitHub Actions is very simple and also substantially increases your confidence in your code's quality. This makes the barrier of entry to integrating code quality checks extremely small.
4. Since python is dynamically typed, validating the input data types is very important becuase almost anything can be passed into the methods. This also makes fuzzing a lot more flexible because many more input formats need to be tested.
5. Utilizing git and GitHub makes collaborating on code seamless. You and a teammate can simultaneously work on the same code from anywhere in the world.
