package app.remix.player
internal object PlaybackCadence {
    fun delay(playing:Boolean, position:Long,duration:Long,fade:Long,overlap:Long,loop:Boolean,sleepRemaining:Long?,mixing:Boolean=false):Long {
        val normal=when {
            mixing->25L
            !playing->2000L
            loop->50L
            duration<=0L&&(fade>0||overlap>0)->500L
            fade>0&&overlap==0L&&position<=fade+500L->50L
            duration>0L&&overlap>0&&duration-position<=overlap+5500L->25L
            duration>0L&&fade>0&&overlap==0L&&duration-position<=fade+500L->50L
            fade>0||overlap>0->500L
            else->2000L
        }
        return if(sleepRemaining==null)normal else minOf(normal,sleepRemaining.coerceIn(1L,2000L))
    }
}
