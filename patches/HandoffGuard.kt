package app.remix.player
internal object HandoffGuard {
    enum class Action { WAIT, BLEND, RESYNC, CUT, CUT_FORWARD }
    fun decide(primary:Long,preview:Long,elapsed:Long,ready:Boolean,resynced:Boolean):Action {
        if(primary<0||preview<0||elapsed<0)return Action.CUT
        val behind=preview>primary&&preview-primary>150
        val aligned=if(preview>=primary)preview-primary<=150 else primary-preview<=150
        if(elapsed>=1800)return if(behind)Action.CUT_FORWARD else Action.CUT
        if(!ready)return Action.WAIT
        if(aligned)return Action.BLEND
        if(behind&&elapsed>=350&&!resynced)return Action.RESYNC
        return Action.WAIT
    }
}
