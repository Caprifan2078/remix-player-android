#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1]);p=root/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:130],s.count(a))
 s=s.replace(a,b)
# Shared color and native icons, replacing boxed purple buttons everywhere.
s,n=re.subn(r'private val bg=Color\.rgb\([^)]*\); private val surface=Color\.rgb\([^)]*\); private val accent=Color\.rgb\([^)]*\); private val muted=Color\.rgb\([^)]*\)', 'private val bg=PremiumChrome.BG; private val surface=PremiumChrome.SURFACE; private val accent=PremiumChrome.ACCENT; private val muted=PremiumChrome.MUTED',s)
assert n==1
a=s.index('    private fun label(');b=s.index('    private fun toast(',a)
s=s[:a]+'''    private fun label(s:String,size:Int=16,c:Int=PremiumChrome.TEXT,b:Boolean=false)=TextView(this).apply{text=s;textSize=size.toFloat();setTextColor(c);typeface=Typeface.create(if(b)"sans-serif-medium" else "sans-serif",Typeface.NORMAL);setPadding(dp(5),dp(6),dp(5),dp(6));includeFontPadding=false}
    private fun btn(s:String,action:()->Unit)=PremiumChrome.Control(this).apply{text=s;contentDescription=when(s){"⇄"->"Случайный порядок воспроизведения";"|◀"->"Предыдущая композиция";"▶|"->"Следующая композиция";"↻"->"Режим повтора";"⋮"->"Действия";"♥"->"Убрать из избранного";"♡"->"В избранное";else->null};isAllCaps=false;textSize=14f;minWidth=0;minimumWidth=0;minHeight=dp(48);minimumHeight=dp(48);setPadding(dp(9),dp(5),dp(9),dp(5));setTextColor(PremiumChrome.TEXT);typeface=Typeface.create("sans-serif-medium",Typeface.NORMAL);background=PremiumChrome.ripple(if(s in listOf("⇄","|◀","▶","Ⅱ","▶|","↻","⋮","♥","♡"))Color.TRANSPARENT else surface,dp(12).toFloat());setOnClickListener{action()}}
'''+s[b:]
a=s.index('    private fun card(');b=s.index('\n',a)
s=s[:a]+'''    private fun card(title:String,sub:String,action:()->Unit){
        val r=row();r.background=PremiumChrome.ripple(surface,dp(14).toFloat());r.setPadding(dp(12),dp(8),dp(12),dp(8));r.isFocusable=true
        val c=column();c.addView(label(title,16,PremiumChrome.TEXT,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END});c.addView(label(sub,12,muted).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})
        r.addView(c,weight());r.addView(label("›",24,muted));r.setOnClickListener{action()};body.addView(r,LinearLayout.LayoutParams(-1,-2).apply{bottomMargin=dp(5)})
    }'''+s[b:]
rep('    private val navButtons=','    private var miniPlay:Button?=null;private var transportRow:LinearLayout?=null;private var navRow:LinearLayout?=null\n    private val navButtons=')
a=s.index('        val nav=row();listOf(');b=s.index('\n',a)
s=s[:a]+'''        val nav=row();navRow=nav;nav.setPadding(0,dp(5),0,0)
        listOf("Музыка","Студия","Текст","Ещё").forEach{name->
            val button=btn(name){if(name=="Ещё")moreMenu()else{screen=name;render()}};button.textSize=11f;button.minHeight=dp(58);button.minimumHeight=dp(58);navButtons[name]=button;nav.addView(button,weight())
        }'''+s[b:]
rep('val controls=row();controls.addView(btn("⇄")','val controls=row();transportRow=controls;controls.addView(btn("⇄")')
rep('bar.addView(controls);root.addView(nav)','''bar.addView(controls)
        val quickPlay=btn("▶"){play.performClick()};miniPlay=quickPlay;nowRow.addView(quickPlay,LinearLayout.LayoutParams(dp(48),dp(48)))
        root.addView(nav)''')
rep('setTextChanged(play,if(playing)"Ⅱ" else "▶")','setTextChanged(play,if(playing)"Ⅱ" else "▶");setTextChanged(miniPlay,if(playing)"Ⅱ" else "▶")')
rep('if(play.contentDescription!=playDescription)play.contentDescription=playDescription','if(play.contentDescription!=playDescription)play.contentDescription=playDescription;miniPlay?.contentDescription=playDescription')
a=s.index('val selected=when(screen)');b=s.index('studioStatusView=null;',a)
s=s[:a]+'''val selected=when(screen){"Жанры","Микшер"->"Студия";"Плеер","Очередь","История","Эквалайзер"->"Музыка";"Версии","Загрузки","Настройки"->"Ещё";else->screen}
        navButtons.forEach{(name,button)->button.isSelected=name==selected;PremiumChrome.nav(button,when(name){"Музыка"->"library";"Студия"->"studio";"Текст"->"lyrics";else->"more"},button.isSelected);button.contentDescription=if(button.isSelected)"$name, текущий раздел" else name}
        val full=screen=="Плеер";transportRow?.visibility=if(full)View.VISIBLE else View.GONE;miniPlay?.visibility=if(full)View.GONE else View.VISIBLE;navRow?.visibility=View.VISIBLE;'''+s[b:]
