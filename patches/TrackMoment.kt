package app.remix.player
internal object TrackMoment {
    fun position(saved:Long?,duration:Long):Long? = saved?.takeIf{duration>0&&it>=0&&it<duration}
    fun canApply(expected:String?,actual:String?,mixing:Boolean,seekable:Boolean)=!mixing&&seekable&&!expected.isNullOrBlank()&&expected==actual
}
