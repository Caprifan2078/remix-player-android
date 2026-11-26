package app.remix.player

/** Pinned multilingual GGML artifacts. Memory thresholds are conservative heuristics, not benchmarks. */
object WhisperModelSpec {
    data class Model(val id:String,val size:Long,val sha:String,val minFreeRam:Long,val revision:String="main"){
        val source get()="https://huggingface.co/ggerganov/whisper.cpp/blob/$revision/ggml-$id.bin"
        val title get()="Whisper $id · ${size/1_000_000} МБ"
    }
    val models=listOf(
        Model("tiny",77691713L,"be07e048e1e599ad46341c8d2a135645097a538221678b7acdd1b1919c6e1b21",512L*1024*1024),
        Model("base-q5_1",59707625L,"422f1ae452ade6f30a004d7e5c6a43195e4433bc370bf23fac9cc591f01a8898",768L*1024*1024,"f281eb45af861ab5e5297d23694b7d46e090c02c"),
        Model("base",147951465L,"60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe",768L*1024*1024),
        Model("small-q5_1",190085487L,"ae85e4a935d7a567bd102fe55afc16bb595bdb618e11b2fc7591bc08120411bb",1536L*1024*1024,"c521a4b02f422512d734391fdf08bb08c0862f68"),
        Model("small",487601967L,"1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b",1536L*1024*1024)
    )
    val maxBytes get()=models.maxOf{it.size}
    fun bySize(size:Long)=models.singleOrNull{it.size==size}
    fun matches(size:Long,sha:String)=bySize(size)?.sha?.equals(sha,true)==true
}
