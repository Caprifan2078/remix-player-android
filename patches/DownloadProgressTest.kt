package app.remix.player
import java.io.*
import java.net.*
import java.security.MessageDigest
fun main(){
 val data=ByteArray(100000){(it*17).toByte()};val sha=MessageDigest.getInstance("SHA-256").digest(data).joinToString(""){"%02x".format(it)}
 var length=data.size.toLong();var body=data;var status=200
 URL.setURLStreamHandlerFactory{protocol->if(protocol!="https")null else object:URLStreamHandler(){override fun openConnection(u:URL)=object:HttpURLConnection(u){override fun connect(){};override fun disconnect(){};override fun usingProxy()=false;override fun getResponseCode()=status;override fun getContentLengthLong()=length;override fun getInputStream():InputStream=ByteArrayInputStream(body)}}}
 val dir=kotlin.io.path.createTempDirectory("model-download-test").toFile();val target=File(dir,"model.tmp")
 try{
  val progress=mutableListOf<Int>();VerifiedDownload.fetch("https://qa.invalid/model",sha,target){progress.add(it)}
  check(target.readBytes().contentEquals(data));check(progress.last()==100&&progress.count{it==100}==1&&progress.zipWithNext().all{(a,b)->a<b});target.delete()
  fun rejected(expected:String=sha,callback:((Int)->Unit)?=null){val events=mutableListOf<Int>();val result=try{runCatching{VerifiedDownload.fetch("https://qa.invalid/model",expected,target){events.add(it);callback?.invoke(it)}}}finally{Thread.interrupted()};check(result.isFailure);check(!target.exists());check(100 !in events){"Reported completion before validation: $events"}}
  rejected("0".repeat(64));length=data.size.toLong()+1;rejected();length=data.size.toLong();status=503;rejected();status=200;rejected(callback={Thread.currentThread().interrupt()})
  body=ByteArray(0);length=0;rejected();body=data;length=601L*1024*1024;rejected()
  println("PASS: valid transfer; wrong checksum; truncation; HTTP error; cancellation; empty and oversized response")
 }finally{dir.deleteRecursively()}
}
