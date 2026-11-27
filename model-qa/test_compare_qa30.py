import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from compare_qa30 import BASELINE, compare
from verify_benchmark import SIZES, EXPECTED, distance

class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        for model in BASELINE:
            for lang in ("en","ru"):
                words=EXPECTED if lang=="en" else "музыка играет послушай песню сегодня это тест".split()
                report=dict(id=model,language=lang,modelBytes=SIZES[model],downloadMs=1,inferenceMs=20,
                            words=len(words),edits=0,wer=0,availableRamAfter=100,peakPssKiB=1,
                            pssSamples=2,minAvailableRam=100,transcript=" ".join(words))
                self.path(model,lang).write_text(json.dumps(report))
    def path(self,model,lang):
        return self.root / ("whisper-"+model+("-ru" if lang=="ru" else "")+".json")
    def update(self,model,lang,**changes):
        p=self.path(model,lang)
        data=json.loads(p.read_text());data.update(changes);p.write_text(json.dumps(data))
    def check(self,expected):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(expected,compare(self.root))
    def test_valid(self):
        self.check(True)
    def test_missing(self):
        self.path("tiny","ru").unlink()
        self.check(False)
    def test_fake_metrics(self):
        self.update("tiny","ru",transcript="несуществующий результат")
        self.check(False)
    def test_wrong_language(self):
        self.update("tiny","ru",language="en")
        self.check(False)
    def test_valid_but_regressed(self):
        self.update("large-v3-q5_0","ru",transcript="музыка играет послушай песню сегодня это текст",edits=1,wer=1/7)
        self.check(False)
    def test_old_gate_still_applies(self):
        self.update("tiny","ru",transcript="музыка",edits=6,wer=6/7)
        self.check(False)
    def test_invalid_ram(self):
        self.update("tiny","en",pssSamples=0)
        self.check(False)

if __name__=="__main__":unittest.main()
