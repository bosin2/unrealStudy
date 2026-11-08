from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.actor import ActorTools as A
import json, gc
unreal.InternationalizationLibrary.set_current_language('en',False)
E=unreal.EditorAssetLibrary
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
AS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(['/Game'],force_rescan=True)
def save(bp):
 B.compile_blueprint(bp);E.save_loaded_asset(bp)
def bp(path,parent):
 obj=E.load_asset(path)
 return obj if obj else B.create(path.rsplit('/',1)[0],path.rsplit('/',1)[1],parent)
def cdo(obj):return B.get_default_object(obj)
def cls(path):return E.load_blueprint_class(path)
def spawn(path,loc,rot=(0,0,0),label=None):
 actor=AS.spawn_actor_from_class(cls(path),unreal.Vector(*loc),unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2]))
 if label:actor.set_actor_label(label)
 return actor
def meshcomp(owner,name,mesh,loc=(0,0,0),scale=(1,1,1),material=None,profile='BlockAllDynamic'):
 comp=A.add_component(owner,unreal.StaticMeshComponent.static_class(),name)
 comp.set_static_mesh(E.load_asset(mesh));comp.set_relative_location(unreal.Vector(*loc),False,False)
 comp.set_relative_scale3d(unreal.Vector(*scale));comp.set_collision_profile_name(profile)
 if material:comp.set_material(0,E.load_asset(material))
 return comp
def mode(path,pawn,pc=None):
 obj=bp(path,unreal.GameModeBase.static_class());d=cdo(obj)
 d.set_editor_property('default_pawn_class',cls(pawn))
 if pc:d.set_editor_property('player_controller_class',cls(pc))
 save(obj);return obj
def world_mode(path):
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 world.get_world_settings().set_editor_property('default_game_mode',cls(path))
def mapcopy(source,dest):
 for key in ['barrel','fire','couch','actor']:
  globals().pop(key,None)
 gc.collect()
 if E.does_asset_exist(dest):
  assert L.load_level(dest), dest
 else:
  assert L.new_level_from_template(dest,source), dest
def add_once(path,loc,label,rot=(0,0,0)):
 for actor in AS.get_all_level_actors():
  if actor.get_actor_label()==label:return actor
 return spawn(path,loc,rot,label)

# 1: The lecture's complete Blueprint shooter, with the original readable node graphs.
mapcopy('/Game/FirstPersonBP/Maps/FirstPersonExampleMap','/Game/Course/Maps/L_01_Shooter')
world_mode('/Game/FirstPersonBP/Blueprints/FirstPersonGameMode')
add_once('/Game/FunctionExample',(250,300,60),'Blue01_FunctionExample')
barrel=add_once('/Game/BP_Barrel',(450,300,100),'Blue02_Barrel')
fire=add_once('/Game/StarterContent/Blueprints/Blueprint_Effect_Fire',(450,300,100),'Blue02_Fire')
fire.set_actor_hidden_in_game(False)
fire.get_component_by_class(unreal.ParticleSystemComponent).set_hidden_in_game(True)
barrel.set_editor_property('BP_Fire',fire)
add_once('/Game/BPConstruction',(700,300,0),'Blue02_Construction_Table')
couch=add_once('/Game/BPConstruction',(1000,300,0),'Blue02_Construction_Couch')
couch.set_editor_property('SM_Mesh',E.load_asset('/Game/StarterContent/Props/SM_Couch'))
L.save_current_level()

# 2: Blueprint communications + basic Actor exercise. The published map retains
# its Level Blueprint actor references, dispatcher binding and spark trigger.
mapcopy('/Game/ThirdPersonBP/Maps/ThirdPersonExampleMap','/Game/Course/Maps/L_02_Basics')
world_mode('/Game/BP_GameModeWithScore')
gm=E.load_asset('/Game/BP_GameModeWithScore')
cdo(gm).set_editor_property('default_pawn_class',cls('/Game/ThirdPersonBP/Blueprints/ThirdPersonCharacter'));save(gm)
add_once('/Game/TestActor',(300,500,100),'Cpp01_TestActor')
L.save_current_level()

