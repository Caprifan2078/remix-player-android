from pathlib import Path
import sys
root=Path(sys.argv[1]); p=root/'app/src/main/java/app/remix/player/MainActivity.kt'; s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:140],s.count(a))
    s=s.replace(a,b)
def section(a,b,new):
    global s
    start=s.index(a);end=s.index(b,start)
    s=s[:start]+new+s[end:]
# Vector icons instead of full-width text buttons; 48dp touch targets remain.
icons={
'heart':'M12,21 L3.7,12.9 C-1,8.2 5.5,1.3 12,7 C18.5,1.3 25,8.2 20.3,12.9 Z',
'heart_on':'M12,21 L3.7,12.9 C-1,8.2 5.5,1.3 12,7 C18.5,1.3 25,8.2 20.3,12.9 Z',
'queue':'M3,5 H21 M3,10 H21 M3,15 H15 M3,20 H12 M18,14 L22,18 L18,22 Z',
'versions':'M3,12 H5 M7,8 V16 M11,4 V20 M15,9 V15 M19,6 V18 M22,12 H23',
'menu':'M4,6 H20 M4,12 H20 M4,18 H20',
'close':'M6,6 L18,18 M18,6 L6,18',
'more':'M12,4 A1.5,1.5 0,1 0,12 7 A1.5,1.5 0,1 0,12 4 M12,10.5 A1.5,1.5 0,1 0,12 13.5 A1.5,1.5 0,1 0,12 10.5 M12,17 A1.5,1.5 0,1 0,12 20 A1.5,1.5 0,1 0,12 17',
'lyrics':'M4,4 H20 V17 H10 L5,21 V17 H4 Z M8,8 H16 M8,12 H14',
'back':'M4,12 H21 M4,12 L11,5 M4,12 L11,19',
'plus':'M12,4 V20 M4,12 H20',
'settings':'M4,6 H20 M4,12 H20 M4,18 H20 M8,3 V9 M16,9 V15 M10,15 V21',
'music':'M10,18 V5 L21,3 V15 M10,18 C10,21 4,22 3,19 C2,16 7,14 10,16 M21,15 C21,18 15,19 14,16 C13,13 18,11 21,13',
'effects':'M4,4 V20 M12,4 V20 M20,4 V20 M1,8 H7 M9,15 H15 M17,10 H23',
'next':'M5,4 L17,12 L5,20 Z M20,4 V20',
'filter':'M3,5 H21 M6,12 H18 M9,19 H15',
}
draw=root/'app/src/main/res/drawable';draw.mkdir(parents=True,exist_ok=True)
for name,path in icons.items():
    filled=name in ('heart_on','more','next')
    fill='#FFFFFFFF' if filled else '#00000000'
    (draw/('remix_'+name+'.xml')).write_text(f'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24"><path android:fillColor="{fill}" android:strokeColor="#FFFFFFFF" android:strokeWidth="1.6" android:strokeLineCap="round" android:strokeLineJoin="round" android:pathData="{path}"/></vector>')
replace('    private fun toast(s:String)',r'''    private fun iconButton(res:Int,description:String,action:()->Unit)=android.widget.ImageButton(this).apply{
        contentDescription=description;setImageResource(res);setColorFilter(accent);scaleType=ImageView.ScaleType.CENTER
        layoutParams=LinearLayout.LayoutParams(dp(48),dp(48));minimumWidth=dp(48);minimumHeight=dp(48)
        background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x25FFFFFF),null,rounded(Color.WHITE,24))
        setOnClickListener{action()}
    }
    private fun sheet(title:String,subtitle:String="",actions:List<Pair<String,()->Unit>>){
        val dialog=android.app.Dialog(this)
        val panel=column().apply{setPadding(dp(18),dp(14),dp(18),dp(18));background=rounded(surface,24)}
        val top=row();top.addView(label(title,20,Color.WHITE,true),weight());top.addView(iconButton(R.drawable.remix_close,"Закрыть меню"){dialog.dismiss()});panel.addView(top)
        if(subtitle.isNotBlank())panel.addView(label(subtitle,14,muted))
        val items=column()
        actions.forEach{(name,action)->val item=label(name,16,Color.WHITE).apply{
            minimumHeight=dp(48);gravity=Gravity.CENTER_VERTICAL;isClickable=true;isFocusable=true
            background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22FFFFFF),null,rounded(Color.WHITE,12))
            setOnClickListener{dialog.dismiss();action()}
        };items.addView(item)}
        val scroll=ScrollView(this);scroll.addView(items);panel.addView(scroll,LinearLayout.LayoutParams(-1,dp(minOf(actions.size*51,resources.configuration.screenHeightDp/2))))
        dialog.setContentView(panel);dialog.setCanceledOnTouchOutside(true);dialog.window?.apply{
            setBackgroundDrawableResource(android.R.color.transparent);setGravity(Gravity.BOTTOM)
        };dialog.show();dialog.window?.setLayout(-1,-2)
    }
    private fun toast(s:String)''')
