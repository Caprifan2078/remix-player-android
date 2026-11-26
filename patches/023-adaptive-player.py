#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def edit(name,a,b):
 p=src/name;s=p.read_text();assert s.count(a)==1,(name,a[:140],s.count(a));p.write_text(s.replace(a,b))
edit('PlaybackTiming.kt','    @Volatile var overlapMs=0L','    @Volatile var overlapMs=0L\n    @Volatile var autoOverlap=true')
edit('PlaybackService.kt','val mixing=overlap?.tick(PlaybackOptions.overlapMs,eligible)==true','val automatic=PlaybackOptions.autoOverlap&&PlaybackOptions.overlapMs==0L;val requested=if(automatic)8000L else PlaybackOptions.overlapMs\n        val mixing=overlap?.tick(requested,eligible,automatic)==true')
edit('PlaybackService.kt','if(PlaybackOptions.overlapMs>0)0 else PlaybackOptions.fadeMs','if(requested>0)0 else PlaybackOptions.fadeMs')
edit('PlaybackService.kt','if(PlaybackOptions.overlapMs>0&&p.playWhenReady)25','if(requested>0&&p.playWhenReady)25')
edit('PlaybackService.kt','PlaybackOptions.overlapMs=getSharedPreferences("play_options",MODE_PRIVATE).getLong("overlap_ms",0).takeIf{it in 1000..8000}?:0L;','PlaybackOptions.overlapMs=0L;PlaybackOptions.autoOverlap=getSharedPreferences("play_options",MODE_PRIVATE).getBoolean("auto_overlap",true);')
edit('LiveOverlap.kt','    private var preview:ExoPlayer?=null','''    private var preview:ExoPlayer?=null
    private val edgeWorker=java.util.concurrent.Executors.newSingleThreadExecutor()
    private var edgeKey:List<String>?=null
    private var edgeFuture:java.util.concurrent.Future<AdaptiveOverlap.Plan>?=null
    private var fadePlan:AdaptiveOverlap.Plan?=null
    private fun clearAnalysis(){edgeFuture?.cancel(true);edgeFuture=null;edgeKey=null}
    private fun adaptivePlan(next:Int,remaining:Long):AdaptiveOverlap.Plan {
        val first=main.currentMediaItem;val second=main.getMediaItemAt(next)
        val a=first?.localConfiguration?.uri?:first?.requestMetadata?.mediaUri
        val b=second.localConfiguration?.uri?:second.requestMetadata.mediaUri
        val key=listOf(first?.mediaId.orEmpty(),a.toString(),second.mediaId,b.toString())
        if(edgeKey!=key){clearAnalysis();edgeKey=key}
        if(edgeFuture==null&&remaining<=45000&&a?.scheme=="content"&&b?.scheme=="content"){
            val firstUri=a!!;val nextUri=b!!
            edgeFuture=edgeWorker.submit<AdaptiveOverlap.Plan>{AdaptiveOverlap.plan(EdgeEnergy.scan(context,firstUri,true),EdgeEnergy.scan(context,nextUri,false))}
        }
        val f=edgeFuture
        return if(f!=null&&f.isDone)runCatching{f.get()}.getOrElse{AdaptiveOverlap.plan(null,null)}else AdaptiveOverlap.plan(null,null)
    }''')
edit('LiveOverlap.kt','fun close(){main.removeListener(listener);abort(false)}','fun close(){main.removeListener(listener);abort(false);clearAnalysis();edgeWorker.shutdownNow()}')
edit('LiveOverlap.kt','fadeWindow=null;startedAt=0L','fadeWindow=null;fadePlan=null;startedAt=0L')
edit('LiveOverlap.kt','fun tick(requested:Long,eligible:Boolean):Boolean','fun tick(requested:Long,eligible:Boolean,automatic:Boolean=false):Boolean')
edit('LiveOverlap.kt','if(requested<=0||!eligible||!main.playWhenReady){if(preview!=null)abort(true);return false}','if(requested<=0||!eligible||!main.playWhenReady){if(preview!=null)abort(true);if(requested<=0||!eligible)clearAnalysis();return false}')
edit('LiveOverlap.kt','if(preview==null&&duration-pos<=requested+5000&&duration-pos>500){','val adaptive=if(automatic)fadePlan?:adaptivePlan(next,duration-pos) else null\n        if(preview==null&&duration-pos<=requested+5000&&duration-pos>500){')
edit('LiveOverlap.kt','OverlapCore.window(duration,p.duration,requested)','OverlapCore.window(duration,p.duration,adaptive?.duration?:requested)')
edit('LiveOverlap.kt','fadeWindow=actual;started=true','fadeWindow=actual;fadePlan=adaptive;started=true')
edit('LiveOverlap.kt','val g=OverlapCore.gains(audible,w.duration);','val g=fadePlan?.let{AdaptiveOverlap.gains(audible,w.duration,it)}?:OverlapCore.gains(audible,w.duration);')
p=src/'MainActivity.kt';s=p.read_text()
a=s.index('panel.addView(label("Плавное затухание в начале и конце песни.')
b=s.index('android.app.AlertDialog.Builder(this).setTitle("Воспроизведение")',a)
s=s[:a]+'''panel.addView(label("Переходы",18,Color.WHITE,true))
        val automatic=CheckBox(this).apply{text="Умный переход между песнями";setTextColor(Color.WHITE);isChecked=PlaybackOptions.autoOverlap}
        automatic.setOnCheckedChangeListener{_,checked->PlaybackOptions.autoOverlap=checked;PlaybackOptions.overlapMs=0L;PlaybackOptions.fadeMs=0L;getSharedPreferences("play_options",MODE_PRIVATE).edit().putBoolean("auto_overlap",checked).putLong("fade_ms",0).apply()}
        panel.addView(automatic);panel.addView(label("Автоматически анализирует громкость концовки и начала следующей песни. Если анализ недоступен, использует безопасный переход. Не накладывает песни при активных эффектах, EQ, A/B или повторе одного трека.",14,muted));'''+s[b:]
