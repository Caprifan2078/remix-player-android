#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player'
def edit(path,a,b):
 s=path.read_text();assert s.count(a)==1,(path.name,a[:100],s.count(a));path.write_text(s.replace(a,b))
p=src/'LiveOverlap.kt'
# A user seek / pause must cancel the current attempt, but must not blacklist the entire song.
edit(p,'if(preview!=null)abort(true)\n        }','if(preview!=null)abort(false)\n            rejectedId=null\n        }')
edit(p,'override fun onPlayWhenReadyChanged(playWhenReady:Boolean,reason:Int){if(!playWhenReady)abort(true)}','override fun onPlayWhenReadyChanged(playWhenReady:Boolean,reason:Int){if(!playWhenReady)abort(false);rejectedId=null}')
edit(p,'override fun onTimelineChanged(timeline:androidx.media3.common.Timeline,reason:Int){if(preview!=null&&!queueMatches())abort(true)}','override fun onTimelineChanged(timeline:androidx.media3.common.Timeline,reason:Int){if(preview!=null&&!queueMatches()){abort(false);rejectedId=null}}')
# Do not retain queued audio analysis when a next item disappears.
edit(p,'if(!main.isPlaying||duration<=0||next==C.INDEX_UNSET||next==main.currentMediaItemIndex||rejectedId==id){if(preview!=null)abort(true);return false}','if(!main.isPlaying||duration<=0||next==C.INDEX_UNSET||next==main.currentMediaItemIndex||rejectedId==id){if(preview!=null)abort(true);if(next==C.INDEX_UNSET||next==main.currentMediaItemIndex)clearAnalysis();return false}')
# A frozen fade window must not be shortened again by a newly arrived analysis result.
edit(p,'val planned=OverlapCore.window(duration,p.duration,adaptive?.duration?:requested)?:run{abort(true);return false}','val planned=fadeWindow?:OverlapCore.window(duration,p.duration,adaptive?.duration?:requested)?:run{abort(true);return false}')
# Isolate the deterministic fixed-overlap acceptance case from the adaptive default.
p=root/'app/src/androidTest/java/app/remix/player/PlaybackInstrumentedTest.kt'
edit(p,'main{PlaybackOptions.overlapMs=0;PlaybackOptions.fadeMs=0;p.setMediaItems(items,0,0);','main{PlaybackOptions.autoOverlap=false;PlaybackOptions.overlapMs=0;PlaybackOptions.fadeMs=0;p.setMediaItems(items,0,0);')
edit(p,'main{PlaybackOptions.overlapMs=0;RepeatRegion.active=null;controller?.let','main{PlaybackOptions.autoOverlap=true;PlaybackOptions.overlapMs=0;RepeatRegion.active=null;controller?.let')
# Preserve the test's incoming-position assertion. Exercise seek/cancel/retry with the same song.
edit(p,'PlaybackOptions.overlapMs=3000;p.setMediaItems(items,0,6500);p.prepare();p.play()}\n            await("Live overlap did not hand off','PlaybackOptions.overlapMs=3000;p.setMediaItems(items,0,6500);p.prepare();p.play()}\n            await("First overlap attempt never reached its window"){p.isPlaying&&p.currentMediaItem?.mediaId==items[0].mediaId&&p.currentPosition in 9300L..11300L}\n            main{p.pause();p.seekTo(6500)};await("Pause after overlap did not reset source"){!p.isPlaying&&p.currentPosition in 6400L..6600L}\n            main{p.play()}\n            await("Live overlap did not hand off')
# One optional local alignment action, using the existing full-word and phrase matching engines.
p=src/'MainActivity.kt';s=p.read_text()
anchor='    private fun calibrateLyrics(t:Track,raw:String){'
assert s.count(anchor)==1
helper='''    private fun alignKnownLyrics(t:Track,raw:String){
        if(stemBusy)return
        if(!WhisperLocal.available||WhisperLocal.installed(this)==null){whisperModelDialog();return}
        val reference=LyricDocument.plain(raw)
        if(reference.isBlank()){toast("Сначала добавьте правильный текст");return}
        val id=t.uri;val revision=lyricRevision(t)
        val stem=getSharedPreferences("stem_cache",MODE_PRIVATE).getString(id,null)?.let{StemEngine.load(this,it)}
        actionSheet("Уточнить по вокалу",245){dialog,panel->
            panel.addView(label("Слова останутся прежними. Whisper определит их время на текущем аудиофайле. При неоднозначном результате ничего не изменится.",14,muted))
            sheetAction(panel,"Начать","Локально · "+if(stem==null)"исходная песня" else "выделенный вокал"){
                dialog.dismiss()
                stemWork("Синхронизация по вокалу…",{
                    val heard=WhisperLocal.transcribe(this,Uri.parse(id),stem,"auto"){updateWork(it)}
                    KnownLyricAlignment.align(heard,reference)
                }){result->
                    if(result==null){toast("Надёжных совпадений недостаточно. Исходный текст сохранён.")}
                    else actionSheet("Синхронизация готова",245){confirm,content->
                        content.addView(label(if(result.wordLevel)"Совпали все слова. Можно применить новые метки слов." else "Совпали все строки. Доступны метки фраз, без выдуманных времён слов.",14,muted))
                        sheetAction(content,"Применить","Сохранить правильный текст с новыми метками"){
                            val target=libraryIndex.get(id)
                            if(target==null||lyricRevision(target)!=revision){toast("Текст или версия изменились");confirm.dismiss();return@sheetAction}
                            val before=target.lyrics;target.lyrics=result.lrc
                            if(!saveLibrary(true)){target.lyrics=before;reindex();toast("Не удалось сохранить текст")}
                            else{confirm.dismiss();render();toast("Синхронизация сохранена")}
                        }
                    }
                }
            }
        }
    }
'''
s=s.replace(anchor,helper+anchor)
a='val raw=rawLyrics(t);body.addView(btn("Редактировать текст / LRC")'
assert s.count(a)==1
s=s.replace(a,'val raw=rawLyrics(t);if(raw.isNotBlank()&&!stemBusy)body.addView(btn("Уточнить по вокалу"){alignKnownLyrics(t,raw)});body.addView(btn("Редактировать текст / LRC")')
p.write_text(s)
print("PASS: cancel/retry overlap without permanent rejection; optional ASR-guided known lyric alignment")