# Compact header and mini-player distinct from expanded playback.
replace('val header=row();header.addView(label("REMIX",26,accent,true),weight());header.addView(btn("Настройки"){screen="Настройки";render()});header.addView(btn("＋ Импорт"){addingTo=null;picker.launch(arrayOf("audio/*"))});root.addView(header)',
'''val header=row();mainHeader=header;header.addView(label("REMIX",22,accent,true),weight());header.addView(iconButton(R.drawable.remix_settings,"Настройки"){screen="Настройки";render()});header.addView(iconButton(R.drawable.remix_plus,"Импорт"){addingTo=null;picker.launch(arrayOf("audio/*"))});root.addView(header)''')
replace('val nav=row();listOf("Музыка"','val nav=row();mainNav=nav;listOf("Музыка"')
replace('bar.addView(now);now.minimumHeight=dp(48);', '''compactTransport=row();now.maxLines=1;now.ellipsize=android.text.TextUtils.TruncateAt.END;compactTransport.addView(now,weight());bar.addView(compactTransport);now.minimumHeight=dp(48);''')
replace('bar.addView(seek)','bar.addView(seek,LinearLayout.LayoutParams(-1,dp(48)))')
replace('bar.addView(controls);root.addView(nav)', '''transportControls=controls;bar.addView(controls);root.addView(nav)
        compactPlay=btn("▶"){play.performClick()}.apply{layoutParams=LinearLayout.LayoutParams(dp(48),dp(48));textSize=22f;background=rounded(Color.TRANSPARENT,24)}
        compactTransport.addView(compactPlay);compactTransport.addView(iconButton(R.drawable.remix_next,"Следующая композиция"){stopPreview();controller?.seekToNext()})
        for(i in 0 until controls.childCount){(controls.getChildAt(i) as? Button)?.apply{
            textSize=if(this===play)26f else 20f
            background=android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22FFFFFF),rounded(if(this===play)accent else Color.TRANSPARENT,30),rounded(Color.WHITE,30))
            if(this===play){setTextColor(bg);layoutParams=LinearLayout.LayoutParams(dp(60),dp(60));background=rounded(accent,30)}
        }}''')
replace('    private fun nowPlaying(){',r'''    private var transportMode=-1
    private lateinit var mainHeader:LinearLayout
    private lateinit var mainNav:LinearLayout
    private lateinit var compactTransport:LinearLayout
    private lateinit var compactPlay:Button
    private lateinit var transportControls:LinearLayout
    private fun updateTransportLayout(){
        if(!::transportControls.isInitialized)return
        val player=screen=="Плеер";val full=player||screen=="Текст"
        val hasTrack=current()!=null||MixerSession.active
        mainHeader.visibility=if(player)View.GONE else View.VISIBLE
        mainNav.visibility=if(player)View.GONE else View.VISIBLE
        if(screen!="Микшер")bar.visibility=if(hasTrack)View.VISIBLE else View.GONE
        val mode=if(full)1 else 0
        if(mode!=transportMode){transportMode=mode;bar.background=if(full)rounded(Color.TRANSPARENT,0) else rounded(surface,16);bar.setPadding(dp(if(full)4 else 10),dp(2),dp(if(full)4 else 10),dp(4))}
        compactTransport.visibility=if(full)View.GONE else View.VISIBLE
        seek.visibility=if(full)View.VISIBLE else View.GONE
        time.visibility=if(full)View.VISIBLE else View.GONE
        transportControls.visibility=if(full)View.VISIBLE else View.GONE
        quickEffectsRow.visibility=View.GONE
        if(compactPlay.text!=play.text)compactPlay.text=play.text
        compactPlay.contentDescription=if(play.text.toString()=="▶")"Воспроизвести" else "Пауза"
    }
    private fun quickPresetSheet(){
        val names=listOf("Оригинал","Sped Up","Sped Up + Reverb","Nightcore","Nightcore Reverb","Slowed + Reverb")
        val choices=names.mapNotNull{name->Presets.all.firstOrNull{it.name==name}?.let{preset->
            (if(preset==Presets.active)"✓ "+name else name) to {if(current()!=null&&!MixerSession.active){applyPreset(preset);render()};Unit}
        }}
        sheet("Эффекты",actions=choices+listOf("Все эффекты" to {allEffectsSheet()}))
    }
    private fun allEffectsSheet(){
        val entries=(Presets.all+customPresets).distinctBy{it.name}
        val actions=entries.map{preset->(if(preset==Presets.active)"✓ " else "")+preset.name+" · "+preset.speed+"×" to {if(current()!=null&&!MixerSession.active){applyPreset(preset);render()};Unit}}
        sheet("Все эффекты","Применяются сразу, без перехода в студию",actions+listOf("Открыть студию ремиксов" to {screen="Студия";render()}))
    }
    private fun nowPlaying(){''')
