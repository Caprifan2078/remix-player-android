package app.remix.player
import java.io.*
fun main(){
    val rng=kotlin.random.Random(42)
    for(n in listOf(0,1,8191,8192,8193,32769)) {
        val bytes=ByteArray(n*4);rng.nextBytes(bytes);val out=ByteArrayOutputStream();val seen=mutableListOf<Long>()
        check(PcmBlockCopy.copy(ByteArrayInputStream(bytes),out,n.toLong(),17){seen.add(it)}==17L+n)
        check(out.toByteArray().contentEquals(bytes));check(seen.drop(1).all{it%8192==0L})
    }
    check(runCatching{PcmBlockCopy.copy(ByteArrayInputStream(ByteArray(3)),ByteArrayOutputStream(),1,0){} }.isFailure)
    Thread.currentThread().interrupt();try{check(runCatching{PcmBlockCopy.copy(ByteArrayInputStream(ByteArray(4)),ByteArrayOutputStream(),1,0){} }.isFailure)}finally{Thread.interrupted()}
    println("PASS: exact PCM bytes, progress boundaries, EOF and cancellation")
}
