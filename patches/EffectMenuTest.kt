package app.remix.player
fun main(){
 val all=Presets.all
 val groups=EffectMenu.groups(all)
 check(all.size==41)
 check(groups.size==6)
 check(groups.values.flatten().size==all.size)
 check(groups.values.flatten().toSet()==all.toSet())
 check(groups.values.flatten().map{EffectMenu.title(it.name)}.distinct().size==all.size)
 check(groups.values.flatten().all{EffectMenu.title(it.name)!=it.name||it.name=="Оригинал"})
 check(EffectMenu.title("Пользовательский")=="Пользовательский")
 println("PASS: 41 stable presets grouped into 6 categories; localized unique titles and no lost DSP presets")
}
