from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player';res=root/'app/src/main/res';p=src/'MainActivity.kt';s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:120],s.count(a))
    s=s.replace(a,b)
def section(a,b,new):
    global s
    start=s.index(a);end=s.index(b,start)
    s=s[:start]+new+s[end:]
replace('setContentView(root)','val frame=android.widget.FrameLayout(this);drawerHost=frame;frame.addView(root,android.widget.FrameLayout.LayoutParams(-1,-1));setContentView(frame)')
replace('val header=row();mainHeader=header;header.addView(label("REMIX",22,accent,true),weight());','val header=row();mainHeader=header;header.addView(iconButton(R.drawable.remix_menu,"Меню навигации"){openDrawer()});header.addView(label("REMIX",22,accent,true),weight());')
replace('transportControls=controls;bar.addView(controls);root.addView(nav)','transportControls=controls;bar.addView(controls);installLibraryTabs();installDrawer(nav)')
replace('if(screen!="Музыка"){screen="Музыка";render()}else{isEnabled=false;', 'if(::drawerOverlay.isInitialized&&drawerOverlay.visibility==View.VISIBLE){closeDrawer()}else if(screen!="Музыка"){screen="Музыка";render()}else{isEnabled=false;')
replace('val button=btn(name){screen=name;render()}','val button=btn(name){closeDrawer();screen=name;render()}')
replace('    private lateinit var mainHeader:LinearLayout',r'''    private lateinit var drawerHost:android.widget.FrameLayout
    private lateinit var drawerOverlay:android.widget.FrameLayout
    private lateinit var libraryTabs:LinearLayout
    private fun openDrawer(){if(::drawerOverlay.isInitialized){drawerOverlay.setPadding(0,root.paddingTop,0,root.paddingBottom);drawerOverlay.visibility=View.VISIBLE;root.importantForAccessibility=View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS}}
    private fun closeDrawer(){if(::drawerOverlay.isInitialized){drawerOverlay.visibility=View.GONE;root.importantForAccessibility=View.IMPORTANT_FOR_ACCESSIBILITY_AUTO}}
    private fun installDrawer(nav:LinearLayout){
        drawerOverlay=android.widget.FrameLayout(this).apply{visibility=View.GONE;setBackgroundColor(0x99000000.toInt());setOnClickListener{closeDrawer()}}
        val panel=column().apply{background=rounded(surface,18);isClickable=true;setPadding(dp(12),dp(16),dp(12),dp(12))}
        val title=row();title.addView(label("REMIX",24,accent,true),weight());title.addView(iconButton(R.drawable.remix_close,"Закрыть меню"){closeDrawer()});panel.addView(title)
        nav.orientation=LinearLayout.VERTICAL
        for(i in 0 until nav.childCount){val v=nav.getChildAt(i) as Button;v.layoutParams=LinearLayout.LayoutParams(-1,dp(52));v.gravity=Gravity.CENTER_VERTICAL or Gravity.START;v.setPadding(dp(16),dp(4),dp(12),dp(4));v.setAutoSizeTextTypeWithDefaults(TextView.AUTO_SIZE_TEXT_TYPE_NONE);v.textSize=16f}
        panel.addView(nav)
        panel.addView(btn("Настройки и память"){closeDrawer();screen="Настройки";render()})
        panel.addView(btn("История"){closeDrawer();screen="История";render()})
        val scroll=ScrollView(this).apply{addView(panel);setBackgroundColor(surface)}
        drawerOverlay.addView(scroll,android.widget.FrameLayout.LayoutParams(dp(minOf(300,resources.configuration.screenWidthDp-48)), -1,Gravity.START))
        drawerHost.addView(drawerOverlay,android.widget.FrameLayout.LayoutParams(-1,-1))
    }
    private fun tabsEnabled()=getSharedPreferences("library_ui",MODE_PRIVATE).getBoolean("category_tabs",true)
    private fun toggleLibraryTabs(){
        val next=!tabsEnabled();getSharedPreferences("library_ui",MODE_PRIVATE).edit().putBoolean("category_tabs",next).apply()
        if(!next){selectedPlaylist=null;category=null;categoryMode=0;shownSongs=100};render()
    }
    private fun folderSheet(){
        val priorMode=categoryMode
        categoryMode=2
        val items=tracks.filter{it.uri==it.group}.map(::categoryValue).distinct().sorted()
        categoryMode=priorMode
        sheet("Папки",if(items.isEmpty())"Нет доступных папок" else "",listOf("Все папки" to {selectedPlaylist=null;categoryMode=2;category=null;shownSongs=100;render()})+items.map{name->name to {selectedPlaylist=null;categoryMode=2;category=name;shownSongs=100;render()}})
    }
    private fun playlistSheet(){
        val names=playlists.keys.toList()
        sheet("Плейлисты",actions=listOf<Pair<String,()->Unit>>("Все песни" to {selectedPlaylist=null;categoryMode=0;category=null;shownSongs=100;render()},"Новый плейлист" to {newPlaylist()})+names.map{name->name to {if(name in playlists){selectedPlaylist=name;categoryMode=0;category=null;sortMode=0;shownSongs=100;render()}}}+listOf("Управление плейлистами" to {playlistFilter()}))
    }
    private fun installLibraryTabs(){
        libraryTabs=row()
        val tabs=listOf<Pair<String,()->Unit>>("Песни" to {selectedPlaylist=null;category=null;categoryMode=0;shownSongs=100;render()},"Папки" to {folderSheet()},"Плейлисты" to {playlistSheet()})
        tabs.forEach{(name,action)->libraryTabs.addView(btn(name,action).apply{background=rounded(Color.TRANSPARENT,10);textSize=12f;setSingleLine()},weight())}
        root.addView(libraryTabs)
    }
    private lateinit var mainHeader:LinearLayout''')
