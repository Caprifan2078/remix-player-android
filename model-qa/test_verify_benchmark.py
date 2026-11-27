import unittest
from verify_benchmark import verify,SIZES
class BenchmarkTest(unittest.TestCase):
    def sample(self,id="tiny"):
        return dict(id=id,modelBytes=SIZES[id],downloadMs=500,inferenceMs=6000,words=13,edits=1,wer=1/13,availableRamAfter=100,transcript="the music is playing listen to the song today this is a",peakPssKiB=1000,pssSamples=2,minAvailableRam=90)
    def test_valid(self):
        for id in SIZES:self.assertIn(id,verify(self.sample(id),id))
    def test_invalid(self):
        for key,value in [("id","wrong"),("modelBytes",0),("words",12),("inferenceMs",0),("edits",-1),("wer",float("nan")),("wer",0),("transcript",""),("availableRamAfter",True),("peakPssKiB",0),("pssSamples",0),("minAvailableRam",-1)]:
            with self.subTest(key=key,value=value):
                with self.assertRaises(ValueError):verify(self.sample()|{key:value},"tiny")
    def test_wrong_identity(self):
        with self.assertRaises(ValueError):verify(self.sample("tiny"),"base-q5_1")
    def test_false_accuracy(self):
        with self.assertRaises(ValueError):verify(self.sample()|{"transcript":"music"},"tiny")
    def test_bad_accuracy(self):
        with self.assertRaisesRegex(ValueError,"below gate"):verify(self.sample()|{"transcript":"music","edits":12,"wer":12/13},"tiny")
    def test_three_errors_boundary(self):
        self.assertIn("tiny",verify(self.sample()|{"transcript":"the music is playing listen to the song today this","edits":3,"wer":3/13},"tiny"))
if __name__=="__main__":unittest.main()
