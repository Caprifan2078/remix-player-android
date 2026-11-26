package app.remix.player
fun main(){
 val s=CoverSwipe
 check(s.direction(90f,10f,60f)==CoverSwipe.Direction.PREVIOUS)
 check(s.direction(-90f,10f,60f)==CoverSwipe.Direction.NEXT)
 check(s.direction(30f,0f,60f)==null)
 check(s.direction(90f,70f,60f)==null)
 check(s.direction(10f,200f,60f)==null)
 check(s.direction(Float.NaN,0f,60f)==null)
 check(s.direction(100f,0f,0f)==null)
 println("PASS: 7 cover swipe checks")
}