rep('now.contentDescription="Открыть экран воспроизведения"','now.contentDescription="Открыть экран воспроизведения"')
rep('seek.max=1000;seek.contentDescription=','seek.max=1000;seek.progressTintList=android.content.res.ColorStateList.valueOf(accent);seek.thumbTintList=android.content.res.ColorStateList.valueOf(accent);seek.contentDescription=')
rep('scaleType=ImageView.ScaleType.FIT_CENTER;setBackgroundColor(surface);contentDescription="Обложка композиции";setImageResource(android.R.drawable.ic_media_play)','scaleType=ImageView.ScaleType.FIT_CENTER;background=PremiumChrome.shape(surface,dp(18).toFloat());clipToOutline=true;contentDescription="Обложка композиции";setImageDrawable(PremiumChrome.icon(this@MainActivity,"disc",muted,100))')
# Give the song list a consistent artwork slot and clean visual title without changing original metadata.
rep('songs.subList(page.start,page.end).forEach{t->val r=row();val col=column();','''songs.subList(page.start,page.end).forEach{t->val r=row();val col=column();
            val art=ImageView(this).apply{scaleType=ImageView.ScaleType.CENTER_INSIDE;background=PremiumChrome.shape(surface,dp(8).toFloat());clipToOutline=true;setImageDrawable(PremiumChrome.icon(this@MainActivity,"disc",muted,27));coverCache.get(t.uri)?.let{setImageBitmap(it);scaleType=ImageView.ScaleType.CENTER_CROP};importantForAccessibility=View.IMPORTANT_FOR_ACCESSIBILITY_NO}
            r.addView(art,LinearLayout.LayoutParams(dp(46),dp(46)).apply{rightMargin=dp(9)});art.setOnClickListener{col.performClick()};''')
# Move advanced entry points behind a short 'More' sheet; navigation labels stay accessible.
helper='''    private fun moreMenu(){
        val names=arrayOf("Версии","Загрузки","Очередь","История","Эквалайзер","Настройки","Тексты библиотеки")
        android.app.AlertDialog.Builder(this).setTitle("Ещё").setItems(names){_,i->if(i==names.lastIndex)batchLyrics()else{screen=names[i];render()}}.setNegativeButton("Закрыть",null).show()
    }
    private data class BatchLyricsItem(val uri:String,val title:String,val artist:String)
    private fun batchLyrics(){
        if(stemBusy){toast("Дождитесь завершения обработки");return}
        val pending=tracks.filter{it.uri==it.group&&it.lyrics.isBlank()}.map{BatchLyricsItem(it.uri,it.title,it.artist)}
        if(pending.isEmpty()){toast("Нет песен без текста");return}
        android.app.AlertDialog.Builder(this).setTitle("Тексты библиотеки").setMessage("Песен без текста: ${pending.size}. Поиск передаёт LRCLIB только название, исполнителя и длительность. Сохраняются лишь однозначные совпадения. Уже существующие тексты не изменяются. Можно отменить операцию.").setNegativeButton("Отмена",null).setPositiveButton("Найти"){_,_->
            stemWork("Поиск текстов…",{
                val found=linkedMapOf<String,String>();var errors=0
                for((i,t) in pending.withIndex()){
                    check(!Thread.currentThread().isInterrupted){"Отменено"}
                    updateWork("Тексты: ${i+1}/${pending.size} · найдено ${found.size}")
                    try{
                        val retriever=MediaMetadataRetriever()
                        val seconds=try{retriever.setDataSource(this,Uri.parse(t.uri));retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull()?.let{(it+500)/1000}}finally{runCatching{retriever.release()}}
                        if(seconds!=null){BatchLyricPolicy.choose(LyricsLookup.search(t.title,t.artist,seconds),t.title,t.artist,seconds)?.let{found[t.uri]=it}}
                    }catch(e:Exception){if(Thread.currentThread().isInterrupted||e is InterruptedException)throw e;errors++}
                    if(i!=pending.lastIndex)Thread.sleep(1100)
                }
                found to errors
            }){result->
                val changed=mutableListOf<Track>()
                result.first.forEach{(id,raw)->libraryIndex.get(id)?.takeIf{it.uri==it.group&&it.lyrics.isBlank()}?.let{it.lyrics=raw;changed.add(it)}}
                if(!saveLibrary(true)){changed.forEach{it.lyrics=""};reindex();toast("Не удалось сохранить тексты")}
                else android.app.AlertDialog.Builder(this).setTitle("Поиск завершён").setMessage("Добавлено: ${changed.size}\\nБез уверенного совпадения: ${pending.size-result.first.size-result.second}\\nОшибки поиска: ${result.second}").setPositiveButton("Готово",null).show()
            }
        }.show()
    }
'''
rep('    private fun effectPicker(){',helper+'    private fun effectPicker(){')
# Make library tools discoverable without filling the main list.
rep('"Сравнить песни по звуку…")){_,i->if(!stemBusy)when(i){0->chooseGenreBatch();1->chooseMoodBatch();2->suggestVersions();3->fingerprintDialog()}', '"Сравнить песни по звуку…","Найти тексты для всех песен")){_,i->if(!stemBusy)when(i){0->chooseGenreBatch();1->chooseMoodBatch();2->suggestVersions();3->fingerprintDialog();4->batchLyrics()}')
# Upgrade platform dialog theme to match the main interface.
p.write_text(s)
style=root/'app/src/main/res/values/styles.xml';style.write_text('''<resources><style name="AppTheme" parent="android:style/Theme.Material.NoActionBar"><item name="android:fontFamily">sans-serif</item><item name="android:windowLightStatusBar">false</item><item name="android:windowBackground">#111216</item><item name="android:colorAccent">#C7E8A2</item><item name="android:statusBarColor">#111216</item><item name="android:navigationBarColor">#111216</item><item name="android:colorBackground">#1D2025</item></style></resources>''')
print("PASS: shared native icon system, four destinations, compact player, batch lyrics")
