package app.remix.player
fun main(){
    val extra=512L*1024*1024
    for(m in WhisperModelSpec.models){
        val expected=if(m.id=="tiny")1 else 3
        check(m.beamSize(m.minFreeRam+extra,false)==expected)
        check(m.beamSize(m.minFreeRam+extra-1,false)==1)
        check(m.beamSize(Long.MAX_VALUE,true)==1)
        check(m.beamSize(0,false)==1)
    }
    check(WhisperModelSpec.models.size==8)
    check(WhisperModelSpec.maxBytes==1081140203L)
    check(WhisperModelSpec.bySize(574041195L)?.id=="large-v3-turbo-q5_0")
    check(WhisperModelSpec.bySize(539212467L)?.id=="medium-q5_0")
    check(WhisperModelSpec.models.all{it.description.isNotBlank()})
    check(WhisperModelSpec.models.filter{it.id.startsWith("large")||it.id.startsWith("medium")}.all{it.revision.matches(Regex("[a-f0-9]{40}"))})
    println("PASS: 38 Whisper model catalog and decoder memory-policy checks")
}