# Make one result list, then explicitly confirm each lyric source. Preserve the existing stale-edit guard.
a=s.index('val result=runCatching{LyricsLookup.fetch(searchTitleValue,searchArtistValue,seconds)}')
b=s.index('.onFailure{toast("Поиск не удался:',a)
s=s[:a]+'''val result=runCatching{LyricsLookup.search(searchTitleValue,searchArtistValue,seconds)};runOnUiThread{if(!isDestroyed){lyricsBusy=false;result.onSuccess{matches->
                if(matches.isEmpty())toast("Текст не найден в LRCLIB. Попробуйте название без Remix или исполнителя.")
                else android.app.AlertDialog.Builder(this).setTitle("Выберите песню").setItems(matches.map{m->m.title+" · "+m.artist+"\\n"+(m.duration?.let{fmt(it*1000)}?:"?")+" · "+if(m.synced!=null)"синхронный текст" else "обычный текст"}.toTypedArray()){_,i->
                    val m=matches[i];val target=libraryIndex.get(t.uri)
                    if(target==null||rawLyrics(target)!=before||target.group!=groupBefore||target.tempoRatio!=ratioBefore){toast("Текст или версия изменились");return@setItems}
                    val sync=m.synced;val plain=m.plain?:sync?.let{Lrc.parse(it).joinToString("\\n"){line->WordLyrics.parse(line).text}}
                    fun store(raw:String){
                        val currentTarget=libraryIndex.get(t.uri)
                        if(currentTarget==null||rawLyrics(currentTarget)!=before||currentTarget.group!=groupBefore||currentTarget.tempoRatio!=ratioBefore){toast("Текст или версия изменились");return}
                        currentTarget.lyrics=if(ratioBefore!=null&&Lrc.parse(raw).isNotEmpty())TimeStretch.lyrics(raw,ratioBefore)else raw
                        val origin=libraryIndex.get(original.uri);if(origin!=null&&origin.uri!=currentTarget.uri&&origin.lyrics==originalBefore&&origin.lyrics.isBlank())origin.lyrics=raw
                        save();toast("Текст сохранён");render()
                    }
                    if(sync!=null&&seconds!=null&&m.duration!=null&&kotlin.math.abs(seconds-m.duration)>3){
                        android.app.AlertDialog.Builder(this).setTitle("Другая длительность").setMessage("У этой версии песни отличаются временные метки. Можно сохранить только слова или использовать метки с ручной настройкой.").setNegativeButton("Отмена",null).setNeutralButton("Только слова"){_,_->if(!plain.isNullOrBlank())store(plain)}.setPositiveButton("С метками"){_,_->store(sync)}.show()
                    }else{val raw=sync?:plain;if(!raw.isNullOrBlank())store(raw)}
                }.setNegativeButton("Отмена",null).show()
            }'''+s[b:]
# Now Playing: keep real album artwork, use existing transport controls and open effects from track screen.
a=s.index('        body.addView(label(t.title,26,Color.WHITE,true));')
b=s.index('\n    }\n    private var loopStart',a)
s=s[:a]+'''        body.addView(label(t.title,24,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})
        val meta=row();meta.addView(label(t.artist,15,muted).apply{maxLines=1;ellipsize=android.text.TextUtils.TruncateAt.END},weight())
        val original=source;meta.addView(btn(if(original.favorite)"♥" else "♡"){original.favorite=!original.favorite;save();render()}.apply{contentDescription=if(original.favorite)"Убрать из избранного" else "В избранное"});body.addView(meta)
        val modes=row()
        modes.addView(btn("Ремикс"){effectPicker()}.apply{contentDescription="Выбрать эффект для текущей песни"},weight())
        modes.addView(btn("Текст"){screen="Текст";render()},weight())
        modes.addView(btn("Очередь"){screen="Очередь";render()},weight());body.addView(modes)
        body.addView(label("Режим: "+EffectMenu.title(Presets.active.name),13,muted))
        val quick=row()
        listOf("Оригинал","Sped Up","Slowed + Reverb").forEach{name->Presets.all.firstOrNull{it.name==name}?.let{preset->quick.addView(btn(EffectMenu.title(name)){applyPreset(preset);render()},weight())}}
        body.addView(quick)
        body.addView(btn("Ещё · инструменты"){android.app.AlertDialog.Builder(this).setTitle("Композиция").setItems(arrayOf("Версии","Микшер","Студия","Таймер и переходы","Повтор A/B","Вырезать фрагмент","Эквалайзер")){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(i){0->{screen="Версии";render()};1->{screen="Микшер";render()};2->{screen="Студия";render()};3->playbackOptionsDialog();4->loopDialog();5->clipDialog(t);6->{screen="Эквалайзер";render()}}}.show()})'''+s[b:]
p.write_text(s)
print("PASS: adaptive live overlap, multiple lyric matches, instant remix controls")
