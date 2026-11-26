package app.remix.player
import android.content.Context
import android.media.*
import android.net.Uri
import android.os.SystemClock
import java.nio.ByteOrder
import kotlin.math.sqrt

/** Decode at most the first or last 12 seconds, off the playback looper.
 * A missing/partial decoder result is not treated as silence. */
object EdgeEnergy {
    fun scan(context:Context,uri:Uri,tail:Boolean):DoubleArray? {
        if(uri.scheme!="content")return null
        val extractor=MediaExtractor();var codec:MediaCodec?=null
        try {
            extractor.setDataSource(context,uri,null)
            val track=(0 until extractor.trackCount).firstOrNull{extractor.getTrackFormat(it).getString(MediaFormat.KEY_MIME)?.startsWith("audio/")==true}?:return null
            extractor.selectTrack(track);val format=extractor.getTrackFormat(track)
            if(!format.containsKey(MediaFormat.KEY_DURATION))return null
            val total=format.getLong(MediaFormat.KEY_DURATION)
            val bins=minOf(48,(total/250000L).coerceIn(0,48).toInt());if(bins<8)return null
            val start=if(tail)total-bins*250000L else 0L;val end=start+bins*250000L
            val sum=DoubleArray(bins);val count=LongArray(bins)
            extractor.seekTo(start,MediaExtractor.SEEK_TO_PREVIOUS_SYNC)
            val decoder=MediaCodec.createDecoderByType(format.getString(MediaFormat.KEY_MIME)?:return null);codec=decoder
            decoder.configure(format,null,null,0);decoder.start()
            var rate=format.getInteger(MediaFormat.KEY_SAMPLE_RATE);var channels=format.getInteger(MediaFormat.KEY_CHANNEL_COUNT);var encoding=AudioFormat.ENCODING_PCM_16BIT
            var inputDone=false;var outputDone=false;val info=MediaCodec.BufferInfo();var idle=0
            val deadline=SystemClock.elapsedRealtime()+8000
            while(!outputDone&&idle<150&&SystemClock.elapsedRealtime()<deadline&&!Thread.currentThread().isInterrupted){
                var progressed=false
                if(!inputDone){val i=decoder.dequeueInputBuffer(5000);if(i>=0){
                    val b=decoder.getInputBuffer(i)?:return null;b.clear();val stamp=extractor.sampleTime
                    val n=if(stamp<0||stamp>=end+500000)-1 else extractor.readSampleData(b,0)
                    if(n<0){decoder.queueInputBuffer(i,0,0,0,MediaCodec.BUFFER_FLAG_END_OF_STREAM);inputDone=true}
                    else{decoder.queueInputBuffer(i,0,n,stamp,0);extractor.advance()};progressed=true
                }}
                when(val i=decoder.dequeueOutputBuffer(info,5000)){
                    MediaCodec.INFO_OUTPUT_FORMAT_CHANGED->{val f=decoder.outputFormat;rate=f.getInteger(MediaFormat.KEY_SAMPLE_RATE);channels=f.getInteger(MediaFormat.KEY_CHANNEL_COUNT);encoding=if(f.containsKey(MediaFormat.KEY_PCM_ENCODING))f.getInteger(MediaFormat.KEY_PCM_ENCODING)else AudioFormat.ENCODING_PCM_16BIT;progressed=true}
                    else->if(i>=0){try{
                        val b=decoder.getOutputBuffer(i)
                        if(b!=null&&info.size>0&&info.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG==0){
                            if(rate !in 8000..384000||channels !in 1..32||encoding !in listOf(AudioFormat.ENCODING_PCM_16BIT,AudioFormat.ENCODING_PCM_FLOAT))return null
                            val bytes=if(encoding==AudioFormat.ENCODING_PCM_FLOAT)4 else 2
                            b.position(info.offset);b.limit(info.offset+info.size);b.order(ByteOrder.nativeOrder())
                            var frame=0L
                            while(b.remaining()>=channels*bytes){
                                val stamp=info.presentationTimeUs+frame*1000000L/rate;frame++
                                var power=0.0;repeat(channels){val v=if(bytes==4)b.float.toDouble()else b.short/32768.0;power+=(if(v.isFinite())v.coerceIn(-1.0,1.0)else 0.0).let{it*it}}
                                if(stamp in start until end){val bin=((stamp-start)/250000L).toInt();sum[bin]+=power/channels;count[bin]++}
                            }
                        }
                        outputDone=info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM!=0||info.presentationTimeUs>=end
                    }finally{decoder.releaseOutputBuffer(i,false)};progressed=true}
                }
                idle=if(progressed)0 else idle+1
            }
            if(Thread.currentThread().isInterrupted||rate<=0||count.any{it<rate*.15})return null
            return DoubleArray(bins){sqrt(sum[it]/count[it])}
        }catch(e:Exception){return null}finally{runCatching{codec?.stop()};runCatching{codec?.release()};extractor.release()}
    }
}
