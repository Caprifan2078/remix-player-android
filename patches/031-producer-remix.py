#!/usr/bin/env python3
from pathlib import Path
import sys
src=Path(sys.argv[1])/'app/src/main/java/app/remix/player'
def edit(name,a,b):
 p=src/name;s=p.read_text();assert s.count(a)==1,(name,a[:100],s.count(a));p.write_text(s.replace(a,b))
edit('AdaptiveGroove.kt','fun voice(style:GenreEngine.Style):Voice=when(style.name){','fun voice(style:GenreEngine.Style):Voice=when(ProducerStyles.family(style)){')
edit('LeadSynth.kt','private val pattern=when(style.name){','private val pattern=when(ProducerStyles.family(style)){')
edit('LeadSynth.kt','private val color=when(style.name){','private val color=when(ProducerStyles.family(style)){')
edit('AudioCore.kt','Preset("Sped Up",1.25f)','Preset("Sped Up",1.25f,bass=.12f,room=.075f,drive=.025f)')
edit('AudioCore.kt','Preset("Nightcore",1.25f,1.25f)','Preset("Nightcore",1.25f,1.25f,bass=.16f,room=.09f,drive=.035f)')
edit('AudioCore.kt','Preset("Slowed + Reverb",.85f,.9f,room=.35f)','Preset("Slowed + Reverb",.85f,.9f,bass=.13f,room=.35f,muffled=.06f)')
# Real-time and offline preset rendering share Dsp. Adapt wet/dry depth to actual PCM.
edit('AudioCore.kt','private val guard=LinkedPeakGuard(rate)','private val guard=LinkedPeakGuard(rate)\n    private val adaptiveDepth=AdaptiveEffectEnvelope(rate)')
edit('AudioCore.kt',';guard.reset() }',';guard.reset();adaptiveDepth.reset() }')
edit('AudioCore.kt','val sweep = if(p.pan>0','val depth=if(processed)adaptiveDepth.frame(input)else 1f\n        val sweep = if(p.pan>0')
edit('AudioCore.kt','out[c]=y','out[c]=if(processed)x+(y-x)*depth else y')
# Spatial movement must not be weakened by the adaptive wet/dry blend.
edit('AudioCore.kt','Preset("8D Audio",pan=.8f,room=.15f)','Preset("8D Audio",pan=.95f,room=.22f)')
edit('AudioCore.kt','private val adaptiveDepth=AdaptiveEffectEnvelope(rate)','private val adaptiveDepth=AdaptiveEffectEnvelope(rate)\n    private val orbit=StereoOrbit(rate)')
edit('AudioCore.kt','guard.reset();adaptiveDepth.reset()','guard.reset();adaptiveDepth.reset();orbit.reset()')
edit('AudioCore.kt','if(channels==2 && p.pan>0) y *= if(c==0) sqrt((1-sweep).coerceAtLeast(0f))*.75f else sqrt((1+sweep).coerceAtLeast(0f))*.75f','// Spatial processing is applied after the channel-linked adaptive mix.')
edit('AudioCore.kt','if(processed)guard.apply(out)','if(channels==2&&p.pan>0)orbit.apply(out,sweep)\n        if(processed)guard.apply(out)')
edit('AudioCore.kt','phase += 2*PI*.19/rate','phase += 2*PI*(when(p.name){"Slow Stereo Orbit"->.10;"Fast Stereo Orbit"->.32;else->.19})/rate')
p=src/'AudioCore.kt'
p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'StereoOrbit.kt').read_text().split('\n',4)[4])
p=src/'AudioCore.kt'
envelope=(Path(__file__).parent/'AdaptiveEffectEnvelope.kt').read_text().splitlines()
p.write_text(p.read_text()+'\n'+'\n'.join(envelope[5:])+'\n')
# Replace the assembled legacy DSP; keep preset definitions, guards, lyric parser and shared helpers.
p=src/'AudioCore.kt';audio=p.read_text()
a=audio.index('class Dsp(');b=audio.index('data class Lyric(',a)
quality=(Path(__file__).parent/'EffectQuality.kt').read_text().split('\n',4)[4]
p.write_text(audio[:a]+quality+'\n'+audio[b:])
# Live-only effect switching: retain export DSP and its exact original path.
(src/'LiveEffectSwitch.kt').write_bytes((Path(__file__).parent/'LiveEffectSwitch.kt').read_bytes())
edit('PlaybackService.kt','private var dsp: Dsp? = null','private var dsp: LiveEffectSwitch? = null')
edit('PlaybackService.kt','dsp=Dsp(inputAudioFormat.sampleRate,a.size)','dsp=LiveEffectSwitch(inputAudioFormat.sampleRate,a.size)')
edit('PlaybackService.kt','if(lastPreset!==p){lastPreset=p;dsp=if(a.isNotEmpty())Dsp(inputAudioFormat.sampleRate,a.size) else null}','if(lastPreset!==p)lastPreset=p')
edit('PlaybackService.kt','(p==Presets.all.first() && levels.all{it==0f}) || d==null','(p==Presets.all.first() && levels.all{it==0f} && d?.canBypass(p)==true) || d==null')
# EQ gain is a cascade: overlapping boosts may exceed the largest slider by several dB.
edit('PlayerExtras.kt','private val headroom=10.0.pow(-levels.maxOrNull()!!.coerceAtLeast(0f)/20.0)', '''// Estimate the combined cascade response, not just the highest individual slider.
    private val headroom=if(filters.isEmpty()||levels.none{it>0f})1.0 else run{
        var peak=1.0
        fun evaluate(hz:Double){
            val w=2*PI*hz/rate;val c=cos(w);val s=sin(w);val c2=cos(2*w);val s2=sin(2*w)
            var power=1.0
            for(f in filters){
                val nr=f.b0+f.b1*c+f.b2*c2;val ni=f.b1*s+f.b2*s2
                val dr=1+f.a1*c+f.a2*c2;val di=f.a1*s+f.a2*s2
                power*=(nr*nr+ni*ni)/(dr*dr+di*di).coerceAtLeast(1e-24)
            }
            peak=max(peak,sqrt(power))
        }
        // Log-spaced coverage resolves low-frequency peaks even at high sample rates.
        val upper=rate*.5
        for(i in 0..1024)evaluate(exp(ln(upper)*i/1024.0))
        EqualizerSettings.frequencies.filter{it<upper}.forEach{evaluate(it.toDouble())}
        .97/peak
    }''')
