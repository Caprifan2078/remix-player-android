from pathlib import Path
import sys
root=Path(sys.argv[1]);p=root/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text();draw=root/'app/src/main/res/drawable'
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:140],s.count(a))
    s=s.replace(a,b)
def section(a,b,new):
    global s
    start=s.index(a);end=s.index(b,start);s=s[:start]+new+s[end:]
def vector(name,path,filled=False):
    fill='#FFFFFFFF' if filled else '#00000000'
    (draw/('remix_'+name+'.xml')).write_text(f'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="{fill}" android:strokeColor="#FFFFFFFF" android:strokeWidth="{0 if filled else 1.8}" android:strokeLineCap="round" android:strokeLineJoin="round" android:pathData="{path}"/></vector>')
for name,path,filled in [
    ('play','M8,5 L20,12 L8,19 Z',True),
    ('pause','M7,5 H10 V19 H7 Z M14,5 H17 V19 H14 Z',True),
    ('previous','M5,5 H7 V19 H5 Z M19,5 L8,12 L19,19 Z',True),
    ('next','M17,5 H19 V19 H17 Z M5,5 L16,12 L5,19 Z',True),
    ('shuffle','M3,6 H5 C11,6 13,18 19,18 H21 M18,15 L21,18 L18,21 M3,18 H5 C11,18 13,6 19,6 H21 M18,3 L21,6 L18,9',False),
    ('repeat','M17,2 L21,6 L17,10 M21,6 H7 A4,4 0 0 0 3,10 M7,22 L3,18 L7,14 M3,18 H17 A4,4 0 0 0 21,14',False),
    ('repeat_one','M17,2 L21,6 L17,10 M21,6 H7 A4,4 0 0 0 3,10 M7,22 L3,18 L7,14 M3,18 H17 A4,4 0 0 0 21,14 M10,10 L12,9 V15',False),
    ('folder','M3,6 H10 L12,8 H21 V19 H3 Z',False),
    ('download','M12,3 V15 M7,10 L12,15 L17,10 M4,17 V21 H20 V17',False),
    ('history','M3,12 A9,9 0 1 0 6,5 M3,4 V10 H9 M12,7 V12 L15,14',False),
    ('search','M10,3 A7,7 0 1 0 10,17 A7,7 0 1 0 10,3 M15,15 L21,21',False),
    ('chevron','M9,5 L16,12 L9,19',False),
]:vector(name,path,filled)
(draw/'remix_artwork.xml').write_text('<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="88dp" android:height="88dp" android:viewportWidth="88" android:viewportHeight="88"><path android:fillColor="#267E73AB" android:pathData="M44,4 A40,40 0,1 0,44 84 A40,40 0,1 0,44 4"/><path android:fillColor="#00FFFFFF" android:strokeColor="#BDB6D2" android:strokeWidth="3.2" android:strokeLineCap="round" android:strokeLineJoin="round" android:pathData="M39,55 V31 L61,26 V49 M39,55 C39,62 25,64 25,57 C25,50 34,48 39,52 M61,49 C61,56 47,58 47,51 C47,44 56,42 61,46"/></vector>')
# Maintain touch targets and text semantics but visually replace symbol glyphs with vectors.
replace('    private var transportMode=-1',r'''    private val transportIconState=mutableMapOf<Button,Pair<Int,Int>>()
    private fun transportIcon(button:Button,res:Int,tint:Int){
        val key=res to tint
        if(transportIconState[button]==key)return
        transportIconState[button]=key
        val glyph=getDrawable(res)?.mutate()?:return
        glyph.setTint(tint)
        val layer=android.graphics.drawable.LayerDrawable(arrayOf(glyph))
        val size=dp(if(button===play)30 else 24)
        layer.setLayerSize(0,size,size);layer.setLayerGravity(0,Gravity.CENTER)
        button.foreground=layer;button.foregroundGravity=Gravity.FILL
        button.setTextColor(Color.TRANSPARENT)
    }
    private fun updateTransportIcons(){
        val p=controller
        val playing=play.text.toString()!="▶"
        transportIcon(play,if(playing)R.drawable.remix_pause else R.drawable.remix_play,bg)
        transportIcon(compactPlay,if(playing)R.drawable.remix_pause else R.drawable.remix_play,Color.WHITE)
        transportIcon(transportControls.getChildAt(0) as Button,R.drawable.remix_shuffle,if(p?.shuffleModeEnabled==true)accent else muted)
        transportIcon(transportControls.getChildAt(1) as Button,R.drawable.remix_previous,Color.WHITE)
        transportIcon(transportControls.getChildAt(3) as Button,R.drawable.remix_next,Color.WHITE)
        val repeat=p?.repeatMode?:0
        transportIcon(transportControls.getChildAt(4) as Button,if(repeat==1)R.drawable.remix_repeat_one else R.drawable.remix_repeat,if(repeat!=0)accent else muted)
    }
    private var transportMode=-1''')
