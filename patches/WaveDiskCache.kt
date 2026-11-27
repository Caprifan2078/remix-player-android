package app.remix.player
import android.content.Context
import android.net.Uri
import android.provider.DocumentsContract
import android.provider.MediaStore
import java.io.*
import java.security.MessageDigest

/** Exact peaks only. Reuse across process starts only when provider supplies a size and modification stamp. */
internal object WaveDiskCache {
    private const val VERSION=1
    private fun fingerprint(c:Context,u:Uri):String?{
        fun probe(modified:String):Pair<Long,Long>?=runCatching{
            c.contentResolver.query(u,arrayOf("_size",modified),null,null,null)?.use{cursor->
                if(!cursor.moveToFirst()||cursor.isNull(0)||cursor.isNull(1))null else (cursor.getLong(0) to cursor.getLong(1)).takeIf{it.first>0&&it.second>0}
            }
        }.getOrNull()
        val meta=probe(DocumentsContract.Document.COLUMN_LAST_MODIFIED)?:probe(MediaStore.MediaColumns.DATE_MODIFIED)?:return null
        val bytes=MessageDigest.getInstance("SHA-256").digest(("$VERSION|$u|"+meta.first+"|"+meta.second).toByteArray(Charsets.UTF_8))
        return bytes.joinToString(""){"%02x".format(it.toInt() and 255)}
    }
    fun readOrDecode(c:Context,u:Uri):FloatArray?{
        val key=fingerprint(c,u)?:return WaveReader.read(c,u)
        val dir=File(c.cacheDir,"wave-v1").apply{mkdirs()}
        val file=File(dir,key)
        if(file.isFile){
            val cached=runCatching{DataInputStream(BufferedInputStream(file.inputStream())).use{input->
                require(file.length()==644L&&input.readInt()==VERSION)
                FloatArray(160){input.readFloat().also{require(it.isFinite()&&it in 0f..1f)}}
            }}.getOrNull()
            if(cached!=null){file.setLastModified(System.currentTimeMillis());return cached}
            file.delete()
        }
        val value=WaveReader.read(c,u)?:return null
        if(Thread.currentThread().isInterrupted||value.size!=160||fingerprint(c,u)!=key)return value
        runCatching{
            val tmp=File.createTempFile("wave-",".tmp",dir)
            try{DataOutputStream(BufferedOutputStream(tmp.outputStream())).use{out->out.writeInt(VERSION);value.forEach{out.writeFloat(it)}};if(!Thread.currentThread().isInterrupted)tmp.renameTo(file)}finally{tmp.delete()}
            dir.listFiles()?.filter{it.isFile&&it.name.length==64}?.sortedByDescending{it.lastModified()}?.drop(128)?.forEach{it.delete()}
        }
        return value
    }
}