edit('PlayerExtras.kt','fun sample(x:Float,c:Int):Float {val clean=if(x.isFinite())x else 0f;if(filters.isEmpty())return clean;var y=clean*headroom;for(f in filters)y=f.next(y,c);return y.coerceIn(-1.0,1.0).toFloat()}', '''private val guard=LinkedPeakGuard(rate)
    private fun raw(x:Float,c:Int):Float {val clean=if(x.isFinite())x else 0f;if(filters.isEmpty())return clean;var y=clean*headroom;for(f in filters)y=f.next(y,c);return if(y.isFinite())y.toFloat()else 0f}
    fun sample(x:Float,c:Int):Float=raw(x,c).coerceIn(-1f,1f)
    fun frame(values:FloatArray){
        require(values.size==channels)
        for(c in values.indices)values[c]=raw(values[c],c)
        if(filters.isNotEmpty())guard.apply(values)
    }''')
edit('PlaybackService.kt','d.frame(a,b,p); for(c in b.indices) out.putShort(((eq?.sample(b[c],c)?:b[c])*32768).roundToInt().coerceIn(-32768,32767).toShort())','d.frame(a,b,p); eq?.frame(b); for(c in b.indices) out.putShort((b[c]*32768).roundToInt().coerceIn(-32768,32767).toShort())')
edit('EqRender.kt','val eq=GraphicEq(44100,2,levels);val flat=','val eq=GraphicEq(44100,2,levels);val frame=FloatArray(2);val flat=')
edit('EqRender.kt','for(c in 0..1){val s=StemCore.readShort(r);StemCore.writeShort(w,if(flat)s else StemCore.pcm(eq.sample(s/32768f,c)))}','if(flat){repeat(2){StemCore.writeShort(w,StemCore.readShort(r))}}else{for(c in frame.indices)frame[c]=StemCore.readShort(r)/32768f;eq.frame(frame);for(x in frame)StemCore.writeShort(w,StemCore.pcm(x))}')
# Do not reuse a render checkpoint from an older DSP algorithm.
edit('EffectCheckpoint.kt','dsp-peak-guard-v60','dsp-quality-v4')
edit('GenreCheckpoint.kt','genre-render-v7','genre-render-v8')
edit('TransitionMix.kt','    fun renderFrames(first:File,second:File,out:File,overlap:Long,progress:(Int)->Unit={}):Long {','''    fun renderFrames(first:File,second:File,out:File,overlap:Long,progress:(Int)->Unit={}):Long = renderInternal(first,second,out,overlap,false,progress)
    fun renderSmartFrames(first:File,second:File,out:File,overlap:Long,progress:(Int)->Unit={}):Long = renderInternal(first,second,out,overlap,true,progress)
    private fun renderInternal(first:File,second:File,out:File,overlap:Long,bassExchange:Boolean,progress:(Int)->Unit):Long {''')
