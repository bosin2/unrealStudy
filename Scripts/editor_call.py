import pathlib,json,time,sys,uuid
root=pathlib.Path(__file__).resolve().parents[1]; q=root/'tmp/editor';q.mkdir(parents=True,exist_ok=True)
ident=uuid.uuid4().hex
code=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8-sig') if len(sys.argv)>1 else sys.stdin.read()
if (q/'command.json').exists():raise RuntimeError('Another editor command is pending')
(q/'command.json').write_text(json.dumps({'id':ident,'code':code}),encoding='utf-8')
deadline=time.monotonic()+240
while time.monotonic()<deadline:
    result=q/(ident+'.json')
    if result.exists():
        print(result.read_text(encoding='utf-8'));sys.exit(0)
    time.sleep(.25)
raise TimeoutError(ident)
