#!/usr/bin/env python3
import pathlib,subprocess,sys,re,xml.etree.ElementTree as ET,time
pkg="app.remix.player"
def adb(*args):return subprocess.check_output(["adb",*args],timeout=30)
def fresh():
    remote="/sdcard/qa-player-transport.xml";adb("shell","rm","-f",remote);r=adb("shell","uiautomator","dump",remote);assert b"ERROR" not in r
    return adb("exec-out","cat",remote)
adb("shell","am","start","-W","-n",pkg+"/.MainActivity")
xml=fresh()
nodes=[n for n in ET.fromstring(xml).iter("node") if n.get("package")==pkg and n.get("content-desc")=="Открыть экран воспроизведения"]
assert len(nodes)==1,"Missing compact player entry"
x,y,X,Y=map(int,re.findall(r"-?\d+",nodes[0].get("bounds")))
adb("shell","input","tap",str((x+X)//2),str((y+Y)//2));time.sleep(.5)
pathlib.Path(sys.argv[2]).write_bytes(fresh())
pathlib.Path("smoke-output/player-transport.png").write_bytes(adb("exec-out","screencap","-p"))
