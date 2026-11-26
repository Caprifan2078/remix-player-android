package app.remix.player
import java.net.URLDecoder
fun main(){
    val title="Тест & песня";val artist="Автор + группа"
    check(BrowserLyricImport.query(title,artist).contains(title))
    check(BrowserLyricImport.query(title,artist).contains(artist))
    check(URLDecoder.decode(BrowserLyricImport.url(title,artist).substringAfter("?q="),"UTF-8")==BrowserLyricImport.query(title,artist))
    check(BrowserLyricImport.query(title,artist,"мы снова идем домой")=="мы снова идем домой lyrics текст песни")
    check(BrowserLyricImport.query(title,artist," ").contains(title))
    check(BrowserLyricImport.query(title,artist,"я".repeat(500)).length<220)
    check(BrowserLyricImport.candidate("\uFEFF  Снова\r\nидем домой  ")=="Снова\nидем домой")
    check(BrowserLyricImport.candidate("https://example.com/song")==null)
    check(BrowserLyricImport.candidate("<html>lyrics</html>")==null)
    check(BrowserLyricImport.candidate("\u0000text")==null)
    check(BrowserLyricImport.candidate("  ")==null)
    check(BrowserLyricImport.candidate("a".repeat(500001))==null)
    check(BrowserLyricImport.candidate("[00:01.000]Привет")=="[00:01.000]Привет")
    check(BrowserLyricImport.candidate("Да")=="Да")
    println("PASS: 14 lyric browser query and import checks")
}
