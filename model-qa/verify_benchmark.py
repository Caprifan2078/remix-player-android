"""Independently validate synthetic speech accuracy and sampled process memory."""
import json
import math
import pathlib
import re
import sys

SIZES={"tiny":77691713,"base-q5_1":59707625,"large-v3-turbo-q5_0":574041195}
EXPECTED="the music is playing listen to the song today this is a test".split()
MAX_EDITS=3  # Synthetic speech smoke gate, not a singing accuracy claim.

def distance(expected, actual):
    prior=list(range(len(actual)+1))
    for i,a in enumerate(expected,1):
        row=[i]
        for j,b in enumerate(actual,1):
            row.append(min(prior[j]+1,row[-1]+1,prior[j-1]+(a!=b)))
        prior=row
    return prior[-1]

def verify(data, model):
    if model not in SIZES or data.get("id") != model:
        raise ValueError("Wrong model identity")
    for name in ("modelBytes","downloadMs","inferenceMs","words","edits","availableRamAfter","peakPssKiB","pssSamples","minAvailableRam"):
        value=data.get(name)
        if type(value) is not int or value<0:
            raise ValueError("Invalid "+name)
    if data["modelBytes"]!=SIZES[model] or data["words"]!=len(EXPECTED) or data["inferenceMs"]<=0:
        raise ValueError("Invalid benchmark fixture or inference duration")
    if data["peakPssKiB"]<=0 or data["pssSamples"]<2:
        raise ValueError("Missing memory sampling")
    transcript=data.get("transcript")
    if not isinstance(transcript,str) or not transcript.strip():
        raise ValueError("Empty transcript")
    actual=re.findall(r"[a-z]+",transcript.lower())
    errors=distance(EXPECTED,actual)
    wer=data.get("wer")
    if data["edits"]!=errors or type(wer) not in (int,float) or not math.isfinite(wer) or abs(wer-errors/len(EXPECTED))>1e-8:
        raise ValueError("Incorrect WER")
    if errors>MAX_EDITS:
        raise ValueError("Synthetic speech accuracy below gate")
    return f'{model}: {data["inferenceMs"]} ms, WER {wer:.3f}, edits {errors}/{len(EXPECTED)}; sampled peak PSS {data["peakPssKiB"]} KiB ({data["pssSamples"]} samples); download {data["downloadMs"]} ms'
if __name__=="__main__":
    print(verify(json.loads(pathlib.Path(sys.argv[1]).read_text()),sys.argv[2]))
