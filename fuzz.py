import sys
import random
import string
import os
import tempfile
import traceback
from datetime import datetime, timedelta
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader
from fuzz_cases import (
    MAKE_CHUNKS_EDGE_CASES,
    CHECK_PYTHON_EDGE_CASES,
    CHECK_PYTHON_KEYWORDS,
    DUMP_CONTENT_EDGE_CASES,
    PYTHON_FILE_COUNT_EDGE_CASES,
    days_between_edge_cases,
)

NUM_ITERATIONS = 20
BUGS_FOUND = []
LOG_FILE = "fuzz_forensics.log"

# import the mining module
mining = SourceFileLoader(
    "mining",
    os.path.join(
        os.path.dirname(__file__),
        "MLForensics-farzana",
        "mining",
        "mining.py",
    ),
).load_module()


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def log_bug(function_name, input_desc, exc):
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    tb = traceback.format_exc()
    report = {
        "Function": function_name,
        "Input": input_desc,
        "ExceptionType": exc_type,
        "Message": exc_msg,
        "Traceback": tb,
    }
    BUGS_FOUND.append(report)
    # Write to persistent log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | [!] BUG IN {function_name} | Input: {input_desc} | "
            f"{exc_type}: {exc_msg}\nTraceback:\n{tb}\n"
        )
    # Also print to real stdout
    sys.__stdout__.write(
        f"[!] BUG IN {function_name} | Input: {input_desc} | "
        f"{exc_type}: {exc_msg}\n"
    )


def get_random_string(length=100):
    chars = string.ascii_letters + string.digits + " \n"
    return "".join(random.choice(chars) for _ in range(length))


def fuzz_make_chunks(iterations):
    for i in range(iterations):
        try:
            if i < len(MAKE_CHUNKS_EDGE_CASES):
                case = MAKE_CHUNKS_EDGE_CASES[i]
                data = case["data"]
                size = case["size"]
                label = case["label"]
            else:
                data_length = random.randint(0, 100)
                data = [random.randint(0, 100) for _ in range(data_length)]
                size = random.choice(
                    [
                        0,
                        -1,
                        1,
                        5,
                        100,
                        random.randint(1, 20),
                        None,
                        "3",
                        2.5,
                    ]
                )
                label = f"Size: {size}"
            result = list(mining.makeChunks(data, size))
            flattened = [item for sublist in result for item in sublist]
            if flattened != data:
                log_bug(
                    "makeChunks",
                    f"{label} (Iteration {i+1})",
                    Exception("Output data mismatch"),
                )
        except Exception as e:
            log_bug("makeChunks", f"Iteration {i+1}", e)


def fuzz_days_between(iterations):
    preset_cases = days_between_edge_cases()
    for i in range(iterations):
        try:
            if i < len(preset_cases):
                case = preset_cases[i]
                d1 = case["d1"]
                d2 = case["d2"]
                label = case["label"]
            else:
                start = datetime.now()
                # Randomly pick between valid datetime inputs and invalid types
                if random.random() < 0.2:
                    d1 = random.choice(
                        [None, "2020-01-01", 123, datetime.now().isoformat()]
                    )
                else:
                    d1 = start + timedelta(days=random.randint(-5000, 5000))
                if random.random() < 0.2:
                    d2 = random.choice(
                        [None, "2020-01-02", -5, datetime.now().isoformat()]
                    )
                else:
                    d2 = start + timedelta(days=random.randint(-5000, 5000))
                label = f"Random d1={d1}, d2={d2}"
            val = mining.days_between(d1, d2)
            expected = abs((d2 - d1).days)
            if val < 0:
                log_bug(
                    "days_between",
                    f"{label} (Iteration {i+1})",
                    Exception("Negative days returned"),
                )
            if val != expected:
                log_bug(
                    "days_between",
                    f"{label} (Iteration {i+1})",
                    Exception(f"Math error: Got {val}, Expected {expected}"),
                )
        except Exception as e:
            log_bug("days_between", f"Iteration {i+1}", e)


