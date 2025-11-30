from datetime import datetime, timedelta

MAKE_CHUNKS_EDGE_CASES = [
    {"data": [1, 2, 3], "size": 0, "label": "size=0 (range step zero)"},
    {"data": [1, 2, 3], "size": -1, "label": "size=-1 (negative step)"},
    {"data": [1, 2, 3], "size": None, "label": "size=None (non-int)"},
    {"data": [1, 2, 3], "size": "2", "label": "size='2' (string)"},
    {"data": [1, 2, 3], "size": 2.5, "label": "size=2.5 (float)"},
    {"data": [], "size": 0, "label": "empty list with size=0"},
    {"data": [1, 2, 3], "size": 10 ** 9, "label": "huge size"},
]


def days_between_edge_cases():
    now = datetime.now()
    return [
        {
            "d1": datetime(2020, 2, 29),
            "d2": datetime(2021, 3, 1),
            "label": "leap year span",
        },
        {
            "d1": now,
            "d2": now - timedelta(days=1),
            "label": "d2 before d1 (1 day apart)",
        },
        {
            "d1": now,
            "d2": now + timedelta(seconds=86399),
            "label": "<1 day apart (should be 0 days)",
        },
        {
            "d1": now,
            "d2": now + timedelta(seconds=86401),
            "label": ">1 day by seconds (should be 1 day)",
        },
        {
            "d1": datetime.max - timedelta(days=1),
            "d2": datetime.max,
            "label": "near datetime.max",
        },
        {
            "d1": datetime.min,
            "d2": datetime.min + timedelta(days=1),
            "label": "near datetime.min",
        },
        {
            "d1": "2020-01-01",
            "d2": datetime(2020, 1, 2),
            "label": "mixed types string/datetime",
        },
        {
            "d1": datetime(2020, 1, 1),
            "d2": "2020-01-02",
            "label": "mixed types datetime/string",
        },
        {"d1": None, "d2": now, "label": "d1 None"},
        {"d1": now, "d2": None, "label": "d2 None"},
    ]


DUMP_CONTENT_EDGE_CASES = [
    {"label": "empty content valid path", "content": "", "path_kind": "valid"},
    {"label": "None content valid path", "content": None, "path_kind": "valid"},
    {"label": "path None", "content": "abc", "path_kind": "none"},
    {"label": "path int", "content": "abc", "path_kind": "int"},
    {"label": "path is directory", "content": "abc", "path_kind": "dir"},
    {
        "label": "missing parent directories",
        "content": "abc",
        "path_kind": "missing_parent",
    },
    {"label": "bytes content", "content": b"binary-bytes", "path_kind": "valid"},
    {"label": "large content", "content": "x" * 5000, "path_kind": "valid"},
]


PYTHON_FILE_COUNT_EDGE_CASES = [
    {"type": "invalid", "path": None, "label": "path None"},
    {"type": "invalid", "path": 123, "label": "path int"},
    {"type": "missing_dir", "label": "nonexistent directory"},
    {"type": "file_path", "label": "file path instead of dir"},
    {"type": "uppercase_ext", "label": "uppercase extensions"},
    {"type": "nested_mix", "label": "nested py/ipynb vs junk"},
]


CHECK_PYTHON_KEYWORDS = [
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


CHECK_PYTHON_EDGE_CASES = [
    {"type": "invalid", "path": None, "label": "path=None"},
    {"type": "invalid", "path": 123, "label": "path=int"},
    {"type": "invalid", "path": "", "label": "path=empty-string"},
    {"type": "file_path", "label": "file path instead of dir", "keyword": "torch"},
    {"type": "py_upper", "label": "uppercase keyword in .py", "keyword": "SKLEARN"},
    {"type": "ipynb", "label": "keyword in .ipynb", "keyword": "tensorflow"},
    {
        "type": "nested",
        "label": "nested dirs with multiple keywords",
        "keywords": ["keras", "torch"],
    },
]
