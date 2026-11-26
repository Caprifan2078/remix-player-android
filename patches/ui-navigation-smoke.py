#!/usr/bin/env python3
import pathlib,re,subprocess,time,xml.etree.ElementTree as ET
out=pathlib.Path("smoke-output/navigation")
out.mkdir(parents=True,exist_ok=True)
pkg="app.remix.player"
def adb(*args):
    return subprocess.check_output(["adb",*args],timeout=45)
def tree():
    adb("shell","rm","-f","/sdcard/remix-nav.xml")
    reply=adb("shell","uiautomator","dump","/sdcard/remix-nav.xml")
    assert b"ERROR" not in reply and b"dumped to" in reply,reply
    return adb("exec-out","cat","/sdcard/remix-nav.xml")
def tap(label):
    deadline=time.monotonic()+12
    while True:
        raw=tree();root=ET.fromstring(raw);nodes=list(root.iter("node"))
        parents={child:parent for parent in root.iter() for child in parent}
        matches=[]
        for node in nodes:
            if node.get("package")!=pkg or node.get("text")!=label:continue
            # Android AlertDialog rows delegate taps to ListView and may report clickable=false.
            parent=parents.get(node)
            if node.get("enabled")=="true" and node.get("resource-id")=="android:id/text1" and parent is not None and parent.get("resource-id")=="android:id/select_dialog_listview":
                matches.append(node)
                continue
            target=node
            while target is not None and target.get("package")==pkg:
                if target.get("clickable")=="true" and target.get("enabled")=="true":
                    if target not in matches:matches.append(target)
                    break
                target=parents.get(target)
        if len(matches)==1:break
        if time.monotonic()>=deadline:
            (out/"failed-tap.xml").write_bytes(raw)
            (out/"failed-tap.png").write_bytes(adb("exec-out","screencap","-p"))
            raise AssertionError(f"{label}: expected one enabled clickable node or parent, got {len(matches)}")
        time.sleep(.4)
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
    (out/(name+".png")).write_bytes(adb("exec-out","screencap","-p"))
    assert adb("shell","pidof",pkg).strip(),name
    print("PASS UI navigation:",name,flush=True)
adb("shell","am","force-stop",pkg)
adb("shell","am","start","-W","-n",pkg+"/.MainActivity")
screens=[("01-library","Музыка","Моя музыка"),("02-versions","Версии","Версии песни"),("03-studio","Студия","Remix Studio"),("04-lyrics","Текст","Текст песни"),("05-downloads","Загрузки","Загрузки"),("06-settings","Настройки","Настройки и память")]
for name,label,heading in screens:
    if label in ("Версии","Загрузки","Настройки"): tap("Ещё")
    tap(label)
    capture(name,heading)
tap("Музыка")
capture("07-return","Моя музыка")
print("PASS: seven screen transitions with actual screenshots")
