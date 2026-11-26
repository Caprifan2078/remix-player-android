package app.remix.player

import kotlin.math.abs

/** Tracks the furthest actually audible incoming position, not the planned fade duration. */
class OverlapHandoff {
    var audibleUntil:Long=0L
        private set
    fun observe(position:Long,duration:Long,volume:Float){
        if(duration>0&&position>=0&&volume.isFinite()&&volume>0f){
            audibleUntil=maxOf(audibleUntil,position.coerceAtMost(duration-1))
        }
    }
    fun reset(){audibleUntil=0L}
    fun target(position:Long,duration:Long):Long {
        if(duration<=0)return audibleUntil
        return maxOf(audibleUntil,position.coerceAtLeast(0)).coerceAtMost(duration-1)
    }
    /** An elapsed timeout is not proof that the decoder has reached the audible intro. */
    fun aligned(primary:Long,preview:Long,previewPlaying:Boolean):Boolean {
        if(primary<0||preview<0||primary<audibleUntil-80)return false
        return if(previewPlaying)abs(primary-preview)<=120 else primary>=audibleUntil-80
    }
}
