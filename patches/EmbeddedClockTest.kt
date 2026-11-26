package app.remix.player
import java.io.ByteArrayInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
fun main(){
 fun be(n:Int)=ByteBuffer.allocate(4).putInt(n).array()
 fun le(n:Int)=ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(n).array()
 fun syn(n:Int)=byteArrayOf((n shr 21 and 127).toByte(),(n shr 14 and 127).toByte(),(n shr 7 and 127).toByte(),(n and 127).toByte())
 fun id3(name:String,p:ByteArray):ByteArray{val frame=name.toByteArray()+be(p.size)+byteArrayOf(0,0)+p;return "ID3".toByteArray()+byteArrayOf(3,0,0)+syn(frame.size)+frame}
 fun read(b:ByteArray)=EmbeddedLyrics.read(ByteArrayInputStream(b))
 check(read(id3("USLT",byteArrayOf(3)+"eng".toByteArray()+byteArrayOf(0)+"first\nsecond".toByteArray()))=="first\nsecond")
 val timed=byteArrayOf(3)+"eng".toByteArray()+byteArrayOf(2,1,0)+"hello".toByteArray()+byteArrayOf(0)+be(1230)+"world".toByteArray()+byteArrayOf(0)+be(2400)
 check(read(id3("SYLT",timed))=="[00:01.230]hello\n[00:02.400]world")
 check(read(id3("SYLT",timed.copyOf(timed.size-1)))==null)
 check(read(byteArrayOf(1,2,3,4))==null)
 val comment="LYRICS=[00:02.00]hello".toByteArray();val block=le(0)+le(1)+le(comment.size)+comment
 check(read("fLaC".toByteArray()+byteArrayOf(0x84.toByte(),0,0,block.size.toByte())+block)=="[00:02.00]hello")
 val m=LyricClock.mapping(LyricClock.Anchor(10000,12000),LyricClock.Anchor(40000,45000))
 check(m.at(10000)==12000L&&m.at(40000)==45000L)
 check(LyricClock.correct("[00:10.000]<00:10.000>first\n[00:40.000]second",m)=="[00:12.000]<00:12.000>first\n[00:45.000]second")
 check(LyricClock.mapping(LyricClock.Anchor(1000,3000)).at(5000)==7000L)
 check(runCatching{LyricClock.mapping(LyricClock.Anchor(1000,1000),LyricClock.Anchor(2000,2000))}.isFailure)
 check(LyricClock.correct("[offset:1000]\n[00:01.000]test",LyricClock.Mapping(1.0,2000.0))=="[00:04.000]test")
 println("PASS: embedded tag parsing and calibration (10 cases)")
}
