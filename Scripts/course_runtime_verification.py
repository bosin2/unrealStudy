"""Run real PIE input/collision checks through a nonblocking editor tick callback."""
import unreal,time,json,pathlib,traceback
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
OUT=ROOT/'Saved/CourseVerification';OUT.mkdir(parents=True,exist_ok=True)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UE=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
G=unreal.GameplayStatics
checks=[]
REPORT='runtime-checks.json'
def world():return UE.get_game_world()
def pawn():return G.get_player_character(world(),0)
def key(name,pressed=True):return unreal.CourseVerificationLibrary.inject_key(G.get_player_controller(world(),0),name,pressed)
def check(name,ok,detail=None):
 checks.append({'test':name,'passed':bool(ok),'detail':detail})
 (OUT/REPORT).write_text(json.dumps({'checks':checks,'running':True},indent=2,default=str),encoding='utf-8')
 unreal.log('COURSE_CHECK '+name+' '+str(bool(ok)))
def actors(path):return G.get_all_actors_of_class(world(),unreal.load_class(None,path))
def open_play(path):
 assert L.load_level(path)
 L.editor_request_begin_play()
def ready():
 # Shader/asset preparation can tick Slate before the new PIE world starts advancing.
 for attempt in range(120):
  if world() and G.get_time_seconds(world())>1:return
  yield .25
 raise RuntimeError('PIE world did not begin advancing')
