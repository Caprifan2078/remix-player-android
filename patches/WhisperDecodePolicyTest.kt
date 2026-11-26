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
    println("PASS: 20 Whisper decoder memory-policy checks")
}