replace('filters.addView(btn(selectedPlaylist?:"Плейлисты"){playlistFilter()}.apply{background=rounded(Color.TRANSPARENT,12)},weight())','filters.addView(label(selectedPlaylist?:category?:"Все песни",14,muted),weight())')
replace('"Найти музыку на телефоне" to {requestScan()},','"Найти музыку на телефоне" to {requestScan()},\n            (if(tabsEnabled())"Скрыть папки и плейлисты внизу" else "Показать папки и плейлисты внизу") to {toggleLibraryTabs()},\n            "Плейлисты" to {playlistSheet()},\n            "Папки" to {folderSheet()},')
replace('private fun settingsScreen(){heading("Настройки и память");','private fun settingsScreen(){heading("Настройки и память");body.addView(btn(if(tabsEnabled())"Папки и плейлисты внизу: вкл." else "Папки и плейлисты внизу: выкл."){toggleLibraryTabs()});')
replace('        mainNav.visibility=if(player)View.GONE else View.VISIBLE','''        if(::libraryTabs.isInitialized){libraryTabs.visibility=if(screen=="Музыка"&&tabsEnabled())View.VISIBLE else View.GONE
            if(libraryTabs.visibility==View.VISIBLE){val selected=if(selectedPlaylist!=null)2 else if(categoryMode==2)1 else 0;for(i in 0 until libraryTabs.childCount)(libraryTabs.getChildAt(i) as Button).setTextColor(if(i==selected)accent else muted)}}''')
replace('    private fun lyrics(){',r'''    private fun manualLyricsSearch(t:Track){
        if(lyricsBusy||stemBusy)return
        val original=libraryIndex.get(t.group)?:t
        val cleaned=LyricsMatch.query(original.title,original.artist)
        val dialog=android.app.Dialog(this)
        val panel=column().apply{background=rounded(surface,22);setPadding(dp(18),dp(14),dp(18),dp(18))}
        panel.addView(label("Найти текст песни",20,Color.WHITE,true))
        val title=EditText(this).apply{hint="Название";setSingleLine();setText(cleaned.title)}
        val artist=EditText(this).apply{hint="Исполнитель (необязательно)";setSingleLine();setText(cleaned.artist)}
        panel.addView(title);panel.addView(artist)
        panel.addView(label("Можно писать по-русски, по-английски или транслитом. Название и исполнитель отправляются в LRCLIB. Выберите правильную запись: обычный текст не выдаётся за синхронный.",13,muted))
        panel.addView(btn("Найти"){
            val q=title.text.toString().trim();val a=artist.text.toString().trim()
            if(q.isBlank()||q.length>200||a.length>200){toast("Уточните название");return@btn}
            dialog.dismiss();val rev=lyricRevision(t);lyricsBusy=true
            io.execute{
                val result=runCatching{LyricsLookup.search(q,a)}
                runOnUiThread{if(!isDestroyed){
                    lyricsBusy=false
                    result.onSuccess{rows->
                        if(rows.isEmpty())toast("В каталоге LRCLIB нет совпадений")
                        else if(screen=="Текст"&&(libraryIndex.get(MixerSession.request?.source)?:current())?.uri==t.uri){
                            val choices=rows.map{r->(r.artist+" — "+r.title+" · "+fmt(r.seconds*1000)+(if(r.synced!=null)" · синхронный" else " · обычный")) to {
                                val live=libraryIndex.get(t.uri)
                                if(live==null||lyricRevision(live)!=rev||(libraryIndex.get(MixerSession.request?.source)?:current())?.uri!=t.uri)toast("Композиция или текст изменились")
                                else{val raw=r.synced?:r.plain.orEmpty();live.lyrics=if(r.synced!=null&&live.tempoRatio!=null)TimeStretch.lyrics(raw,live.tempoRatio!!)else raw;save();render()};Unit
                            }}
                            sheet("Результаты поиска","Выберите запись, соответствующую вашей версии песни",choices)
                        }
                    }.onFailure{toast("Поиск недоступен: "+(it.message?:"ошибка сети"))}
                }}
            }
        });panel.addView(btn("Отмена"){dialog.dismiss()})
        dialog.setContentView(panel);dialog.window?.setBackgroundDrawableResource(android.R.color.transparent);dialog.show();dialog.window?.setLayout(-1,-2)
    }
    private fun lyrics(){''')
