#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b)
# Reuse the actual transport widgets, never create a second playback controller.
rep('private var headerImport:Button?=null','private var headerImport:Button?=null;private var headerBrand:TextView?=null;private var compactNowRow:LinearLayout?=null;private var playerActions:LinearLayout?=null')
rep('header.addView(label("REMIX",22,PremiumChrome.TEXT,true),weight())','val brand=label("REMIX",22,PremiumChrome.TEXT,true);headerBrand=brand;header.addView(brand,weight())')
rep('val nowRow=row();bar.addView(nowRow);','val nowRow=row();compactNowRow=nowRow;bar.addView(nowRow);')
rep('studioStatusView=null;backupStatus=null;', 'restoreTransport();playerActions=null;headerBrand?.apply{text=if(full)"СЕЙЧАС ИГРАЕТ" else "REMIX";textSize=if(full)12f else 22f;gravity=if(full)Gravity.CENTER else Gravity.START or Gravity.CENTER_VERTICAL;setTextColor(if(full)muted else PremiumChrome.TEXT)};studioStatusView=null;backupStatus=null;')
# When a song is present, move the original transport widgets into the scrollable player.
# Restore before each render (including navigation and track transitions).
rep('    private fun nowPlaying(){','''    private fun movePlayerView(view:View,destination:LinearLayout,index:Int=-1){
        (view.parent as? android.view.ViewGroup)?.removeView(view)
        destination.addView(view,index,LinearLayout.LayoutParams(-1,-2))
    }
    private fun restoreTransport(){
        val row=compactNowRow?:return
        if(time.parent!==row){(time.parent as? android.view.ViewGroup)?.removeView(time);row.addView(time,1,LinearLayout.LayoutParams(-2,-2))}
        if(seek.parent!==bar)movePlayerView(seek,bar,1)
        transportRow?.let{if(it.parent!==bar)movePlayerView(it,bar)}
    }
    private fun nowPlaying(){''')
rep('heading("Сейчас играет");val t=current()?:run{body.addView(label("Выберите композицию",16,muted));return}', 'val t=current()?:run{heading("Сейчас играет");body.addView(label("Выберите композицию",16,muted));return};bar.visibility=View.GONE;body.gravity=Gravity.CENTER_HORIZONTAL')
rep('body.addView(image,LinearLayout.LayoutParams(-1,dp(if(resources.configuration.screenHeightDp<500)180 else 270)))','''val cfg=resources.configuration
        val coverDp=minOf((cfg.screenWidthDp-48).coerceAtLeast(96),(cfg.screenHeightDp-440).coerceAtLeast(96),256)
        body.addView(image,LinearLayout.LayoutParams(dp(coverDp),dp(coverDp)).apply{topMargin=dp(4);bottomMargin=dp(6)})''')
rep('body.addView(label(t.title,24,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})','body.addView(label(t.title,24,PremiumChrome.TEXT,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END},LinearLayout.LayoutParams(-1,-2))')
rep('body.addView(meta)','body.addView(meta,LinearLayout.LayoutParams(-1,-2));movePlayerView(seek,body);movePlayerView(time,body);time.gravity=Gravity.CENTER;transportRow?.let{movePlayerView(it,body)}')
rep('val modes=row()\n        modes.addView(btn("Ремикс"){effectPicker()}','val modes=row();playerActions=modes\n        modes.addView(btn("Ремикс"){effectPicker()}')
rep('body.addView(modes)\n        body.addView(label("Режим: "+EffectMenu.title(Presets.active.name),13,muted))','body.addView(modes,LinearLayout.LayoutParams(-1,-2).apply{topMargin=dp(8)});if(Presets.active!=Presets.all.first())body.addView(label(EffectMenu.title(Presets.active.name),13,muted))')
# Never leak center alignment into library and other screens.
rep('body.removeAllViews();activeLyrics=','body.removeAllViews();body.gravity=Gravity.TOP or Gravity.START;activeLyrics=')
(p.parent/'CoverSwipe.kt').write_bytes((Path(__file__).parent/'CoverSwipe.kt').read_bytes())
rep('val token=++coverToken', '''installCoverSwipe(image,t.uri)
        val token=++coverToken''')
rep('    private fun nowPlaying(){','''    @android.annotation.SuppressLint("ClickableViewAccessibility")
    private fun installCoverSwipe(image:ImageView,id:String){
        image.contentDescription="Обложка · влево следующая песня, вправо предыдущая"
        var x=0f;var y=0f;var horizontal=false
        val slop=android.view.ViewConfiguration.get(this).scaledTouchSlop
        image.setOnTouchListener{v,e->
            when(e.actionMasked){
                android.view.MotionEvent.ACTION_DOWN->{x=e.x;y=e.y;horizontal=false;true}
                android.view.MotionEvent.ACTION_MOVE->{
                    val dx=e.x-x;val dy=e.y-y
                    if(!horizontal&&kotlin.math.abs(dx)>slop&&kotlin.math.abs(dx)>kotlin.math.abs(dy)*1.6f){
                        horizontal=true;v.parent?.requestDisallowInterceptTouchEvent(true)
                    }
                    true
                }
                android.view.MotionEvent.ACTION_UP->{
                    v.parent?.requestDisallowInterceptTouchEvent(false)
                    val d=CoverSwipe.direction(e.x-x,e.y-y,dp(56).toFloat())
                    if(horizontal&&d!=null&&current()?.uri==id){
                        controller?.let{p->
                            val can=if(d==CoverSwipe.Direction.NEXT)p.hasNextMediaItem() else p.hasPreviousMediaItem()
                            if(can){stopPreview();if(d==CoverSwipe.Direction.NEXT)p.seekToNextMediaItem() else p.seekToPreviousMediaItem()}
                        }
                    }else if(!horizontal&&kotlin.math.abs(e.x-x)<=slop&&kotlin.math.abs(e.y-y)<=slop)v.performClick()
                    horizontal=false;true
                }
                android.view.MotionEvent.ACTION_CANCEL,android.view.MotionEvent.ACTION_POINTER_DOWN->{horizontal=false;v.parent?.requestDisallowInterceptTouchEvent(false);false}
                else->true
            }
        }
    }
    private fun nowPlaying(){''')
p.write_text(s)
print("PASS: shared real controls are relocated into the player; adaptive artwork and single header")
