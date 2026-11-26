package app.remix.player

/** State reflects the actual saved text first; an error must never hide a usable lyric. */
object LyricScanState {
    enum class State(val label:String){ WORDS("По словам"), LINES("По строкам"), PLAIN("Без времени"), REVIEW("Нужна проверка"), MISSING("Не найдено"), ERROR("Ошибка"), NEW("Не проверено") }
    fun classify(hasText:Boolean, hasLines:Boolean, allWords:Boolean, draft:Boolean, attempt:String?):State=when{
        hasText&&hasLines&&allWords->State.WORDS
        hasText&&hasLines->State.LINES
        hasText->State.PLAIN
        draft->State.REVIEW
        attempt=="error"->State.ERROR
        attempt=="done"->State.MISSING
        else->State.NEW
    }
    fun needsReview(state:State)=state in setOf(State.PLAIN,State.REVIEW,State.MISSING,State.ERROR)
    fun pending(state:State,attempted:Boolean,retry:Boolean):Boolean = state!=State.WORDS && if(retry) needsReview(state)||state==State.LINES else !attempted
    data class Match(val text:String,val matched:Int,val total:Int,val aligned:String?)
    /** Never auto-accept competing distinct texts, or one without observed timing. */
    fun choose(matches:List<Match>):String?=matches.filter{it.total>0&&it.matched>=5&&it.matched.toDouble()/it.total>=.55&& !it.aligned.isNullOrBlank()}.distinctBy{it.text}.singleOrNull()?.aligned
}