replace('        updateQuickEffects()\n        if(!::seek.isInitialized)return','        updateTransportLayout()\n        if(!::seek.isInitialized)return')
replace('heading("Сейчас играет");val t=current()?:run{body.addView(label("Выберите композицию",16,muted));return}', '''val header=row();header.addView(iconButton(R.drawable.remix_back,"Назад к музыке"){screen="Музыка";render()});header.addView(label("Сейчас играет",14,muted),weight());header.addView(iconButton(R.drawable.remix_queue,"Очередь"){screen="Очередь";render()});body.addView(header)
        val t=current()?:run{body.addView(label("Выберите композицию",16,muted));return}''')
replace('setBackgroundColor(surface);contentDescription="Обложка композиции";setImageResource(android.R.drawable.ic_media_play)', '''background=rounded(surface,20);clipToOutline=true;contentDescription="Обложка композиции";scaleType=ImageView.ScaleType.CENTER;setImageResource(R.drawable.remix_music)''')
replace('body.addView(image,LinearLayout.LayoutParams(-1,dp(if(resources.configuration.screenHeightDp<600)140 else 220)))', '''val side=dp(minOf(300,resources.configuration.screenWidthDp-64,(resources.configuration.screenHeightDp*.36).toInt()).coerceAtLeast(120));body.addView(image,LinearLayout.LayoutParams(side,side).apply{gravity=Gravity.CENTER_HORIZONTAL;topMargin=dp(6);bottomMargin=dp(12)})''')
replace('if(cached!=null)image.setImageBitmap(cached)', 'if(cached!=null){image.scaleType=ImageView.ScaleType.CENTER_CROP;image.setImageBitmap(cached)}')
replace('&&current()?.uri==t.uri)image.setImageBitmap(bitmap)', '&&current()?.uri==t.uri){image.scaleType=ImageView.ScaleType.CENTER_CROP;image.setImageBitmap(bitmap)}')
# Replace action area, retaining every existing player action in compact icons/sheets.
a='        body.addView(label(t.title,26,Color.WHITE,true));'
b='\n    private var loopStart:Pair<String,Long>?=null'
section(a,b,r'''        val meta=row();val names=column()
        names.addView(label(t.title,23,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})
        names.addView(label(t.artist,14,muted).apply{maxLines=1;ellipsize=android.text.TextUtils.TruncateAt.END})
        meta.addView(names,weight())
        meta.addView(iconButton(if(source.favorite)R.drawable.remix_heart_on else R.drawable.remix_heart,if(source.favorite)"Убрать из избранного" else "В избранное"){source.favorite=!source.favorite;save();render()})
        meta.addView(iconButton(R.drawable.remix_more,"Ещё"){
            sheet("Композиция",actions=listOf(
                "Микшер" to {screen="Микшер";render()},
                "Таймер сна и переходы" to {playbackOptionsDialog()},
                "Повтор фрагмента" to {loopDialog()},
                "Вырезать аудиофрагмент" to {if(current()?.uri==t.uri)clipDialog(t)},
                "Эквалайзер" to {screen="Эквалайзер";render()}
            ))
        });body.addView(meta)
        val tools=row()
        tools.addView(iconButton(R.drawable.remix_lyrics,"Текст песни"){screen="Текст";render()},weight())
        tools.addView(iconButton(R.drawable.remix_versions,"Версии композиции"){screen="Версии";render()},weight())
        tools.addView(iconButton(R.drawable.remix_effects,"Эффекты"){quickPresetSheet()},weight())
        body.addView(tools)
    }
''')
# Replace the cryptic A/B menu with plain-language, live-position actions.
section('    private fun loopDialog(){','    private val tempoSearchCache',r'''    private fun loopDialog(){
        val p=controller?:return;val id=p.currentMediaItem?.mediaId?:return
        if(p.duration<=0||MixerSession.active){toast("Повтор фрагмента доступен после загрузки песни");return}
        val a=loopStart?.takeIf{it.first==id}?.second
        val active=RepeatRegion.active?.takeIf{it.id==id}
        fun valid()=p.currentMediaItem?.mediaId==id&&p.duration>0&&!MixerSession.active
        val actions=mutableListOf<Pair<String,()->Unit>>()
        actions.add("Отметить начало" to {if(valid()){loopStart=id to p.currentPosition.coerceIn(0,p.duration);RepeatRegion.active=null;toast("Начало: "+fmt(loopStart!!.second))}})
        if(a!=null)actions.add("Отметить конец и повторять" to {if(valid()){val region=LoopCore.create(id,a,p.currentPosition.coerceIn(0,p.duration),p.duration);if(region==null)toast("Конец должен быть минимум на 0,5 с позже")else{RepeatRegion.active=region;p.seekTo(region.start);toast("Повтор включён")}}})
        if(a!=null||active!=null)actions.add("Выключить повтор" to {if(valid()){RepeatRegion.active=null;loopStart=null;toast("Повтор выключен")}})
        actions.add("Назад на 10 секунд" to {if(valid()&&p.isCurrentMediaItemSeekable)p.seekTo((p.currentPosition-10000).coerceAtLeast(0))})
        actions.add("Закладка момента" to {if(valid())momentDialog(id)})
        val status=if(active!=null)"Повтор "+fmt(active.start)+" — "+fmt(active.end) else if(a!=null)"Начало "+fmt(a)+" · выберите конец" else "Отметьте начало и конец, чтобы зациклить часть песни."
        sheet("Повтор фрагмента",status,actions)
    }
''')
# Move secondary library actions out of the initial scroll area.
section('    private fun library(){','        fun fill(){',r'''    private fun libraryMenu(){
        sheet("Медиатека",actions=listOf(
            "Найти музыку на телефоне" to {requestScan()},
            "Темп / скорость" to {tempoSearchDialog()},
            "Сортировка: "+listOf(if(selectedPlaylist==null)"По добавлению" else "Порядок плейлиста","По названию","По исполнителю")[sortMode] to {sortMode=(sortMode+1)%3;shownSongs=100;render()},
            "Каталог: "+(category?:listOf("Все песни","Альбомы","Папки","Исполнители")[categoryMode]) to {chooseCategory()},
            "История" to {screen="История";render()},
            "Эквалайзер" to {screen="Эквалайзер";render()},
            ("Случайные версии: "+if(randomVersions)"вкл" else "выкл") to {randomVersions=!randomVersions;getSharedPreferences("play_options",MODE_PRIVATE).edit().putBoolean("random_versions",randomVersions).apply();render()},
            "Добавить найденные песни в плейлист" to {bulkPlaylistDialog()},
            "Добавить найденные песни в очередь" to {bulkQueueDialog()},
            "AI-сортировка по жанрам" to {if(!stemBusy)chooseGenreBatch()},
            "AI-сортировка по настроению" to {if(!stemBusy)chooseMoodBatch()},
            "Найти версии по названию" to {if(!stemBusy)suggestVersions()},
            "Сравнить песни по звуку" to {if(!stemBusy)fingerprintDialog()}
        ))
    }
    private fun library(){
        heading("Моя музыка")
        val searchRow=row()
        val search=EditText(this).apply{hint="Поиск музыки";contentDescription="Поиск по песне, исполнителю, альбому или ремиксу";setSingleLine();setText(query)}
        searchRow.addView(search,weight());searchRow.addView(iconButton(R.drawable.remix_filter,"Фильтры и инструменты"){libraryMenu()});body.addView(searchRow)
        val filters=row()
        filters.addView(btn(selectedPlaylist?:"Плейлисты"){playlistFilter()}.apply{background=rounded(Color.TRANSPARENT,12)},weight())
        filters.addView(iconButton(if(onlyFavorites)R.drawable.remix_heart_on else R.drawable.remix_heart,"Фильтр избранного"){onlyFavorites=!onlyFavorites;shownSongs=100;render()})
        body.addView(filters)
        if(tracks.isEmpty())body.addView(btn(if(scanBusy)"Сканирование…" else "Найти музыку на телефоне"){requestScan()})
        if(stemBusy)body.addView(label(stemStatus,13,accent))
        val list=column();body.addView(list)
''')
# Add separation to library rows, limit long titles, make secondary actions icons.
replace('col.addView(label(t.title,17,Color.WHITE,true))','col.addView(label(t.title,16,Color.WHITE,true).apply{maxLines=2;ellipsize=android.text.TextUtils.TruncateAt.END})')
replace('r.addView(btn(if(t.favorite)"♥" else "♡"){t.favorite=!t.favorite;save();fill()});r.addView(btn("⋮"){songMenu(t)})','r.addView(iconButton(if(t.favorite)R.drawable.remix_heart_on else R.drawable.remix_heart,"Избранное"){t.favorite=!t.favorite;save();fill()});r.addView(iconButton(R.drawable.remix_more,"Действия с песней"){songMenu(t)})')
# Lyrics content first, controls in a single expandable section even without synced text.
replace('    private fun lyrics(){',r'''    private fun collapseLyricsTools(){
        val tools=column()
        while(body.childCount>1){val view=body.getChildAt(1);body.removeViewAt(1);tools.addView(view)}
        val actions=mutableListOf<Pair<String,()->Unit>>()
        for(i in 0 until tools.childCount){val v=tools.getChildAt(i);if(v is Button)actions.add(v.text.toString() to {v.performClick();Unit})}
        val track=libraryIndex.get(MixerSession.request?.source)?:current()
        if(track!=null)actions.add(0,"Найти по названию и исполнителю…" to {manualLyricsSearch(track)})
        val row=row();row.addView(label(track?.title.orEmpty(),14,muted).apply{maxLines=1;ellipsize=android.text.TextUtils.TruncateAt.END},weight())
        row.addView(iconButton(R.drawable.remix_more,"Инструменты текста"){sheet("Текст и синхронизация",actions=actions)});body.addView(row)
        if(stemBusy)body.addView(label(stemStatus,14,accent))
    }
    private fun lyrics(){''')
