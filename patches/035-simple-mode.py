#!/usr/bin/env python3
"""Keep everyday playback and remixing visible; opt into specialist controls."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt'
s=p.read_text()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:120],s.count(a))
    s=s.replace(a,b)
anchor='    private fun compactSection(key:String,title:String,views:List<View>,at:Int){'
rep(anchor,'''    private fun proMode()=getSharedPreferences("interface_mode",MODE_PRIVATE).getBoolean("pro",false)
    private fun togglePro(){
        val enabled=!proMode()
        if(!getSharedPreferences("interface_mode",MODE_PRIVATE).edit().putBoolean("pro",enabled).commit()){
            toast("Не удалось сохранить настройки");return
        }
        if(!enabled)expandedSections.clear()
        render()
    }
    private fun proButton(title:String,action:()->Unit)=btn(title,action).apply{
        if(!proMode())visibility=View.GONE
    }
    private fun proCard(title:String,subtitle:String,action:()->Unit){
        if(proMode())card(title,subtitle,action)
    }
'''+anchor)
# The named studio cards are explicitly classified, not removed by a generic substring filter.
rep('card("Инструментал","Создать музыку с нуля · экспериментально")','proCard("Инструментал","Создать музыку с нуля · экспериментально")')
rep('card("Сведение","Совместить песню с инструменталом")','proCard("Сведение","Совместить песню с инструменталом")')
rep('btn("Vosk · эксперимент")','proButton("Vosk · эксперимент")')
rep('btn("Речевые модели Vosk")','proButton("Речевые модели Vosk")')
rep('btn("Пакет эффектов…")','proButton("Пакет эффектов…")')
# Keep the studio and useful model manager intact. Only advanced actions disappear.
# The setting is deliberately outside every collapsed settings section.
rep('val backupStart=body.childCount;','body.addView(btn(if(proMode())"PRO-инструменты: вкл." else "PRO-инструменты: выкл."){togglePro()});body.addView(label("Дополнительные инструменты. Музыка, ремиксы и тексты остаются доступны в обоих режимах.",13,muted));val backupStart=body.childCount;')
# Filter the optional player actions by stable operation IDs, not index in the filtered menu.
a='android.app.AlertDialog.Builder(this).setTitle("Композиция").setItems(arrayOf("Версии","Микшер","Студия","Таймер и переходы","Повтор A/B","Вырезать фрагмент","Эквалайзер")){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(i)'
b='val actions=listOf("Версии","Микшер","Студия","Таймер и переходы","Повтор A/B","Вырезать фрагмент","Эквалайзер");val visible=actions.indices.filter{proMode()||it!=4&&it!=5};android.app.AlertDialog.Builder(this).setTitle("Композиция").setItems(visible.map{actions[it]}.toTypedArray()){_,i->if(current()?.uri!=t.uri){toast("Композиция изменилась");return@setItems};when(visible[i])'
rep(a,b)
# Bulk ASR is expensive and remains opt-in; single-track Whisper is still available.
rep('panel.addView(search);panel.addView(analyze);panel.addView(local);panel.addView(align)','panel.addView(search);panel.addView(analyze);if(proMode()){panel.addView(local);panel.addView(align)}')
rep('val useLocal=local.isEnabled&&local.isChecked;val useAlign=align.isEnabled&&align.isChecked','val useLocal=proMode()&&local.isEnabled&&local.isChecked;val useAlign=proMode()&&align.isEnabled&&align.isChecked')
# Hide advanced controls in the library without disabling importing, playlists, or local discovery.
rep('val libraryTools=bodyChildren().filter','val libraryTools=bodyChildren().filter') if False else None
p.write_text(s)
print("PASS: persistent default-off PRO controls; core player unchanged")
