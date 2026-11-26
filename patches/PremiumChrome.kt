package app.remix.player

import android.content.Context
import android.graphics.*
import android.graphics.drawable.Drawable
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.content.res.ColorStateList
import android.widget.Button
import android.view.Gravity

/** Shared, native drawing primitives: no emoji, bitmap assets or added dependency. */
object PremiumChrome {
    const val BG=0xff111216.toInt()
    const val SURFACE=0xff1d2025.toInt()
    const val ACCENT=0xffc7e8a2.toInt()
    const val MUTED=0xff969da6.toInt()
    const val TEXT=0xfff0f1ee.toInt()
    fun shape(color:Int,radius:Float)=GradientDrawable().apply{setColor(color);cornerRadius=radius}
    fun ripple(color:Int,radius:Float)=RippleDrawable(ColorStateList.valueOf(0x20ffffff),shape(color,radius),shape(Color.WHITE,radius))
    fun dp(c:Context,n:Int)=(n*c.resources.displayMetrics.density+.5f).toInt()
    fun icon(c:Context,name:String,color:Int=TEXT,size:Int=24)=Icon(name,color,dp(c,size))
    private val transport=mapOf("⇄" to "shuffle","|◀" to "previous","▶" to "play","Ⅱ" to "pause","▶|" to "next","↻" to "repeat","⋮" to "more","♥" to "heartFill","♡" to "heart")
    class Control(context:Context):Button(context){
        override fun onDraw(canvas:Canvas){
            val name=transport[text.toString()]
            if(name==null){super.onDraw(canvas);return}
            val primary=name=="play"||name=="pause"
            val side=dp(context,if(primary)26 else 22)
            val x=(width-side)/2;val y=(height-side)/2
            if(primary){
                val p=Paint(Paint.ANTI_ALIAS_FLAG).apply{color=ACCENT}
                canvas.drawCircle(width/2f,height/2f,minOf(width,height)/2f-dp(context,3),p)
            }
            val d=Icon(name,if(primary)BG else currentTextColor,side)
            d.setBounds(x,y,x+side,y+side);d.draw(canvas)
        }
    }
    fun nav(b:Button,name:String,selected:Boolean){
        val c=b.context;val tint=if(selected)ACCENT else MUTED
        b.setTextColor(tint);b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL))
        b.setCompoundDrawablesWithIntrinsicBounds(null,icon(c,name,tint,22),null,null)
        b.compoundDrawablePadding=dp(c,3);b.gravity=Gravity.CENTER
        b.background=ripple(if(selected)0xff292f27.toInt() else Color.TRANSPARENT,dp(c,13).toFloat())
        b.setPadding(dp(c,3),dp(c,7),dp(c,3),dp(c,6))
    }
    class Icon(private val name:String,private val color:Int,private val size:Int):Drawable(){
        private val p=Paint(Paint.ANTI_ALIAS_FLAG).apply{strokeWidth=1.7f;strokeCap=Paint.Cap.ROUND;strokeJoin=Paint.Join.ROUND}
        override fun getIntrinsicWidth()=size
        override fun getIntrinsicHeight()=size
        override fun setAlpha(a:Int){p.alpha=a}
        override fun setColorFilter(f:ColorFilter?){p.colorFilter=f}
        @Deprecated("Deprecated in Android") override fun getOpacity()=PixelFormat.TRANSLUCENT
        override fun draw(c:Canvas){
            c.save();c.translate(bounds.left.toFloat(),bounds.top.toFloat());c.scale(bounds.width()/24f,bounds.height()/24f)
            p.color=color;p.style=Paint.Style.STROKE
            fun line(a:Float,b:Float,x:Float,y:Float)=c.drawLine(a,b,x,y,p)
            fun path(vararg v:Float,fill:Boolean=false){val q=Path();q.moveTo(v[0],v[1]);for(i in 2 until v.size step 2)q.lineTo(v[i],v[i+1]);if(fill)q.close();p.style=if(fill)Paint.Style.FILL else Paint.Style.STROKE;c.drawPath(q,p);p.style=Paint.Style.STROKE}
            fun dot(x:Float,y:Float,r:Float=1.3f){p.style=Paint.Style.FILL;c.drawCircle(x,y,r,p);p.style=Paint.Style.STROKE}
            when(name){
                "library"->{c.drawRoundRect(3f,4f,7f,20f,1f,1f,p);c.drawRoundRect(10f,4f,14f,20f,1f,1f,p);path(17f,5f,21f,4f,23f,19f,19f,20f,17f,5f)}
                "studio"->{for((i,y) in listOf(8f,15f,10f).withIndex()){val x=5f+7*i;line(x,3f,x,21f);p.style=Paint.Style.FILL;c.drawCircle(x,y,2.5f,p);p.style=Paint.Style.STROKE}}
                "lyrics"->{c.drawRoundRect(3f,4f,21f,20f,4f,4f,p);line(7f,9f,17f,9f);line(7f,13f,15f,13f);line(7f,17f,12f,17f)}
                "more"->{dot(5f,12f);dot(12f,12f);dot(19f,12f)}
                "play"->path(7f,4f,20f,12f,7f,20f,fill=true)
                "pause"->{p.style=Paint.Style.FILL;c.drawRoundRect(6f,4f,10f,20f,1f,1f,p);c.drawRoundRect(14f,4f,18f,20f,1f,1f,p)}
                "previous"->{path(18f,5f,7f,12f,18f,19f,fill=true);line(5f,5f,5f,19f)}
                "next"->{path(6f,5f,17f,12f,6f,19f,fill=true);line(19f,5f,19f,19f)}
                "shuffle"->{path(3f,6f,7f,6f,17f,18f,21f,18f);path(17f,14f,21f,18f,17f,22f);path(3f,18f,7f,18f,17f,6f,21f,6f);path(17f,2f,21f,6f,17f,10f)}
                "repeat"->{path(4f,11f,4f,5f,19f,5f);path(16f,2f,19f,5f,16f,8f);path(20f,13f,20f,19f,5f,19f);path(8f,16f,5f,19f,8f,22f)}
                "heart","heartFill"->{val q=Path().apply{moveTo(12f,21f);cubicTo(9f,18f,2f,13f,2f,8f);cubicTo(2f,1f,10f,2f,12f,7f);cubicTo(14f,2f,22f,1f,22f,8f);cubicTo(22f,13f,15f,18f,12f,21f);close()};p.style=if(name=="heartFill")Paint.Style.FILL else Paint.Style.STROKE;c.drawPath(q,p)}
                "disc"->{c.drawCircle(12f,12f,10f,p);c.drawCircle(12f,12f,3f,p);c.drawArc(5f,5f,19f,19f,190f,75f,false,p);c.drawArc(5f,5f,19f,19f,10f,75f,false,p)}
                else->{dot(12f,12f)}
            };c.restore()
        }
    }
}
