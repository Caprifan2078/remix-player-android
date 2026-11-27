from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player'
def edit(name,a,b):
    p=src/name;s=p.read_text();assert s.count(a)==1,(name,a[:120],s.count(a));p.write_text(s.replace(a,b))
shutil.copyfile(Path(__file__).parent/'SmartCrossfade.kt',src/'SmartCrossfade.kt')
# Missing preference means fresh/default settings. Explicit off stays off, including upgrades.
edit('PlaybackService.kt','getLong("overlap_ms",0).takeIf{it in 1000..8000}?:0L','getLong("overlap_ms",SmartCrossfade.DEFAULT_MS).takeIf{it in 1000..8000}?:0L')
edit('PlaybackService.kt','overlap?.tick(PlaybackOptions.overlapMs,eligible)','overlap?.tick(PlaybackOptions.overlapMs,eligible,SmartCrossfade.enabled(getSharedPreferences("play_options",MODE_PRIVATE)))')
edit('LiveOverlap.kt','fun tick(requested:Long,eligible:Boolean):Boolean','fun tick(requested:Long,eligible:Boolean,smart:Boolean=false):Boolean')
edit('LiveOverlap.kt','val planned=OverlapCore.window(duration,p.duration,requested)','val effective=if(smart)SmartCrossfade.duration(duration,p.duration,requested) else requested\n        val planned=OverlapCore.window(duration,p.duration,effective)')
# No additional permanent buttons: smart/normal/off are one menu.
p=src/'MainActivity.kt';s=p.read_text()
a=s.index('    private fun liveTransitionMenu(){');b=s.index('    private fun bindArtworkSwipe(',a)
s=s[:a]+r'''    private fun liveTransitionMenu(){
        val fades=listOf(0L,1000L,2000L,3000L,5000L)
        val overlaps=listOf(1000L,2000L,3000L,5000L,8000L)
        val prefs=getSharedPreferences("play_options",MODE_PRIVATE)
        fun display(v:Long)=if(v==0L)"выкл." else (v/1000).toString()+" с"
        val smart=SmartCrossfade.enabled(prefs)
        val mode=if(PlaybackOptions.overlapMs==0L)"выкл." else if(smart)"авто" else display(PlaybackOptions.overlapMs)
        fun select(ms:Long,automatic:Boolean){
            PlaybackOptions.overlapMs=ms
            prefs.edit().putLong("overlap_ms",ms).putBoolean("smart_overlap",automatic).apply()
            liveTransitionMenu()
        }
        sheet("Плавные переходы","Умный режим выбирает длину наложения по длительности песен. При несовместимых эффектах или сбое декодера наложение пропускается. BPM и тональность доступны в отдельном DJ-миксе.",listOf(
            "Crossfade · "+mode to {
                sheet("Crossfade",actions=listOf<Pair<String,()->Unit>>(
                    ((if(smart&&PlaybackOptions.overlapMs>0)"✓ " else "")+"Умный · авто") to {select(SmartCrossfade.DEFAULT_MS,true)},
                    ((if(PlaybackOptions.overlapMs==0L)"✓ " else "")+"Выключено") to {select(0L,false)}
                )+overlaps.map{v->((if(!smart&&v==PlaybackOptions.overlapMs)"✓ " else "")+display(v)) to {select(v,false)}})
            },
            "Затухание · "+display(PlaybackOptions.fadeMs) to {
                sheet("Затухание",actions=fades.map{v->((if(v==PlaybackOptions.fadeMs)"✓ " else "")+display(v)) to {PlaybackOptions.fadeMs=v;prefs.edit().putLong("fade_ms",v).apply();liveTransitionMenu()}})
            }
        ))
    }
'''+s[b:]
# Explicitly use themed builder for all app-owned legacy dialogs.
s=s.replace('android.app.AlertDialog.Builder(this)','android.app.AlertDialog.Builder(this,R.style.RemixAlert)')
# Add top-level quick presets with common alternatives, no additional persistent screen controls.
old='val names=listOf("Оригинал","Sped Up","Sped Up + Reverb","Nightcore","Nightcore Reverb","Slowed + Reverb")'
assert s.count(old)==1
s=s.replace(old,'val names=listOf("Оригинал","Sped Up","Nightcore","Slowed + Reverb","Sped Up + Reverb","Nightcore Reverb","8D","Echo")')
p.write_text(s)
print("PASS: default-on adaptive overlap, explicit off preserved, themed legacy dialogs and quick presets")