def steps():
 open_play('/Game/Course/Maps/L_01_Shooter');yield 3
 yield from ready()
 p=pawn();check('Shooter pawn',p is not None and 'FirstPersonBP' in p.get_class().get_path_name())
 check('HUD initial values',[p.get_editor_property(k) for k in ['PlayerHealth','PlayerStamina','PlayerCurrentAmmo','TargetsEliminated']]==[1.,1.,30,0])
 widgets=unreal.WidgetLibrary.get_all_widgets_of_class(world(),unreal.load_class(None,'/Game/FirstPersonBP/UI/HUD.HUD_C'),False)
 check('HUD on viewport',len(widgets)==1 and widgets[0].is_in_viewport())
 key('LeftShift');yield .4
 check('Sprint 2200',abs(pawn().character_movement.max_walk_speed-2200)<.1,pawn().character_movement.max_walk_speed)
 key('LeftShift',False);yield .4
 check('Sprint release 600',abs(pawn().character_movement.max_walk_speed-600)<.1,pawn().character_movement.max_walk_speed)
 key('RightMouseButton');yield .7
 check('Zoom FOV 45',abs(pawn().get_components_by_class(unreal.CameraComponent)[0].field_of_view-45)<.1,pawn().get_components_by_class(unreal.CameraComponent)[0].field_of_view)
 key('RightMouseButton',False);yield .7
 check('Zoom release FOV 90',abs(pawn().get_components_by_class(unreal.CameraComponent)[0].field_of_view-90)<.1)
 # A clear elevated firing lane leaves the saved level untouched.
 p=pawn();p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
 p.set_actor_location(unreal.Vector(0,0,700),False,True)
 G.get_player_controller(world(),0).set_control_rotation(unreal.Rotator(0,0,0))
 target=actors('/Game/FirstPersonBP/Blueprints/BP_CylinderTarget.BP_CylinderTarget_C')[0]
 target.set_actor_location(unreal.Vector(500,0,750),False,True)
 target.set_actor_scale3d(unreal.Vector(3,3,3))
 target.set_editor_property('Speed',0.)
 before=p.get_editor_property('PlayerCurrentAmmo');score=p.get_editor_property('TargetsEliminated')
 key('LeftMouseButton');yield .3
 key('LeftMouseButton',False);yield .4
 check('Firing consumes one ammo',p.get_editor_property('PlayerCurrentAmmo')==before-1,p.get_editor_property('PlayerCurrentAmmo'))
 check('First hit primes cylinder',target.get_editor_property('Primed'))
 key('LeftMouseButton');yield .3
 key('LeftMouseButton',False);yield .4
 check('Second hit destroys cylinder',not unreal.SystemLibrary.is_valid(target))
 check('Eliminated count increments',p.get_editor_property('TargetsEliminated')==score+1,p.get_editor_property('TargetsEliminated'))
 unreal.SystemLibrary.execute_console_command(world(),'shot showui',G.get_player_controller(world(),0));yield .5
 del p,target,widgets
 L.editor_request_end_play();yield 1

 open_play('/Game/Course/Maps/L_02_Basics');yield 2
 yield from ready()
 p=pawn();gm=G.get_game_mode(world())
 check('Basics GameModeWithScore','BP_GameModeWithScore' in gm.get_class().get_name())
 floating=actors('/Game/TestActor.TestActor_C')[0];z=floating.get_actor_location().z;t=G.get_time_seconds(world());yield .6
 for attempt in range(40):
  dt=G.get_time_seconds(world())-t
  if dt>.1:break
  yield .25
 dz=floating.get_actor_location().z-z
 check('TestActor rises at 25 cm/s',dt>0 and abs(dz/max(dt,.001)-25)<1,{'speed':dz/max(dt,.001),'dt':dt})
 collectibles=actors('/Game/BP_Collectable.BP_Collectable_C')
 check('Collectable exists',len(collectibles)>0)
 if collectibles:
  collectible=collectibles[0];score=gm.get_editor_property('GameScore')
  p.set_actor_location(collectible.get_actor_location()+unreal.Vector(0,0,50),False,True);yield .5
  check('Collectable adds 50',gm.get_editor_property('GameScore')==score+50,gm.get_editor_property('GameScore'))
  check('Collectable destroyed',not unreal.SystemLibrary.is_valid(collectible))
 del p,gm,floating,collectibles
 L.editor_request_end_play();yield 1

 open_play('/Game/Course/Maps/L_03_ThirdPerson');yield 2
 yield from ready()
 p=pawn();check('C++ third person pawn',p.get_class().get_path_name()=='/Game/BP_MyTPC.BP_MyTPC_C')
 base=p.character_movement.max_walk_speed
 key('LeftShift');yield .4
 check('Walk multiplier .4',abs(p.character_movement.max_walk_speed-base*.4)<.1,p.character_movement.max_walk_speed)
 key('LeftShift',False);yield .4
 check('Walk restores speed',abs(p.character_movement.max_walk_speed-base)<.1)
 start=p.get_actor_location();key('W');yield .5
 key('W',False);yield .2
 move=p.get_actor_location()-start
 check('W moves C++ character',move.x*move.x+move.y*move.y>1600,move.to_tuple())
 key('SpaceBar');yield .2
 check('Jump launches character',p.character_movement.is_falling() and p.get_velocity().z>0,p.get_velocity().to_tuple())
 key('SpaceBar',False)
 check('Mannequin animation instance',p.mesh.get_anim_instance() is not None)
 del p
 L.editor_request_end_play();yield 1

 open_play('/Game/Course/Maps/L_04_Dodgeball');yield 2
 yield from ready()
 p=pawn();check('Dodgeball pawn','BP_DodgeballCharacter' in p.get_class().get_name())
 arm=p.get_component_by_class(unreal.SpringArmComponent)
 check('Topdown camera',abs(arm.target_arm_length-900)<.1 and abs(arm.get_editor_property('relative_rotation').pitch+70)<.1)
 enemies=actors('/Game/Course/Dodgeball/BP_EnemyCharacter.BP_EnemyCharacter_C')
 balls=actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C')
 check('Enemies automatically throw',len(balls)>0,{'enemies':len(enemies),'balls':len(balls)})
 if balls:
  check('Deferred projectile speed 2200',balls[0].get_component_by_class(unreal.ProjectileMovementComponent).initial_speed==2200)
 wall=actors('/Game/Course/Dodgeball/BP_Wall.BP_Wall_C')
 normal=next(a for a in wall if a.get_class().get_name()=='BP_Wall_C')
 ghost=next(a for a in wall if a.get_class().get_name()=='BP_GhostWall_C')
 wm=normal.get_component_by_class(unreal.StaticMeshComponent);gm=ghost.get_component_by_class(unreal.StaticMeshComponent)
 check('Normal wall blocks sight',wm.get_collision_response_to_channel(unreal.CollisionChannel.ECC_ENEMY_SIGHT)==unreal.CollisionResponseType.ECR_BLOCK)
 check('Ghost overlaps sight and dodgeballs',all(gm.get_collision_response_to_channel(ch)==unreal.CollisionResponseType.ECR_OVERLAP for ch in [unreal.CollisionChannel.ECC_ENEMY_SIGHT,unreal.CollisionChannel.ECC_DODGEBALL]))
 check('Ghost still blocks player',gm.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponseType.ECR_BLOCK)
 # Place the enemy and player across each actual wall to exercise native traces.
 enemy=enemies[0]
 enemy.set_actor_location(normal.get_actor_location()+unreal.Vector(0,-300,100),False,True)
 p.set_actor_location(normal.get_actor_location()+unreal.Vector(0,300,100),False,True);yield .2
 check('Normal wall occludes enemy line trace',not enemy.can_see_actor(p))
 enemy.set_actor_location(ghost.get_actor_location()+unreal.Vector(-300,0,100),False,True)
 p.set_actor_location(ghost.get_actor_location()+unreal.Vector(300,0,100),False,True);yield .2
 check('Ghost permits enemy line trace',enemy.can_see_actor(p))
 start=p.get_actor_location();key('W');yield .4
 key('W',False);yield .1
 move=p.get_actor_location()-start
 check('Dodgeball movement',move.x*move.x+move.y*move.y>400,move.to_tuple())
 victory=actors('/Game/Course/Dodgeball/BP_VictoryBox.BP_VictoryBox_C')[0]
 p.set_actor_location(victory.get_actor_location()+unreal.Vector(0,0,110),False,True);yield 1
 check('Victory overlap exits PIE',not L.is_in_play_in_editor())
 yield 0

def start(sequence=None,report_name='runtime-checks.json'):
 global iterator,next_time,handle,checks,REPORT
 checks=[];REPORT=report_name
 iterator=(sequence or steps)();next_time=0
 handle=unreal.register_slate_post_tick_callback(tick)
def tick(delta):
 global next_time,in_tick
 # Map loading can pump Slate recursively; never advance a running generator.
 if globals().get('in_tick',False) or time.monotonic()<next_time:return
 in_tick=True
 try:
  delay=next(iterator);next_time=time.monotonic()+delay
 except StopIteration:
  finish()
 except Exception:
  checks.append({'test':'runner exception','passed':False,'detail':traceback.format_exc()});finish()
 finally:
  in_tick=False
def finish():
 unreal.unregister_slate_post_tick_callback(handle)
 if L.is_in_play_in_editor():L.editor_request_end_play()
 (OUT/REPORT).write_text(json.dumps({'running':False,'passed':all(c['passed'] for c in checks),'checks':checks},indent=2,default=str),encoding='utf-8')
 unreal.log('COURSE_RUNTIME_CHECKS_FINISHED')


