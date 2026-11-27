package app.remix.player
import android.content.Context
import android.media.*
import android.net.Uri
import android.os.SystemClock
import java.nio.ByteOrder
/** Lightweight waveform-only decode: no FFT, tempo analysis, temporary file or AI model. */
internal object WaveReader {
    fun read(context:Context,uri:Uri,onPreview:((FloatArray,Int)->Unit)?=null):FloatArray?{
        val extractor=MediaExtractor();var codec:MediaCodec?=null
        try{
            extractor.setDataSource(context,uri,null)
            val track=(0 until extractor.trackCount).firstOrNull{extractor.getTrackFormat(it).getString(MediaFormat.KEY_MIME)?.startsWith("audio/")==true}?:return null
            extractor.selectTrack(track);val format=extractor.getTrackFormat(track);val mime=format.getString(MediaFormat.KEY_MIME)?:return null
            if(!format.containsKey(MediaFormat.KEY_DURATION))return null
            val duration=format.getLong(MediaFormat.KEY_DURATION);if(duration !in 1..900_000_000L)return null
            var rate=format.getInteger(MediaFormat.KEY_SAMPLE_RATE);if(rate !in 8000..384000)return null
            var channels=format.getInteger(MediaFormat.KEY_CHANNEL_COUNT);var encoding=AudioFormat.ENCODING_PCM_16BIT
            var bins=WaveBins(duration,rate);var gotPcm=false
            val decoder=MediaCodec.createDecoderByType(mime);codec=decoder;decoder.configure(format,null,null,0);decoder.start()
            val info=MediaCodec.BufferInfo();var inputDone=false;var outputDone=false;var idle=0
            val deadline=SystemClock.elapsedRealtime()+25000;var lastPreview=0L
            while(!outputDone&&idle<150&&SystemClock.elapsedRealtime()<deadline&&!Thread.currentThread().isInterrupted){
                var progressed=false
                if(!inputDone){val i=decoder.dequeueInputBuffer(5000);if(i>=0){
                    val b=decoder.getInputBuffer(i)?:return null;b.clear();val n=extractor.readSampleData(b,0)
                    if(n<0){decoder.queueInputBuffer(i,0,0,0,MediaCodec.BUFFER_FLAG_END_OF_STREAM);inputDone=true}
                    else{decoder.queueInputBuffer(i,0,n,extractor.sampleTime,0);extractor.advance()};progressed=true
                }}
                when(val i=decoder.dequeueOutputBuffer(info,5000)){
                    MediaCodec.INFO_OUTPUT_FORMAT_CHANGED->{
                        val f=decoder.outputFormat;val next=f.getInteger(MediaFormat.KEY_SAMPLE_RATE)
                        if(next !in 8000..384000||gotPcm&&next!=rate)return null
                        if(next!=rate){rate=next;bins=WaveBins(duration,rate)}
                        channels=f.getInteger(MediaFormat.KEY_CHANNEL_COUNT)
                        encoding=if(f.containsKey(MediaFormat.KEY_PCM_ENCODING))f.getInteger(MediaFormat.KEY_PCM_ENCODING)else AudioFormat.ENCODING_PCM_16BIT
                        progressed=true
                    }
                    else->if(i>=0){
                        try{
                            val b=decoder.getOutputBuffer(i)
                            if(b!=null&&info.size>0&&info.flags and MediaCodec.BUFFER_FLAG_CODEC_CONFIG==0){
                                if(channels !in 1..8||encoding !in listOf(AudioFormat.ENCODING_PCM_16BIT,AudioFormat.ENCODING_PCM_FLOAT))return null
                                b.position(info.offset);b.limit(info.offset+info.size);b.order(ByteOrder.nativeOrder())
                                bins.add(b,channels,encoding==AudioFormat.ENCODING_PCM_FLOAT,info.presentationTimeUs);gotPcm=true
                                val now=SystemClock.elapsedRealtime();if(onPreview!=null&&now-lastPreview>=250){bins.preview()?.let{onPreview(it.first,it.second);lastPreview=now}}
                            }
                            outputDone=info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM!=0
                        }finally{decoder.releaseOutputBuffer(i,false)}
                        progressed=true
                    }
                }
                idle=if(progressed)0 else idle+1
            }
            if(!gotPcm||Thread.currentThread().isInterrupted)return null
            val complete=if(outputDone)bins.finish()else null
            if(complete==null)bins.preview()?.let{onPreview?.invoke(it.first,it.second)}
            return complete
        }finally{runCatching{codec?.stop()};runCatching{codec?.release()};extractor.release()}
    }
}
