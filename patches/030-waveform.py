#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt'
s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b)
rep('private var playerActions:LinearLayout?=null','private var playerActions:LinearLayout?=null;private val waveLoader by lazy{WaveformLoader(this)}')
rep('seek=SeekBar(this);seek.max=1000;','seek=WaveSeekBar(this);seek.max=1000;')
rep('val full=screen=="Плеер";','val full=screen=="Плеер";if(!full){waveLoader.clear();(seek as WaveSeekBar).setEnvelope(null)};')
rep('val t=current()?:run{heading("Сейчас играет");','val t=current()?:run{waveLoader.clear();(seek as WaveSeekBar).setEnvelope(null);heading("Сейчас играет");')
rep('movePlayerView(seek,body);movePlayerView(time,body);','movePlayerView(seek,body);seek.layoutParams=LinearLayout.LayoutParams(-1,dp(52));waveLoader.show(t.uri){samples->if(!isDestroyed&&screen=="Плеер"&&current()?.uri==t.uri)(seek as WaveSeekBar).setEnvelope(samples)};movePlayerView(time,body);')
rep('coverIo.shutdownNow();coverCache.evictAll();','coverIo.shutdownNow();waveLoader.close();coverCache.evictAll();')
p.write_text(s)
print("PASS: real decoded waveform with native seek, lifecycle cancellation and bounded session cache")
