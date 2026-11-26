from pathlib import Path
import sys
p=Path(sys.argv[1])/'app/src/main/java/app/remix/player/MainActivity.kt';s=p.read_text()
old='''toast("Темп не определён")}else android.app.AlertDialog.Builder(this).setTitle("Рекомендации · эвристика").setItems(picks.map{"${it.style.name} · ${it.style.target} BPM · скорость ${String.format(java.util.Locale.US,"%.2f",it.speed)}×"}.toTypedArray())'''
new='''toast("Недостаточно уверенный BPM или слишком тихий сигнал. Проверьте анализ и при необходимости задайте BPM вручную.")}else android.app.AlertDialog.Builder(this).setTitle("Подбор по темпу и характеру звука").setItems(picks.map{"${it.style.name} · ${String.format(java.util.Locale.ROOT,"%.0f",it.effectiveBpm)} BPM\\n${it.reasons.joinToString(" · ")}"}.toTypedArray())'''
assert s.count(old)==1
p.write_text(s.replace(old,new))
print("PASS: show measured achievable BPM and transparent recommendation reasons")
