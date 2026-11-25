from pathlib import Path
import sys
root=Path(sys.argv[1])/"app/src/main/java/app/remix/player"
def replace(name,a,b):
    p=root/name;s=p.read_text();assert s.count(a)==1,(name,a);p.write_text(s.replace(a,b))
replace("VerifiedDownload.kt","while(true){val n=input.read(b);if(n<0)break;digest.update(b,0,n)}",'while(true){check(!Thread.currentThread().isInterrupted){"Отменено"};val n=input.read(b);if(n<0)break;digest.update(b,0,n)}')
replace("VerifiedDownload.kt","return digest.digest()", 'check(!Thread.currentThread().isInterrupted){"Отменено"};return digest.digest()')
replace("VerifiedDownload.kt","(100*total/len).toInt().coerceIn(0,100)","(99*total/len).toInt().coerceIn(0,99)")
replace("VerifiedDownload.kt",'require(matches(file,sha)){"SHA-256 не совпадает"};progress(100)','require(matches(file,sha)){"SHA-256 не совпадает"};check(!Thread.currentThread().isInterrupted){"Отменено"};progress(100)')
replace("CatalogDownload.kt",";progress(100);return",';check(!Thread.currentThread().isInterrupted){"Отменено"};progress(100);return')
print("PASS: cancellation-aware model checksum and verified completion")
