package app.remix.player
object QuickEffects {
    private val ids=listOf("Оригинал","Sped Up","Slowed + Reverb","Nightcore","Slowed","Bass Boost","8D Audio")
    fun defaults(presets:List<Preset>)=ids.mapNotNull{n->presets.firstOrNull{it.name==n}}
    fun extra(presets:List<Preset>)=presets.filterNot{p->p.name in ids}
    fun subtitle(p:Preset):String = when(p.name){
        "Оригинал"->"Без обработки"
        "Sped Up"->"Быстрее · исходный тон"
        "Slowed + Reverb"->"Медленнее · реверберация"
        "Nightcore"->"Быстрее · выше тон"
        "Slowed"->"Медленнее · исходный тон"
        "Bass Boost"->"Выразительные низкие частоты"
        "8D Audio"->"Пространственное движение"
        else->"Темп ×"+p.speed
    }
}
