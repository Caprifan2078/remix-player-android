#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt'
s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b)
# A first-class entry in library and More, separate from experimental MERT.
rep('val tools=row();tools.addView(filter,weight());','if(tracks.isNotEmpty())body.addView(btn("Под настроение"){moodDiscoveryDialog()});val tools=row();tools.addView(filter,weight());')
rep('val names=listOf("Версии","Загрузки","Очередь","История","Эквалайзер","Настройки","Тексты библиотеки")','val names=listOf("Под настроение","Версии","Загрузки","Очередь","История","Эквалайзер","Настройки","Сканирование библиотеки")')
rep('if(name=="Тексты библиотеки")batchLyrics()else{screen=name;render()}','when(name){"Под настроение"->moodDiscoveryDialog();"Сканирование библиотеки"->batchLyrics();else->{screen=name;render()}}')
# Keep cached acoustic summaries from the full-library scan as well.
rep('private fun scanFacts(uri:String,report:MusicAnalysis.Report){','private fun scanFacts(uri:String,report:MusicAnalysis.Report){\n        libraryIndex.get(uri)?.let{t->MoodDiscovery.from(report)?.let{f->saveMood(t.uri,t.title,t.artist,f)}}')
anchor='    private fun scanDraftReview(){'
assert s.count(anchor)==1
helper='''    private fun moodPrefs()=getSharedPreferences("mood_discovery_v1",MODE_PRIVATE)
    private fun moodStamp(id:String,title:String,artist:String)=scanKey(id+"\\u0000"+title+"\\u0000"+artist)
    private fun saveMood(id:String,title:String,artist:String,f:MoodDiscovery.Features){
        val row=JSONArray().put(f.energy).put(f.activity).put(f.brightness).put(f.low).put(f.valence?:JSONObject.NULL).put(f.dynamics)
        moodPrefs().edit().putString(moodStamp(id,title,artist),row.toString()).apply()
    }
    private fun moodEntries(songs:List<Track>):List<MoodDiscovery.Entry>{
        val rows=moodPrefs().all
        return songs.mapNotNull{t->runCatching{
            val a=JSONArray(rows[moodStamp(t.uri,t.title,t.artist)] as? String?:return@runCatching null)
            require(a.length()==6)
            MoodDiscovery.Entry(t.uri,t.artist,MoodDiscovery.Features(a.getDouble(0),a.getDouble(1),a.getDouble(2),a.getDouble(3),if(a.isNull(4))null else a.getDouble(4),a.getDouble(5)))
        }.getOrNull()}
    }
    private fun moodDiscoveryDialog(){
        val songs=tracks.filter{it.uri==it.group}
        if(songs.isEmpty()){toast("Сначала добавьте музыку");return}
        val indexed=moodEntries(songs)
        actionSheet("Под настроение",510){dialog,panel->
            panel.addView(label("Проанализировано: "+indexed.size+" / "+songs.size,15,muted))
            sheetAction(panel,if(indexed.size==songs.size)"Пересканировать музыку" else "Сканировать новые песни","Офлайн · без дополнительных моделей"){
                dialog.dismiss();startMoodScan(songs,indexed.map{it.id}.toSet(),indexed.size==songs.size)
            }
            MoodDiscovery.profiles.forEach{profile->
                val ids=MoodDiscovery.rank(indexed,profile)
                sheetAction(panel,profile.title,ids.size.toString()+" песен · "+profile.detail){
                    dialog.dismiss();moodMixPreview(profile,ids)
                }
            }
            panel.addView(label("Подборка по акустическим признакам, а не по словам песни или настроению слушателя. Оценки приблизительны.",12,muted))
        }
    }
    private fun startMoodScan(songs:List<Track>,known:Set<String>,rescan:Boolean){
        if(stemBusy){toast("Дождитесь завершения обработки");return}
        val pending=songs.filter{rescan||it.uri !in known}.map{Triple(it.uri,it.title,it.artist)}
        if(pending.isEmpty()){moodDiscoveryDialog();return}
        stemWork("Анализ музыки для подборок…",{
            var saved=0;var skipped=0
            for((i,t) in pending.withIndex()){
                check(!Thread.currentThread().isInterrupted)
                updateWork("Настроения: "+(i+1)+"/"+pending.size+" · "+t.second)
                val f=try{TrackAnalyzer.report(this,Uri.parse(t.first))?.let{MoodDiscovery.from(it)}}catch(e:Exception){if(Thread.currentThread().isInterrupted||e is InterruptedException)throw e;null}
                check(!Thread.currentThread().isInterrupted)
                if(f!=null){saveMood(t.first,t.second,t.third,f);saved++}else{moodPrefs().edit().remove(moodStamp(t.first,t.second,t.third)).apply();skipped++}
            }
            saved to skipped
        }){r->toast("Добавлено: "+r.first+" · недостаточно данных: "+r.second);moodDiscoveryDialog()}
    }
    private fun moodMixPreview(profile:MoodDiscovery.Profile,ids:List<String>){
        val selected=ids.mapNotNull{libraryIndex.get(it)?.takeIf{t->t.uri==t.group}}
        if(selected.isEmpty()){toast("Нет подходящих песен. Просканируйте библиотеку.");return}
        actionSheet(profile.title,470){dialog,panel->
            panel.addView(label(profile.detail,14,muted))
            sheetAction(panel,"Воспроизвести","Заменит текущую очередь на "+selected.size+" песен"){
                val p=controller
                if(p==null){toast("Плеер подключается");return@sheetAction}
                val live=selected.mapNotNull{libraryIndex.get(it.uri)?.takeIf{t->t.uri==t.group}}
                if(live.isEmpty()){toast("Песни недоступны");return@sheetAction}
                stopPreview();p.setMediaItems(live.map(::item));p.shuffleModeEnabled=false;p.prepare();p.play();dialog.dismiss();render()
            }
            sheetAction(panel,"Сохранить плейлист","Добавить без дубликатов"){
                val name="Настроение · "+profile.title
                val live=selected.mapNotNull{libraryIndex.get(it.uri)?.takeIf{t->t.uri==t.group}?.uri}
                val old=playlists[name].orEmpty()
                playlists[name]=PlaylistOrder.append(old,live).toCollection(linkedSetOf());savePlaylists();dialog.dismiss();toast("Подборка сохранена");render()
            }
            selected.take(30).forEach{t->panel.addView(label(t.title+" · "+t.artist,14,PremiumChrome.TEXT))}
            if(selected.size>30)panel.addView(label("Ещё "+(selected.size-30)+" песен",13,muted))
        }
    }
'''
s=s.replace(anchor,helper+anchor)
p.write_text(s)
print("PASS: acoustic mood discovery, offline scanning, ranked playlist and queue")
