#!/usr/bin/env python3
"""Require one start and one successful finish for each declared Android test."""
from collections import Counter
from pathlib import Path
import re, sys

def expected_cases(root):
    cases=[]
    for p in Path(root).rglob('*.kt'):
        s=p.read_text()
        methods=re.findall(r'^\s*@Test\s+fun\s+(\w+)\s*\(',s,re.M)
        if methods:
            package=re.search(r'^package\s+([\w.]+)',s,re.M)
            classes=re.findall(r'^class\s+(\w+)',s,re.M)
            if not package or len(classes)!=1: raise ValueError(f'Ambiguous test class: {p}')
            cases.extend(package[1]+'.'+classes[0]+'#'+m for m in methods)
    if not cases or len(set(cases))!=len(cases): raise ValueError('Empty or duplicate source test identities')
    return cases

def verify_cases(log, expected):
    fields={}; started=Counter(); finished=Counter(); active=None
    for line in log.splitlines():
        if line.startswith('INSTRUMENTATION_STATUS: '):
            k,sep,v=line[len('INSTRUMENTATION_STATUS: '):].partition('=')
            if sep: fields[k]=v
        elif line.startswith('INSTRUMENTATION_STATUS_CODE: '):
            code=int(line.split(':',1)[1]); ident=fields.get('class','')+'#'+fields.get('test','')
            if code==1:
                if active is not None or ident not in expected or started[ident]: return False
                active=ident;started[ident]+=1
            elif code==0:
                if active!=ident or finished[ident]:return False
                finished[ident]+=1;active=None
            elif code<0:return False
            fields={}
    return active is None and started==finished==Counter(expected) and re.findall(r'\bOK \((\d+) tests?\)',log)==[str(len(expected))] and re.findall(r'^INSTRUMENTATION_CODE:\s*(-?\d+)\s*$',log,re.M)==['-1']

def selftest():
    expected=['qa.Test#a','qa.Test#b']
    def case(name,code):return f'INSTRUMENTATION_STATUS: class=qa.Test\nINSTRUMENTATION_STATUS: test={name}\nINSTRUMENTATION_STATUS_CODE: {code}\n'
    end='OK (2 tests)\nINSTRUMENTATION_CODE: -1\n'
    good=case('a',1)+case('a',0)+case('b',1)+case('b',0)+end
    fixtures=[(good,True),(case('a',1)+case('a',0)+case('a',1)+case('a',0)+end,False),(case('a',1)+case('a',0)+case('c',1)+case('c',0)+end,False),(end,False),(good.replace('test=b\nINSTRUMENTATION_STATUS_CODE: 0','test=b\nINSTRUMENTATION_STATUS_CODE: -2'),False),(good.replace(case('b',1),''),False),(good.replace('INSTRUMENTATION_CODE: -1','INSTRUMENTATION_CODE: 0'),False),(good.replace(case('a',0),''),False)]
    for log,want in fixtures:assert verify_cases(log,expected)==want
    print('PASS: 8 exact test identity fixtures (duplicates, substitutions, missing starts/results, failures rejected)')
if __name__=='__main__':
    if sys.argv[1]=='--selftest':selftest()
    else:
        expected=expected_cases(sys.argv[2]);ok=verify_cases(Path(sys.argv[1]).read_text(errors='replace'),expected)
        print(f'{"PASS" if ok else "FAIL"}: exact start/finish identities for {len(expected)} declared Android tests');sys.exit(not ok)
