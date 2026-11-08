import unreal, pathlib, json, traceback
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
QUEUE=ROOT/'tmp/editor'; QUEUE.mkdir(parents=True,exist_ok=True)
def course_tick(delta):
    command=QUEUE/'command.json'
    if not command.exists(): return
    job=json.loads(command.read_text(encoding='utf-8-sig'));command.unlink()
    try:
        namespace={'unreal':unreal,'ROOT':ROOT,'result':None}
        exec(compile(job['code'],job.get('name','course_command'),'exec'),namespace)
        value={'ok':True,'result':namespace.get('result')}
    except Exception:
        value={'ok':False,'error':traceback.format_exc()}
    (QUEUE/(job['id']+'.json')).write_text(json.dumps(value,ensure_ascii=False,default=str),encoding='utf-8')
    namespace.clear()
handle=unreal.register_slate_post_tick_callback(course_tick)
(QUEUE/'ready.json').write_text(json.dumps({'project':str(ROOT),'ready':True}),encoding='utf-8')
unreal.log('COURSE_EDITOR_BRIDGE_READY')
