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
# Do not reuse a render checkpoint from an older DSP algorithm.
edit('EffectCheckpoint.kt','dsp-peak-guard-v60','dsp-adaptive-depth-orbit-v2')
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
p.write_text(s)
print("PASS: 40 procedural genres, refined quick effects, offline DJ bass exchange")
# The hard-dance kick is rendered per genre, not the same oscillator with a different label.
edit('GenreEngine.kt','private val kicks=DoubleArray(ceil(.36*rate).toInt())','private val kicks=HardKick.curve(style.name,rate)?:DoubleArray(ceil(.36*rate).toInt())')
p=src/'GenreEngine.kt'
p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'ProducerStyles.kt').read_text().split('\n',1)[1]+'\n'+(Path(__file__).parent/'HardKick.kt').read_text().split('\n',2)[2])
p=src/'TransitionMix.kt'
p.write_text(p.read_text()+'\n'+(Path(__file__).parent/'DjBassExchange.kt').read_text().split('\n',2)[2])