edit('TransitionMix.kt','copy(x,a-overlap);repeatFrames(overlap)','val exchange=if(bassExchange)DjBassExchange()else null;copy(x,a-overlap);repeatFrames(overlap)')
edit('TransitionMix.kt','repeat(2){val l=StemCore.readShort(x)/32768.0;val r=StemCore.readShort(y)/32768.0;StemCore.writeShort(w,StemCore.pcm(((l*gainA+r*gainB)/norm).toFloat()))}','repeat(2){ch->val l=StemCore.readShort(x)/32768.0;val r=StemCore.readShort(y)/32768.0;val mixed=exchange?.sample(ch,l,r,t,gainA,gainB,norm)?:((l*gainA+r*gainB)/norm);StemCore.writeShort(w,StemCore.pcm(mixed.toFloat()))}')
edit('DjTransition.kt','TransitionMix.renderFrames(first,prepared,out,n){progress("Сведение: $it%")}','TransitionMix.renderSmartFrames(first,prepared,out,n){progress("Сведение: $it%")}')
edit('DjTransition.kt','return Result(TransitionMix.renderSmartFrames','notes.add("Обмен басом между песнями");return Result(TransitionMix.renderSmartFrames')
p=src/'MainActivity.kt';s=p.read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b)
rep('val styles=List(a.length()){i->GenreEngine.styles.single{it.name==a.getString(i)}}','val styles=List(a.length()){i->ProducerStyles.all.single{it.name==a.getString(i)}}')
rep('GenreEngine.styles.forEach{style->card(style.name,"Цель: ${style.target} BPM · новые ударные и бас"){generateGenres(source,listOf(style))}}','''val featured=ProducerStyles.featured()
        body.addView(label("Популярные направления",20,PremiumChrome.TEXT,true))
        featured.forEach{style->card(style.name,style.target.toString()+" BPM · "+ProducerStyles.describe(style)){generateGenres(source,listOf(style))}}
        val moreStart=body.childCount
        ProducerStyles.more().forEach{style->card(style.name,style.target.toString()+" BPM · "+ProducerStyles.describe(style)){generateGenres(source,listOf(style))}}
        compactSection("genre-more","Все направления · "+ProducerStyles.more().size,bodyChildren().drop(moreStart),moreStart)''')
rep('val styles=GenreEngine.styles;val selected=BooleanArray(styles.size)','val styles=ProducerStyles.all;val selected=BooleanArray(styles.size)')
rep('.setNeutralButton("Все 30"){_,_->confirmBatch(source,styles)}','.setNeutralButton("30 основных"){_,_->confirmBatch(source,GenreEngine.styles)}')
rep('if(chosen.isEmpty())toast("Выберите хотя бы один жанр") else confirmBatch(source,chosen)','if(chosen.isEmpty())toast("Выберите хотя бы один жанр") else if(chosen.size>30)toast("Не более 30 версий за пакет") else confirmBatch(source,chosen)')
rep('panel.addView(label("Быстрые режимы",12,muted,true))','''sheetAction(panel,"Hardstyle и жанровые ремиксы","Создать новую версию с новыми ударными и басом"){dialog.dismiss();screen="Жанры";render()}
            panel.addView(label("Моментальные эффекты",12,muted,true))
            panel.addView(label("Интенсивность меняется по громкости песни; скорость и тон остаются выбранными.",12,muted))''')
rep('popular.size*61+65','popular.size*61+175')
# Neural mood analysis is optional and only used on an explicit recommendation request.
rep('if(cached!=null){showRecommendations(source,cached)}else stemWork("Анализ для рекомендаций…",{TrackAnalyzer.report(this,Uri.parse(source.uri),full=true)?:error("Не удалось проанализировать")}){r->completeReports[source.uri]=r;reports[source.uri]=r;showRecommendations(source,r)}','smartRecommendations(source,cached)')
rep('    private fun showRecommendations(source:Track,report:MusicAnalysis.Report){','''    private fun smartRecommendations(source:Track,cached:MusicAnalysis.Report?){
        if(stemBusy)return
        val model=MoodModel.model(this)
        stemWork("Подбор ремиксов…",{
            val report=cached?:TrackAnalyzer.report(this,Uri.parse(source.uri),full=true)?:error("Не удалось проанализировать")
            var arousal:Double?=null
            if(model.isFile){
                val am=getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
                val info=android.app.ActivityManager.MemoryInfo();am.getMemoryInfo(info)
                if(ModelMemoryBudget.canStart(model.length(),info.availMem,info.lowMemory)){
                    try{
                        val mood=MoodModel.classify(this,Uri.parse(source.uri)){updateWork(it)}
                        if(mood.label!=null)arousal=mood.arousal.toDouble().takeIf{it.isFinite()&&it in 0.0..1.0}
                    }catch(e:Exception){
                        if(e is InterruptedException||Thread.currentThread().isInterrupted)throw e
                    }
                }
            }
            check(!Thread.currentThread().isInterrupted)
            report to arousal
        }){(report,arousal)->
            if(libraryIndex.get(source.uri)!=null){completeReports[source.uri]=report;reports[source.uri]=report;showRecommendations(source,report,arousal)}
        }
    }
    private fun showRecommendations(source:Track,report:MusicAnalysis.Report,neuralArousal:Double?=null){''')
