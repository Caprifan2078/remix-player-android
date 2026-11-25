#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]);p=root/"app/src/main/java/app/remix/player/MainActivity.kt";s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new)
replace('window.statusBarColor=bg; window.navigationBarColor=bg; load();','lyricFollow=getSharedPreferences("lyrics_ui",MODE_PRIVATE).getBoolean("follow",true); window.statusBarColor=bg; window.navigationBarColor=bg; load();')
replace('lyricFollow=!lyricFollow;follow.text=','lyricFollow=!lyricFollow;getSharedPreferences("lyrics_ui",MODE_PRIVATE).edit().putBoolean("follow",lyricFollow).apply();follow.text=')
p.write_text(s)
print("PASS: persist lyrics follow preference")
