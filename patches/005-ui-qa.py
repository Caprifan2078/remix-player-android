from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/MainActivity.kt"
s=p.read_text()
old='hint="Песня, исполнитель, альбом или ремикс";setSingleLine();setText(query)'
new='hint="Поиск музыки";contentDescription="Поиск по песне, исполнителю, альбому или ремиксу";setSingleLine();setText(query)'
assert s.count(old)==1,"Search UI source changed"
p.write_text(s.replace(old,new))
print("PASS: concise search hint and full accessible description")