# Preserve the exact exercise-2.04 Pawn and GameMode inheritance in its own
# small example map: it intentionally has no movement script.
for name,parent,text in [('BP_MyPawn',unreal.Pawn,'My Pawn has started!'),('BP_MyPC',unreal.PlayerController,'My PC has started!'),('BP_MyGameMode',unreal.GameMode,'My Game Mode has started!')]:
 obj=bp('/Game/Course/Basics/'+name,parent.static_class())
 g=B.get_graph(obj,'EventGraph')
 B.write_graph_dsl(g,'(event EventBeginPlay (Development|PrintString "'+text+'" :Duration 10.0))')
 save(obj)
gm=E.load_asset('/Game/Course/Basics/BP_MyGameMode')
cdo(gm).set_editor_property('default_pawn_class',cls('/Game/Course/Basics/BP_MyPawn'))
cdo(gm).set_editor_property('player_controller_class',cls('/Game/Course/Basics/BP_MyPC'));save(gm)
# Framework map is copied from the real Third Person template below.

# 3: Third-person C++ character with the exact chapter-4 input action assets.
third=E.load_asset('/Game/BP_MyTPC')
if not E.does_asset_exist('/Game/Course/ThirdPerson/BP_MyTPC_Adam'):
 E.duplicate_asset('/Game/BP_MyTPC','/Game/Course/ThirdPerson/BP_MyTPC_Adam')
d=cdo(third)
for key,path in [('IC_Character','IC_Character'),('IA_Move','IA_Movement'),('IA_Jump','IA_Jump'),('IA_Look','IA_Look'),('IA_Walk','IA_Walk')]:d.set_editor_property(key,E.load_asset('/Game/'+path))
d.get_editor_property('mesh').set_skeletal_mesh_asset(E.load_asset('/Game/Mannequin/Character/Mesh/SK_Mannequin'))
d.get_editor_property('mesh').set_anim_instance_class(cls('/Game/Mannequin/Animations/Anim_Mannequin'))
d.get_editor_property('mesh').set_relative_location(unreal.Vector(0,0,-96),False,False)
d.get_editor_property('mesh').set_relative_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0),False,False)
save(third)
mode('/Game/Course/ThirdPerson/BP_ThirdPersonGameMode','/Game/BP_MyTPC')
mode('/Game/Course/ThirdPerson/BP_AdamGameMode','/Game/Course/ThirdPerson/BP_MyTPC_Adam')

gan=bp('/Game/Course/ThirdPerson/BP_Ganfault',unreal.load_class(None,'/Script/Study_Unreal_Shooter.MyThirdPersonChar'))
gd=cdo(gan)
for key,path in [('IC_Character','IC_Character'),('IA_Move','IA_Movement'),('IA_Jump','IA_Jump'),('IA_Look','IA_Look'),('IA_Walk','IA_Walk')]:gd.set_editor_property(key,E.load_asset('/Game/'+path))
gd.get_editor_property('mesh').set_skeletal_mesh_asset(E.load_asset('/Game/Ganfault/Mesh/Ganfault_Aure'))
gd.get_editor_property('mesh').set_anim_instance_class(cls('/Game/Ganfault/Anims/Anim_Ganfault'))
gd.get_editor_property('mesh').set_relative_location(unreal.Vector(0,0,-96),False,False)
gd.get_editor_property('mesh').set_relative_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0),False,False);save(gan)
mode('/Game/Course/ThirdPerson/BP_GanfaultGameMode','/Game/Course/ThirdPerson/BP_Ganfault')


# 4: Dodgeball: code from chapter 5/6, no later health/damage systems.
ball=bp('/Game/Course/Dodgeball/BP_DodgeballProjectile',unreal.load_class(None,'/Script/Study_Unreal_Shooter.DodgeballProjectile'))
if not any(x.get_name().startswith('BallMesh') for x in A.get_components(cdo(ball))):
 meshcomp(ball,'BallMesh','/Engine/BasicShapes/Sphere',scale=(.65,.65,.65),profile='NoCollision')
