import sys
import random
import string
import os
import csv
import tempfile
from datetime import datetime, timedelta
from contextlib import contextmanager

import MLForensics.mining.mining as mining

NUM_ITERATIONS = 50
BUGS_FOUND = []
LOG_FILE = "fuzz_forensics.log"


@contextmanager
def suppress_stdout():
    """Suppress stdout temporarily for cleaner fuzzing runs."""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def log_bug(function_name, input_desc, error_msg):
    """Log bugs to stdout, BUGS_FOUND list, and log file."""
    report = f"[!] BUG IN {function_name} | Input: {input_desc} | Error: {error_msg}"
    sys.__stdout__.write(report + "\n")  # Print to console even if stdout suppressed
    BUGS_FOUND.append(report)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | {report}\n")
    except Exception as e:
        sys.__stdout__.write(f"[!] Failed to write log: {e}\n")


def log_info(message):
    """Optional info logging."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | INFO: {message}\n")
    except Exception:
        pass  # Fail silently for info logs


def get_random_string(length=100):
    chars = string.ascii_letters + string.digits + " \n"
    return "".join(random.choice(chars) for _ in range(length))


def fuzz_make_chunks(iterations):
    log_info("Starting fuzz_make_chunks")
    for i in range(iterations):
        data_length = random.randint(0, 100)
        data = [random.randint(0, 100) for _ in range(data_length)]
        size = random.choice([0, 1, 5, 100, random.randint(1, 20)])
        try:
            result = list(mining.makeChunks(data, size))
            flattened = [item for sublist in result for item in sublist]
            if flattened != data:
                log_bug("makeChunks", f"Size: {size} (Iteration {i+1})", "Output data mismatch")
        except Exception as e:
            log_bug("makeChunks", f"Size: {size} (Iteration {i+1})", f"CRASH: {e}")


def fuzz_days_between(iterations):
    log_info("Starting fuzz_days_between")
    for i in range(iterations):
        start = datetime.now()
        d1 = start + timedelta(days=random.randint(-5000, 5000))
        d2 = start + timedelta(days=random.randint(-5000, 5000))
        try:
            val = mining.days_between(d1, d2)
            expected = abs((d2 - d1).days)
            if val < 0:
                log_bug("days_between", f"{d1} vs {d2} (Iteration {i+1})", "Negative days returned")
            if val != expected:
                log_bug("days_between", f"{d1} vs {d2} (Iteration {i+1})", f"Math error: Got {val}, Expected {expected}")
        except Exception as e:
            log_bug("days_between", f"{d1} vs {d2} (Iteration {i+1})", f"CRASH: {e}")


def fuzz_dump_content(iterations):
    log_info("Starting fuzz_dump_content")
    for i in range(iterations):
        content = get_random_string(random.randint(10, 500))
        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = os.path.join(temp_dir, f"fuzz_test_{random.randint(0,1000)}.txt")
            try:
                size_str = mining.dumpContentIntoFile(content, target_path)
                if not os.path.exists(target_path):
                    log_bug("dumpContentIntoFile", f"Iteration {i+1}", "File not created")
                if str(len(content)) != size_str:
                    log_bug("dumpContentIntoFile", f"Iteration {i+1}", f"Size mismatch: returned {size_str}")
            except Exception as e:
                log_bug("dumpContentIntoFile", f"Iteration {i+1}", f"CRASH: {e}")


def fuzz_get_python_file_count(iterations):
    log_info("Starting fuzz_get_python_file_count")
    for i in range(iterations):
        with tempfile.TemporaryDirectory() as temp_dir:
            py_count = random.randint(0, 10)
            junk_count = random.randint(0, 10)
            for j in range(py_count):
                open(os.path.join(temp_dir, f"test{j}.py"), "w").close()
            for j in range(junk_count):
                open(os.path.join(temp_dir, f"junk{j}.txt"), "w").close()
            try:
                count = mining.getPythonFileCount(temp_dir)
                if count != py_count:
                    log_bug("getPythonFileCount", f"Created {py_count} py files (Iteration {i+1})", f"Counted {count}")
            except Exception as e:
                log_bug("getPythonFileCount", f"Iteration {i+1}", f"CRASH: {e}")


def fuzz_check_python_file(iterations):
    log_info("Starting fuzz_check_python_file")
    known_keywords = ["sklearn", "tensorflow", "keras", "torch"]
    for i in range(iterations):
        target_word = random.choice(known_keywords)
        with tempfile.TemporaryDirectory() as temp_dir:
            f_path = os.path.join(temp_dir, "model.py")
            content = f"{get_random_string(10)} {target_word} {get_random_string(10)}"
            with open(f_path, "w", encoding="utf-8") as f:
                f.write(content)
            try:
                hits = mining.checkPythonFile(temp_dir)
                if hits == 0:
                    log_bug("checkPythonFile", f"Hidden word: '{target_word}' (Iteration {i+1})", "Failed to detect keyword")
            except Exception as e:
                log_bug("checkPythonFile", f"Iteration {i+1}", f"CRASH: {e}")


def write_fuzz_artifacts():
    # Write fuzz_report.csv
    try:
        with open("fuzz_report.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Function", "Input", "Error"])
            for bug in BUGS_FOUND:
                try:
                    parts = bug.replace("[!] BUG IN ", "").split(" | ")
                    func = parts[0]
                    input_desc = parts[1].replace("Input: ", "")
                    error_msg = parts[2].replace("Error: ", "")
                    writer.writerow([func, input_desc, error_msg])
                except IndexError as e:
                    log_bug("write_fuzz_artifacts", bug, f"IndexError while parsing bug: {e}")
                    writer.writerow([bug, "", "IndexError parsing bug"])
    except Exception as e:
        sys.__stdout__.write(f"[!] Failed to write CSV: {e}\n")

    # Write log file
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for bug in BUGS_FOUND:
                f.write(bug + "\n")
    except Exception as e:
        sys.__stdout__.write(f"[!] Failed to write log: {e}\n")

    # Create empty files if no bugs
    if not BUGS_FOUND:
        open("fuzz_report.csv", "w").close()
        open(LOG_FILE, "w").close()


def main():
    print("--- Starting Fuzzing ---")
    with suppress_stdout():
        fuzz_make_chunks(NUM_ITERATIONS)
        fuzz_days_between(NUM_ITERATIONS)
        fuzz_dump_content(NUM_ITERATIONS)
        fuzz_get_python_file_count(NUM_ITERATIONS)
        fuzz_check_python_file(NUM_ITERATIONS)

    # Write CSV and log files
    write_fuzz_artifacts()

    if BUGS_FOUND:
        print(f"\n[FAILURE] Found {len(BUGS_FOUND)} bugs/crashes.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] No bugs found. Code is stable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
