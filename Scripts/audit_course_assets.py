import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.actor import ActorTools as A
E=unreal.EditorAssetLibrary
paths=set()
for folder in ['/Game/Course','/Game/FirstPersonBP','/Game/ThirdPersonBP','/Game/Mannequin','/Game/Ganfault','/Game/MixamoAnimPack','/Game/Characters/Mannequins/Animations']:
 paths.update(str(p) for p in E.list_assets(folder,True,False))
paths.update('/Game/'+n for n in ['FunctionExample','BP_Barrel','BPConstruction','BP_LightSwitch','BP_Collectable','BP_GameModeWithScore','BP_Platform','BP_Platform_Sparks','TestActor','BP_MyTPC'])
report={'blueprints':{},'defaults':{},'maps':[]}
for path in sorted(paths):
 data=E.find_asset_data(path)
 kind=str(data.asset_class_path.asset_name)
 if kind=='World':
  if path.startswith('/Game/Course/'):report['maps'].append(path)
  continue
 if kind not in ['Blueprint','AnimBlueprint','WidgetBlueprint']:continue
 asset=E.load_asset(path)
 B.compile_blueprint(asset)
 report['blueprints'][path]=str(asset.get_editor_property('status'))
 assert 'BS_ERROR' not in report['blueprints'][path],path
 E.save_loaded_asset(asset)
for path,props in [('/Game/FirstPersonBP/Blueprints/BP_CylinderTarget',['Speed','TimeToChange','Direction','Primed']),('/Game/TestActor',['VerticalSpeed']),('/Game/Physics/PM_Dodgeball',['friction','restitution'])]:
 asset=E.load_asset(path);d=B.get_default_object(asset) if isinstance(asset,unreal.Blueprint) else asset
 report['defaults'][path]={p:str(d.get_editor_property(p)) for p in props}
third=B.get_default_object(E.load_asset('/Game/BP_MyTPC'))
report['defaults']['ThirdPerson']={'capsule_radius':third.capsule_component.get_unscaled_capsule_radius(),'capsule_half_height':third.capsule_component.get_unscaled_capsule_half_height(),'camera_arm':third.get_component_by_class(unreal.SpringArmComponent).target_arm_length}
context=E.load_asset('/Game/IC_Character')
report['defaults']['EnhancedInput']=str(context.default_key_mappings)
report['passed']=True
(ROOT/'Saved/CourseVerification/asset-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
result={'compiled_blueprints':len(report['blueprints']),'maps':report['maps'],'defaults':report['defaults']}
