from pathlib import Path
import shutil,sys
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player'
shutil.copyfile(Path(__file__).parent/'HandoffGuard.kt',src/'HandoffGuard.kt')
shutil.copyfile(Path(__file__).parent/'TrackMoment.kt',src/'TrackMoment.kt')
p=src/'LiveOverlap.kt';s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:180],s.count(a))
    s=s.replace(a,b)
replace('private var blendSince=0L;','private var blendSince=0L;private var resynced=false;')
replace('blendSince=0L;main.volume=0f;p.volume=1f\n        handoffTarget=','blendSince=0L;resynced=false;main.volume=0f;p.volume=1f\n        handoffTarget=')
replace('autoPending=true;return','main.volume=0f;autoPending=true;return')
a=s.index('        if(handing){val p=preview?:return false')
b=s.index('        val id=main.currentMediaItem',a)
s=s[:a]+'''        if(handing){val p=preview?:return false
            if(!queueMatches()){abort(true);return false}
            val elapsed=now-handoffAt
            val correctItem=main.currentMediaItemIndex==to
            val previewReady=p.playbackState==Player.STATE_READY&&p.playerError==null
            val action=HandoffGuard.decide(main.currentPosition,p.currentPosition,if(previewReady)elapsed else 1800L,correctItem&&main.isPlaying&&p.isPlaying,resynced)
            fun forward(){
                if(!correctItem||!queueMatches()||!main.playWhenReady)return
                val target=OverlapCore.handoffPosition(p.currentPosition,p.duration)
                if(target<=main.currentPosition)return
                handoffTarget=target;internalSeek=true
                try{main.seekTo(to,target)}finally{internalSeek=false}
            }
            when(action){
                HandoffGuard.Action.BLEND->{
                    if(blendSince==0L)blendSince=now
                    val g=OverlapCore.gains(now-blendSince,120);p.volume=g.outgoing;main.volume=g.incoming
                    if(now-blendSince>=120){abort(false);return false}
                }
                HandoffGuard.Action.RESYNC->{
                    blendSince=0L;resynced=true;main.volume=0f;p.volume=1f;forward()
                }
                HandoffGuard.Action.CUT_FORWARD->{forward();abort(false);return false}
                HandoffGuard.Action.CUT->{abort(false);return false}
                HandoffGuard.Action.WAIT->{blendSince=0L;main.volume=0f;p.volume=1f}
            }
            return true
        }
'''+s[b:]
p.write_text(s)
# Immediate replay stays in the existing A/B menu, not a new toolbar.
p=src/'MainActivity.kt';s=p.read_text()
replace('"Выключить повтор A/B");android.app.AlertDialog.Builder(this).setTitle','"Выключить повтор A/B","Переслушать последние 10 секунд","Закладка момента…");android.app.AlertDialog.Builder(this).setTitle')
replace('2->{RepeatRegion.active=null;loopStart=null;toast("Повтор выключен")}};render()','2->{RepeatRegion.active=null;loopStart=null;toast("Повтор выключен")};3->{if(p.isCurrentMediaItemSeekable)p.seekTo((p.currentPosition-10000).coerceAtLeast(0))};4->{momentDialog(id)}};render()')
replace('    private fun loopDialog(){',r'''    private fun momentDialog(id:String){
        val p=controller?:return
        if(!TrackMoment.canApply(id,p.currentMediaItem?.mediaId,MixerSession.active,p.isCurrentMediaItemSeekable))return
        val now=TrackMoment.position(p.currentPosition,p.duration)?:return
        val prefs=getSharedPreferences("track_moments",MODE_PRIVATE)
        val stored=runCatching{prefs.getLong(id,-1L)}.getOrDefault(-1L)
        val saved=TrackMoment.position(stored,p.duration)
        val actions=if(saved==null)arrayOf("Запомнить ${fmt(now)}")else arrayOf("Запомнить ${fmt(now)}","Перейти к ${fmt(saved)}","Удалить закладку")
        android.app.AlertDialog.Builder(this).setTitle("Любимый момент").setItems(actions){_,choice->
            if(!TrackMoment.canApply(id,p.currentMediaItem?.mediaId,MixerSession.active,p.isCurrentMediaItemSeekable)){toast("Композиция изменилась");return@setItems}
            when(choice){
                0->{if(TrackMoment.position(now,p.duration)!=null){prefs.edit().putLong(id,now).apply();toast("Момент сохранён")}}
                1->{val target=TrackMoment.position(saved,p.duration);if(target!=null){RepeatRegion.active=null;loopStart=null;p.seekTo(target)}}
                2->{prefs.edit().remove(id).apply();toast("Закладка удалена")}
            }
        }.setNegativeButton("Закрыть",null).show()
    }
    private fun loopDialog(){''')
p.write_text(s)
print('PASS: bounded forward-only handoff correction, aligned blend, ten-second replay, per-track moment bookmark')
