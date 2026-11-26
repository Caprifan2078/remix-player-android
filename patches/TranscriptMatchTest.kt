package app.remix.player
fun main(){
    val original="В темном городе горят большие окна мы идем домой сквозь тихий дождь и ветер"
    val typo="В тёмном городе горят чужие окна мы идем домой сквозь тихий дождь и ветер"
    check(TranscriptMatch.score(original,original).fraction==1.0)
    check(TranscriptMatch.score(typo,original).plausible)
    check(!TranscriptMatch.score(original,"Совсем другие слова про далекое море солнце и песок").plausible)
    check(!TranscriptMatch.score("да да да да да да да",original).plausible)
    check(!TranscriptMatch.score("мы идем",original).plausible)
    check(TranscriptMatch.score("Ёлка горит во дворе ночью ветер разносит снег","елка горит во дворе ночью ветер разносит снег").fraction==1.0)
    check(TranscriptMatch.query("да да да\nВ темном городе горят большие окна").contains("городе"))
    check(TranscriptMatch.query("да да да").isEmpty())
    println("PASS: 8 transcript verification and query tests")
}
