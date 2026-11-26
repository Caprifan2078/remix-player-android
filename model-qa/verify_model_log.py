import pathlib,re,sys

def verify(s,test):
    assert re.findall(r'^INSTRUMENTATION_STATUS: test=(.*)$',s,re.M)==[test,test], 'Wrong test identity'
    assert re.findall(r'^INSTRUMENTATION_STATUS_CODE: (-?\d+)$',s,re.M)==['1','0'], 'Unsuccessful test'
    assert re.findall(r'\bOK \(1 test\)',s)==['OK (1 test)'], 'Missing success'
    assert re.findall(r'^INSTRUMENTATION_CODE: (-?\d+)$',s,re.M)==['-1'], 'Bad terminal result'

if __name__=='__main__':
    verify(pathlib.Path(sys.argv[1]).read_text(),sys.argv[2])
