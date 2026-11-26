from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/SmartMix.kt'
s=p.read_text()
old='        if(!radio)result.addAll(entries.filterNot(::measured))'
new='''        if(!radio){
            // Keep the seed and improve the complete route, not just the next hop.
            // The distance is symmetric, so a reversal changes only its two boundary edges.
            val n=result.size
            if(n>=3){
                val scores=Array(n){DoubleArray(n)}
                for(i in 0 until n)for(j in i+1 until n){val d=distance(result[i],result[j]);scores[i][j]=d;scores[j][i]=d}
                val order=IntArray(n){it}
                repeat(8){
                    var best=1e-9;var left=-1;var right=-1
                    for(i in 1 until n-1)for(j in i+1 until n){
                        val a=order[i-1];val b=order[i];val c=order[j]
                        val gain=scores[a][b]-scores[a][c]+if(j+1<n){val d=order[j+1];scores[c][d]-scores[b][d]}else 0.0
                        if(gain>best){best=gain;left=i;right=j}
                    }
                    if(left<0)return@repeat
                    while(left<right){val t=order[left];order[left]=order[right];order[right]=t;left++;right--}
                }
                val optimized=order.map{result[it]};result.clear();result.addAll(optimized)
            }
            result.addAll(entries.filterNot(::measured))
        }'''
assert s.count(old)==1
p.write_text(s.replace(old,new))
print('PASS: bounded route optimization without changing seed or removing tracks')