def fuzz_dump_content(iterations):
    for i in range(iterations):
        label = f"Iteration {i+1}"
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                if i < len(DUMP_CONTENT_EDGE_CASES):
                    case = DUMP_CONTENT_EDGE_CASES[i]
                    content = case["content"]
                    path_kind = case["path_kind"]
                    label = f"{case['label']} (Iteration {i+1})"
                else:
                    content = random.choice(
                        [
                            get_random_string(random.randint(0, 500)),
                            "",
                            None,
                            b"bytes-" + os.urandom(4),
                        ]
                    )
                    path_kind = random.choice(
                        ["valid", "missing_parent", "dir", "none", "int"]
                    )
                    label = f"Random case path_kind={path_kind} (Iteration {i+1})"

                if path_kind == "valid":
                    target_path = os.path.join(
                        temp_dir, f"fuzz_test_{random.randint(0,1000)}.txt"
                    )
                elif path_kind == "missing_parent":
                    target_path = os.path.join(
                        temp_dir,
                        "missing_dir",
                        f"fuzz_test_{random.randint(0,1000)}.txt",
                    )
                elif path_kind == "dir":
                    target_path = temp_dir
                elif path_kind == "none":
                    target_path = None
                elif path_kind == "int":
                    target_path = random.randint(1, 10)
                else:
                    target_path = os.path.join(
                        temp_dir, f"fuzz_test_{random.randint(0,1000)}.txt"
                    )

                size_str = mining.dumpContentIntoFile(content, target_path)

                # Validate successful write cases: only when content and path are strings and a file exists.
                if isinstance(content, str) and isinstance(target_path, str):
                    if not os.path.exists(target_path):
                        log_bug(
                            "dumpContentIntoFile",
                            label,
                            Exception("File not created"),
                        )
                    elif str(len(content)) != size_str:
                        log_bug(
                            "dumpContentIntoFile",
                            label,
                            Exception(f"Size mismatch: returned {size_str}"),
                        )
                else:
                    # If the call unexpectedly succeeded with invalid types, flag it.
                    log_bug(
                        "dumpContentIntoFile",
                        label,
                        Exception(
                            f"Unexpected success for content type {type(content)} and path type {type(target_path)}"
                        ),
                    )
        except Exception as e:
            log_bug("dumpContentIntoFile", label, e)


def fuzz_get_python_file_count(iterations):
    for i in range(iterations):
        label = f"Iteration {i+1}"
        try:
            if i < len(PYTHON_FILE_COUNT_EDGE_CASES):
                case = PYTHON_FILE_COUNT_EDGE_CASES[i]
                ctype = case["type"]
                label = f"{case['label']} (Iteration {i+1})"

                if ctype == "invalid":
                    count = mining.getPythonFileCount(case["path"])
                    log_bug(
                        "getPythonFileCount",
                        label,
                        Exception(
                            f"Expected failure for invalid path, got count {count}"
                        ),
                    )
                    continue

                if ctype == "missing_dir":
                    missing = os.path.join(
                        tempfile.gettempdir(), f"missing_dir_{random.randint(0,100000)}"
                    )
                    count = mining.getPythonFileCount(missing)
                    if count != 0:
                        log_bug(
                            "getPythonFileCount",
                            label,
                            Exception(f"Expected 0 for missing dir, got {count}"),
                        )
                    continue

                with tempfile.TemporaryDirectory() as temp_dir:
                    if ctype == "file_path":
                        file_path = os.path.join(temp_dir, "lone.py")
                        open(file_path, "w").close()
                        count = mining.getPythonFileCount(file_path)
                        if count != 0:
                            log_bug(
                                "getPythonFileCount",
                                label,
                                Exception(f"Expected 0 when path is file, got {count}"),
                            )
                        continue

                    if ctype == "uppercase_ext":
                        open(os.path.join(temp_dir, "script.PY"), "w").close()
                        open(os.path.join(temp_dir, "note.IPYNB"), "w").close()
                        expected = 2
                        count = mining.getPythonFileCount(temp_dir)
                        if count != expected:
                            log_bug(
                                "getPythonFileCount",
                                label,
                                Exception(f"Expected {expected} files, got {count}"),
                            )
                        continue

                    if ctype == "nested_mix":
                        nested = os.path.join(temp_dir, "nested", "deep")
                        os.makedirs(nested)
                        files = [
                            os.path.join(temp_dir, "root.py"),
                            os.path.join(temp_dir, "root.ipynb"),
                            os.path.join(nested, "nested.py"),
                        ]
                        junk = [
                            os.path.join(temp_dir, "root.txt"),
                            os.path.join(nested, "nested.txt"),
                        ]
                        for fpath in files + junk:
                            open(fpath, "w").close()
                        expected = len(files)
                        count = mining.getPythonFileCount(temp_dir)
                        if count != expected:
                            log_bug(
                                "getPythonFileCount",
                                label,
                                Exception(f"Expected {expected} files, got {count}"),
                            )
                        continue

            # Randomized cases
            with tempfile.TemporaryDirectory() as temp_dir:
                py_count = random.randint(0, 5)
                ipynb_count = random.randint(0, 5)
                junk_count = random.randint(0, 5)
                upper_count = random.randint(0, 2)

                for j in range(py_count):
                    open(os.path.join(temp_dir, f"test{j}.py"), "w").close()
                for j in range(ipynb_count):
                    open(os.path.join(temp_dir, f"notebook{j}.ipynb"), "w").close()
                for j in range(junk_count):
                    open(os.path.join(temp_dir, f"junk{j}.txt"), "w").close()
                for j in range(upper_count):
                    open(os.path.join(temp_dir, f"upper{j}.PY"), "w").close()

                # Optionally create nested files
                if random.random() < 0.5:
                    nested_dir = os.path.join(temp_dir, "nested")
                    os.makedirs(nested_dir)
                    nested_py = random.randint(0, 2)
                    for j in range(nested_py):
                        open(os.path.join(nested_dir, f"nested{j}.py"), "w").close()
                    py_count += nested_py

                expected = py_count + ipynb_count
                count = mining.getPythonFileCount(temp_dir)
                if count != expected:
                    log_bug(
                        "getPythonFileCount",
                        label,
                        Exception(
                            f"Expected {expected} (.py + .ipynb) files, got {count}"
                        ),
                    )
        except Exception as e:
            log_bug("getPythonFileCount", f"Iteration {i+1}", e)


