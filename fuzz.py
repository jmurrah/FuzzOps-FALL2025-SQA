import sys
import random
import string
import os
import tempfile
from datetime import datetime, timedelta
from contextlib import contextmanager

import MLForensics.mining.mining as mining

NUM_ITERATIONS = 50
BUGS_FOUND = []


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def log_bug(function_name, input_desc, error_msg):
    report = f"[!] BUG IN {function_name} | Input: {input_desc} | Error: {error_msg}"
    sys.__stdout__.write(
        report + "\n"
    )  # writes directly to real stdout to work around suppression
    BUGS_FOUND.append(report)


def get_random_string(length=100):
    chars = string.ascii_letters + string.digits + " \n"
    return "".join(random.choice(chars) for _ in range(length))


def fuzz_make_chunks(iterations):
    for _ in range(iterations):
        data_length = random.randint(0, 100)
        data = [random.randint(0, 100) for _ in range(data_length)]
        size = random.choice([0, 1, 5, 100, random.randint(1, 20)])

        try:
            result = list(mining.makeChunks(data, size))
            flattened = [item for sublist in result for item in sublist]
            if flattened != data:
                log_bug("makeChunks", f"Size: {size}", "Output data mismatch")
        except Exception as e:
            log_bug("makeChunks", f"Size: {size}", f"CRASH: {e}")


def fuzz_days_between(iterations):
    for _ in range(iterations):
        start = datetime.now()
        d1 = start + timedelta(days=random.randint(-5000, 5000))
        d2 = start + timedelta(days=random.randint(-5000, 5000))

        try:
            val = mining.days_between(d1, d2)
            if val < 0:
                log_bug("days_between", f"{d1} vs {d2}", "Negative days returned")
            expected = abs((d2 - d1).days)
            if val != expected:
                log_bug(
                    "days_between",
                    f"{d1} vs {d2}",
                    f"Math error: Got {val}, Expected {expected}",
                )
        except Exception as e:
            log_bug("days_between", f"{d1}, {d2}", f"CRASH: {e}")


def fuzz_dump_content(iterations):
    for _ in range(iterations):
        content = get_random_string(random.randint(10, 500))
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = os.path.join(
                temp_dir, f"fuzz_test_{random.randint(0,1000)}.txt"
            )
            try:
                size_str = mining.dumpContentIntoFile(content, target_path)
                if not os.path.exists(target_path):
                    log_bug("dumpContentIntoFile", "Standard Input", "File not created")
                if str(len(content)) != size_str:
                    log_bug(
                        "dumpContentIntoFile",
                        f"Len: {len(content)}",
                        f"Size mismatch: returned {size_str}",
                    )
            except Exception as e:
                log_bug("dumpContentIntoFile", "Random String", f"CRASH: {e}")


def fuzz_get_python_file_count(iterations):
    for _ in range(iterations):
        with tempfile.TemporaryDirectory() as temp_dir:
            py_count = random.randint(0, 10)
            junk_count = random.randint(0, 10)
            for i in range(py_count):
                open(os.path.join(temp_dir, f"test{i}.py"), "w").close()
            for i in range(junk_count):
                open(os.path.join(temp_dir, f"junk{i}.txt"), "w").close()

            try:
                count = mining.getPythonFileCount(temp_dir)
                if count != py_count:
                    log_bug(
                        "getPythonFileCount",
                        f"Created {py_count} py files",
                        f"Counted {count}",
                    )
            except Exception as e:
                log_bug("getPythonFileCount", temp_dir, f"CRASH: {e}")


def fuzz_check_python_file(iterations):
    known_keywords = ["sklearn", "tensorflow", "keras", "torch"]
    for _ in range(iterations):
        target_word = random.choice(known_keywords)
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, "model.py")
            content = f"{get_random_string(10)} {target_word} {get_random_string(10)}"
            with open(f_path, "w", encoding="utf-8") as f:
                f.write(content)

            try:
                hits = mining.checkPythonFile(temp_dir)
                if hits == 0:
                    log_bug(
                        "checkPythonFile",
                        f"Hidden word: '{target_word}'",
                        "Failed to detect keyword",
                    )
            except Exception as e:
                log_bug("checkPythonFile", temp_dir, f"CRASH: {e}")


def main():
    print("--- Starting Fuzzing ---")
    with suppress_stdout():
        fuzz_make_chunks(NUM_ITERATIONS)
        fuzz_days_between(NUM_ITERATIONS)
        fuzz_dump_content(NUM_ITERATIONS)
        fuzz_get_python_file_count(NUM_ITERATIONS)
        fuzz_check_python_file(NUM_ITERATIONS)

    if BUGS_FOUND:
        print(f"\n[FAILURE] Found {len(BUGS_FOUND)} bugs/crashes.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] No bugs found. Code is stable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
