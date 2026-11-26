#!/usr/bin/env python3
import pathlib,re,subprocess,time,xml.etree.ElementTree as ET
out=pathlib.Path("smoke-output/navigation")
out.mkdir(parents=True,exist_ok=True)
pkg="app.remix.player"
def adb(*args):
    return subprocess.check_output(["adb",*args],timeout=45)
def tree():
    remote="/sdcard/remix-nav.xml"
    adb("shell","rm","-f",remote)
    reply=adb("shell","uiautomator","dump",remote)
    if b"ERROR" in reply or b"dumped to" not in reply:
        raise RuntimeError("Fresh navigation hierarchy unavailable: "+reply.decode(errors="replace"))
    raw=adb("exec-out","cat",remote)
    nodes=list(ET.fromstring(raw).iter("node"))
    if any(n.get("package")=="android" and n.get("resource-id")=="android:id/alertTitle" for n in nodes):
        raise RuntimeError("System dialog blocks navigation")
    if not any(n.get("package")==pkg for n in nodes):
        raise RuntimeError("Navigation hierarchy does not belong to app")
    return raw
def tap(label):
    nodes=list(ET.fromstring(tree()).iter("node"))
    matches=[n for n in nodes if n.get("package")==pkg and n.get("clickable")=="true" and n.get("text")==label]
    assert len(matches)==1,f"{label}: expected one clickable node, got {len(matches)}"
    x,y,X,Y=map(int,re.findall(r"-?\d+",matches[0].get("bounds")))
    assert X>x and Y>y,label
    adb("shell","input","tap",str((x+X)//2),str((y+Y)//2))
def capture(name,heading):
    end=time.monotonic()+15
    while True:
        raw=tree()
        nodes=list(ET.fromstring(raw).iter("node"))
        if any(n.get("package")==pkg and n.get("text")==heading for n in nodes):break
        if time.monotonic()>=end:raise AssertionError(f"{name}: missing heading {heading}")
        time.sleep(.5)
    (out/(name+".xml")).write_bytes(raw)
    png=adb("exec-out","screencap","-p")
    assert png.startswith(bytes.fromhex("89504e470d0a1a0a")), "Invalid screen capture: "+name
    (out/(name+".png")).write_bytes(png)
    assert adb("shell","pidof",pkg).strip(),name
    print("PASS UI navigation:",name,flush=True)
adb("shell","am","force-stop",pkg)
adb("shell","am","start","-W","-n",pkg+"/.MainActivity")
screens=[("01-library","Музыка","Моя музыка"),("02-versions","Версии","Версии песни"),("03-studio","Студия","Remix Studio"),("04-lyrics","Текст","Текст песни"),("05-downloads","Загрузки","Загрузки"),("06-settings","Настройки","Настройки и память")]
for name,label,heading in screens:
    tap(label)
    capture(name,heading)
tap("Музыка")
capture("07-return","Моя музыка")
print("PASS: seven screen transitions with actual screenshots")
