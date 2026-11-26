package app.remix.player
import java.io.*
import java.security.MessageDigest
fun main(args:Array<String>){
    val input=File(args[0]);val out=File(args[1]);val before=input.readBytes();val digest=input.inputStream().use{r->out.outputStream().use{w->Mp3Lyrics.write(r,w,"Привет мир\nHello world","[00:01.00]Привет мир")}}
    fun payload(bytes:ByteArray):ByteArray {if(String(bytes,0,3)!="ID3")return bytes;val n=(6..9).fold(0){a,i->(a shl 7)+(bytes[i].toInt() and 127)};return bytes.copyOfRange(10+n,bytes.size)}
    check(payload(before).contentEquals(payload(out.readBytes())));check(before.contentEquals(input.readBytes()));check(digest==MessageDigest.getInstance("SHA-256").digest(payload(before)).joinToString(""){"%02x".format(it)})
    val rewritten=ByteArrayOutputStream();out.inputStream().use{Mp3Lyrics.write(it,rewritten,"Новый текст","[00:02.00]Новый текст")};check(payload(rewritten.toByteArray()).contentEquals(payload(before)))
    val old=out.readBytes();val bad=old.copyOf().also{it[5]=128.toByte()};val reject=ByteArrayOutputStream();check(runCatching{Mp3Lyrics.write(bad.inputStream(),reject,"x","")}.isFailure&&reject.size()==0)
    check(runCatching{Mp3Lyrics.write(ByteArray(20).inputStream(),ByteArrayOutputStream(),"x","")}.isFailure)
    println("PASS MP3 payload identity, original unchanged, replacement, unsupported flags and malformed file; SHA256 $digest")
}
