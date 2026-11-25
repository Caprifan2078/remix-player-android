package app.remix.player
import java.io.*
import java.nio.file.Files
import java.util.zip.*
import kotlin.random.Random
fun main(){
 val r=Random(66);val root=Files.createTempDirectory("remix-adversarial").toFile()
 try{
 val names=listOf("../escape.wav","audio/../escape.wav","audio/../../escape.wav","/audio/0.wav","audio\\0.wav","audio/00.wav","audio/1.wav","audio/0.WAV","audio/0.exe","audio/0.wav/","audio/0.wav\u0000","audio//0.wav","./audio/0.wav","audio/0.wav/../0.wav")
 for((i,n) in names.withIndex()){
 val bytes=ByteArrayOutputStream();ZipOutputStream(bytes).use{z->fun entry(name:String,b:ByteArray){z.putNextEntry(ZipEntry(name));z.write(b);z.closeEntry()};entry("remix-backup-v1","1".toByteArray());entry("library.json","{}".toByteArray());entry(n,byteArrayOf(1,2,3));entry("complete",byteArrayOf(82,80,66,1))}
 val d=File(root,"bad-$i");val err=runCatching{BackupCore.read(bytes.toByteArray().inputStream(),d)}.exceptionOrNull();check(err is IllegalArgumentException && err.message=="Недопустимая запись архива"){"$n $err"};check(!d.exists())}
 repeat(100){i->val data=ByteArray(r.nextInt(1,8193));r.nextBytes(data);val out=ByteArrayOutputStream();val meta="{\"id\":$i}".toByteArray();BackupCore.write(out,meta,listOf(BackupCore.Item("wav"){data.inputStream()}));val zip=out.toByteArray();val d=File(root,"good-$i");val back=BackupCore.read(zip.inputStream(),d);check(back.metadata.contentEquals(meta));check(back.files.single().readBytes().contentEquals(data));d.deleteRecursively();val trunc=File(root,"trunc-$i");check(runCatching{BackupCore.read(zip.copyOf(zip.size/3).inputStream(),trunc)}.isFailure);check(!trunc.exists())}
 println("PASS: 14 hostile paths; 100 random backup round trips; 100 truncation rollbacks")
 repeat(10000){val raw=buildString{append("[offset:").append(r.nextLong(-100000,100001)).append("]\n");repeat(r.nextInt(1,12)){append("[").append(r.nextInt(1000)).append(":").append(r.nextInt(100).toString().padStart(2,'0')).append('.').append(r.nextInt(1000)).append("]<00:01.250>привет <00:02.000>мир\n")}};val lines=Lrc.parse(raw);check(lines.zipWithNext().all{(a,b)->a.ms<=b.ms});check(lines.all{it.ms in 0..Lrc.MAX_MS});val p=r.nextLong(-10000,Lrc.MAX_MS+10001);check(Lrc.current(lines,p)==lines.indexOfLast{it.ms<=p});for(l in lines){val w=WordLyrics.parse(l);check(w.words.zipWithNext().all{(a,b)->a.ms<=b.ms});check(w.words.all{it.start>=0&&it.end<=w.text.length&&it.start<it.end&&it.ms>=l.ms});check(WordLyrics.current(w,p)==w.words.indexOfLast{it.ms<=p})}}
 println("PASS: 10,000 randomized LRC inputs: timestamps, word bounds, binary lookup vs linear reference")
 }finally{root.deleteRecursively()}
}
