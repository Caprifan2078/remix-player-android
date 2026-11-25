#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])
def replace(file,old,new):
    p=root/file
    s=p.read_text()
    if s.count(old)!=1:raise ValueError(f"{file}: expected one occurrence of {old[:80]}")
    p.write_text(s.replace(old,new))
main="app/src/main/java/app/remix/player/MainActivity.kt"
replace(main,'previewLabel=label("Предпрослушивание",14,accent);body.addView(previewLabel!!)','''// Render the actual position immediately instead of waiting for a ticker.
        val shownFrame=(if(MixerSession.request?.source==source.uri)MixerSession.position()else previewFrame).coerceIn(0L,bundle.frames)
        previewLabel=label("Микшер · "+fmt(shownFrame*1000/44100),14,accent);body.addView(previewLabel!!)''')
replace(main,'progress=(previewFrame/441).toInt();setOnSeekBarChangeListener','progress=(shownFrame/441).toInt().coerceIn(0,max);setOnSeekBarChangeListener')
smoke="tests/android-mixer-smoke.sh"
replace(smoke,'''dump smoke-output/mixer-ui.xml
python3 - <<'PY'
import re,xml.etree.ElementTree as ET
texts=[n.get('text','') for n in ET.parse('smoke-output/mixer-ui.xml').iter('node')]
positions=[int(m[1])*60+int(m[2]) for t in texts if (m:=re.fullmatch(r'Микшер · (\d+):(\d+)',t))]
assert positions and max(positions)>=5, texts
PY
tap_label 'Ⅱ Пауза микса'
sleep 2''','''# XML snapshots may lag behind visual frames. Require bounded actual UI progress.
confirmed=0
for attempt in 1 2 3 4; do
    dump smoke-output/mixer-ui.xml
    adb exec-out screencap -p > smoke-output/mixer-resumed.png
    if python3 - <<'PY'
import re,xml.etree.ElementTree as ET
texts=[n.get('text','') for n in ET.parse('smoke-output/mixer-ui.xml').iter('node')]
positions=[int(m[1])*60+int(m[2]) for t in texts if (m:=re.fullmatch(r'Микшер · (\d+):(\d+)',t))]
assert positions and max(positions)>=5 and 'Ⅱ Пауза микса' in texts, texts
print("PASS: mixer resumed in UI at",max(positions),"seconds")
PY
    then confirmed=1;break;fi
    sleep 1
done
test "$confirmed" = 1
tap_label 'Ⅱ Пауза микса'
sleep 2
dump smoke-output/mixer-paused.xml
python3 - <<'PY'
import xml.etree.ElementTree as ET
texts=[n.get('text','') for n in ET.parse('smoke-output/mixer-paused.xml').iter('node')]
assert '▶ Слушать микс' in texts and 'Ⅱ Пауза микса' not in texts,texts
print("PASS: UI mixer pause confirmed")
PY''')
print("Applied current-position render and bounded mixer UI regression")
