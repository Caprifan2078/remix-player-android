package app.remix.player
object ModelMemoryBudget {
    const val LARGE_MODEL = 32L*1024*1024
    const val MIN_FREE = 4L*1024*1024*1024
    const val SMALL_MIN_FREE = 64L*1024*1024
    // Conservative admission policy, not a bound on native inference memory.
    fun canStart(bytes:Long,available:Long,lowMemory:Boolean):Boolean {
        if(bytes<=0 || available<=0 || lowMemory || bytes>available/4)return false
        return available>=if(bytes<=LARGE_MODEL) SMALL_MIN_FREE else MIN_FREE
    }
}