phys=E.load_asset('/Game/Physics/PM_Dodgeball')
if not phys:phys=unreal.AssetToolsHelpers.get_asset_tools().create_asset('PM_Dodgeball','/Game/Physics',unreal.PhysicalMaterial,unreal.PhysicalMaterialFactoryNew())
phys.set_editor_property('friction',.7);phys.set_editor_property('restitution',.95);E.save_loaded_asset(phys)
cdo(ball).get_component_by_class(unreal.SphereComponent).set_phys_material_override(phys);save(ball)
player=bp('/Game/Course/Dodgeball/BP_DodgeballCharacter',unreal.load_class(None,'/Script/Study_Unreal_Shooter.DodgeballCharacter'))
enemy=bp('/Game/Course/Dodgeball/BP_EnemyCharacter',unreal.load_class(None,'/Script/Study_Unreal_Shooter.EnemyCharacter'))
for obj in [player,enemy]:
 d=cdo(obj);m=d.get_editor_property('mesh')
 m.set_skeletal_mesh_asset(E.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple'))
 m.set_anim_instance_class(cls('/Game/Characters/Mannequins/Animations/ABP_Quinn'))
 m.set_relative_location(unreal.Vector(0,0,-83),False,False)
 m.set_relative_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0),False,False)
 save(obj)
cdo(player).set_editor_property('IC_Character',E.load_asset('/Game/IC_Character'))
cdo(player).set_editor_property('IA_Move',E.load_asset('/Game/IA_Movement'));save(player)
cdo(enemy).set_editor_property('DodgeballClass',ball.generated_class());save(enemy)
wall=bp('/Game/Course/Dodgeball/BP_Wall',unreal.load_class(None,'/Script/Study_Unreal_Shooter.Wall'))
if not any(x.get_name().startswith('WallMesh') for x in A.get_components(cdo(wall))):
 meshcomp(wall,'WallMesh','/Game/StarterContent/Architecture/Wall_400x400',loc=(-200,0,0),material='/Game/StarterContent/Materials/M_Metal_Steel',profile='BlockAll')
for m in A.get_components(cdo(wall),unreal.StaticMeshComponent.static_class()):
 m.set_material(0,E.load_asset('/Game/StarterContent/Materials/M_Metal_Steel'))
 m.set_collision_profile_name('BlockAll')
save(wall)
ghost=bp('/Game/Course/Dodgeball/BP_GhostWall',wall.generated_class())
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for handle in sds.k2_gather_subobject_data_for_blueprint(ghost):
 data=unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
 m=unreal.SubobjectDataBlueprintFunctionLibrary.get_object_for_blueprint(data,ghost)
 if not isinstance(m,unreal.StaticMeshComponent):continue
 assert '/BP_GhostWall.' in m.get_path_name(), m.get_path_name()
 m.set_material(0,E.load_asset('/Game/StarterContent/Materials/M_Metal_Copper'))
 m.set_collision_response_to_channel(unreal.CollisionChannel.ECC_ENEMY_SIGHT,unreal.CollisionResponseType.ECR_OVERLAP)
 m.set_collision_response_to_channel(unreal.CollisionChannel.ECC_DODGEBALL,unreal.CollisionResponseType.ECR_OVERLAP)
save(ghost)
victory=bp('/Game/Course/Dodgeball/BP_VictoryBox',unreal.load_class(None,'/Script/Study_Unreal_Shooter.VictoryBox'))
if not any(x.get_name().startswith('VictoryPlate') for x in A.get_components(cdo(victory))):
 meshcomp(victory,'VictoryPlate','/Game/StarterContent/Architecture/Floor_400x400',loc=(-150,-150,20),scale=(.75,.75,.75),material='/Game/StarterContent/Materials/M_Metal_Gold',profile='BlockAll')
cdo(victory).get_component_by_class(unreal.BoxComponent).set_collision_profile_name('Trigger');save(victory)
mode('/Game/Course/Dodgeball/BP_DodgeballGameMode','/Game/Course/Dodgeball/BP_DodgeballCharacter')
# All non-shooter stages use the canonical template-copy implementation.
import pathlib
exec(compile((pathlib.Path(unreal.Paths.project_dir())/'Scripts/rebuild_cpp_stages.py').read_text(encoding='utf-8-sig'), 'rebuild_cpp_stages.py', 'exec'))
