package app.remix.player

/** Crossfade two DSP states for 24 ms. Keep only the newest request during an in-flight switch. */
class LiveEffectSwitch(private val rate:Int,private val channels:Int){
    private val frames=(rate*24/1000).coerceAtLeast(1)
    private var active:Dsp=Dsp(rate,channels)
    private var current:Preset?=null
    private var incoming:Dsp?=null
    private var next:Preset?=null
    private var elapsed=0
    private val oldFrame=FloatArray(channels)
    private val newFrame=FloatArray(channels)
    fun frame(input:FloatArray,out:FloatArray,preset:Preset){
        if(current==null)current=preset
        if(incoming==null&&current!=preset){incoming=Dsp(rate,channels);next=preset;elapsed=0}
        val target=incoming
        if(target==null){active.frame(input,out,current!!);return}
        active.frame(input,oldFrame,current!!)
        target.frame(input,newFrame,next!!)
        val mix=elapsed.toFloat()/frames
        for(c in 0 until channels)out[c]=oldFrame[c]+(newFrame[c]-oldFrame[c])*mix
        if(++elapsed>=frames){active=target;current=next;incoming=null;next=null;elapsed=0}
    }
}
