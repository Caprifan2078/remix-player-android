from pathlib import Path
import sys
p=Path(sys.argv[1])/"app/src/main/java/app/remix/player/ModelCatalog.kt"
s=p.read_text()
old='||h=="cas-bridge.xethub.hf.co"'
new=old+'||h in setOf("us.aws.cdn.hf.co","us.gcp.cdn.hf.co","cdn-lfs-eu-1.hf.co","transfer.xethub.hf.co","transfer.xethub-eu.hf.co")'
assert s.count(old)==1
s=s.replace(old,new)
old='{"Неподдерживаемое перенаправление модели"}'
new='{"Неподдерживаемое перенаправление модели: ${it.host?.take(128) ?: "неизвестный сервер"}"}'
assert s.count(old)==1
p.write_text(s.replace(old,new))
print("PASS: explicit documented Hugging Face CDN download hosts, unchanged SHA pins and scheme restrictions")
