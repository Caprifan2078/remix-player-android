import copy, hashlib, pathlib, re, sys, zipfile

def keep(name):
    return not (name.startswith('lib/') and not name.startswith('lib/arm64-v8a/')) and not re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC)|SIG-[^/]+)',name,re.I)

def payload(path):
    with zipfile.ZipFile(path) as z:
        names=[i.filename for i in z.infolist() if not i.is_dir() and keep(i.filename)]
        if len(names)!=len(set(names)): raise ValueError('Duplicate payload entries')
        return {n:hashlib.sha256(z.read(n)).hexdigest() for n in names}

def verify(src,dst):
    with zipfile.ZipFile(src) as z,zipfile.ZipFile(dst) as a:
        abis={n.split('/')[1] for n in a.namelist() if n.startswith('lib/') and n.endswith('.so')}
        assert abis=={'arm64-v8a'},abis
        assert any(n.startswith('lib/x86_64/') for n in z.namelist()),'Not universal source'
        assert a.testzip() is None,'CRC failed'
        assert all(i.compress_type==zipfile.ZIP_STORED for i in a.infolist() if i.filename.endswith('.so')),'Compressed native library'
    assert payload(src)==payload(dst),'ARM64 or common payload changed'
    assert pathlib.Path(dst).stat().st_size < pathlib.Path(src).stat().st_size*.65,'Size gate failed'
    print('PASS: identical ARM64 and common payloads; only ARM64 native ABI; size',pathlib.Path(dst).stat().st_size)

def filter_apk(src,dst):
    with zipfile.ZipFile(src) as z,zipfile.ZipFile(dst,'w') as a:
        for i in z.infolist():
            if not keep(i.filename): continue
            j=copy.copy(i);j.extra=b''
            a.writestr(j,z.read(i))
    verify(src,dst)

if __name__=='__main__':
    mode,src,dst=sys.argv[1:]
    {'filter':filter_apk,'verify':verify}[mode](src,dst)
