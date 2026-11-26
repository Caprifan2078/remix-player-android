package app.remix.player
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
/** Bounded, read-only metadata extraction. Unsupported frames are ignored. */
object EmbeddedLyrics {
 private const val LIMIT=4*1024*1024
 private fun read(input:InputStream,n:Int):ByteArray {
  require(n in 0..LIMIT);val b=ByteArray(n);var p=0
  while(p<n){val k=input.read(b,p,n-p);if(k<=0)throw java.io.EOFException();p+=k};return b
 }
 private fun u(b:Byte)=b.toInt() and 255
 private fun size(b:ByteArray,p:Int,n:Int,sync:Boolean=false):Int {
  require(p>=0&&p+n<=b.size);var result=0L
  for(i in p until p+n){val x=u(b[i]);require(!sync||x<128);result=(result shl (if(sync)7 else 8))+x}
  require(result<=LIMIT);return result.toInt()
 }
 private fun clean(s:String):String?=s.trim('\u0000','\uFEFF',' ','\n','\r','\t').replace("\r\n","\n").replace('\r','\n').takeIf{it.isNotBlank()&&it.length<=500000&&it.none{c->c.isISOControl()&&c !in "\n\t"}}
 private fun charset(enc:Int)=when(enc){0->Charsets.ISO_8859_1;1->Charsets.UTF_16;2->Charsets.UTF_16BE;3->Charsets.UTF_8;else->error("Encoding")}
 private fun end(b:ByteArray,p:Int,enc:Int):Int {
  val step=if(enc in 1..2)2 else 1;var i=p
  while(i+step<=b.size){if((0 until step).all{b[i+it]==0.toByte()})return i;i+=step};return b.size
 }
 private fun decode(b:ByteArray,a:Int,z:Int,enc:Int)=String(b,a,z-a,charset(enc))
 private fun afterTerm(b:ByteArray,p:Int,enc:Int)=(end(b,p,enc)+if(enc in 1..2)2 else 1).coerceAtMost(b.size)
 private fun unsynced(b:ByteArray):String?{
  if(b.size<5)return null;val enc=u(b[0]);if(enc !in 0..3)return null
  val p=afterTerm(b,4,enc);return clean(decode(b,p,b.size,enc))
 }
 private fun synced(b:ByteArray):String? {
  if(b.size<8)return null;val enc=u(b[0]);if(enc !in 0..3||u(b[4])!=2||u(b[5])!=1)return null
  var p=afterTerm(b,6,enc);val lines=mutableListOf<Pair<Long,String>>()
  while(p<b.size&&lines.size<5000){
   val z=end(b,p,enc);val value=decode(b,p,z,enc);p=afterTerm(b,p,enc);if(p+4>b.size)return null
   var ms=0L;repeat(4){ms=(ms shl 8)+u(b[p++])};if(ms>900000)return null
   if(value.isNotBlank())lines.add(ms to value)
  }
  if(p!=b.size||lines.isEmpty()||!lines.zipWithNext().all{(a,z)->a.first<=z.first})return null
  return clean(lines.groupBy{it.first}.map{(ms,v)->"["+SubtitleCore.stamp(ms)+"]"+v.joinToString(" "){it.second.replace('\n',' ').replace('[','(').replace(']',')')}}.joinToString("\n"))
 }
 private fun id3(input:InputStream,first:ByteArray):String?{
  val h=first+read(input,6);val version=u(h[3]);val flags=u(h[5]);if(version !in 3..4||(flags and 0xc0)!=0)return null
  val tag=read(input,size(h,6,4,true));var p=0;var plain:String?=null
  while(p+10<=tag.size){
   val id=String(tag,p,4,Charsets.ISO_8859_1);if(!id.matches(Regex("[A-Z0-9]{4}")))break
   val n=size(tag,p+4,4,version==4);val flags2=u(tag[p+9]);p+=10;if(n==0||p+n>tag.size)break
   if(flags2==0&&(id=="USLT"||id=="SYLT")){
    val payload=tag.copyOfRange(p,p+n);if(id=="SYLT")synced(payload)?.let{return it}else if(plain==null)plain=unsynced(payload)
   };p+=n
  };return plain
 }
 private fun flac(input:InputStream):String?{
  var total=4;var plain:String?=null
  repeat(64){
   val h=read(input,4);val n=size(h,1,3);total+=4+n;if(total>LIMIT)return plain
   val data=read(input,n)
   if((u(h[0]) and 127)==4){
    val b=ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
    fun text():String{val n2=b.int;require(n2>=0&&n2<=b.remaining());val v=ByteArray(n2);b.get(v);return String(v,Charsets.UTF_8)}
    text();val num=b.int;require(num in 0..10000)
    repeat(num){val v=text();val k=v.substringBefore('=').uppercase(java.util.Locale.ROOT);if(k in setOf("LYRICS","UNSYNCEDLYRICS","UNSYNCED LYRICS","SYNCEDLYRICS","SYNCED LYRICS")){val raw=clean(v.substringAfter('=',""));if(raw!=null){if(Lrc.parse(raw).isNotEmpty())return raw;if(plain==null)plain=raw}}}
   }
   if((u(h[0]) and 128)!=0)return plain
  };return plain
 }
 fun read(input:InputStream):String?=runCatching{
  val h=read(input,4);when{String(h,0,3,Charsets.ISO_8859_1)=="ID3"->id3(input,h);String(h,Charsets.ISO_8859_1)=="fLaC"->flac(input);else->null}
 }.getOrNull()
}
