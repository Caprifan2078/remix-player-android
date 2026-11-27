package app.remix.player

/** Bounded, duration-aware live overlap. No claims of live BPM matching. */
internal object SmartCrossfade {
    const val DEFAULT_MS=5000L
    fun enabled(stored:Boolean?,hasDuration:Boolean):Boolean=stored?:!hasDuration
    fun duration(current:Long,next:Long,maximum:Long):Long {
        if(current<2000||next<2000||maximum !in 1000L..8000L)return 0L
        // Short tracks keep their intro/outro. Long songs use the user's cap.
        return (minOf(current,next)/10).coerceIn(1000L,maximum)
    }
}
