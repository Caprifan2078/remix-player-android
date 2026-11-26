import unittest
from verify_benchmark import verify,SIZES
class BenchmarkTest(unittest.TestCase):
    def sample(self,id="tiny"):
        return dict(id=id,modelBytes=SIZES[id],downloadMs=500,inferenceMs=6000,words=13,edits=1,wer=1/13,availableRamAfter=100,transcript="the music is playing")
    def test_valid(self):
        for id in SIZES:self.assertIn(id,verify(self.sample(id),id))
    def test_invalid(self):
        for key,value in [("id","wrong"),("modelBytes",0),("words",12),("inferenceMs",0),("edits",-1),("wer",float("nan")),("wer",0),("transcript",""),("availableRamAfter",True)]:
            with self.subTest(key=key,value=value):
                with self.assertRaises(ValueError):verify(self.sample()|{key:value},"tiny")
    def test_wrong_identity(self):
        with self.assertRaises(ValueError):verify(self.sample("tiny"),"base-q5_1")
if __name__=="__main__":unittest.main()
