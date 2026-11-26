package app.remix.player
fun main(){
 val sad=MoodDiscovery.Features(.23,.20,.30,.35,.20,.40)
 val gym=MoodDiscovery.Features(.87,.88,.50,.72,.8,.30)
 val uncertain=sad.copy(valence=null)
 val p=MoodDiscovery.profiles.associateBy{it.title}
 check(p.size==8)
 check(MoodDiscovery.score(sad,p.getValue("Меланхолия"))!!>.95)
 check(MoodDiscovery.score(gym,p.getValue("Меланхолия"))==null)
 check(MoodDiscovery.score(uncertain,p.getValue("Меланхолия"))==null)
 check(MoodDiscovery.score(gym,p.getValue("Тренировка"))!!>.95)
 check(MoodDiscovery.score(sad,p.getValue("Тренировка"))==null)
 val rows=listOf(MoodDiscovery.Entry("1","A",sad),MoodDiscovery.Entry("2","A",sad),MoodDiscovery.Entry("3","B",sad),MoodDiscovery.Entry("1","A",sad))
 check(MoodDiscovery.rank(rows,p.getValue("Меланхолия"))==listOf("1","3","2"))
 check(MoodDiscovery.rank(rows,p.getValue("Меланхолия"),2)==listOf("1","3"))
 val unknown=listOf(MoodDiscovery.Entry("1","",sad),MoodDiscovery.Entry("2","A",sad.copy(energy=.30)))
 check(MoodDiscovery.rank(unknown,p.getValue("Меланхолия")).first()=="1")
 val r=MusicAnalysis.Report(null,null,null,0.0,0.0,20.0,listOf(0.0,0.0))
 check(MoodDiscovery.from(r)==null)
 val spec=SoundProfile.Features(.35,.5,.15,500.0,30)
 val frame=SectionMap.Frame(0.0,.04,.35,.5,.15,.20,List(12){1.0/12})
 val measured=r.copy(key="A minor",keyConfidence=.15,rms=.04,energy=listOf(.02,.04,.06,.08,.09),spectrum=spec,featureFrames=listOf(frame))
 val actual=MoodDiscovery.from(measured)!!
 check(actual.valence==.2&&actual.activity==.2)
 check(MoodDiscovery.from(measured.copy(keyConfidence=0.0))!!.valence==null)
 val many=(0 until 10000).map{MoodDiscovery.Entry(it.toString(),"Artist "+it%50,sad)}
 check(MoodDiscovery.rank(many,p.getValue("Меланхолия"),100).distinct().size==100)
 println("PASS: 13 mood ranking checks including 10,000-entry library")
}
