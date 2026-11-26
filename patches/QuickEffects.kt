package app.remix.player
object QuickEffects {
    private val ids=listOf("Оригинал","Sped Up","Slowed + Reverb","Nightcore","Slowed","Bass Boost","8D Audio")
    fun defaults(presets:List<Preset>)=ids.mapNotNull{n->presets.firstOrNull{it.name==n}}
    fun extra(presets:List<Preset>)=presets.filterNot{p->p.name in ids}
    fun subtitle(p:Preset):String = when(p.name){
        "Оригинал"->"Без обработки"
        "Sped Up"->"Темп +25% · исходный тон · лёгкая плотность и пространство"
        "Slowed + Reverb"->"Темп −15% · понижение тона · реверберация и низ"
        "Nightcore"->"Темп и тон +25% · лёгкая сатурация и пространство"
        "Slowed"->"Медленнее · исходный тон"
        "Bass Boost"->"Выразительные низкие частоты"
        "8D Audio"->"Пространственное движение"
        else->buildList{
 if(p.speed!=1f)add("Темп ×"+p.speed)
 if(p.pitch!=1f)add("Тон ×"+p.pitch)
 if(p.bass>0)add("Усиление низких частот")
 if(p.room>0)add("Реверберация")
 if(p.pan>0)add("Стереодвижение")
 if(p.drive>0)add("Сатурация / искажение")
 if(p.muffled>0)add("Смягчение высоких частот")
 }.joinToString(" · ").ifBlank{"Без обработки"}
    }
}
