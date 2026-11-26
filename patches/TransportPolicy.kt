package app.remix.player
internal object TransportPolicy {
    val speeds=mapOf("speed80" to .8f,"speed100" to 1f,"speed125" to 1.25f,"speed150" to 1.5f)
    fun target(command:String,position:Long,duration:Long,seekable:Boolean):Long? {
        if(!seekable||duration<=0)return null
        val p=position.coerceIn(0,duration)
        return when(command){
            "back10"->(p-10000).coerceAtLeast(0)
            "forward10"->p+minOf(10000,duration-p)
            "quarter"->duration/4
            "middle"->duration/2
            "threequarters"->duration-duration/4
            else->null
        }
    }
}
