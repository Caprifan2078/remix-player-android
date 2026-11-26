package app.remix.player
/** Separate procedural templates; original symbolic-model indices stay stable. */
object ProducerStyles {
 data class Profile(val style:GenreEngine.Style,val family:String,val description:String)
 val extra=listOf(
  Profile(GenreEngine.Style("Euphoric Hardstyle",150,intArrayOf(0,4,8,12),intArrayOf(4,12,15),intArrayOf(2,6,10,14),0.58f,0.02f,1.16f),"Hardstyle","Мелодичный хардстайл: плотный кик и гармонический лид."),
  Profile(GenreEngine.Style("Xtra Raw",160,intArrayOf(0,4,7,8,12,14),intArrayOf(4,12),intArrayOf(2,6,9,14,15),1.00f,0.00f,1.03f),"Rawstyle","Рваный ритм, жёсткий насыщенный кик."),
  Profile(GenreEngine.Style("Uptempo Hardcore",210,intArrayOf(0,2,4,6,8,10,12,14,15),intArrayOf(4,12),intArrayOf(1,5,9,13),0.99f,0.00f,1.08f),"Hardcore","Частые жёсткие удары и экстремальный темп."),
  Profile(GenreEngine.Style("Schranz",160,intArrayOf(0,4,8,12),intArrayOf(3,7,11,15),intArrayOf(1,2,5,6,9,10,13,14),0.88f,0.02f,1.08f),"Hard Techno","Индустриальный пульс и плотная перкуссия."),
  Profile(GenreEngine.Style("Hard Bounce",148,intArrayOf(0,4,8,10,12,15),intArrayOf(4,12),intArrayOf(2,5,6,10,14),0.46f,0.05f,1.24f),"Jumpstyle","Пружинящий бас и удары между долями."),
  Profile(GenreEngine.Style("Psy Hard",150,intArrayOf(0,4,8,12),intArrayOf(4,12),intArrayOf(1,2,3,5,6,7,9,10,11,13,14,15),0.66f,0.02f,1.18f),"Hard Techno","Прямой кик, частые хэты и басовые импульсы."),
  Profile(GenreEngine.Style("Mandelão",132,intArrayOf(0,3,5,8,11,14),intArrayOf(3,7,10,15),intArrayOf(2,5,9,13),0.74f,0.00f,1.26f),"Brazilian Funk","Бразильские синкопы и плотный низ."),
  Profile(GenreEngine.Style("Montagem Hard",142,intArrayOf(0,2,5,8,10,13,15),intArrayOf(4,7,12,14),intArrayOf(1,3,6,9,13,15),0.97f,0.00f,1.27f),"Montagem","Агрессивный montagem с резкими акцентами."),
  Profile(GenreEngine.Style("Jersey Bounce",150,intArrayOf(0,4,8,10,12,13,15),intArrayOf(4,12),intArrayOf(2,6,9,14),0.31f,0.05f,1.13f),"Jersey Club","Подпрыгивающий рисунок кика и сбивки."),
  Profile(GenreEngine.Style("UK Speed Bass",138,intArrayOf(0,6,8,10,14),intArrayOf(4,12),intArrayOf(2,3,6,9,11,14,15),0.35f,0.05f,1.26f),"Speed Garage","Ломаный гаражный ритм, свинг и усиленный низ.")
 )
 val all get()=GenreEngine.styles+extra.map{it.style}
 fun family(s:GenreEngine.Style)=extra.firstOrNull{it.style.name==s.name}?.family?:s.name
 private val names=listOf("Hardstyle","Jumpstyle","Hardtekk","Euphoric Hardstyle","Rawstyle","Xtra Raw","Uptempo Hardcore","Hard Techno","Brazilian Phonk","Montagem","Montagem Hard","Mandelão","Automotivo","Drift Phonk","Jersey Club","Drum & Bass")
 fun featured()=names.map{n->all.single{it.name==n}}
 fun more()=all.filterNot{it.name in names}
 fun describe(s:GenreEngine.Style)=extra.firstOrNull{it.style.name==s.name}?.description?:when(s.name){
 "Hardstyle","Rawstyle","Hardcore","Frenchcore","Hardtekk","Hard Techno"->"Плотный искажённый кик, бас и синтезатор."
 "Jumpstyle"->"Прыгающий ритм с дополнительными ударами."
 "Drift Phonk","Brazilian Phonk","Memphis Phonk","House Phonk","Montagem","Automotivo","Krushfunk","Brazilian Funk"->"Синкопированный ритм, насыщенный низ."
 "Drum & Bass","Breakcore"->"Быстрые ломаные ударные и бас."
 "UK Garage","Speed Garage","Jersey Club"->"Клубные сбивки и свинг."
 "Lo-Fi","Synthwave"->"Мягкая перкуссия и атмосферный звук."
 "Trap","Dubstep"->"Половинный ритм, низкий бас."
 else->"Новые ударные, гармонический бас и лид."
 }
}
