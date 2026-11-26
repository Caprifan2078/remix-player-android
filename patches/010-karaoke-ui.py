#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/MainActivity.kt"
s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,("Expected exactly one match",old[:100])
    s=s.replace(old,new)
replace('private var lyricToolsExpanded=false','private var lyricToolsExpanded=false\n    private var lyricFollow=true\n    private var lyricInkAnimation:android.animation.ValueAnimator?=null\n    class LyricInk(var color:Int):android.text.style.CharacterStyle(),android.text.style.UpdateAppearance{\n        override fun updateDrawState(paint:android.text.TextPaint){paint.color=color}\n    }')
replace('val scroll=ScrollView(this);lyricScroll=scroll;','''val follow=btn(if(lyricFollow)"Автопрокрутка: вкл." else "Автопрокрутка: выкл."){}
        follow.setOnClickListener{lyricFollow=!lyricFollow;follow.text=if(lyricFollow)"Автопрокрутка: вкл." else "Автопрокрутка: выкл.";if(lyricFollow){lyricViews.getOrNull(lastLine)?.let{v->lyricScroll?.smoothScrollTo(0,(v.top-dp(110)).coerceAtLeast(0))}}}
        body.addView(follow)
        val scroll=ScrollView(this);lyricScroll=scroll;''')
replace('lyricScroll?.post{lyricScroll?.smoothScrollTo(0,(v.top-dp(110)).coerceAtLeast(0))}','if(lyricFollow){val target=lyricScroll;target?.post{if(lyricFollow&&lyricScroll===target&&screen=="Текст")target.smoothScrollTo(0,(v.top-dp(110)).coerceAtLeast(0))}}')
replace('if(w>=0){val word=line.words[w];span.setSpan(android.text.style.ForegroundColorSpan(Color.WHITE),word.start,word.end,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)}','''WordLyrics.highlight(line,w)?.let{h->
                for(k in 0 until w){val done=line.words[k];span.setSpan(android.text.style.ForegroundColorSpan(Color.WHITE),done.start,done.end,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)}
                // Fixed text geometry: no underline or size changes as words advance.
                val view=lyricViews[i]
                val ink=LyricInk(accent)
                span.setSpan(ink,h.activeStart,h.activeEnd,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
                val evaluator=android.animation.ArgbEvaluator()
                lyricInkAnimation=android.animation.ValueAnimator.ofFloat(0f,1f).apply{
                    duration=140L
                    addUpdateListener{anim->
                        if(screen!="Текст"||!view.isAttachedToWindow){anim.cancel()}
                        else{ink.color=evaluator.evaluate(anim.animatedFraction,accent,Color.WHITE) as Int;view.invalidate()}
                    }
                    start()
                }
            }''')
replace('if(i==lastLine&&w==lastWord)return','if(i==lastLine&&w==lastWord)return\n        lyricInkAnimation?.cancel();lyricInkAnimation=null')
replace('body.removeAllViews();activeLyrics=emptyList();','lyricInkAnimation?.cancel();lyricInkAnimation=null;body.removeAllViews();activeLyrics=emptyList();')
p.write_text(s)
print("PASS karaoke UI overlay")
