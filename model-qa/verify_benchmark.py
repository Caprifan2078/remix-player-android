"""Independently validate synthetic speech accuracy and sampled process memory."""
import json
import math
import pathlib
import re
import sys

SIZES={"tiny":77691713,"base-q5_1":59707625,"base":147951465,"small-q5_1":190085487,"small":487601967,"medium-q5_0":539212467,"large-v3-turbo-q5_0":574041195,"large-v3-q5_0":1081140203}
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

def verify(data, model, language="en"):
    if language not in ("en","ru") or data.get("language","en")!=language:
        raise ValueError("Wrong language")
    expected=EXPECTED if language=="en" else "музыка играет послушай песню сегодня это тест".split()
    if model not in SIZES or data.get("id") != model:
        raise ValueError("Wrong model identity")
    for name in ("modelBytes","downloadMs","inferenceMs","words","edits","availableRamAfter","peakPssKiB","pssSamples","minAvailableRam"):
        value=data.get(name)
        if type(value) is not int or value<0:
            raise ValueError("Invalid "+name)
    if data["modelBytes"]!=SIZES[model] or data["words"]!=len(expected) or data["inferenceMs"]<=0:
        raise ValueError("Invalid benchmark fixture or inference duration")
    if data["peakPssKiB"]<=0 or data["pssSamples"]<2:
        raise ValueError("Missing memory sampling")
    transcript=data.get("transcript")
    if not isinstance(transcript,str) or not transcript.strip():
        raise ValueError("Empty transcript")
    actual=re.findall(r"[^\W\d_]+",transcript.lower(),re.UNICODE)
    errors=distance(expected,actual)
    wer=data.get("wer")
    if data["edits"]!=errors or type(wer) not in (int,float) or not math.isfinite(wer) or abs(wer-errors/len(expected))>1e-8:
        raise ValueError("Incorrect WER")
    if errors>MAX_EDITS:
        raise ValueError("Synthetic speech accuracy below gate")
    return f'{model} ({language}): {data["inferenceMs"]} ms, WER {wer:.3f}, edits {errors}/{len(expected)}; sampled peak PSS {data["peakPssKiB"]} KiB ({data["pssSamples"]} samples); download {data["downloadMs"]} ms'
if __name__=="__main__":
    print(verify(json.loads(pathlib.Path(sys.argv[1]).read_text()),sys.argv[2],sys.argv[3] if len(sys.argv)>3 else "en"))
