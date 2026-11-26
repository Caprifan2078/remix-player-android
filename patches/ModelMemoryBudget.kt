package app.remix.player
object ModelMemoryBudget {
    const val LARGE_MODEL = 32L*1024*1024
    const val MIN_FREE = 4L*1024*1024*1024
    fun canStart(bytes:Long,available:Long,lowMemory:Boolean):Boolean =
        bytes>0 && (bytes<=LARGE_MODEL || (!lowMemory&&available>=MIN_FREE))
}
