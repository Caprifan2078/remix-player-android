package app.remix.player
fun main(){
 val raw="[00:01.000]<00:01.000>Первое <00:06.500>длинное <00:09.250>слово\n[00:12.000]Следующая строка"
 val s=SubtitleExport.srt(raw)
 check("00:00:01,000 --> 00:00:10,250" in s){"Long timed line lost its final word: $s"}
 val last=SubtitleExport.srt("[offset:200]\n[00:01]<00:01>First <00:10.500>last")
 check("00:00:01,200 --> 00:00:11,700" in last){last}
 val bounded=SubtitleExport.srt("[00:01]<00:01>first <00:09>late\n[00:08]next")
 check("00:00:01,000 --> 00:00:07,000" in bounded){bounded}
 check("00:00:02,100 --> 00:00:08,100" in SubtitleExport.srt("[offset:100]\n[00:01]Hello\n[00:02]World\n[00:10]Again"))
 val negative=SubtitleExport.srt("[offset:-2000]\n[00:01]<00:01>First <00:10>last")
 check("00:00:00,000 --> 00:00:09,000" in negative){negative}
 println("PASS: SRT long word-timed cues, final line, offset, next cue boundaries and ordinary cap")
}
