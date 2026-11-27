"""Validate the actual per-model Android benchmark file, not logcat output."""
import json
import math
import pathlib
import sys

SIZES={"tiny":77691713,"base-q5_1":59707625,"large-v3-turbo-q5_0":574041195}
def verify(data, model):
    if model not in SIZES or data.get("id") != model:
        raise ValueError("Wrong model identity")
    for name in ("modelBytes","downloadMs","inferenceMs","words","edits","availableRamAfter"):
        value=data.get(name)
        if type(value) is not int or value<0:
            raise ValueError("Invalid "+name)
    if data["modelBytes"]!=SIZES[model] or data["words"]!=13 or data["inferenceMs"]<=0:
        raise ValueError("Invalid benchmark fixture or inference duration")
    wer=data.get("wer")
    if type(wer) not in (int,float) or not math.isfinite(wer) or abs(wer-data["edits"]/data["words"])>1e-8:
        raise ValueError("Incorrect WER")
    transcript=data.get("transcript")
    if not isinstance(transcript,str) or not transcript.strip():
        raise ValueError("Empty transcript")
    return f'{model}: {data["inferenceMs"]} ms, WER {wer:.3f}, edits {data["edits"]}/{data["words"]}; download {data["downloadMs"]} ms'
if __name__=="__main__":
    print(verify(json.loads(pathlib.Path(sys.argv[1]).read_text()),sys.argv[2]))
