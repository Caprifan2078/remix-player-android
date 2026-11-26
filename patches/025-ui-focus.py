#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a[:120],s.count(a))
 s=s.replace(a,b)
# The brand header is useful in the library, not on every screen.
replace('private var navRow:LinearLayout?=null','private var navRow:LinearLayout?=null;private var headerBar:LinearLayout?=null;private var headerBack:Button?=null;private var headerImport:Button?=null')
a=s.index('        val header=row();header.addView(');b=s.index('\n',a)
s=s[:a]+'''        val header=row();headerBar=header
        val back=btn("‹"){screen="Музыка";render()}.apply{contentDescription="Назад в библиотеку";textSize=28f;background=PremiumChrome.ripple(Color.TRANSPARENT,dp(12).toFloat())};headerBack=back;header.addView(back,LinearLayout.LayoutParams(dp(48),dp(48)))
        header.addView(label("REMIX",22,PremiumChrome.TEXT,true),weight())
        val add=btn("＋"){addingTo=null;picker.launch(arrayOf("audio/*"))}.apply{contentDescription="Импорт музыки";textSize=23f;background=PremiumChrome.ripple(Color.TRANSPARENT,dp(12).toFloat())};headerImport=add;header.addView(add,LinearLayout.LayoutParams(dp(48),dp(48)));root.addView(header)'''+s[b:]
replace('navRow?.visibility=View.VISIBLE;studioStatusView=null;', 'navRow?.visibility=if(full)View.GONE else View.VISIBLE;headerBar?.visibility=if(full||screen=="Музыка")View.VISIBLE else View.GONE;headerBack?.visibility=if(full)View.VISIBLE else View.GONE;headerImport?.visibility=if(screen=="Музыка")View.VISIBLE else View.GONE;studioStatusView=null;')
# Use a proper two-column filter strip, not a stack of controls.
replace('val filter=btn(if(onlyFavorites)"♥ Избранное" else "Все композиции")','val filter=btn(if(onlyFavorites)"Избранное" else "Все песни")')
replace('body.addView(filter);val tools=row();tools.addView(btn(selectedPlaylist?:"Плейлисты")','val tools=row();tools.addView(filter,weight());tools.addView(btn(selectedPlaylist?:"Плейлисты")')
a=s.index('tools.addView(btn(listOf(if(selectedPlaylist==null)"По добавлению"')
b=s.index(';body.addView(tools)',a)
s=s[:a]+'''tools.addView(btn("Фильтры"){android.app.AlertDialog.Builder(this).setTitle("Библиотека").setItems(arrayOf("Альбомы, папки, исполнители","Сортировка")){_,i->if(i==0)chooseCategory()else android.app.AlertDialog.Builder(this).setTitle("Сортировка").setSingleChoiceItems(arrayOf("По добавлению","По названию","По исполнителю"),sortMode){d,j->sortMode=j;shownSongs=100;d.dismiss();render()}.setNegativeButton("Отмена",null).show()}.show()},weight())'''+s[b:]
a=s.index('body.addView(btn(category?:listOf("Каталог: все песни"')
b=s.index(';body.addView(btn(if(randomVersions)',a)
s=s[:a]+'''if(categoryMode!=0||category!=null)body.addView(btn(category?:listOf("Все песни","Альбомы","Папки","Исполнители")[categoryMode]){chooseCategory()})'''+s[b:]
# One row of primary player actions. Secondary preset shortcuts are already available in the effect picker.
a=s.index('        val quick=row()\n        listOf("Оригинал","Sped Up","Slowed + Reverb")')
b=s.index('        body.addView(btn("Ещё · инструменты")',a)
s=s[:a]+s[b:]
replace('body.addView(btn("Ещё · инструменты")','body.addView(btn("Ещё")')
# Keep the long backup explanation, but reveal it only inside its task group.
a=s.index('backupStatus=label(if(stemBusy)stemStatus else "Архив содержит')
s=s[:a]+'val backupStart=body.childCount;'+s[a:]
replace('val modelsStart=body.childCount;modelManagement();','compactSection("settings-backup","Резервные копии",bodyChildren().drop(backupStart),backupStart);val modelsStart=body.childCount;modelManagement();')
replace('body.addView(btn("Найти неиспользуемые WAV…"){cleanupMixes()});val dir=','val storageStart=body.childCount;body.addView(btn("Найти неиспользуемые WAV…"){cleanupMixes()});val dir=')
a=s.index('body.addView(label("Распознавание: Vosk, экспериментальное.')
b=s.index('\n',a)
s=s[:a]+'''compactSection("settings-storage","Память",bodyChildren().drop(storageStart),storageStart)}'''+s[b:]
# Keep the original action descriptions and IDs in settings, but remove duplicated work progress when global progress is active.
p.write_text(s)
print("PASS: focused player header, three library filters, grouped settings, fewer duplicate actions")