replace('compactPlay.contentDescription=if(play.text.toString()=="▶")"Воспроизвести" else "Пауза"','compactPlay.contentDescription=if(play.text.toString()=="▶")"Воспроизвести" else "Пауза";updateTransportIcons()')
# Keep the existing 48dp action regions; add short captions only to three ambiguous player actions.
replace('        val tools=row()\n        tools.addView(iconButton(R.drawable.remix_lyrics,"Текст песни"){screen="Текст";render()},weight())\n        tools.addView(iconButton(R.drawable.remix_versions,"Версии композиции"){screen="Версии";render()},weight())\n        tools.addView(iconButton(R.drawable.remix_effects,"Эффекты"){quickPresetSheet()},weight())\n        body.addView(tools)',r'''        body.addView(View(this),LinearLayout.LayoutParams(-1,0,1f))
        val tools=row()
        fun action(res:Int,description:String,caption:String,run:()->Unit){
            val cell=column().apply{gravity=Gravity.CENTER_HORIZONTAL}
            cell.addView(iconButton(res,description,run))
            cell.addView(label(caption,11,muted).apply{gravity=Gravity.CENTER;setPadding(0,0,0,dp(4));importantForAccessibility=View.IMPORTANT_FOR_ACCESSIBILITY_NO})
            tools.addView(cell,weight())
        }
        action(R.drawable.remix_lyrics,"Текст песни","Текст"){screen="Текст";render()}
        action(R.drawable.remix_versions,"Версии композиции","Версии"){screen="Версии";render()}
        action(R.drawable.remix_effects,"Эффекты","Эффекты"){quickPresetSheet()}
        body.addView(tools)''')
replace('contentDescription="Обложка композиции";scaleType=ImageView.ScaleType.CENTER;setImageResource(R.drawable.remix_music)', '''contentDescription="Обложка композиции";scaleType=ImageView.ScaleType.CENTER_INSIDE;setImageResource(R.drawable.remix_artwork)''')
replace('val side=dp(minOf(300,resources.configuration.screenWidthDp-64,(resources.configuration.screenHeightDp*.36).toInt()).coerceAtLeast(120))','val side=dp(minOf(320,resources.configuration.screenWidthDp-56,(resources.configuration.screenHeightDp*.34).toInt()).coerceAtLeast(100))')
# All sheets use the same typography, top-only corners, and measured scroll cap.
section('    private fun sheet(title:String,','    private fun toast(s:String)',r'''    private fun sheet(title:String,subtitle:String="",actions:List<Pair<String,()->Unit>>){
        val dialog=android.app.Dialog(this)
        val panel=column().apply{
            setPadding(dp(16),dp(8),dp(16),dp(12))
            background=GradientDrawable().apply{setColor(surface);cornerRadii=floatArrayOf(dp(24).toFloat(),dp(24).toFloat(),dp(24).toFloat(),dp(24).toFloat(),0f,0f,0f,0f)}
        }
        val handle=View(this).apply{background=rounded(muted,3);alpha=.55f}
        panel.addView(handle,LinearLayout.LayoutParams(dp(34),dp(4)).apply{gravity=Gravity.CENTER_HORIZONTAL;bottomMargin=dp(6)})
        val top=row();top.addView(label(title,20,Color.WHITE,true),weight());top.addView(iconButton(R.drawable.remix_close,"Закрыть меню"){dialog.dismiss()});panel.addView(top)
        if(subtitle.isNotBlank())panel.addView(label(subtitle,13,muted).apply{setLineSpacing(dp(2).toFloat(),1f)})
        val items=column()
        actions.forEach{(name,action)->
            val item=label(name,15,if(name.startsWith("✓ "))accent else Color.WHITE).apply{
                minimumHeight=dp(48);gravity=Gravity.CENTER_VERTICAL;isClickable=true;isFocusable=true
                setPadding(dp(10),dp(10),dp(10),dp(10));setLineSpacing(dp(2).toFloat(),1f)
                background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22FFFFFF),null,rounded(Color.WHITE,12))
                setOnClickListener{dialog.dismiss();action()}
            };items.addView(item,LinearLayout.LayoutParams(-1,-2))
        }
        val scroll=object:ScrollView(this){
            override fun onMeasure(w:Int,h:Int){
                val cap=dp((resources.configuration.screenHeightDp*.56).toInt().coerceAtLeast(100))
                val size=if(View.MeasureSpec.getMode(h)==View.MeasureSpec.UNSPECIFIED)cap else minOf(cap,View.MeasureSpec.getSize(h))
                super.onMeasure(w,View.MeasureSpec.makeMeasureSpec(size,View.MeasureSpec.AT_MOST))
            }
        }
        scroll.isFillViewport=false;scroll.isVerticalScrollBarEnabled=actions.size>6
        scroll.addView(items);panel.addView(scroll,LinearLayout.LayoutParams(-1,-2))
        dialog.setContentView(panel);dialog.setCanceledOnTouchOutside(true)
        dialog.window?.setBackgroundDrawableResource(android.R.color.transparent)
        dialog.show();dialog.window?.apply{setGravity(Gravity.BOTTOM);setLayout(-1,-2);navigationBarColor=surface}
    }
''')
# Consistent drawer entries with meaningful icons instead of a stack of large filled buttons.
replace('    private fun installDrawer(nav:LinearLayout){',r'''    private fun decorateNav(button:Button,res:Int){
        val glyph=getDrawable(res)?.mutate()?.apply{setTint(muted)}
        button.setCompoundDrawablesWithIntrinsicBounds(glyph,null,null,null);button.compoundDrawablePadding=dp(16)
        button.gravity=Gravity.CENTER_VERTICAL or Gravity.START;button.setPadding(dp(14),dp(4),dp(12),dp(4))
        button.background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22FFFFFF),null,rounded(Color.WHITE,12))
    }
    private var lastNavStyle=""
    private fun styleDrawer(){
        if(lastNavStyle==screen)return;lastNavStyle=screen
        navButtons.forEach{(name,button)->
            val color=if(name==screen)accent else muted
            button.setTextColor(color);button.compoundDrawables.filterNotNull().forEach{it.setTint(color)}
            button.background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22FFFFFF),if(name==screen)rounded(0x22C0B0FF,12)else null,rounded(Color.WHITE,12))
        }
    }
    private fun installDrawer(nav:LinearLayout){''')
