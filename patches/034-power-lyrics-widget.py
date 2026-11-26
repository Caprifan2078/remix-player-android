from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player';res=root/'app/src/main/res';patch=Path(__file__).parent
def replace(p,old,new):
    s=p.read_text();assert s.count(old)==1,(p.name,old,s.count(old));p.write_text(s.replace(old,new))
for name in ['PlaybackCadence.kt','Mp3Lyrics.kt','PulseWidget.kt']:shutil.copyfile(patch/name,src/name)
for name,folder in [('pulse_widget.xml','layout'),('pulse_widget_info.xml','xml'),('pulse_widget_bg.xml','drawable')]:
    (res/folder).mkdir(exist_ok=True);shutil.copyfile(patch/name,res/folder/name)
p=root/'app/src/main/AndroidManifest.xml'
replace(p,'    </application>','''        <receiver android:name=".PulseWidget" android:exported="false" android:label="Pulse">
            <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/></intent-filter>
            <meta-data android:name="android.appwidget.provider" android:resource="@xml/pulse_widget_info"/>
        </receiver>
    </application>''')
p=src/'AudioCore.kt'
replace(p,'Preset("Fast Stereo Orbit",1.2f,1.05f,pan=.95f,room=.15f))','''Preset("Fast Stereo Orbit",1.2f,1.05f,pan=.95f,room=.15f),
        Preset("Sped Up + Bass",1.25f,1f,bass=.40f),
        Preset("Nightcore + Bass",1.35f,1.35f,bass=.25f),
        Preset("Slowed + Bass",.80f,.80f,bass=.50f))''')
p=root/'tests/CoreTest.kt'
replace(p,'check(Presets.all.size==41)','check(Presets.all.size==44)')
replace(p,'41 presets','44 presets')
p=src/'PlaybackService.kt'
replace(p,'dsp=Dsp(inputAudioFormat.sampleRate,a.size);lastPreset=null','dsp=null;lastPreset=null')
replace(p,'        if(lastPreset!==p){lastPreset=p;dsp=if(a.isNotEmpty())Dsp(inputAudioFormat.sampleRate,a.size) else null}','''        val needsDsp=p.bass!=0f||p.room!=0f||p.pan!=0f||p.drive!=0f||p.muffled!=0f
        if(lastPreset!==p){lastPreset=p;dsp=if(needsDsp&&a.isNotEmpty())Dsp(inputAudioFormat.sampleRate,a.size) else null}''')
replace(p,'if((p==Presets.all.first() && levels.all{it==0f}) || d==null || a.isEmpty() || inputBuffer.remaining()%(a.size*2)!=0)','if((!needsDsp&&frameEq==null)||(needsDsp&&d==null)||a.isEmpty()||inputBuffer.remaining()%(a.size*2)!=0)')
replace(p,'d.frame(a,b,p); frameEq?.frame(b);','if(d!=null)d.frame(a,b,p)else a.copyInto(b); frameEq?.frame(b);')
replace(p,'handler.postDelayed(this,if(PlaybackOptions.overlapMs>0&&p.playWhenReady)25 else if((PlaybackOptions.fadeMs>0||RepeatRegion.active!=null)&&p.isPlaying)50 else 500)','''handler.removeCallbacks(this)
        val sleep=PlaybackOptions.sleepDeadline.takeIf{it>0}?.let{it-now}
        handler.postDelayed(this,PlaybackCadence.delay(p.isPlaying||(p.playWhenReady&&PlaybackOptions.overlapMs>0),p.currentPosition,p.duration,PlaybackOptions.fadeMs,PlaybackOptions.overlapMs,RepeatRegion.active!=null,sleep,mixing))''')
