from pathlib import Path


def load_fixture(filename: str) -> str:
    path = Path(__file__).parent / filename
    with open(path) as f:
        return f.read()