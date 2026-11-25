#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/MainActivity.kt"
s=p.read_text()
def replace(old,new):
    global s
    assert s.count(old)==1, f"Expected one match: {old[:100]}"
    s=s.replace(old,new)
# Keep ordinary transport in all other screens, including empty mixer.
replace('if(!::body.isInitialized)return;if(renderedScreen.isNotEmpty())','if(!::body.isInitialized)return;bar.visibility=View.VISIBLE;previewDragging=false;if(renderedScreen.isNotEmpty())')
replace('val gains=stemGains[source.uri]?.takeIf{it.size==bundle.count}', '''// Mixer has its own transport; reclaim the duplicated mini-player area.
        bar.visibility=View.GONE
        val gains=stemGains[source.uri]?.takeIf{it.size==bundle.count}''')
replace('body.addView(label("Микшер продолжает играть при сворачивании. Остановить можно здесь или из уведомления.",13,muted))\n        body.addView(label("${bundle.count} дорожки · настраивайте громкость и создавайте версию. Изменения громкости слышны в режиме предпрослушивания.",14,muted))','body.addView(label("${bundle.count} дорожки · микшер играет и в фоне",13,muted))')
replace('previewSeek=SeekBar(this).apply{max=(bundle.frames/441).toInt();progress=(shownFrame/441).toInt().coerceIn(0,max);setOnSeekBarChangeListener(object:SeekBar.OnSeekBarChangeListener{override fun onStartTrackingTouch(s:SeekBar){previewDragging=true};override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){};override fun onStopTrackingTouch(s:SeekBar){val was=MixerSession.active;previewFrame=s.progress*441L;previewDragging=false;if(was)beginPreview(bundle,gains)else {previewLabel?.text="Позиция · ${fmt(previewFrame*1000/44100)}"}}})};body.addView(previewSeek!!)','''fun seekMixer(s:SeekBar){
            if(previewSeek!==s||previewSource!=source.uri)return
            previewFrame=(s.progress*441L).coerceIn(0L,bundle.frames-1)
            if(MixerSession.active)beginPreview(bundle,gains)
            else setTextChanged(previewLabel,"Микшер · "+fmt(previewFrame*1000/44100))
        }
        previewSeek=SeekBar(this).apply{
            contentDescription="Позиция микшера";minimumHeight=dp(48)
            max=(bundle.frames/441).toInt();progress=(shownFrame/441).toInt().coerceIn(0,max)
            setOnSeekBarChangeListener(object:SeekBar.OnSeekBarChangeListener{
                override fun onStartTrackingTouch(s:SeekBar){if(previewSeek===s)previewDragging=true}
                override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){if(user&&!previewDragging)seekMixer(s)}
                override fun onStopTrackingTouch(s:SeekBar){if(previewSeek===s){previewDragging=false;seekMixer(s)}}
            })
        };body.addView(previewSeek!!)''')
replace('val slider=SeekBar(this).apply{contentDescription="Громкость: ${StemCore.names[i]}";max=100;progress=(gains[i]*100).toInt();setOnSeekBarChangeListener(object:SeekBar.OnSeekBarChangeListener{override fun onStartTrackingTouch(s:SeekBar){};override fun onStopTrackingTouch(s:SeekBar){persistMixerGains(gains)};override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){if(!user)return;gains[i]=p/100f;if(MixerSession.request?.source==previewSource)MixerSession.update(gains);title.text="${StemCore.names[i]} · $p%"}})}','''val slider=SeekBar(this).apply{contentDescription="Громкость: ${StemCore.names[i]}";minimumHeight=dp(48);max=100;progress=(gains[i]*100).toInt();setOnSeekBarChangeListener(object:SeekBar.OnSeekBarChangeListener{
            private var touching=false
            override fun onStartTrackingTouch(s:SeekBar){touching=true}
            override fun onStopTrackingTouch(s:SeekBar){touching=false;if(previewSource==source.uri)persistMixerGains(gains)}
            override fun onProgressChanged(s:SeekBar,p:Int,user:Boolean){if(!user||previewSource!=source.uri)return;gains[i]=p/100f;if(MixerSession.request?.source==source.uri)MixerSession.update(gains);title.text="${StemCore.names[i]} · $p%";if(!touching)persistMixerGains(gains)}
        })}''')
replace('override fun onStop(){seekTarget=null;dragging=false;uiStarted=false;','override fun onStop(){seekTarget=null;dragging=false;previewDragging=false;uiStarted=false;')
p.write_text(s)
print('PASS: compact mixer layout, accessible seek and gain persistence')
