from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.blueprint_node import PinID
import json
unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(['/Game'],force_rescan=True)
paths=['/Game/FirstPersonBP/Blueprints/FirstPersonCharacter','/Game/FirstPersonBP/Blueprints/BP_CylinderTarget','/Game/FirstPersonBP/UI/HUD','/Game/BP_MyTPC','/Game/TestActor','/Game/FunctionExample']
report={}
for p in paths:
 try:
  bp=unreal.load_asset(p);B.compile_blueprint(bp)
  d={'parent':str(B.get_parent(bp)),'variables':str(B.list_variables(bp)), 'graphs':{}}
  for g in B.list_graphs(bp):
   try:d['graphs'][g.get_name()]=B.read_graph_dsl(g)
   except Exception as ex:d['graphs'][g.get_name()]=str(ex)
  report[p]=d
 except Exception as ex:report[p]={'error':str(ex)}
(ROOT/'tmp/course-inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
result={'project':unreal.Paths.get_project_file_path(),'world':str(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()),'assets':{p: list(d.keys()) for p,d in report.items()}}
