from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player';res=root/'app/src/main/res';patch=Path(__file__).parent
def replace(p,old,new):
    s=p.read_text();assert s.count(old)==1,(p.name,old,s.count(old));p.write_text(s.replace(old,new))
shutil.copyfile(patch/'WidgetPolicy.kt',src/'WidgetPolicy.kt')
for name in ['pulse_widget_chip.xml','pulse_widget_chip_active.xml','pulse_widget_art.xml']:
    shutil.copyfile(patch/name,res/'drawable'/name)
p=src/'MainActivity.kt'
replace(p,'    private var lyricToolsExpanded=false',r'''    private var pendingWidgetRoute:Pair<String,String>?=null
    private fun readWidgetRoute(value:Intent){
        if(value.action!=PulseWidget.OPEN)return
        val route=value.getStringExtra(PulseWidget.ROUTE)
        if(route=="player"){screen="Плеер";pendingWidgetRoute=null;return}
        val id=value.getStringExtra(PulseWidget.TRACK)
        if(route in WidgetPolicy.routes&&!id.isNullOrBlank())pendingWidgetRoute=route!! to id
    }
    override fun onNewIntent(intent:Intent){
        super.onNewIntent(intent);setIntent(intent);readWidgetRoute(intent);render();consumeWidgetRoute()
    }
    private fun consumeWidgetRoute(){
        val p=controller?:return
        val (route,id)=pendingWidgetRoute?:return
        pendingWidgetRoute=null
        val t=current()
        if(t==null||!WidgetPolicy.allowed(id,p.currentMediaItem?.mediaId,MixerSession.active)){toast("Композиция уже изменилась");return}
        when(route){
            "edit"->{if(stemBusy){toast("Дождитесь завершения обработки");return};screen="Плеер";render();editCustomPreset()}
            "genres"->{screen="Жанры";render()}
            "lyrics"->{screen="Текст";render()}
            "save"->{
                val preset=Presets.active
                if(stemBusy||preset==Presets.all.first()||!CustomPresetCore.exportable(preset)){toast("Выберите эффект для сохранения");return}
                android.app.AlertDialog.Builder(this).setTitle("Сохранить ремикс").setMessage(t.title+" · "+preset.name+"\nБудет создана отдельная версия, оригинал не изменится.").setNegativeButton("Отмена",null).setPositiveButton("Создать"){_,_->
                    if(current()?.uri==id&&Presets.active==preset&&!MixerSession.active)saveEffect(t,preset)else toast("Песня или эффект изменились")
                }.show()
            }
        }
    }
    private var lyricToolsExpanded=false''')
replace(p,'        future=MediaController.Builder(this,SessionToken','        readWidgetRoute(intent)\n        future=MediaController.Builder(this,SessionToken')
replace(p,'restoreQueue(it)};render()}.onFailure','restoreQueue(it)};render();consumeWidgetRoute()}.onFailure')
replace(p,'private fun applyPreset(p:Preset){Presets.active=p;controller?.playbackParameters=PlaybackParameters(p.speed,p.pitch)}','private fun applyPreset(p:Preset){Presets.active=p;controller?.playbackParameters=PlaybackParameters(p.speed,p.pitch);PulseWidget.refresh(this)}')
print('PASS: three responsive studio widget sizes, quick effect controls, track-bound editor and explicit save routes')