replace('        panel.addView(nav)\n        panel.addView(btn("Настройки и память"){closeDrawer();screen="Настройки";render()})\n        panel.addView(btn("История"){closeDrawer();screen="История";render()})',r'''        val glyphs=listOf(R.drawable.remix_music,R.drawable.remix_versions,R.drawable.remix_effects,R.drawable.remix_lyrics,R.drawable.remix_download)
        for(i in 0 until nav.childCount)decorateNav(nav.getChildAt(i) as Button,glyphs[i])
        panel.addView(nav)
        val divider=View(this).apply{setBackgroundColor(0x33FFFFFF)}
        panel.addView(divider,LinearLayout.LayoutParams(-1,dp(1)).apply{topMargin=dp(8);bottomMargin=dp(8)})
        panel.addView(btn("Настройки и память"){closeDrawer();screen="Настройки";render()}.apply{decorateNav(this,R.drawable.remix_settings)})
        panel.addView(btn("История"){closeDrawer();screen="История";render()}.apply{decorateNav(this,R.drawable.remix_history)})''')
replace('        if(::libraryTabs.isInitialized){libraryTabs.visibility=', '        styleDrawer()\n        if(::libraryTabs.isInitialized){libraryTabs.visibility=')
replace('tabs.forEach{(name,action)->libraryTabs.addView(btn(name,action).apply{background=rounded(Color.TRANSPARENT,10);textSize=12f;setSingleLine()},weight())}',r'''tabs.forEachIndexed{i,(name,action)->libraryTabs.addView(btn(name,action).apply{
            background=rounded(Color.TRANSPARENT,10);textSize=11f;setSingleLine();gravity=Gravity.CENTER
            val res=listOf(R.drawable.remix_music,R.drawable.remix_folder,R.drawable.remix_queue)[i]
            val glyph=getDrawable(res)?.mutate()?.apply{setTint(muted);setBounds(0,0,dp(20),dp(20))}
            setCompoundDrawables(null,glyph,null,null);compoundDrawablePadding=dp(1);setPadding(0,dp(3),0,dp(3))
        },weight())}''')
replace('for(i in 0 until libraryTabs.childCount)(libraryTabs.getChildAt(i) as Button).setTextColor(if(i==selected)accent else muted)','for(i in 0 until libraryTabs.childCount){val tab=libraryTabs.getChildAt(i) as Button;val tint=if(i==selected)accent else muted;tab.setTextColor(tint);tab.compoundDrawables.filterNotNull().forEach{it.setTint(tint)}}')
# Search gets a compact quiet surface and an actual icon; no extra huge button.
replace('val searchRow=row()\n        val search=EditText(this).apply{hint="Поиск музыки";contentDescription="Поиск по песне, исполнителю, альбому или ремиксу";setSingleLine();setText(query)}','''val searchRow=row().apply{background=rounded(surface,14);setPadding(dp(10),0,dp(4),0)}
        val search=EditText(this).apply{hint="Поиск музыки";contentDescription="Поиск по песне, исполнителю, альбому или ремиксу";setSingleLine();setText(query);textSize=15f;setHintTextColor(muted);setTextColor(Color.WHITE);background=null;minimumHeight=dp(48);val glyph=getDrawable(R.drawable.remix_search)?.mutate()?.apply{setTint(muted);setBounds(0,0,dp(20),dp(20))};setCompoundDrawables(glyph,null,null,null);compoundDrawablePadding=dp(8)}''')
# Common legacy buttons no longer visually fuse together; layout/touch size remains unchanged.
start=s.index('    private fun btn(');end=s.index('    private fun iconButton(',start)
fragment=s[start:end]
old='rounded(surface,12),rounded(Color.WHITE,12))'
assert fragment.count(old)==1,fragment[:500]
fragment=fragment.replace(old,'android.graphics.drawable.InsetDrawable(rounded(surface,12),dp(2)),rounded(Color.WHITE,12))')
s=s[:start]+fragment+s[end:]
p.write_text(s)
print('PASS: vector transport, compact player actions, coherent navigation, adaptive sheets and quiet search')
