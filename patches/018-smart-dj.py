from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
p=src/'TransitionMix.kt';s=p.read_text()
old='        val a=first.length()/4;val b=second.length()/4;val overlap=minOf(seconds*44100L,a/2,b/2);require(overlap>=2){"Слишком короткие файлы"};val length=a+b-overlap'
new='''        return renderFrames(first,second,out,minOf(seconds*44100L,first.length()/8,second.length()/8),progress)
    }
    fun renderFrames(first:File,second:File,out:File,overlap:Long,progress:(Int)->Unit={}):Long {
        require(first.isFile&&second.isFile&&first.length()>0&&second.length()>0&&first.length()%4==0L&&second.length()%4==0L)
        require(out.canonicalFile!=first.canonicalFile&&out.canonicalFile!=second.canonicalFile)
        val a=first.length()/4;val b=second.length()/4;require(overlap in 2..minOf(441000L,a/2,b/2)){"Недопустимая длина наложения"};val length=a+b-overlap'''
assert s.count(old)==1;p.write_text(s.replace(old,new))
p=src/'MainActivity.kt';s=p.read_text();a=s.index('    private fun transitionDialog()');b=s.index('    private fun queueIds(',a)
s=s[:a]+'''    private fun transitionDialog(){
        if(stemBusy){toast("Дождитесь завершения обработки");return}
        val player=controller?:return;val i=player.currentMediaItemIndex
        if(i<0||i+1>=player.mediaItemCount){toast("В очереди нужна следующая композиция");return}
        val a=libraryIndex.get(player.getMediaItemAt(i).mediaId)?:return
        val b=libraryIndex.get(player.getMediaItemAt(i+1).mediaId)?:return
        val durations=listOf(1,3,5,8,10);val panel=column()
        panel.addView(label(a.title+" → "+b.title,17,Color.WHITE,true))
        panel.addView(label("Длительность наложения",14,muted))
        val durationChoice=Spinner(this).apply{adapter=android.widget.ArrayAdapter(this@MainActivity,android.R.layout.simple_spinner_dropdown_item,durations.map{"$it с"});setSelection(2)};panel.addView(durationChoice)
        val smart=CheckBox(this).apply{text="Подогнать BPM и доли";setTextColor(Color.WHITE);isChecked=true};panel.addView(smart)
        val key=CheckBox(this).apply{text="Подогнать тональность (до 2 полутонов)";setTextColor(Color.WHITE)};panel.addView(key)
        smart.setOnCheckedChangeListener{_,checked->key.isEnabled=checked;if(!checked)key.isChecked=false}
        panel.addView(label("Умный режим изменяет темп второй песни не более чем на 8%, если анализ достаточно уверен. Тональность меняется только по вашему выбору. Начало второй песни не вырезается. Оригиналы не изменяются; результат — отдельный WAV, не живой переход.",14,muted))
        val scroll=ScrollView(this);scroll.addView(panel)
        android.app.AlertDialog.Builder(this).setTitle("Создать DJ-переход").setView(scroll).setNegativeButton("Отмена",null).setPositiveButton("Создать"){_,_->
            val seconds=durations[durationChoice.selectedItemPosition.coerceIn(0,durations.lastIndex)];val useSmart=smart.isChecked;val fitKey=key.isChecked
            stemWork("Декодирование для DJ-перехода…",{
                val x=java.io.File.createTempFile("transition-a-",".pcm",cacheDir);val y=java.io.File.createTempFile("transition-b-",".pcm",cacheDir)
                val out=java.io.File.createTempFile("transition-",".wav",java.io.File(filesDir,"mixes").apply{mkdirs()})
                try{StemEngine.decode(this,Uri.parse(a.uri),x);StemEngine.decode(this,Uri.parse(b.uri),y)
                    val notes=if(useSmart)DjTransition.render(x,y,out,seconds,fitKey){updateWork(it)}.notes else {TransitionMix.render(x,y,out,seconds){updateWork("Сведение: $it%")};emptyList()}
                    out to notes
                }catch(e:Throwable){out.delete();throw e}finally{x.delete();y.delete()}
            },discard={it.first.delete()}){result->
                val file=result.first;val uri=batchUri(file);val t=Track(uri,a.title+" → "+b.title,"DJ Mix",uri);tracks.add(t)
                if(saveLibrary(true)){screen="Музыка";toast("DJ-переход сохранён отдельной композицией");if(result.second.isNotEmpty())android.app.AlertDialog.Builder(this).setTitle("Умный DJ-переход").setMessage(result.second.joinToString("\\n")).setPositiveButton("Готово",null).show()}
                else{tracks.remove(t);reindex();file.delete();toast("Не удалось сохранить библиотеку")}
            }
        }.show()
    }
'''+s[b:]
p.write_text(s)
print('PASS: smart DJ entry, opt-in key matching and atomic library save')
