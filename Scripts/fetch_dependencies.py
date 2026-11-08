from pathlib import Path
import json,re,shutil
from fetch_course_assets import fetch,CPP
R=Path(__file__).resolve().parents[1]
tree=json.loads((R/'tmp/pdfs'/f'{CPP}-tree.json').read_text(encoding='utf-8-sig'))['tree']
for prefix,seeds in [
 ('Chapter13/Exercise13.02/Content/', ['StarterContent/Architecture/Wall_400x400','StarterContent/Architecture/Floor_400x400','StarterContent/Materials/M_Metal_Steel','StarterContent/Materials/M_Metal_Copper']),
 ('Chapter16/Exercise16.01/Project/Content/', ['Characters/Mannequins/Animations/ABP_Quinn']),
]:
 index={e['path'][len(prefix):-7]:e for e in tree if e['type']=='blob' and e['path'].startswith(prefix) and e['path'].endswith('.uasset')}
 queue=list(seeds);seen=set()
 while queue:
  rel=queue.pop(0)
  if rel in seen:continue
  seen.add(rel)
  dst=R/'Content'/(rel+'.uasset')
  if dst.exists():continue
  if rel not in index:print('Not in source:',rel,flush=True);continue
  p=Path(fetch((CPP,index[rel])))
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
  data=p.read_bytes()
  refs=set(x.decode() for x in re.findall(rb'/Game/[A-Za-z0-9_/+\-]+',data))
  for ref in refs:
   name=ref[6:]
   if name in index and name not in seen:queue.append(name)
  print('Imported dependency',rel,flush=True)
