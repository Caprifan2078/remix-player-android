import importlib.util,pathlib,tempfile,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('startup_ui',pathlib.Path(__file__).with_name('startup-ui.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
GOOD='<hierarchy><node package="app.remix.player" text="Моя музыка"/><node package="app.remix.player" text="Найти музыку на телефоне"/></hierarchy>'.encode()
ANR=b'''<hierarchy><node package="android" resource-id="android:id/alertTitle" text="Pixel Launcher isn't responding"/><node package="android" resource-id="android:id/aerr_close" clickable="true" bounds="[10,20][30,40]"/></hierarchy>'''
BAD=ANR.replace(b'Pixel Launcher',b'REMIX')
class Gate(unittest.TestCase):
 def run_case(self, snapshots, expect, expected_tap=False):
  queue=iter(snapshots);calls=[]
  def fake(*args):
   calls.append(args)
   if args[:2]==('shell','uiautomator'):return b'UI hierarchy dumped to: /sdcard/remix-startup.xml'
   if args[:2]==('exec-out','cat'):return next(queue)
   if args[:2]==('shell','pidof'):return b'1234'
   return b''
  with tempfile.TemporaryDirectory() as tmp:
   dest=pathlib.Path(tmp)/'ui.xml';dest.write_bytes(b'STALE')
   with patch.object(m,'adb',fake),patch.object(m.time,'sleep',lambda _:None):
    if expect:m.capture(dest,attempts=len(snapshots));self.assertEqual(dest.read_bytes(),GOOD)
    else:
     with self.assertRaises(SystemExit):m.capture(dest,attempts=len(snapshots))
     self.assertFalse(dest.exists())
   self.assertEqual(any(x[:3]==('shell','input','tap') for x in calls),expected_tap)
   self.assertTrue(any(x[:3]==('shell','rm','-f') for x in calls))
 def test_good(self):self.run_case([GOOD],True)
 def test_launcher_then_app(self):self.run_case([ANR,GOOD],True,True)
 def test_app_anr_fails(self):self.run_case([BAD],False)
 def test_non_app_fails(self):self.run_case([GOOD.replace(b'app.remix.player',b'other.app')],False)
 def test_malformed_fails(self):self.run_case([b'<broken'],False)
 def test_unrecognized_system_dialog_fails(self):self.run_case([ANR.replace(b'aerr_close',b'other')],False)
 def test_failed_dump_never_reuses_stale(self):
  with tempfile.TemporaryDirectory() as tmp:
   dest=pathlib.Path(tmp)/'ui.xml';dest.write_bytes(GOOD)
   def fake(*args):
    if args[:2]==('shell','uiautomator'):return b'ERROR: could not get idle state.'
    if args[:2]==('exec-out','cat'):raise AssertionError('Must not read stale file')
    return b''
   with patch.object(m,'adb',fake),patch.object(m.time,'sleep',lambda _:None):
    with self.assertRaises(SystemExit):m.capture(dest,attempts=1)
   self.assertFalse(dest.exists())
if __name__=='__main__':unittest.main()