rep('RemixAdvisor.recommend(report,manualBeat(source)?.bpm,goals[i])','RemixAdvisor.recommend(report,manualBeat(source)?.bpm,goals[i],neuralArousal)')
# Keep popular genres ahead of secondary controls on the existing genre screen.
rep('if(available)body.addView(btn(if(useSeparation)','val genreToolsStart=body.childCount\n        if(available)body.addView(btn(if(useSeparation)')
rep('val featured=ProducerStyles.featured()','''val genreTools=bodyChildren().drop(genreToolsStart)
        val advisor=genreTools.filterIsInstance<Button>().firstOrNull{it.text.toString()=="Подобрать 5 ремиксов по характеру"}
        if(advisor!=null){body.removeView(advisor);body.addView(advisor,genreToolsStart)}
        val featured=ProducerStyles.featured()''')
rep('compactSection("genre-more","Все направления · "+ProducerStyles.more().size,bodyChildren().drop(moreStart),moreStart)','''compactSection("genre-more","Все направления · "+ProducerStyles.more().size,bodyChildren().drop(moreStart),moreStart)
        val controls=genreTools.filter{it!==advisor}
        compactSection("genre-options","Настройки аранжировки и модели",controls,body.childCount-controls.size)''')
p.write_text(s)
print("PASS: 40 procedural genres, refined quick effects, offline DJ bass exchange")
# Keep the earlier separated-bass sidechain; use the new hard-specific envelope only for hard genres.
edit('GenreEngine.kt','val kickSpace=KickSpace();val sourceLow=SourceLowEnd()','val kickSpace=KickSpace();val sourceLow=SourceLowEnd();val hardMix=HardMixSpace(44100);val hardStyle=HardKick.profile(style.name)!=null')
edit('GenreEngine.kt','sourceLow.frame(l,rr,kickGain);dynamics.frame(sourceLow.left+b,sourceLow.right+b);','if(hardStyle){hardMix.frame(l,rr,beat.kickEnvelope*levels.drums*controls.drums,true);dynamics.frame(hardMix.left+b,hardMix.right+b)}else{sourceLow.frame(l,rr,kickGain);dynamics.frame(sourceLow.left+b,sourceLow.right+b)};')
# Bundle the exact small upstream ONNX graph and its original license; no network or audio upload.
import base64,hashlib
pitch_dir=Path(__file__).parent/'basic-pitch'
weights=base64.b64decode((pitch_dir/'nmp.onnx.b64').read_text().strip(),validate=True)
assert len(weights)==230444 and hashlib.sha256(weights).hexdigest()=='2c3c1d144bfa61ad236e92e169c13535c880469a12a047d4e73451f2c059a0ec'
assets=Path(sys.argv[1])/'app/src/main/assets/basic-pitch'
assets.mkdir(parents=True,exist_ok=True)
(assets/'nmp.onnx').write_bytes(weights)
for filename in ('LICENSE','NOTICE'):
    (assets/filename).write_bytes((pitch_dir/filename).read_bytes())
for filename in ('BasicPitchHint.kt','BasicPitchModel.kt'):
    (src/filename).write_bytes((Path(__file__).parent/filename).read_bytes())
edit('GenreEngine.kt','val oldDrums:Float,val bass:Float)','val oldDrums:Float,val bass:Float,val kickHz:Double?=null)')
edit('GenreCheckpoint.kt','o.writeFloat(s.oldDrums);o.writeFloat(s.bass)','o.writeFloat(s.oldDrums);o.writeFloat(s.bass);o.writeBoolean(s.kickHz!=null);s.kickHz?.let{o.writeDouble(it)}')
# The hard-dance kick is rendered per genre, not the same oscillator with a different label.
edit('GenreEngine.kt','private val kicks=DoubleArray(ceil(.36*rate).toInt())','private val kicks=HardKick.curve(style.name,rate,style.kickHz)?:DoubleArray(ceil(.36*rate).toInt())')
p=src/'GenreEngine.kt'
p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'ProducerStyles.kt').read_text().split('\n',1)[1]+'\n'+(Path(__file__).parent/'HardKick.kt').read_text().split('\n',2)[2])
p=src/'TransitionMix.kt'
p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'DjBassExchange.kt').read_text().split('\n',2)[2])
