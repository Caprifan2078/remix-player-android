#!/usr/bin/env python3
import sys,re,xml.etree.ElementTree as ET,subprocess
tree=ET.parse(sys.argv[1])
density=subprocess.check_output(['adb','shell','wm','density'],text=True)
dpi=int(re.findall(r'(?:Physical|Override) density:\s*(\d+)',density)[-1])
nodes=[n for n in tree.iter('node') if n.get('package')=='app.remix.player' and n.get('clickable')=='true']
# The startup fixture has no songs; its transport must be absent.
# Loaded-track touch targets are now verified on real Android by
# compactLibraryAndExpandedPlayerHaveOneTitleAndVisibleSeek.
expected={"Меню навигации","Настройки","Импорт","Фильтры и инструменты","Фильтр избранного"}
fail=[]
for desc in expected:
    matching=[n for n in nodes if n.get("content-desc")==desc]
    if len(matching)!=1:fail.append(desc+": missing/duplicate");continue
    b=list(map(int,re.findall(r"-?\d+",matching[0].get("bounds",""))))
    if len(b)!=4 or min(b[2]-b[0],b[3]-b[1])*160/dpi<47.9:fail.append(desc+": small target")
if any(n.get("text") in {"⇄","|◀","▶|","↻"} for n in nodes):fail.append("Empty library has full transport")
if fail:raise SystemExit("FAIL startup accessibility: "+", ".join(fail))
print("PASS: 5 accessible startup icons; empty transport absent")
