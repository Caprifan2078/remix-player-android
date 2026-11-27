"""Compare identical QA30 speech fixtures, not a singing benchmark."""
import json
import pathlib
import sys

BASELINE = {
    "tiny": 9, "base-q5_1": 6, "base": 5, "small-q5_1": 3,
    "small": 4, "medium-q5_0": 1, "large-v3-turbo-q5_0": 0,
    "large-v3-q5_0": 0,
}

def compare(directory):
    ok = True
    for model, ru_before in BASELINE.items():
        for lang, before in (("en", 0), ("ru", ru_before)):
            suffix = "-ru" if lang == "ru" else ""
            path = directory / f"whisper-{model}{suffix}.json"
            try:
                report = json.loads(path.read_text())
                assert report["id"] == model and report["language"] == lang
                assert report["words"] == (7 if lang == "ru" else 13)
                edits = report["edits"]
                assert type(edits) is int and edits >= 0
                # Existing accuracy gate remains 3 errors; do not regress a
                # previously passing model on the exact same fixed fixture.
                passed = edits <= min(3, before)
                print(f"{model} {lang}: {before} -> {edits}; "
                      f"{'PASS' if passed else 'FAIL'}; inference={report['inferenceMs']} ms")
                ok = ok and passed
            except (OSError, ValueError, KeyError, AssertionError, TypeError) as exc:
                print(f"{model} {lang}: invalid/missing report: {exc}")
                ok = False
    return ok

if __name__ == "__main__":
    sys.exit(0 if compare(pathlib.Path(sys.argv[1])) else 1)
