package app.remix.player

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.core.content.FileProvider
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
import java.io.File
import java.io.ByteArrayOutputStream
import java.io.ByteArrayInputStream
import java.security.MessageDigest
import java.util.zip.ZipInputStream
import kotlin.math.sin

/** Real Android filesystem, FileProvider and MediaCodec; generated audio only. */
@RunWith(AndroidJUnit4::class)
class StudioAcceptanceTest {
    private val c=InstrumentationRegistry.getInstrumentation().targetContext
    private fun folder()=File(File(c.filesDir,"mixes").apply{mkdirs()},"qa-studio-"+java.util.UUID.randomUUID()).apply{check(mkdirs())}
    private fun raw(f:File,n:Int=44100,freq:Double=440.0){
        f.outputStream().buffered().use{w->repeat(n){i->val v=(sin(2*Math.PI*i*freq/44100)*4000).toInt().toShort();StemCore.writeShort(w,v);StemCore.writeShort(w,(-v).toShort())}}
    }
    private fun wav(raw:File,out:File){
        out.outputStream().buffered().use{w->StemCore.header(w,raw.length()/4);raw.inputStream().use{it.copyTo(w)}}
    }
    private fun decode(f:File,dst:File)=StemEngine.decode(c,FileProvider.getUriForFile(c,"app.remix.player.files",f),dst)
    private fun hash(f:File)=MessageDigest.getInstance("SHA-256").digest(f.readBytes()).joinToString(""){"%02x".format(it)}
    @Test fun allOfflineEffectsAndAndroidDecoder(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,22050);val expected=hash(input)
            assertEquals(41,Presets.all.size)
            for((i,preset) in Presets.all.withIndex()){
                val out=File(dir,"effect.wav");val pcm=File(dir,"decoded.pcm")
                EffectRender.render(input,out,preset)
                assertEquals(preset.name,EffectRender.outputBytes(input.length()/4,preset),out.length())
                assertEquals(preset.name,(out.length()-44)/4,decode(out,pcm))
                assertArrayEquals(preset.name,out.readBytes().copyOfRange(44,out.length().toInt()),pcm.readBytes())
                if(i==0)assertArrayEquals(input.readBytes(),pcm.readBytes())
                out.delete();pcm.delete()
            }
            assertEquals(expected,hash(input))
            assertTrue(dir.listFiles()!!.none{it.name.startsWith("pitch-")||it.name.startsWith("stretch-")})
            println("PASS Android: 41 effect exports + independent MediaCodec WAV decode")
        }finally{dir.deleteRecursively()}
    }
    @Test fun thirtyGenresDistinctDecodableAndNonSilent(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,88200)
            val before=hash(input);val hashes=mutableSetOf<String>()
            assertEquals(30,GenreEngine.styles.size)
            for(style in GenreEngine.styles){
                val out=File(dir,"genre.wav");val pcm=File(dir,"decoded.pcm")
                GenreEngine.renderFromMix(input,out,style,120.0,0.0,emptyList(),listOf(.1))
                assertEquals(style.name,88200L,decode(out,pcm))
                assertTrue(style.name,pcm.readBytes().any{it!=0.toByte()})
                assertTrue("Duplicate output: "+style.name,hashes.add(hash(pcm)))
                out.delete();pcm.delete()
            }
            assertEquals(before,hash(input));assertEquals(30,hashes.size)
            println("PASS Android: 30 distinct procedural genre WAV outputs")
        }finally{dir.deleteRecursively()}
    }
    @Test fun flacRoundTripAndTenBandEqualizer(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,12345)
            val source=File(dir,"source.wav");wav(input,source)
            val flac=File(dir,"output.flac");val pcm=File(dir,"decoded.pcm")
            source.inputStream().buffered().use{r->flac.outputStream().buffered().use{FlacExport.encode(r,it)}}
            assertEquals(12345L,decode(flac,pcm));assertArrayEquals(input.readBytes(),pcm.readBytes())
            val eq=File(dir,"eq.wav");EqRender.render(input,eq,List(10){0f});assertEquals(12345L,decode(eq,pcm))
            assertArrayEquals(input.readBytes(),pcm.readBytes())
            EqRender.render(input,eq,List(10){if(it==4)9f else 0f});assertEquals(12345L,decode(eq,pcm))
            assertFalse(input.readBytes().contentEquals(pcm.readBytes()))
            println("PASS Android: bit-exact FLAC, flat EQ identity, non-flat EQ signal change")
        }finally{dir.deleteRecursively()}
    }
    @Test fun fourAndSixStemCacheMixExportAndInvalidCache(){
        for(count in listOf(4,6)){
            val dir=File(File(c.filesDir,"stems").apply{mkdirs()},java.util.UUID.randomUUID().toString()).apply{check(mkdirs())}
            var mix:File?=null
            try{
                val frames=4410L
                repeat(count){raw(File(dir,"$it.pcm"),frames.toInt(),110.0*(it+1))}
                File(dir,"meta").writeText("$frames\n$count\n")
                val b=StemEngine.load(c,dir.name)?:error("Valid cache rejected")
                assertEquals(count,b.count);assertEquals(frames,b.frames)
                mix=StemEngine.render(c,b,FloatArray(count){if(it==3)1f else 0f})
                assertArrayEquals(File(dir,"3.pcm").readBytes(),mix.readBytes().copyOfRange(44,mix.length().toInt()))
                val bytes=ByteArrayOutputStream()
                StemZip.export(dir,frames,count,bytes)
                val names=listOf("drums","bass","other","vocals","guitar","piano")
                ZipInputStream(ByteArrayInputStream(bytes.toByteArray())).use{z->
                    repeat(count){i->assertEquals(names[i]+".wav",z.nextEntry!!.name);val wav=z.readBytes();assertEquals(44+frames*4,wav.size.toLong());assertArrayEquals(File(dir,"$i.pcm").readBytes(),wav.copyOfRange(44,wav.size));z.closeEntry()}
                    assertNull(z.nextEntry)
                }
                File(dir,"0.pcm").writeBytes(byteArrayOf(1))
                assertNull(StemEngine.load(c,dir.name))
                assertTrue(runCatching{StemZip.export(dir,frames,count,ByteArrayOutputStream())}.isFailure)
                println("PASS Android: $count cached stems, solo vocal mix, ZIP and damaged cache rejection")
            }finally{mix?.delete();dir.deleteRecursively()}
        }
    }
    @Test fun backupRoundTripAndMaliciousArchiveRollback(){
        val dir=folder()
        try{
            val original=File(dir,"input.pcm");raw(original,2205);val source=File(dir,"song.wav");wav(original,source)
            val archive=ByteArrayOutputStream()
            val metadata="""{"tracks":[{"title":"QA synthetic"}]}""".toByteArray()
            BackupCore.write(archive,metadata,listOf(BackupCore.Item("wav"){source.inputStream()}))
            val restored=BackupCore.read(ByteArrayInputStream(archive.toByteArray()),File(dir,"restore"))
            assertArrayEquals(metadata,restored.metadata);assertArrayEquals(source.readBytes(),restored.files.single().readBytes())
            val decoded=File(dir,"restored.pcm");assertEquals(2205L,decode(restored.files.single(),decoded))
            // Android 14+ can reject traversal inside ZipInputStream before application validation.
            // A syntactically safe but invalid ordinal independently exercises our own validator.
            for(entryName in listOf("audio/00.wav","../escape.wav")){
                val malicious=ByteArrayOutputStream()
                java.util.zip.ZipOutputStream(malicious).use{z->
                    for((name,data) in listOf("remix-backup-v1" to "1".toByteArray(),"library.json" to metadata,entryName to source.readBytes())){
                        z.putNextEntry(java.util.zip.ZipEntry(name));z.write(data);z.closeEntry()
                    }
                }
                val bad=File(dir,"bad")
                val rejected=runCatching{BackupCore.read(ByteArrayInputStream(malicious.toByteArray()),bad)}.exceptionOrNull()
                val appRejection=rejected is IllegalArgumentException&&rejected.message=="Недопустимая запись архива"
                val platformRejection=entryName=="../escape.wav"&&android.os.Build.VERSION.SDK_INT>=34&&rejected is java.util.zip.ZipException&&rejected.message.orEmpty().contains(entryName)
                assertTrue("Expected specific path rejection: "+rejected?.javaClass?.simpleName+": "+rejected?.message,appRejection||platformRejection)
                assertFalse(bad.exists());assertFalse(File(dir,"escape.wav").exists())
            }
            println("PASS Android: portable audio backup restore, playable file and traversal rollback")
        }finally{dir.deleteRecursively()}
    }
    @Test fun audioAnalyzerAndInvalidMedia(){
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,44100*4);val source=File(dir,"source.wav");wav(input,source)
            val report=TrackAnalyzer.report(c,FileProvider.getUriForFile(c,"app.remix.player.files",source))?:error("Analysis rejected valid audio")
            assertEquals(4.0,report.duration,.02);assertTrue(report.rms>.01)
            val bad=File(dir,"invalid.wav");bad.writeText("not an audio file")
            assertTrue(runCatching{decode(bad,File(dir,"bad.pcm"))}.isFailure)
            println("PASS Android: actual media analysis duration, non-silent signal, invalid audio rejected")
        }finally{dir.deleteRecursively()}
    }
    @Test fun smartDjAlignmentAndMediaDecoder(){
        val dir=folder()
        try{
            val frames=44100*16
            fun fixture(name:String,bpm:Double,phase:Double,hz:Double)=File(dir,name).apply{outputStream().buffered(65536).use{out->repeat(frames){i->
                val t=i/44100.0;val beat=((t-phase)%(60/bpm)+60/bpm)%(60/bpm)
                val v=(sin(2*Math.PI*hz*t)*(.03+.5*kotlin.math.exp(-beat*25))*32767).toInt().toShort()
                StemCore.writeShort(out,v);StemCore.writeShort(out,v)
            }}}
            val a=fixture("a.pcm",120.0,.1,220.0);val b=fixture("b.pcm",115.0,.23,330.0)
            val beforeA=hash(a);val beforeB=hash(b)
            val plan=DjTransition.plan(DjTransition.analyze(a,true),DjTransition.analyze(b,false),false)
            assertTrue(plan.speed in 1.02..1.07)
            val out=File(dir,"smart.wav");val result=DjTransition.render(a,b,out,5,false)
            assertEquals(44+result.frames*4,out.length())
            assertTrue(result.overlap in 210000L..231000L)
            val decoded=File(dir,"decoded.pcm");assertEquals(result.frames,decode(out,decoded))
            assertEquals("Decoded length",out.length()-44,decoded.length())
            // Compare every byte, without allocating three copies of the song in a 16 MiB heap.
            java.io.DataInputStream(out.inputStream().buffered()).use{expected->
                java.io.DataInputStream(decoded.inputStream().buffered()).use{actual->
                    expected.readFully(ByteArray(44))
                    val x=ByteArray(16384);val y=ByteArray(16384)
                    var remaining=decoded.length();var offset=0L
                    while(remaining>0){val n=minOf(x.size.toLong(),remaining).toInt();expected.readFully(x,0,n);actual.readFully(y,0,n);for(i in 0 until n)if(x[i]!=y[i])fail("PCM mismatch at byte "+(offset+i));remaining-=n;offset+=n}
                    assertEquals(-1,expected.read());assertEquals(-1,actual.read())
                }
            }
            assertEquals(beforeA,hash(a));assertEquals(beforeB,hash(b));assertTrue(dir.listFiles()!!.none{it.name.startsWith("dj-fit-")})
            println("PASS Android: measured BPM matching, rendered smart transition and independently decoded WAV")
        }finally{dir.deleteRecursively()}
    }
    @Test fun realWaveformFromDecodedAudio(){
        val dir=folder()
        try{
            val file=File(dir,"waveform.wav")
            val frames=44100*4
            file.outputStream().buffered(65536).use{out->
                StemCore.header(out,frames.toLong())
                repeat(frames){i->
                    val amplitude=if(i<frames/2)3500 else 14000
                    val v=(sin(2*Math.PI*440*i/44100)*amplitude).toInt().toShort()
                    StemCore.writeShort(out,v);StemCore.writeShort(out,(-v).toShort())
                }
            }
            val uri=FileProvider.getUriForFile(c,"app.remix.player.files",file)
            val before=hash(file)
            val data=WaveformDecode.scan(c,uri)?:error("Actual WAV decode failed")
            assertEquals(96,data.size)
            assertTrue("Stereo antiphase must not disappear",data.take(40).all{it in .47f..0.53f})
            assertTrue("Louder second half should have bigger peaks",data.takeLast(40).all{it in .97f..1f})
            assertEquals(before,hash(file))
            val invalid=File(dir,"invalid.wav").apply{writeText("invalid")}
            assertNull(WaveformDecode.scan(c,FileProvider.getUriForFile(c,"app.remix.player.files",invalid)))
            println("PASS Android: actual WAV waveform, quiet/loud sections, antiphase, invalid file, source unchanged")
        }finally{dir.deleteRecursively()}
    }
    @Test fun producerVariantsAndBassExchange(){
        val all=ProducerStyles.all
        assertEquals(40,all.size);assertEquals(40,all.map{it.name}.distinct().size)
        assertEquals(30,GenreEngine.styles.size)
        val dir=folder()
        try{
            val input=File(dir,"input.pcm");raw(input,44100*2)
            val hashes=mutableSetOf<String>()
            for(p in ProducerStyles.extra){
                val out=File(dir,"genre.wav")
                GenreEngine.renderFromMix(input,out,p.style,p.style.target.toDouble(),0.0,emptyList(),emptyList()){}
                assertEquals(44+input.length(),out.length());assertTrue(hashes.add(hash(out)))
                assertEquals(input.length()/4,decode(out,File(dir,"decoded.pcm")))
                out.delete();File(dir,"decoded.pcm").delete()
            }
            val e=DjBassExchange()
            assertEquals(1.0,e.lowGain(0.0,false),0.0);assertEquals(1.0,e.lowGain(1.0,true),0.0)
            assertEquals(1.0,e.lowGain(.5,false)+e.lowGain(.5,true),1e-9)
            assertEquals(.75,e.sample(0,.75,-.3,0.0,1.0,0.0,1.0),0.0)
            assertEquals(-.3,e.sample(0,.75,-.3,1.0,0.0,1.0,1.0),0.0)
        }finally{dir.deleteRecursively()}
    }
    @Test fun basicPitchRunsRealBundledOnnxOnAndroid(){
        val probabilities=BasicPitchModel.probe(c)
        assertEquals(BasicPitchHint.FRAMES*BasicPitchHint.NOTES,probabilities.size)
        assertTrue(probabilities.all{it.isFinite()&&it in 0f..1f})
        assertTrue("Model output must respond to synthetic audio",(probabilities.maxOrNull()?:0f)-(probabilities.minOrNull()?:0f)>.0001f)
        assertTrue(c.assets.open("basic-pitch/LICENSE").bufferedReader().use{it.readText()}.contains("Apache License"))
        println("PASS Android: real pinned Basic Pitch ONNX inference and finite note probabilities")
    }

    @androidx.media3.common.util.UnstableApi
    @Test fun crossfadeDoesNotReplayIncomingIntroAfterDelayedTick(){
        val dir=folder()
        val inst=InstrumentationRegistry.getInstrumentation()
        var ownedPlayer:androidx.media3.exoplayer.ExoPlayer?=null
        var ownedOverlap:LiveOverlap?=null
        lateinit var player:androidx.media3.exoplayer.ExoPlayer
        lateinit var overlap:LiveOverlap
        fun onMain(block:()->Unit){inst.runOnMainSync(block)}
        fun await(message:String,timeout:Long=15000L,condition:()->Boolean){
            val end=android.os.SystemClock.elapsedRealtime()+timeout
            var ok=false
            while(!ok&&android.os.SystemClock.elapsedRealtime()<end){
                onMain{ok=condition()}
                if(!ok)android.os.SystemClock.sleep(30)
            }
            assertTrue(message,ok)
        }
        try{
            val a=File(dir,"first.wav");val b=File(dir,"next.wav");val pcm=File(dir,"source.pcm")
            raw(pcm,44100*12,440.0);wav(pcm,a)
            raw(pcm,44100*12,660.0);wav(pcm,b)
            fun item(f:File,id:String)=androidx.media3.common.MediaItem.Builder().setMediaId(id).setUri(FileProvider.getUriForFile(c,"app.remix.player.files",f)).build()
            onMain{
                player=androidx.media3.exoplayer.ExoPlayer.Builder(c).build();ownedPlayer=player
                overlap=LiveOverlap(c,player);ownedOverlap=overlap
                player.setMediaItems(listOf(item(a,"qa-first"),item(b,"qa-next")))
                player.seekTo(0,6500L);player.prepare();player.play()
            }
            await("First track never became ready"){player.isPlaying&&player.currentMediaItemIndex==0}
            await("Incoming track never became audible"){
                overlap.tick(4000L,true)
                player.currentMediaItemIndex==0&&player.volume<.70f&&player.currentPosition>8000L
            }
            // No coordinator ticks until Media3 auto-advances, reproducing a busy main clock.
            await("Automatic transition did not occur",10000L){player.currentMediaItemIndex==1}
            onMain{assertEquals("The stale intro must stay muted on automatic advance",0f,player.volume,.001f)}
            await("Primary did not continue from the already heard intro",10000L){
                overlap.tick(4000L,true)
                player.currentMediaItemIndex==1&&player.isPlaying&&player.currentPosition>=2000L&&player.volume>.99f
            }
            var previous=0L
            onMain{previous=player.currentPosition}
            repeat(10){
                android.os.SystemClock.sleep(80)
                onMain{
                    overlap.tick(4000L,true)
                    assertEquals(1,player.currentMediaItemIndex)
                    assertTrue("Incoming position moved backwards",player.currentPosition>=previous-80)
                    previous=player.currentPosition
                }
            }
            println("PASS Android: real automatic crossfade transition preserves already heard incoming intro")
        }finally{
            onMain{ownedOverlap?.close();ownedPlayer?.release()}
            dir.deleteRecursively()
        }
    }

    @androidx.media3.common.util.UnstableApi
    @Test fun liveEffectSwitchKeepsPcmContinuousWithoutFlush(){
        val processor=RemixProcessor()
        val previous=Presets.active;val eq=EqualizerSettings.get()
        try{
            EqualizerSettings.set(List(10){0f})
            val original=Presets.all.first()
            val bass=Presets.all.single{it.name=="Deep Bass"}
            Presets.active=original
            processor.configure(androidx.media3.common.audio.AudioProcessor.AudioFormat(44100,2,androidx.media3.common.C.ENCODING_PCM_16BIT))
            processor.flush()
            var frame=0
            fun tone(i:Int)=(8192*kotlin.math.sin(2*kotlin.math.PI*55*i/44100)).toInt()
            fun block(preset:Preset,frames:Int):IntArray{
                Presets.active=preset
                val buffer=java.nio.ByteBuffer.allocateDirect(frames*4).order(java.nio.ByteOrder.nativeOrder())
                repeat(frames){val v=tone(frame++);buffer.putShort(v.toShort());buffer.putShort((-v).toShort())};buffer.flip()
                processor.queueInput(buffer);assertFalse(buffer.hasRemaining())
                val output=processor.getOutput().order(java.nio.ByteOrder.nativeOrder());assertEquals(frames*4,output.remaining())
                return IntArray(frames){val l=output.short.toInt();val r=output.short.toInt();assertTrue(kotlin.math.abs(l+r)<=2);l}
            }
            assertTrue(block(original,2048).withIndex().all{it.value==tone(it.index)})
            val start=frame
            val boosted=block(bass,44100)
            val tail=boosted.indices.drop(22050)
            assertTrue(tail.sumOf{boosted[it].toDouble()*boosted[it]}>1.3*tail.sumOf{tone(start+it).toDouble()*tone(start+it)})
            val afterStart=frame
            val after=block(original,4410)
            var last=boosted.last()
            for(v in after){assertTrue("Abrupt PCM switch",kotlin.math.abs(v-last)<250);last=v}
            assertTrue(after.indices.drop(2000).all{after[it]==tone(afterStart+it)})
            val finalStart=frame
            assertTrue(block(original,2048).withIndex().all{it.value==tone(finalStart+it.index)})
        }finally{processor.reset();Presets.active=previous;EqualizerSettings.set(eq)}
    }

}
