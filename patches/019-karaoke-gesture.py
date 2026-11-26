from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
old='''        body.addView(follow)
        val scroll=ScrollView(this);lyricScroll=scroll;val lines=column();scroll.addView(lines);body.addView(scroll,LinearLayout.LayoutParams(-1,dp(330)));'''
new='''        body.addView(label(t.title,18,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})
        if(t.artist.isNotBlank())body.addView(label(t.artist,14,muted))
        body.addView(follow)
        val scroll=object:ScrollView(this){
            private var downX=0f;private var downY=0f;private var watching=false
            private val slop=ViewConfiguration.get(context).scaledTouchSlop.toFloat()
            override fun dispatchTouchEvent(event:MotionEvent):Boolean{
                when(event.actionMasked){
                    MotionEvent.ACTION_DOWN->{downX=event.x;downY=event.y;watching=true;parent?.requestDisallowInterceptTouchEvent(true)}
                    MotionEvent.ACTION_MOVE->if(watching&&event.pointerCount==1&&kotlin.math.abs(event.y-downY)>slop&&kotlin.math.abs(event.y-downY)>kotlin.math.abs(event.x-downX)){
                        watching=false
                        if(lyricFollow){lyricFollow=false;getSharedPreferences("lyrics_ui",MODE_PRIVATE).edit().putBoolean("follow",false).apply();follow.text="Автопрокрутка: выкл."}
                    }
                    MotionEvent.ACTION_POINTER_DOWN->watching=false
                    MotionEvent.ACTION_UP,MotionEvent.ACTION_CANCEL->{watching=false;parent?.requestDisallowInterceptTouchEvent(false)}
                }
                return super.dispatchTouchEvent(event)
            }
        }.apply{tag="karaoke-scroll";isFillViewport=true}
        lyricScroll=scroll;val lines=column();scroll.addView(lines);body.addView(scroll,LinearLayout.LayoutParams(-1,dp((resources.configuration.screenHeightDp*.53).toInt().coerceIn(260,520))));'''
assert s.count(old)==1
p.write_text(s.replace(old,new))
print('PASS: adaptive karaoke viewport, track heading, manual vertical scroll pauses follow')
