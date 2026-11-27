package app.remix.player

/** Pinned multilingual GGML artifacts. Memory thresholds are conservative heuristics, not benchmarks. */
object WhisperModelSpec {
    data class Model(val id:String,val size:Long,val sha:String,val minFreeRam:Long,val revision:String="main"){
        /** Conservative extra memory margins; not a measured peak. */
        fun beamSize(available:Long,lowMemory:Boolean,language:String="en"):Int {
            if(lowMemory||available<minFreeRam)return 1
            val extra=available-minFreeRam
            val lightweight=id in listOf("tiny","base-q5_1","base","small-q5_1","small")
            // Russian and automatic detection benefit from more hypotheses on smaller models.
            // Keep heavy-model latency and previous English settings unchanged.
            if(language in listOf("ru","auto")&&lightweight){
                if(extra>=1024L*1024*1024)return 5
                if(extra>=512L*1024*1024)return 3
            }
            return if(id!="tiny"&&extra>=512L*1024*1024)3 else 1
        }
        val russianAdvice get()=when(id){
            "tiny","base-q5_1","base"->"Русский: низкая точность в QA30; для быстрого черновика"
            "small-q5_1","small"->"Русский: промежуточный вариант, требуются правки"
            "medium-q5_0"->"Русский: 1 ошибка из 7 слов в QA30"
            "large-v3-turbo-q5_0","large-v3-q5_0"->"Русский: 0 ошибок из 7 слов в QA30"
            else->"Точность русского не измерена"
        }
        val description get()=when(id){
            "tiny"->"Быстрая проверка · на пении часто пропускает слова"
            "base-q5_1"->"Экономная Base · сжатые веса"
            "base"->"Полная Base · простые записи"
            "small-q5_1"->"Баланс · сжатая Small"
            "small"->"Полная Small · точнее на обычной речи, чем Base"
            "medium-q5_0"->"Мощнее Small · медленная обработка"
            "large-v3-turbo-q5_0"->"Рекомендуется попробовать для сложного вокала · быстрый декодер"
            "large-v3-q5_0"->"Тяжёлый режим · максимальный потенциал, без гарантии на пении"
            else->"Многоязычная модель"
        }
        val source get()="https://huggingface.co/ggerganov/whisper.cpp/blob/$revision/ggml-$id.bin"
        val title get()="Whisper $id · ${size/1_000_000} МБ"
    }
    val models=listOf(
        Model("tiny",77691713L,"be07e048e1e599ad46341c8d2a135645097a538221678b7acdd1b1919c6e1b21",512L*1024*1024),
        Model("base-q5_1",59707625L,"422f1ae452ade6f30a004d7e5c6a43195e4433bc370bf23fac9cc591f01a8898",768L*1024*1024,"f281eb45af861ab5e5297d23694b7d46e090c02c"),
        Model("base",147951465L,"60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe",768L*1024*1024),
        Model("small-q5_1",190085487L,"ae85e4a935d7a567bd102fe55afc16bb595bdb618e11b2fc7591bc08120411bb",1536L*1024*1024,"c521a4b02f422512d734391fdf08bb08c0862f68"),
        Model("small",487601967L,"1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b",1536L*1024*1024),
        Model("medium-q5_0",539212467L,"19fea4b380c3a618ec4723c3eef2eb785ffba0d0538cf43f8f235e7b3b34220f",2560L*1024*1024,"0b364b566045a405be7225ee1e415a073e04da77"),
        Model("large-v3-turbo-q5_0",574041195L,"394221709cd5ad1f40c46e6031ca61bce88931e6e088c188294c6d5a55ffa7e2",3072L*1024*1024,"0b364b566045a405be7225ee1e415a073e04da77"),
        Model("large-v3-q5_0",1081140203L,"d75795ecff3f83b5faa89d1900604ad8c780abd5739fae406de19f23ecd98ad1",4096L*1024*1024,"fb5ed9369c26eaf08392504d8446da431e0fffb9")
    )
    val maxBytes get()=models.maxOf{it.size}
    fun bySize(size:Long)=models.singleOrNull{it.size==size}
    fun matches(size:Long,sha:String)=bySize(size)?.sha?.equals(sha,true)==true
}
