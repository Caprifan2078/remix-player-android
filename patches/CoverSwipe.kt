package app.remix.player
import kotlin.math.abs
object CoverSwipe {
    enum class Direction { PREVIOUS, NEXT }
    fun direction(dx:Float,dy:Float,minDistance:Float):Direction? {
        if(!dx.isFinite()||!dy.isFinite()||!minDistance.isFinite()||minDistance<=0f)return null
        if(abs(dx)<minDistance||abs(dx)<abs(dy)*1.6f)return null
        return if(dx>0)Direction.PREVIOUS else Direction.NEXT
    }
}