replace('if(activeLyrics.isEmpty()){body.addView(label(if(raw.isBlank())','if(activeLyrics.isEmpty()){collapseLyricsTools();if(raw.isBlank())body.addView(btn("Найти текст песни"){manualLyricsSearch(t)});body.addView(label(if(raw.isBlank())')
a='val tools=column();while(body.childCount>1){val view=body.getChildAt(1);body.removeViewAt(1);tools.addView(view)};val toggle=btn(if(lyricToolsExpanded)"Скрыть инструменты текста" else "Инструменты текста…"){};toggle.setOnClickListener{lyricToolsExpanded=!lyricToolsExpanded;tools.visibility=if(lyricToolsExpanded)View.VISIBLE else View.GONE;toggle.text=if(lyricToolsExpanded)"Скрыть инструменты текста" else "Инструменты текста…"};body.addView(toggle);tools.visibility=if(lyricToolsExpanded||stemBusy)View.VISIBLE else View.GONE;body.addView(tools);'
replace(a,'collapseLyricsTools();')
replace('body.addView(follow)\n        val scroll=ScrollView(this);lyricScroll=scroll;', 'follow.background=rounded(Color.TRANSPARENT,12);body.addView(follow)\n        val scroll=ScrollView(this);lyricScroll=scroll;scroll.isVerticalScrollBarEnabled=false;')
replace('body.addView(scroll,LinearLayout.LayoutParams(-1,dp(330)))','body.addView(scroll,LinearLayout.LayoutParams(-1,dp((resources.configuration.screenHeightDp*.48).toInt().coerceIn(220,520))))')
replace('label(wordLines[idx].text,22,muted,true).apply{','label(wordLines[idx].text,28,0xff858594.toInt(),true).apply{setPadding(dp(8),dp(14),dp(8),dp(14));setLineSpacing(dp(3).toFloat(),1f);')
replace('label(visibleTranslation[idx],15,muted)','label(visibleTranslation[idx],17,muted)')
replace('v.setTextColor(accent);if(lyricFollow)','v.setTextColor(Color.WHITE);if(lyricFollow)')
# Start decoding while the user is on the library screen, not after opening the player.
replace('android.util.LruCache<String,FloatArray>(16)','android.util.LruCache<String,FloatArray>(32)')
replace('if(uiStarted&&screen=="Плеер"&&!MixerSession.active&&!stemBusy)current()else null','if(uiStarted&&!MixerSession.active&&!stemBusy)current()else null')
replace('&&uiStarted&&screen=="Плеер"&&current()?.uri==uri','&&uiStarted&&current()?.uri==uri')
replace('android.os.Process.THREAD_PRIORITY_BACKGROUND','android.os.Process.THREAD_PRIORITY_DEFAULT+2')
p.write_text(s)
print('PASS: compact library, distinct mini/full transport, vector icons, readable loop sheet and lyrics-first layout')