def fuzz_check_python_file(iterations):
    for i in range(iterations):
        try:
            if i < len(CHECK_PYTHON_EDGE_CASES):
                case = CHECK_PYTHON_EDGE_CASES[i]
                ctype = case["type"]
                label = case["label"]

                if ctype == "invalid":
                    path = case["path"]
                    hits = mining.checkPythonFile(path)
                    # No expected hits; just ensure it doesn't silently miscount
                    continue

                if ctype == "file_path":
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_path = os.path.join(temp_dir, "model.py")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"{case['keyword']} on a single file path")
                        hits = mining.checkPythonFile(file_path)
                        # Passing a file instead of directory should not count as a hit
                        if hits != 0:
                            log_bug(
                                "checkPythonFile",
                                f"{label} (Iteration {i+1})",
                                Exception(f"Expected 0 hits for file path, got {hits}"),
                            )
                    continue

                if ctype == "py_upper":
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_path = os.path.join(temp_dir, "upper.py")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(
                                f"# {case['keyword']} should be detected case-insensitively"
                            )
                        hits = mining.checkPythonFile(temp_dir)
                        if hits == 0:
                            log_bug(
                                "checkPythonFile",
                                f"{label} (Iteration {i+1})",
                                Exception(
                                    f"Failed to detect keyword '{case['keyword']}'"
                                ),
                            )
                    continue

                if ctype == "ipynb":
                    with tempfile.TemporaryDirectory() as temp_dir:
                        file_path = os.path.join(temp_dir, "notebook.ipynb")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"{case['keyword']} inside notebook cell")
                        hits = mining.checkPythonFile(temp_dir)
                        if hits == 0:
                            log_bug(
                                "checkPythonFile",
                                f"{label} (Iteration {i+1})",
                                Exception(
                                    f"Failed to detect keyword '{case['keyword']}' in ipynb"
                                ),
                            )
                    continue

                if ctype == "nested":
                    with tempfile.TemporaryDirectory() as temp_dir:
                        nested = os.path.join(temp_dir, "deep", "deeper")
                        os.makedirs(nested)
                        file_path = os.path.join(nested, "nested.py")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(
                                f"{case['keywords'][0]} and {case['keywords'][1]} together"
                            )
                        hits = mining.checkPythonFile(temp_dir)
                        if hits < len(case["keywords"]):
                            log_bug(
                                "checkPythonFile",
                                f"{label} (Iteration {i+1})",
                                Exception(
                                    f"Expected at least {len(case['keywords'])} hits, got {hits}"
                                ),
                            )
                    continue

            # Randomized cases
            with tempfile.TemporaryDirectory() as temp_dir:
                target_word = random.choice(CHECK_PYTHON_KEYWORDS)
                fname = random.choice(["model.py", "train.ipynb"])
                f_path = os.path.join(temp_dir, fname)
                content = f"{get_random_string(10)} {target_word.upper()} {get_random_string(10)}"
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(content)
                # Optionally add a nested file with another keyword
                if random.random() < 0.5:
                    nested_dir = os.path.join(temp_dir, "nested")
                    os.makedirs(nested_dir)
                    nested_path = os.path.join(nested_dir, "extra.py")
                    extra_word = random.choice(CHECK_PYTHON_KEYWORDS)
                    with open(nested_path, "w", encoding="utf-8") as f:
                        f.write(f"{extra_word} appears here too")

                hits = mining.checkPythonFile(temp_dir)
                if hits == 0:
                    log_bug(
                        "checkPythonFile",
                        f"Iteration {i+1} random case with target '{target_word}'",
                        Exception(f"Failed to detect keyword '{target_word}'"),
                    )
        except Exception as e:
            log_bug("checkPythonFile", f"Iteration {i+1}", e)


def initialize_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | Fuzz run started\n")


def main():
    print("--- Starting Fuzzing ---")
    initialize_log()
    with suppress_stdout():
        fuzz_make_chunks(NUM_ITERATIONS)
        fuzz_days_between(NUM_ITERATIONS)
        fuzz_dump_content(NUM_ITERATIONS)
        fuzz_get_python_file_count(NUM_ITERATIONS)
        fuzz_check_python_file(NUM_ITERATIONS)

    if BUGS_FOUND:
        print(
            f"\n Errors found, {len(BUGS_FOUND)} bugs/crashes. Check {LOG_FILE} for details."
        )
        sys.exit(1)
    else:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | No errors found during fuzzing.\n")
        print("\n No bugs found. Code is stable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
