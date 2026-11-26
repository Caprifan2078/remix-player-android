package app.remix.player
import java.io.File
import java.net.URI
import java.net.HttpURLConnection
/** Only known official HTTPS endpoints, exact artifact bytes, no audio upload. */
object WhisperDownload {
    private val hosts=setOf("huggingface.co","cdn-lfs.huggingface.co","cdn-lfs.hf.co","cdn-lfs-us-1.hf.co","cas-bridge.xethub.hf.co","us.aws.cdn.hf.co","us.gcp.cdn.hf.co","cdn-lfs-eu-1.hf.co","transfer.xethub.hf.co","transfer.xethub-eu.hf.co")
    fun allowed(uri:URI)=uri.scheme=="https"&&uri.host?.lowercase(java.util.Locale.ROOT) in hosts&&uri.userInfo==null&&uri.fragment==null&&uri.port in listOf(-1,443)
    fun source(spec:WhisperModelSpec.Model):URI {require(spec in WhisperModelSpec.models);return URI(spec.source.replace("/blob/","/resolve/"))}
    fun redirect(from:URI,to:String)=from.resolve(to).also{require(allowed(it)){"Неподдерживаемый сервер загрузки модели"}}
    fun fetch(spec:WhisperModelSpec.Model,file:File,progress:(Int)->Unit){
        require(!file.exists());var uri=source(spec)
        try{for(hop in 0..5){
            check(!Thread.currentThread().isInterrupted){"Отменено"};require(allowed(uri))
            val c=uri.toURL().openConnection() as HttpURLConnection
            try{
                c.instanceFollowRedirects=false;c.connectTimeout=15000;c.readTimeout=20000;c.setRequestProperty("Accept-Encoding","identity")
                val code=c.responseCode
                if(code in listOf(301,302,303,307,308)){require(hop<5){"Слишком много перенаправлений"};uri=redirect(uri,c.getHeaderField("Location")?:error("Нет адреса перенаправления"));continue}
                require(code==200){"HTTP $code"};val length=c.contentLengthLong;require(length<0||length==spec.size){"Неожиданный размер файла"}
                var total=0L;var last=-1
                c.inputStream.buffered().use{input->file.outputStream().buffered().use{out->
                    val bytes=ByteArray(65536)
                    while(true){check(!Thread.currentThread().isInterrupted){"Отменено"};val n=input.read(bytes);if(n<0)break;total+=n;require(total<=spec.size&&file.parentFile!!.usableSpace>16L*1024*1024){"Недостаточно места или неверный размер"};out.write(bytes,0,n)
                        val p=(total*99/spec.size).toInt();if(p!=last){last=p;progress(p)}
                    }
                }}
                require(total==spec.size){"Загрузка не завершена"}
                require(VerifiedDownload.matches(file,spec.sha)){"SHA-256 не совпадает"};check(!Thread.currentThread().isInterrupted){"Отменено"};progress(100);return
            }finally{c.disconnect()}
        };error("Слишком много перенаправлений")}catch(e:Throwable){file.delete();throw e}
    }
}
