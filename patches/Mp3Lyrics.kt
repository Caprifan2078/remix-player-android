package app.remix.player
import java.io.*
import java.security.MessageDigest
/** Conservative ID3v2.3/2.4 copy writer. Reject unsupported tag features instead of losing metadata. */
internal object Mp3Lyrics {
    private const val LIMIT=16*1024*1024
    private fun sync(n:Int)=byteArrayOf((n ushr 21 and 127).toByte(),(n ushr 14 and 127).toByte(),(n ushr 7 and 127).toByte(),(n and 127).toByte())
    private fun size(b:ByteArray,p:Int,sync:Boolean):Int {var n=0L;for(i in p until p+4){val v=b[i].toInt() and 255;require(!sync||v<128);n=(n shl (if(sync)7 else 8))+v};require(n<=LIMIT);return n.toInt()}
    private fun length(n:Int,v:Int)=if(v==4)sync(n)else byteArrayOf((n ushr 24).toByte(),(n ushr 16).toByte(),(n ushr 8).toByte(),n.toByte())
    private fun mpeg(h:ByteArray):Boolean {val b=h.map{it.toInt() and 255};return b.size>=4&&b[0]==255&&b[1] and 224==224&&b[1] and 24!=8&&b[1] and 6==2&&b[2] ushr 4 in 1..14&&(b[2] ushr 2 and 3)!=3}
    private fun frame(id:String,body:ByteArray,v:Int)=id.toByteArray(Charsets.US_ASCII)+length(body.size,v)+byteArrayOf(0,0)+body
    private fun utf(s:String)=if(s.isEmpty())byteArrayOf(0xfe.toByte(),0xff.toByte())else s.toByteArray(Charsets.UTF_16)
    fun write(input:InputStream,output:OutputStream,plain:String,lrc:String):String {
        require(plain.isNotBlank()&&plain.length<=500000&&lrc.length<=500000&&'\u0000' !in plain&&'\u0000' !in lrc)
        val r=DataInputStream(input);val h=ByteArray(10);r.readFully(h);var version=3;val kept=ByteArrayOutputStream();val first:ByteArray
        if(h.copyOfRange(0,3).contentEquals("ID3".toByteArray())){
            version=h[3].toInt();require(version in 3..4&&h[4].toInt()==0&&h[5].toInt()==0){"Unsupported ID3 tag; original unchanged"}
            val tag=ByteArray(size(h,6,true));r.readFully(tag);var p=0
            while(p<tag.size){if(tag[p]==0.toByte()){require((p until tag.size).all{tag[it]==0.toByte()});break};require(tag.size-p>=10)
                val id=String(tag,p,4,Charsets.US_ASCII);require(id.matches(Regex("[A-Z0-9]{4}")));val n=size(tag,p+4,version==4);require(n>0&&n<=tag.size-p-10);require(tag[p+8]==0.toByte()&&tag[p+9]==0.toByte()){ "Unsupported ID3 frame flags" }
                if(id!="USLT"&&id!="SYLT")kept.write(tag,p,n+10)
                p+=n+10
            };first=ByteArray(4);r.readFully(first)
        }else first=h
        require(mpeg(first)){"Not a supported MPEG Layer III file"}
        fun lyrics(desc:String,text:String)=byteArrayOf(1)+"und".toByteArray(Charsets.US_ASCII)+utf(desc)+byteArrayOf(0,0)+utf(text)
        kept.write(frame("USLT",lyrics("",plain),version));if(lrc.isNotBlank()&&lrc!=plain)kept.write(frame("USLT",lyrics("LRC",lrc),version))
        require(kept.size()<=LIMIT);output.write("ID3".toByteArray());output.write(byteArrayOf(version.toByte(),0,0));output.write(sync(kept.size()));kept.writeTo(output)
        val digest=MessageDigest.getInstance("SHA-256");output.write(first);digest.update(first);val buf=ByteArray(65536)
        while(true){check(!Thread.currentThread().isInterrupted){"Cancelled"};val n=r.read(buf);if(n<0)break;if(n>0){output.write(buf,0,n);digest.update(buf,0,n)}}
        return digest.digest().joinToString(""){"%02x".format(it)}
    }
}
