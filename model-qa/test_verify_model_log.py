from verify_model_log import verify
s='INSTRUMENTATION_STATUS: test=actual\nINSTRUMENTATION_STATUS_CODE: 1\nINSTRUMENTATION_STATUS: test=actual\nINSTRUMENTATION_STATUS_CODE: 0\nOK (1 test)\nINSTRUMENTATION_CODE: -1\n'
verify(s,'actual')
for bad in [s.replace('actual','wrong'),s.replace('CODE: 0','CODE: -2'),s.replace('OK (1 test)','FAILURES'),s.replace('CODE: -1','CODE: 0'),s+s,s.split('OK')[0]]:
    try: verify(bad,'actual')
    except AssertionError: pass
    else: raise AssertionError('accepted invalid log')
print('PASS: 1 valid and 6 invalid model logs')