section('    private fun whisperModelDialog(){','    private fun recognizeWhisper(',r'''    private fun whisperModelDialog(){
        if(stemBusy)return
        if(!WhisperLocal.available){toast("Whisper не включён в сборку");return}
        val active=WhisperLocal.installed(this)?.title?:"не установлена"
        val actions=WhisperModelSpec.models.map{spec->
            spec.title+" · "+spec.description to {
                sheet(spec.title,spec.description+"\nСвободная ОЗУ: ориентир "+(spec.minFreeRam/1048576)+" МиБ. Аудио остаётся на устройстве. Точность пения не гарантирована.",listOf("Скачать модель" to {
                    if(!stemBusy)stemWork("Загрузка Whisper…",{WhisperLocal.download(this,spec){updateWork("Whisper: $it%")}}){id->toast("Whisper $id установлен");render()}
                }))
            }
        }
        sheet("Распознавание вокала","Установлена: "+active,actions+listOf("Импорт файла" to {whisperPicker.launch(arrayOf("*/*"))}))
    }
''')
replace('time=label("0:00 / 0:00",12,muted);bar.addView(time);addQuickEffects()', 'time=label("0:00",12,muted);timeEnd=label("0:00",12,muted);timeRow=row();timeRow.addView(time,weight());timeRow.addView(timeEnd);bar.addView(timeRow);addQuickEffects()')
replace('    private lateinit var libraryTabs:LinearLayout','    private lateinit var libraryTabs:LinearLayout\n    private lateinit var timeRow:LinearLayout\n    private lateinit var timeEnd:TextView')
replace('time.visibility=if(full)View.VISIBLE else View.GONE','timeRow.visibility=if(full)View.VISIBLE else View.GONE')
replace('setTextChanged(time,"${fmt(pos)} / ${fmt(dur)}")','run{setTextChanged(time,fmt(pos));setTextChanged(timeEnd,fmt(dur))}')
replace('setTextChanged(time,"${fmt(preview)} / ${fmt(duration)}")','run{setTextChanged(time,fmt(preview));setTextChanged(timeEnd,fmt(duration))}')
replace('runCatching{WaveReader.read(app,Uri.parse(uri))}',r'''runCatching{WaveDiskCache.readOrDecode(app,Uri.parse(uri)){values,ready->
                if(!Thread.currentThread().isInterrupted)runOnUiThread{
                    if(!isDestroyed&&generation==waveEpoch&&uiStarted&&current()?.uri==uri&&!MixerSession.active)bar.setWaveformPreview(values,ready)
                }
            }}''')
replace('if(result!=null){waveCache.put(uri,result);bar.setWaveform(result)}','if(result!=null){waveCache.put(uri,result);bar.setWaveform(result)}else bar.setWaveform(null)')
p.write_text(s)
for name in ['LyricsLookup.kt','LyricsMatch.kt','WaveDiskCache.kt','LibrarySearch.kt']:shutil.copyfile(Path(__file__).parent/name,src/name)
core=root/'tests/run-core.sh';coreText=core.read_text();assert coreText.count('TimedLineEdit,LibrarySearch,')==1;core.write_text(coreText.replace('TimedLineEdit,LibrarySearch,','TimedLineEdit,LibrarySearch,LyricsMatch,'))
styles=res/'values/styles.xml';xml=styles.read_text()
assert '</style></resources>' in xml
xml=xml.replace('</style></resources>','<item name="android:alertDialogTheme">@style/RemixAlert</item></style><style name="RemixAlert" parent="android:style/Theme.Material.Dialog.Alert"><item name="android:fontFamily">sans</item><item name="android:colorAccent">#C0B0FF</item><item name="android:colorBackgroundFloating">#1D202B</item><item name="android:textColorPrimary">#F5F3FA</item><item name="android:textColorSecondary">#BCB8CB</item><item name="android:windowBackground">@drawable/remix_dialog_bg</item></style></resources>')
styles.write_text(xml)
(res/'drawable/remix_dialog_bg.xml').write_text('<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle"><solid android:color="#1D202B"/><corners android:radius="20dp"/><padding android:left="12dp" android:top="8dp" android:right="12dp" android:bottom="8dp"/></shape>')
print("PASS: drawer, optional categories, manual lyric search, model sheet and dark dialog theme")
