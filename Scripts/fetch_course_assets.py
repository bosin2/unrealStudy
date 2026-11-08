import concurrent.futures, hashlib, json, pathlib, urllib.request, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
BLUE = '-Blueprints-Visual-Scripting-for-Unreal-Engine-5'
CPP = 'Elevating-Game-Experiences-with-Unreal-Engine-5-Second-Edition'
tasks = []
for repo in [BLUE, CPP]:
    tree = json.loads((ROOT/'tmp/pdfs'/f'{repo}-tree.json').read_text(encoding='utf-8-sig'))['tree']
    for e in tree:
        p = e['path']
        if e['type'] != 'blob': continue
        if repo == BLUE:
            selected = p.startswith(('Chapter07/Content/', 'Chapter07/Config/', 'Chapter02/Content/', 'Chapter03/Content/', 'Chapter04/Content/')) or p == 'LICENSE'
        else:
            selected = p.startswith(('Chapter01/', 'Chapter02/Exercise2.03/ExerciseFiles/', 'Chapter02/Exercise2.05/ExerciseFiles/Content/', 'Chapter02/Activity2.01/ActivityFiles/Content/Ganfault/', 'Chapter03/Exercise3.02/ExerciseFiles/', 'Chapter04/Activity4.01/', 'Chapter05/Exercise5.01/', 'Chapter06/')) or p == 'LICENSE'
            selected = selected and not p.endswith(('.png','.rar'))
        if selected: tasks.append((repo,e))

def fetch(task):
    repo,e = task; p=e['path']; dst=ROOT/'tmp/official'/('blue' if repo==BLUE else 'cpp')/p
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and dst.stat().st_size>200: return str(dst)
    for attempt in range(4):
        try:
            url='https://raw.githubusercontent.com/PacktPublishing/'+repo+'/main/'+urllib.parse.quote(p)
            try: data=urllib.request.urlopen(url,timeout=90).read()
            except urllib.error.HTTPError as ex:
                if ex.code !=404: raise
                url=url.replace('/main/','/master/'); data=urllib.request.urlopen(url,timeout=90).read()
            if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=e['sha']:
                raise ValueError('Git blob SHA mismatch: '+p)
            if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
                meta=dict(line.split(' ',1) for line in data.decode().splitlines()[1:])
                url=url.replace('raw.githubusercontent.com/','media.githubusercontent.com/media/')
                data=urllib.request.urlopen(url,timeout=120).read()
                if hashlib.sha256(data).hexdigest()!=meta['oid'].split(':')[1]:raise ValueError('LFS SHA mismatch')
            dst.write_bytes(data)
            return str(dst)
        except Exception:
            if attempt==3:raise
            time.sleep(1+attempt)

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for i,path in enumerate(pool.map(fetch,tasks),1):
            if i%25==0: print(f'{i}/{len(tasks)} files verified',flush=True)
    print('DONE',len(tasks),flush=True)
