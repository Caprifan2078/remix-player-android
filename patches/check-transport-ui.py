#!/usr/bin/env python3
import sys,re,xml.etree.ElementTree as ET,subprocess
tree=ET.parse(sys.argv[1])
density=subprocess.check_output(['adb','shell','wm','density'],text=True)
dpi=int(re.findall(r'(?:Physical|Override) density:\s*(\d+)',density)[-1])
nodes=[n for n in tree.iter('node') if n.get('package')=='app.remix.player' and n.get('clickable')=='true']
expected={'⇄':'Случайный порядок воспроизведения','|◀':'Предыдущая композиция','▶|':'Следующая композиция','↻':'Режим повтора'}
fail=[]
for label,description in expected.items():
    matching=[n for n in nodes if n.get('text')==label]
    if len(matching)!=1:fail.append(f'{label}: missing/duplicate');continue
    n=matching[0]; b=list(map(int,re.findall(r'-?\d+',n.get('bounds',''))))
    width,height=(b[2]-b[0])*160/dpi,(b[3]-b[1])*160/dpi
    print(f'{label}: {width:.1f}x{height:.1f} dp; accessibility={n.get("content-desc")}')
    if min(width,height)<47.9 or n.get('content-desc')!=description:fail.append(label)
if fail:raise SystemExit('FAIL transport accessibility: '+', '.join(fail))
print('PASS: 4 transport controls on installed Android')
