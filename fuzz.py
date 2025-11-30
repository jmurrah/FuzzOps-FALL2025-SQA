import sys
import random
import string
import os
import tempfile
import traceback
from datetime import datetime, timedelta
from contextlib import contextmanager
from importlib.machinery import SourceFileLoader

NUM_ITERATIONS = 50
BUGS_FOUND = []
LOG_FILE = "fuzz_forensics.log"

# import the mining module
mining = SourceFileLoader(
    "mining",
    os.path.join(
        os.path.dirname(__file__),
        "MLForensics",
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
            data_length = random.randint(0, 100)
            data = [random.randint(0, 100) for _ in range(data_length)]
            size = random.choice([0, 1, 5, 100, random.randint(1, 20)])
            result = list(mining.makeChunks(data, size))
            flattened = [item for sublist in result for item in sublist]
            if flattened != data:
                log_bug(
                    "makeChunks",
                    f"Size: {size} (Iteration {i+1})",
                    Exception("Output data mismatch"),
                )
        except Exception as e:
            log_bug("makeChunks", f"Iteration {i+1}", e)


def fuzz_days_between(iterations):
    for i in range(iterations):
        try:
            start = datetime.now()
            d1 = start + timedelta(days=random.randint(-5000, 5000))
            d2 = start + timedelta(days=random.randint(-5000, 5000))
            val = mining.days_between(d1, d2)
            expected = abs((d2 - d1).days)
            if val < 0:
                log_bug(
                    "days_between",
                    f"{d1} vs {d2} (Iteration {i+1})",
                    Exception("Negative days returned"),
                )
            if val != expected:
                log_bug(
                    "days_between",
                    f"{d1} vs {d2} (Iteration {i+1})",
                    Exception(f"Math error: Got {val}, Expected {expected}"),
                )
        except Exception as e:
            log_bug("days_between", f"Iteration {i+1}", e)


def fuzz_dump_content(iterations):
    for i in range(iterations):
        try:
            content = get_random_string(random.randint(10, 500))
            with tempfile.TemporaryDirectory() as temp_dir:
                target_path = os.path.join(
                    temp_dir, f"fuzz_test_{random.randint(0,1000)}.txt"
                )
                size_str = mining.dumpContentIntoFile(content, target_path)
                if not os.path.exists(target_path):
                    log_bug(
                        "dumpContentIntoFile",
                        f"Iteration {i+1}",
                        Exception("File not created"),
                    )
                if str(len(content)) != size_str:
                    log_bug(
                        "dumpContentIntoFile",
                        f"Iteration {i+1}",
                        Exception(f"Size mismatch: returned {size_str}"),
                    )
        except Exception as e:
            log_bug("dumpContentIntoFile", f"Iteration {i+1}", e)


def fuzz_get_python_file_count(iterations):
    for i in range(iterations):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                py_count = random.randint(0, 10)
                junk_count = random.randint(0, 10)
                for j in range(py_count):
                    open(os.path.join(temp_dir, f"test{j}.py"), "w").close()
                for j in range(junk_count):
                    open(os.path.join(temp_dir, f"junk{j}.txt"), "w").close()
                count = mining.getPythonFileCount(temp_dir)
                if count != py_count:
                    log_bug(
                        "getPythonFileCount",
                        f"Iteration {i+1}",
                        Exception(f"Created {py_count} py files, Counted {count}"),
                    )
        except Exception as e:
            log_bug("getPythonFileCount", f"Iteration {i+1}", e)


def fuzz_check_python_file(iterations):
    known_keywords = [
        "sklearn",
        "h5py",
        "gym",
        "rl",
        "tensorflow",
        "keras",
        "tf",
        "stable_baselines",
        "tensorforce",
        "rl_coach",
        "pyqlearning",
        "MAMEToolkit",
        "chainer",
        "torch",
        "chainerrl",
    ]
    for i in range(iterations):
        try:
            target_word = random.choice(known_keywords)
            with tempfile.TemporaryDirectory() as temp_dir:
                f_path = os.path.join(temp_dir, "model.py")
                content = (
                    f"{get_random_string(10)} {target_word} {get_random_string(10)}"
                )
                with open(f_path, "w", encoding="utf-8") as f:
                    f.write(content)
                hits = mining.checkPythonFile(temp_dir)
                if hits == 0:
                    log_bug(
                        "checkPythonFile",
                        f"Iteration {i+1}",
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