replace(p,'val checkpoint=object:Runnable{override fun run(){bookmark();historyTick();handler.postDelayed(this,5000)}}','val checkpoint=object:Runnable{override fun run(){if(session?.player?.isPlaying==true){bookmark();historyTick();handler.postDelayed(this,5000)}}}')
replace(p,'{bookmark();historyTick()}}})','{bookmark();historyTick();handler.removeCallbacks(checkpoint);if(player.isPlaying)handler.postDelayed(checkpoint,5000);handler.removeCallbacks(playbackClock);handler.post(playbackClock)}}})')
replace(p,'handler.postDelayed(checkpoint,5000);handler.post(playbackClock)','PulseWidget.attach(this,player);handler.postDelayed(checkpoint,5000);handler.post(playbackClock)')
replace(p,'override fun onDestroy() { handler.removeCallbacks(checkpoint);','override fun onDestroy() { PulseWidget.detach(this);handler.removeCallbacks(checkpoint);')
p=root/'app/src/androidTest/java/app/remix/player/PlaybackInstrumentedTest.kt'
replace(p,'if(preset==Presets.all.first())assertArrayEquals("Original PCM changed",original,bytes)','if(preset.bass==0f&&preset.room==0f&&preset.pan==0f&&preset.drive==0f&&preset.muffled==0f)assertArrayEquals("Unprocessed PCM changed",original,bytes)')
p=src/'MainActivity.kt'
replace(p,'    private fun editLyrics(t:Track){',r'''    private data class TaggedMp3Request(val uri:String,val raw:String)
    private var taggedMp3Request:TaggedMp3Request?=null
    private val taggedMp3Picker=registerForActivityResult(ActivityResultContracts.CreateDocument("audio/mpeg")){dest->
        val request=taggedMp3Request;taggedMp3Request=null
        if(dest!=null&&request!=null&&!stemBusy&&dest.toString()!=request.uri){
            stemWork("Запись текста без перекодирования…",{
                val temp=java.io.File.createTempFile("tagged-lyrics-",".mp3",cacheDir)
                try{
                    val plain=Lrc.parse(request.raw).map{WordLyrics.parse(it).text}.joinToString("\n").ifBlank{request.raw}
                    contentResolver.openInputStream(Uri.parse(request.uri))?.buffered()?.use{r->temp.outputStream().buffered().use{w->Mp3Lyrics.write(r,w,plain,request.raw)}}?:error("MP3 недоступен")
                    check(!Thread.currentThread().isInterrupted)
                    contentResolver.openOutputStream(dest,"w")?.use{w->temp.inputStream().use{r->AudioFileCore.copy(r,w)}}?:error("Файл недоступен")
                }catch(e:Throwable){runCatching{contentResolver.delete(dest,null,null)};throw e}finally{temp.delete()}
            }){toast("Копия MP3 с текстом сохранена. Оригинал не изменён.")}
        }else if(dest!=null)toast("Экспорт отменён: источник изменился или занята обработка")
    }
    private fun tagMp3(t:Track,raw:String){
        if(stemBusy||raw.isBlank())return
        android.app.AlertDialog.Builder(this).setTitle("MP3 с текстом").setMessage("Сохранить отдельную копию MP3 с обычным текстом и LRC? Аудиоданные не перекодируются. Поддерживаются обычные ID3v2.3/2.4; исходный файл не меняется.").setNegativeButton("Отмена",null).setPositiveButton("Сохранить копию"){_,_->
            taggedMp3Request=TaggedMp3Request(t.uri,raw)
            taggedMp3Picker.launch(t.title.take(80).replace(Regex("[^\\p{L}\\p{N} ._-]"),"_")+".mp3")
        }.show()
    }
    private val autoLyricAttempted=linkedSetOf<String>()
    private fun autoLyricsEnabled()=getSharedPreferences("play_options",MODE_PRIVATE).getBoolean("auto_lyrics",false)
    private fun toggleAutoLyrics(){
        if(autoLyricsEnabled()){getSharedPreferences("play_options",MODE_PRIVATE).edit().putBoolean("auto_lyrics",false).apply();render();return}
        android.app.AlertDialog.Builder(this).setTitle("Автопоиск текста").setMessage("При открытии текста пустой песни Pulse один раз запросит LRCLIB по названию, исполнителю и длительности. Аудио не отправляется. В фоне поиск и Whisper не запускаются.").setNegativeButton("Отмена",null).setPositiveButton("Включить"){_,_->getSharedPreferences("play_options",MODE_PRIVATE).edit().putBoolean("auto_lyrics",true).apply();autoLyricAttempted.clear();render()}.show()
    }
    private fun maybeAutoLyrics(t:Track){
        if(!autoLyricsEnabled()||lyricsBusy||stemBusy||!uiStarted||rawLyrics(t).isNotBlank()||!autoLyricAttempted.add(t.uri))return
        if(autoLyricAttempted.size>128)autoLyricAttempted.remove(autoLyricAttempted.first())
        val original=libraryIndex.get(t.group)?:t;val revision=lyricRevision(t);val sourceBefore=original.lyrics
        val seconds=if(MixerSession.active)MixerSession.request?.frames?.div(44100L) else controller?.duration?.takeIf{it>0}?.let{(it*(t.tempoRatio?:1.0)/1000).toLong()}
        val title=original.title;val artist=original.artist;val sourceId=original.uri;val targetId=t.uri;val ratio=t.tempoRatio
        lyricsBusy=true
        io.execute{val result=runCatching{LyricsLookup.fetch(title,artist,seconds)}
            runOnUiThread{if(!isDestroyed){
                lyricsBusy=false;val raw=result.getOrNull();val target=libraryIndex.get(targetId)
                if(autoLyricsEnabled()&&raw!=null&&target!=null&&lyricRevision(target)==revision&&rawLyrics(target).isBlank()){
                    target.lyrics=if(ratio!=null)TimeStretch.lyrics(raw,ratio)else raw
                    val origin=libraryIndex.get(sourceId);if(origin!=null&&origin.uri!=target.uri&&origin.lyrics==sourceBefore&&origin.lyrics.isBlank())origin.lyrics=raw
                    save()
                }
                if(screen=="Текст")render()
            }}
        }
    }
    private fun editLyrics(t:Track){''')
replace(p,'});val raw=rawLyrics(t);body.addView(btn("Редактировать текст / LRC"){editLyrics(t)});','''});maybeAutoLyrics(t);val raw=rawLyrics(t);body.addView(btn("Автопоиск текста: "+if(autoLyricsEnabled())"вкл." else "выкл."){toggleAutoLyrics()});body.addView(btn("Редактировать текст / LRC"){editLyrics(t)});if(raw.isNotBlank()&&!stemBusy)body.addView(btn("Сохранить MP3 с текстом…"){tagMp3(t,raw)});''')
print('PASS: adaptive playback cadence, exact DSP bypass, three presets, opt-in lyrics lookup, MP3 tag copy and event-driven home widget')
