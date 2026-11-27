"""Verify diagnostic experiments without using them to select production transcripts."""
import json
import math
import pathlib
import re
import sys
from verify_benchmark import distance

EXPECTED="музыка играет послушай песню сегодня это тест".split()
MODELS=("tiny","base-q5_1","base","small-q5_1","small")

def verify_report(model,report):
    if report.get("id")!=model or report.get("language")!="ru":
        raise ValueError("Wrong report identity")
    rows=report.get("experiments")
    if not isinstance(rows,list) or len(rows)!=2:
        raise ValueError("Missing profile")
    profiles={"filtered-wide":(5,False),"raw-legacy":(1 if model=="tiny" else 3,True)}
    for row in rows:
        key=row.get("profile")
        if key not in profiles or (row.get("beam"),row.get("rawInput"))!=profiles.pop(key):
            raise ValueError("Unexpected or duplicate profile")
        if "error" in row:
            raise ValueError(f"{key}: {row['error']}")
        if type(row.get("inferenceMs")) is not int or row["inferenceMs"]<=0:
            raise ValueError("Invalid inference duration")
        transcript=row.get("transcript")
        if not isinstance(transcript,str) or not transcript.strip():
            raise ValueError("Missing transcript")
        words=re.findall(r"[^\W\d_]+",transcript.lower(),re.UNICODE)
        edits=distance(EXPECTED,words)
        if type(row.get("edits")) is not int or row["edits"]!=edits:
            raise ValueError("Incorrect edit distance")
        wer=row.get("wer")
        if type(wer) not in (int,float) or not math.isfinite(wer) or abs(wer-edits/7)>1e-8:
            raise ValueError("Incorrect WER")
        print(f"{model} {key}: {edits}/7 edits, {row['inferenceMs']} ms")
    return True

def main(root):
    ok=True
    for model in MODELS:
        try:
            verify_report(model,json.loads((root/f"ablation-{model}.json").read_text()))
        except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
            print(f"{model}: INVALID: {exc}")
            ok=False
    return 0 if ok else 1

if __name__=="__main__":
    sys.exit(main(pathlib.Path(sys.argv[1])))
