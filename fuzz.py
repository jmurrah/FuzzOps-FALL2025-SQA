import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import MLForensics.mining.mining as mining

BUGS = []
PATTERN_DICT = [
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


def bug(name, detail, exc=None):
    BUGS.append((name, detail, repr(exc) if exc else None))
    print(f"[BUG] {name}: {detail} {f' exc={exc}' if exc else ''}")


def fuzz_dump_content(n=40):
    with TemporaryDirectory() as tmpdir:
        for i in range(n):
            content = "".join(
                random.choices(string.ascii_letters + string.digits + " \n", k=random.randint(0, 200))
            )
            path = Path(tmpdir) / f"file_{i}.txt"
            try:
                size = int(mining.dumpContentIntoFile(content, str(path)))
                if size != len(content):
                    bug("dumpContentIntoFile", f"size mismatch expected={len(content)} got={size}")
            except Exception as exc:
                bug("dumpContentIntoFile", f"exception for {path}", exc)


def fuzz_make_chunks(n=50):
    for _ in range(n):
        data = [random.randint(-1000, 1000) for _ in range(random.randint(0, 50))]
        size = random.randint(1, max(1, len(data) or 1))
        try:
            chunks = list(mining.makeChunks(data, size))
            if [x for chunk in chunks for x in chunk] != data:
                bug("makeChunks", "flattened output does not match input")
            if any(len(chunk) > size for chunk in chunks if chunk):
                bug("makeChunks", "chunk larger than requested size")
        except Exception as exc:
            bug("makeChunks", f"exception size={size} len={len(data)}", exc)


def expected_hits(lines):
    hits = 0
    for text in lines:
        low = text.lower()
        for pat in PATTERN_DICT:
            if pat.lower() in low:
                hits += 1
    return hits


def fuzz_check_python_file(n=25):
    with TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        try:
            if mining.checkPythonFile(str(base)) != 0:
                bug("checkPythonFile", "empty dir did not return zero")
        except Exception as exc:
            bug("checkPythonFile", "exception on empty dir", exc)

        for i in range(n):
            lines = []
            for _ in range(random.randint(1, 5)):
                if random.random() < 0.6:
                    lines.append(f"This line mentions {random.choice(PATTERN_DICT)}")
                else:
                    lines.append("noise")
            expect = expected_hits(lines)
            sub = base / f"case_{i}"
            sub.mkdir()
            (sub / f"f_{i}.py").write_text("\n".join(lines), encoding="latin-1")
            try:
                got = mining.checkPythonFile(str(sub))
                if got != expect:
                    bug("checkPythonFile", f"expected {expect} got {got} in {sub}")
            except Exception as exc:
                bug("checkPythonFile", f"exception in {sub}", exc)


def fuzz_days_between(n=50):
    for _ in range(n):
        start = datetime(2000, 1, 1)
        d1 = start + timedelta(days=random.randint(0, 5000))
        d2 = start + timedelta(days=random.randint(0, 5000))
        try:
            got = mining.days_between(d1, d2)
            expect = abs((d2 - d1).days)
            if got != expect:
                bug("days_between", f"expected {expect} got {got}")
        except Exception as exc:
            bug("days_between", f"exception for {d1} {d2}", exc)


def fuzz_get_python_file_count(n=25):
    with TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        for i in range(n):
            sub = base / f"case_{i}"
            sub.mkdir()
            expected = 0
            for j in range(random.randint(0, 6)):
                ext = random.choice(["py", "ipynb", "txt", "md"])
                if ext in ("py", "ipynb"):
                    expected += 1
                (sub / f"f{j}.{ext}").write_text("print('hi')\n", encoding="utf-8")
            if random.random() < 0.4:
                nested = sub / "nested"
                nested.mkdir()
                (nested / "n.py").write_text("# nested\n", encoding="utf-8")
                expected += 1
            try:
                got = mining.getPythonFileCount(str(sub))
                if got != expected:
                    bug("getPythonFileCount", f"expected {expected} got {got} in {sub}")
            except Exception as exc:
                bug("getPythonFileCount", f"exception in {sub}", exc)


def main():
    random.seed(0)
    fuzz_dump_content()
    fuzz_make_chunks()
    fuzz_check_python_file()
    fuzz_days_between()
    fuzz_get_python_file_count()
    if BUGS:
        print(f"Fuzzing found {len(BUGS)} potential bugs.")
        for name, detail, exc in BUGS:
            print(f"- {name}: {detail} {f'({exc})' if exc else ''}")
        raise SystemExit(1)
    print("Fuzzing completed with no bugs discovered.")


if __name__ == "__main__":
    main()
