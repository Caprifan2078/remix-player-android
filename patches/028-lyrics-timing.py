#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b)
rep('Track(uri.toString(),title,artist,target?:uri.toString(),album=album,folder=', 'Track(uri.toString(),title,artist,target?:uri.toString(),lyrics=TrackLyricSource.embedded(this,uri).orEmpty(),album=album,folder=')
rep('val result=runCatching{LyricsLookup.search(searchTitleValue,searchArtistValue,seconds)}','val result=runCatching{TrackLyricSource.search(this,Uri.parse(original.uri),searchTitleValue,searchArtistValue,seconds)}')
rep('result.onSuccess{matches->','result.onSuccess{(matches,sourceSeconds)->')
rep('LyricsSearchPlan.isComposite(searchTitleValue)||(seconds!=null&&m.duration!=null&&kotlin.math.abs(seconds-m.duration)>3)','m.id!=-1L&&(LyricsSearchPlan.isComposite(searchTitleValue)||(sourceSeconds!=null&&m.duration!=null&&kotlin.math.abs(sourceSeconds-m.duration)>3))')
rep('if(seconds!=null){BatchLyricPolicy.choose(LyricsLookup.search(t.title,t.artist,seconds,false),t.title,t.artist,seconds)?.let{found[t.uri]=it}}','val embedded=TrackLyricSource.embedded(this,Uri.parse(t.uri));if(embedded!=null)found[t.uri]=embedded else if(seconds!=null){val info=TrackLyricSource.metadata(this,Uri.parse(t.uri),t.title,t.artist,seconds);BatchLyricPolicy.choose(LyricsLookup.search(info.title,info.artist,info.seconds,false),info.title,info.artist,info.seconds)?.let{found[t.uri]=it}}')
rep('body.addView(btn("Подстроить синхронизацию ±…"){shiftLyricsDialog(t,raw)})','body.addView(btn("Настроить синхронизацию"){calibrateLyrics(t,raw)})')
a=s.index('    private fun shiftLyricsDialog(')
helper='''    private fun calibrateLyrics(t:Track,raw:String){
        val lines=Lrc.parse(raw);if(lines.isEmpty())return
        val revision=lyricRevision(t);val id=t.uri
        var first:LyricClock.Anchor?=null;var second:LyricClock.Anchor?=null
        actionSheet("Синхронизация",420){dialog,panel->
            panel.addView(label("Выберите строку и отметьте момент, когда услышите её. Вторая точка исправляет постепенный уход текста.",14,muted))
            val choices=lines.map{fmt(it.ms)+" · "+WordLyrics.parse(it).text.take(70)}
            val spinner=Spinner(this).apply{adapter=android.widget.ArrayAdapter(this@MainActivity,android.R.layout.simple_spinner_dropdown_item,choices)}
            panel.addView(spinner,LinearLayout.LayoutParams(-1,dp(52)))
            val state=label("Нет отметок",14,muted);panel.addView(state)
            fun position():Long?=if(MixerSession.active){if(MixerSession.request?.source==id)MixerSession.position()*1000/44100 else null}else controller?.takeIf{it.currentMediaItem?.mediaId==id}?.currentPosition
            val buttons=row();buttons.addView(btn("▶ / Ⅱ"){if(position()!=null)play.performClick()},weight());buttons.addView(btn("К строке"){if(position()!=null)seekLyrics(lines[spinner.selectedItemPosition].ms)},weight());panel.addView(buttons)
            panel.addView(btn("Отметить услышанную строку"){
                val pos=position();if(pos==null){toast("Включите эту песню");return@btn}
                val anchor=LyricClock.Anchor(lines[spinner.selectedItemPosition].ms,pos)
                if(first==null||second!=null){first=anchor;second=null;state.text="Первая точка: "+fmt(pos)}else{
                    runCatching{LyricClock.mapping(requireNotNull(first),anchor)}.onSuccess{second=anchor;state.text="Две точки · коррекция темпа и сдвига"}.onFailure{toast(it.message?:"Выберите более позднюю строку")}
                }
            })
            panel.addView(btn("Применить"){
                val f=first;if(f==null){toast("Добавьте хотя бы одну отметку");return@btn}
                runCatching{val target=libraryIndex.get(id)?:error("Песня удалена");require(lyricRevision(target)==revision){"Текст изменился"};val corrected=LyricClock.correct(raw,LyricClock.mapping(f,second));val previous=target.lyrics;target.lyrics=corrected;if(!saveLibrary(true)){target.lyrics=previous;reindex();error("Не удалось сохранить синхронизацию")};dialog.dismiss();render()}.onFailure{toast(it.message?:"Ошибка синхронизации")}
            })
            sheetAction(panel,"Точный сдвиг ±","Настройка в миллисекундах"){dialog.dismiss();shiftLyricsDialog(t,raw)}
        }
    }
'''
s=s[:a]+helper+s[a:]
p.write_text(s)
p=src/'WhisperSegments.kt';s=p.read_text()
old='"[${SubtitleCore.stamp(seg.startMs)}]$text"'
assert s.count(old)==1
s=s.replace(old,'"[${SubtitleCore.stamp(if(valid)seg.wordStarts.first() else seg.startMs)}]$text"')
p.write_text(s)
print("PASS: embedded ID3/FLAC lyrics, source metadata, two-anchor calibration, actual word onset")
