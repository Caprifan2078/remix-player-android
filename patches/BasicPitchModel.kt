package app.remix.player

import android.content.Context
import ai.onnxruntime.*
import java.io.File
import java.nio.FloatBuffer
import java.security.MessageDigest

/** Optional inference during a hard-dance render. Exact upstream weights, CPU only.
 * No audio leaves the device. Return no hint for ambiguous or insufficient input. */
object BasicPitchModel {
    private const val INPUT="serving_default_input_2:0"
    private const val NOTE="StatefulPartitionedCall:1"
    fun estimate(context:Context,raw:File):Int?{
        val total=raw.length()/4
        val length=BasicPitchHint.SAMPLES*2
        if(raw.length()%4!=0L||total<length*2L)return null
        val am=context.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        val mem=android.app.ActivityManager.MemoryInfo();am.getMemoryInfo(mem)
        if(mem.lowMemory||mem.availMem<256L*1024*1024)return null
        return withSession(context){session->
                val last=total-length;val starts=listOf(last/5,last/2,last*4/5).distinct()
                val hints=starts.map{start->
                    check(!Thread.currentThread().isInterrupted)
                    val pcm=AnalysisPcm.excerpt(raw,start,length,targetRate=BasicPitchHint.RATE)
                    if(pcm.size<BasicPitchHint.SAMPLES-1||pcm.any{!it.isFinite()})null
                    else{
                        val samples=FloatArray(BasicPitchHint.SAMPLES){i->pcm.getOrElse(i){0f}.coerceIn(-1f,1f)}
                        BasicPitchHint.window(infer(session,samples))
                    }
                }
                check(!Thread.currentThread().isInterrupted)
                BasicPitchHint.consensus(hints)
        }
    }
    private fun <T> withSession(context:Context,run:(OrtSession)->T):T{
        val bytes=context.assets.open("basic-pitch/nmp.onnx").use{it.readBytes()}
        require(bytes.size==BasicPitchHint.BYTES)
        val sha=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString(""){(it.toInt() and 255).toString(16).padStart(2,'0')}
        require(sha==BasicPitchHint.SHA)
        val env=OrtEnvironment.getEnvironment()
        return OrtSession.SessionOptions().use{opts->
            opts.setIntraOpNumThreads(1);opts.setInterOpNumThreads(1)
            opts.setCPUArenaAllocator(false);opts.setMemoryPatternOptimization(false)
            env.createSession(bytes,opts).use{session->
                val input=session.inputInfo[INPUT]?.info as? TensorInfo?:error("Basic Pitch input")
                val output=session.outputInfo[NOTE]?.info as? TensorInfo?:error("Basic Pitch note output")
                require(session.inputNames==setOf(INPUT)&&input.type==OnnxJavaType.FLOAT&&input.shape.size==3&&input.shape[0] in listOf(-1L,1L)&&input.shape[1] in listOf(-1L,BasicPitchHint.SAMPLES.toLong())&&input.shape[2]==1L)
                require(output.type==OnnxJavaType.FLOAT&&output.shape.size==3&&output.shape[0] in listOf(-1L,1L)&&output.shape[1] in listOf(-1L,BasicPitchHint.FRAMES.toLong())&&output.shape[2]==BasicPitchHint.NOTES.toLong())
                run(session)
            }
        }
    }
    private fun infer(session:OrtSession,samples:FloatArray):FloatArray {
        require(samples.size==BasicPitchHint.SAMPLES&&samples.all{it.isFinite()&&it in -1f..1f})
        return OnnxTensor.createTensor(OrtEnvironment.getEnvironment(),FloatBuffer.wrap(samples),longArrayOf(1,BasicPitchHint.SAMPLES.toLong(),1)).use{tensor->
            session.run(mapOf(INPUT to tensor),setOf(NOTE)).use{result->
                val notes=result.get(NOTE).orElseThrow{IllegalStateException("Basic Pitch note") } as OnnxTensor
                val buffer=notes.floatBuffer
                require(buffer.remaining()==BasicPitchHint.FRAMES*BasicPitchHint.NOTES)
                FloatArray(buffer.remaining()).also{buffer.get(it);require(it.all{v->v.isFinite()&&v in 0f..1f})}
            }
        }
    }
    internal fun probe(context:Context):FloatArray=withSession(context){session->
        val samples=FloatArray(BasicPitchHint.SAMPLES){i->(.3*kotlin.math.sin(2*kotlin.math.PI*110*i/BasicPitchHint.RATE)).toFloat()}
        infer(session,samples)
    }
}
