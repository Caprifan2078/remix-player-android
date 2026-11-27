from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:120],s.count(a))
    s=s.replace(a,b)
replace('    private fun nowPlaying(){',r'''    private fun transitionMenu(){
        sheet("Переходы между песнями","Живое воспроизведение или создание отдельного DJ-микса",listOf(
            "Плавное затухание и Crossfade" to {liveTransitionMenu()},
            "Умный DJ-переход · BPM и тональность" to {transitionDialog()},
            "Таймер сна" to {sleepMenu()}
        ))
    }
    private fun sleepMenu(){
        val remaining=PlaybackTiming.remaining(android.os.SystemClock.elapsedRealtime(),PlaybackOptions.sleepDeadline)
        sheet("Таймер сна",if(remaining>0)"Осталось "+fmt(remaining) else "Выключен",
            listOf("Выключить" to {PlaybackOptions.sleepDeadline=0L;toast("Таймер выключен")})+
            listOf(15,30,45,60,90,120).map{minutes->"$minutes мин" to {PlaybackOptions.sleepDeadline=PlaybackTiming.deadline(android.os.SystemClock.elapsedRealtime(),minutes);toast("Таймер установлен")}})
    }
    private fun liveTransitionMenu(){
        val fades=listOf(0L,1000L,2000L,3000L,5000L)
        val overlaps=listOf(0L,1000L,2000L,3000L,5000L,8000L)
        fun display(v:Long)=if(v==0L)"выкл." else (v/1000).toString()+" с"
        sheet("Плавные переходы","Crossfade работает в обычном плеере без несовместимых эффектов. DJ-переход создаётся отдельно.",listOf(
            "Затухание · "+display(PlaybackOptions.fadeMs) to {
                sheet("Затухание",actions=fades.map{v->((if(v==PlaybackOptions.fadeMs)"✓ " else "")+display(v)) to {PlaybackOptions.fadeMs=v;getSharedPreferences("play_options",MODE_PRIVATE).edit().putLong("fade_ms",v).apply();liveTransitionMenu()}})
            },
            "Наложение · "+display(PlaybackOptions.overlapMs) to {
                sheet("Crossfade",actions=overlaps.map{v->((if(v==PlaybackOptions.overlapMs)"✓ " else "")+display(v)) to {PlaybackOptions.overlapMs=v;getSharedPreferences("play_options",MODE_PRIVATE).edit().putLong("overlap_ms",v).apply();liveTransitionMenu()}})
            }
        ))
    }
    private fun bindArtworkSwipe(image:ImageView,trackId:String){
        var x=0f;var y=0f;var horizontal=false;var valid=false;var startIndex=-1
        val slop=android.view.ViewConfiguration.get(this).scaledTouchSlop
        fun reset(){horizontal=false;valid=false;image.translationX=0f;image.alpha=1f;image.parent?.requestDisallowInterceptTouchEvent(false)}
        image.setOnTouchListener{_,e->
            when(e.actionMasked){
                android.view.MotionEvent.ACTION_DOWN->{x=e.x;y=e.y;horizontal=false;valid=true;startIndex=controller?.currentMediaItemIndex?:-1;true}
                android.view.MotionEvent.ACTION_POINTER_DOWN,android.view.MotionEvent.ACTION_CANCEL->{reset();true}
                android.view.MotionEvent.ACTION_MOVE->{
                    if(!valid)return@setOnTouchListener true
                    val dx=e.x-x+image.translationX;val dy=e.y-y
                    if(!horizontal&&kotlin.math.abs(dy)>slop&&kotlin.math.abs(dy)>kotlin.math.abs(dx)){reset();return@setOnTouchListener false}
                    if(!horizontal&&kotlin.math.abs(dx)>slop&&kotlin.math.abs(dx)>1.5f*kotlin.math.abs(dy)){horizontal=true;image.parent?.requestDisallowInterceptTouchEvent(true)}
                    if(horizontal){image.translationX=dx.coerceIn(-image.width*.33f,image.width*.33f);image.alpha=1f-kotlin.math.abs(image.translationX)/image.width.coerceAtLeast(1)*.45f}
                    true
                }
                android.view.MotionEvent.ACTION_UP->{
                    val dx=e.x-x+image.translationX;val dy=e.y-y
                    val player=controller
                    val direction=if(valid&&horizontal&&kotlin.math.abs(dx)>=maxOf(dp(48).toFloat(),image.width*.18f)&&kotlin.math.abs(dx)>1.5f*kotlin.math.abs(dy))if(dx<0)1 else -1 else 0
                    reset()
                    if(direction!=0&&player!=null&&screen=="Плеер"&&!MixerSession.active&&player.currentMediaItem?.mediaId==trackId&&player.currentMediaItemIndex==startIndex){
                        val index=if(direction>0)player.nextMediaItemIndex else player.previousMediaItemIndex
                        if(index in 0 until player.mediaItemCount&&index!=startIndex){player.seekToDefaultPosition(index)}
                    }
                    true
                }
                else->true
            }
        }
    }
    private fun nowPlaying(){''')
replace('val token=++coverToken','bindArtworkSwipe(image,t.uri);val token=++coverToken')
replace('"Таймер сна и переходы" to {playbackOptionsDialog()},','"Переходы между песнями" to {transitionMenu()},\n                "Таймер сна" to {sleepMenu()},')
replace('sheet("Эффекты",actions=choices+listOf("Все эффекты" to {allEffectsSheet()}))','sheet("Эффекты",actions=choices+listOf("Все эффекты" to {allEffectsSheet()},"Переходы между песнями" to {transitionMenu()}))')
replace('body.addView(btn("Таймер сна и переходы"){playbackOptionsDialog()})','body.addView(btn("Переходы и таймер сна"){transitionMenu()})')
p.write_text(s)
print("PASS: swipe artwork, live crossfade and DJ transition entry points, no added permanent player controls")
