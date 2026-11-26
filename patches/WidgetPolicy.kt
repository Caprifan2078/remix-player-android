package app.remix.player
internal object WidgetPolicy {
    enum class Size { COMPACT, MIX, STUDIO }
    fun size(width:Int,height:Int)=when {
        width>=280&&height>=184->Size.STUDIO
        width>=230&&height>=116->Size.MIX
        else->Size.COMPACT
    }
    val effects=mapOf("fast" to "Sped Up + Bass","night" to "Nightcore + Bass","slow" to "Slowed + Reverb","reset" to "Оригинал")
    val routes=setOf("edit","save","genres","lyrics")
    fun allowed(expected:String?,current:String?,mixing:Boolean)=!mixing&&!expected.isNullOrBlank()&&expected==current
    fun selection(command:String,active:String):String?=effects[command]?.let{if(it==active)"Оригинал" else it}
}
