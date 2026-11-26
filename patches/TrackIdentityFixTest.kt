package app.remix.player
fun main(){
 val f=TrackIdentityFix
 val t=TrackIdentityFix.Identity("track_17.mp3","unknown")
 check(f.fromTags(t,"Real title","Real artist")==TrackIdentityFix.Identity("Real title","Real artist"))
 check(f.fromTags(t.copy(title="Song (Hardstyle Remix).mp3"),"Song","Author").title=="Song (Hardstyle Remix)")
 check(f.fromTags(t.copy(title="My edit"),"Other","Artist").title=="My edit")
 check(f.fromTags(t.copy(artist="Known"),"Song","Other").artist=="Known")
 check(f.fromTags(t,"Song",null).artist=="unknown")
 check(f.verifiedArtist("unknown",listOf("Artist","artist"))=="Artist")
 check(f.verifiedArtist("unknown",listOf("A","B"))=="unknown")
 check(f.verifiedArtist("Known",listOf("A"))=="Known")
 check(f.verifiedArtist("unknown",emptyList())=="unknown")
 println("PASS: 9 conservative metadata repair checks")
}
