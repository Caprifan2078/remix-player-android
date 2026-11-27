from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]);src=root/'app/src/main/java/app/remix/player';patch=Path(__file__).parent
for name in ['WaveBins.kt','WaveReader.kt','WaveSeekBar.kt']:shutil.copyfile(patch/name,src/name)
p=src/'MainActivity.kt';s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1,(old[:150],s.count(old))
    s=s.replace(old,new)
replace('    private fun nowPlaying(){',r'''    private val waveCache=android.util.LruCache<String,FloatArray>(16)
    private val waveIo=java.util.concurrent.ThreadPoolExecutor(0,1,15L,java.util.concurrent.TimeUnit.SECONDS,java.util.concurrent.ArrayBlockingQueue<Runnable>(1),java.util.concurrent.ThreadPoolExecutor.AbortPolicy())
    private var waveJob:java.util.concurrent.Future<*>?=null
    private var waveKey:String?=null
    private var waveEpoch=0L
    private lateinit var quickEffectsRow:LinearLayout
    private val quickEffectButtons=linkedMapOf<Preset,Button>()
    private var quickEffectState:Preset?=null
    private fun addQuickEffects(){
        quickEffectsRow=row();quickEffectsRow.visibility=View.GONE
        for((name,caption) in listOf("Оригинал" to "1×","Sped Up" to "Speed","Nightcore" to "Nightcore","Slowed + Reverb" to "Slow+Rev")){
            val preset=Presets.all.first{it.name==name}
            val b=btn(caption){if(current()!=null&&!MixerSession.active){applyPreset(preset);updateQuickEffects()}}.apply{maxLines=1;textSize=11f;contentDescription=name}
            if(name=="Sped Up"||name=="Nightcore")b.setOnLongClickListener{
                if(current()!=null&&!MixerSession.active){
                    val combined=Presets.all.first{it.name==if(name=="Sped Up")"Sped Up + Reverb" else "Nightcore Reverb"}
                    applyPreset(combined);updateQuickEffects();toast(combined.name)
                };true
            }
            quickEffectButtons[preset]=b;quickEffectsRow.addView(b,weight())
        }
        quickEffectsRow.addView(btn("A/B"){loopDialog()}.apply{textSize=11f;contentDescription="Повтор участка A/B"},weight())
        bar.addView(quickEffectsRow)
    }
    private fun updateQuickEffects(){
        if(!::quickEffectsRow.isInitialized)return
        val visible=screen=="Плеер"&&current()!=null&&!MixerSession.active
        val v=if(visible)View.VISIBLE else View.GONE
        if(quickEffectsRow.visibility!=v)quickEffectsRow.visibility=v
        val active=Presets.active
        if(quickEffectState!=active){
            quickEffectState=active
            quickEffectButtons.forEach{(p,b)->
                val selected=p==active||(p.name=="Sped Up"&&active.name=="Sped Up + Reverb")||(p.name=="Nightcore"&&active.name=="Nightcore Reverb")
                b.isSelected=selected;b.setTextColor(if(selected)accent else Color.WHITE)
            }
        }
    }
    private fun cancelWave(){
        waveEpoch++;waveJob?.cancel(true);waveJob=null;waveIo.queue.clear();waveKey=null
        if(::seek.isInitialized)(seek as? WaveSeekBar)?.setWaveform(null)
    }
    private fun syncWave(){
        updateQuickEffects()
        if(!::seek.isInitialized)return
        val t=if(uiStarted&&screen=="Плеер"&&!MixerSession.active&&!stemBusy)current()else null
        if(t==null){if(waveKey!=null)cancelWave();return}
        if(waveKey==t.uri)return
        cancelWave();waveKey=t.uri
        val bar=seek as WaveSeekBar
        waveCache.get(t.uri)?.let{bar.setWaveform(it);return}
        val generation=waveEpoch;val uri=t.uri;val app=applicationContext
        waveJob=waveIo.submit{
            android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_BACKGROUND)
            val result=runCatching{WaveReader.read(app,Uri.parse(uri))}.getOrNull()
            if(!Thread.currentThread().isInterrupted)runOnUiThread{
                if(!isDestroyed&&generation==waveEpoch&&uiStarted&&screen=="Плеер"&&current()?.uri==uri&&!MixerSession.active){
                    if(result!=null){waveCache.put(uri,result);bar.setWaveform(result)}
                    waveJob=null
                }
            }
        }
    }
    private fun nowPlaying(){''')
replace('seek=SeekBar(this);seek.max=1000;','seek=WaveSeekBar(this);seek.max=1000;')
replace('time=label("0:00 / 0:00",12,muted);bar.addView(time)','time=label("0:00 / 0:00",12,muted);bar.addView(time);addQuickEffects()')
replace('val targetScreen=screen;mainScroll.post','syncWave();val targetScreen=screen;mainScroll.post')
replace('override fun onStop(){seekTarget=null;','override fun onStop(){cancelWave();seekTarget=null;')
replace('override fun onStart(){super.onStart();uiStarted=true;','override fun onStart(){super.onStart();uiStarted=true;syncWave();')
replace('override fun onDestroy(){uiStarted=false;','override fun onDestroy(){cancelWave();waveIo.shutdownNow();waveCache.evictAll();uiStarted=false;')
replace('setTextChanged(time,"${fmt(pos)} / ${fmt(dur)}")','if(!dragging)setTextChanged(time,"${fmt(pos)} / ${fmt(dur)}");syncWave()')
replace('override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){if(user&&!dragging)applySeek(currentSeekTarget(),p)}',r'''override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){
                s.invalidate()
                if(!user)return
                if(!dragging){applySeek(currentSeekTarget(),p);return}
                val target=seekTarget;val actual=currentSeekTarget()
                val request=MixerSession.request
                val length=request?.frames?:controller?.duration?:0L
                val value=PlayerUiSafety.seekPosition(target,actual,length,p)?:return
                val preview=if(request!=null)value*1000/44100 else value
                val duration=if(request!=null)length*1000/44100 else length
                setTextChanged(time,"${fmt(preview)} / ${fmt(duration)}")
            }''')
replace('found.onSuccess{list->reports.clear();completeReports.clear();tempoSearchCache.clear();tempos.clear();','found.onSuccess{list->cancelWave();waveCache.evictAll();reports.clear();completeReports.clear();tempoSearchCache.clear();tempos.clear();')
replace('if(seek.progress!=progress)seek.progress=progress','if(seek.progress!=progress){seek.progress=progress;seek.invalidate()}')
# Player screen remains compact; the transport waveform is always usable immediately.
replace('dp(if(resources.configuration.screenHeightDp<500)180 else 270)','dp(if(resources.configuration.screenHeightDp<600)140 else 220)')
p.write_text(s)
print('PASS: one native waveform seekbar, bounded foreground-only decoding, quick effects and existing A/B controls')
