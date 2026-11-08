import unreal
import course_runtime_verification as v
def steps():
 v.open_play('/Game/Course/Maps/L_01_Shooter');yield 2
 yield from v.ready()
 p=v.pawn();barrel=v.actors('/Game/BP_Barrel.BP_Barrel_C')[0]
 fire=barrel.get_editor_property('BP_Fire');particle=fire.get_component_by_class(unreal.ParticleSystemComponent)
 v.check('Fire initially hidden at particle component',particle.get_editor_property('hidden_in_game') and not fire.hidden)
 # Sweep the actual player capsule into the solid barrel to dispatch Event Hit.
 loc=barrel.get_actor_location()
 p.character_movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
 p.set_actor_location(loc+unreal.Vector(-180,0,80),False,True)
 v.G.get_player_controller(v.world(),0).set_control_rotation(unreal.Rotator(0,0,0))
 v.key('W');yield .6
 v.key('W',False);yield .1
 v.check('Barrel hit reveals referenced fire',not particle.get_editor_property('hidden_in_game'))
 del p,barrel,fire,particle
 v.L.editor_request_end_play();yield 1

 v.open_play('/Game/Course/Maps/L_02_Basics');yield 2
 yield from v.ready()
 p=v.pawn();switch=v.actors('/Game/BP_LightSwitch.BP_LightSwitch_C')[0]
 light=switch.get_editor_property('Light').get_component_by_class(unreal.PointLightComponent)
 before=light.visible
 p.set_actor_location(switch.get_actor_location()+unreal.Vector(20,20,100),False,True);yield .4
 v.check('LightSwitch overlap toggles lamp',light.visible!=before)
 sparks=v.actors('/Game/BP_Platform_Sparks.BP_Platform_Sparks_C')[0]
 platform=sparks.get_editor_property('BP_Platform')
 component=sparks.get_component_by_class(unreal.ParticleSystemComponent)
 p.set_actor_location(platform.get_actor_location()+unreal.Vector(0,0,60),False,True);yield .5
 v.check('Platform dispatcher activates sparks',component.is_active())
 del p,switch,light,sparks,platform,component
 v.L.editor_request_end_play();yield 1

 v.open_play('/Game/Course/Basics/L_02_Framework');yield 2
 yield from v.ready()
 pc=v.G.get_player_controller(v.world(),0);p=v.G.get_player_pawn(v.world(),0)
 v.check('Framework custom Pawn and PC',p.get_class().get_name()=='BP_MyPawn_C' and pc.get_class().get_name()=='BP_MyPC_C')
 v.check('Framework custom GameMode',v.G.get_game_mode(v.world()).get_class().get_name()=='BP_MyGameMode_C')
 del pc,p
 v.L.editor_request_end_play();yield 1
 for path,expected in [('/Game/Course/Basics/L_02_GanfaultAnimation','Ganfault'),('/Game/Course/ThirdPerson/L_03_MixamoAdam','Adam')]:
  v.open_play(path);yield 2
  yield from v.ready()
  p=v.pawn();anim=p.mesh.get_anim_instance()
  v.check(expected+' animation instance',anim is not None,{'mesh':str(p.mesh.get_skeletal_mesh_asset()),'anim':str(anim)})
  key_start=p.get_actor_location();v.key('W');yield .4
  v.key('W',False);yield .1
  delta=p.get_actor_location()-key_start
  v.check(expected+' movement',delta.x*delta.x+delta.y*delta.y>400,delta.to_tuple())
  del p,anim
  v.L.editor_request_end_play();yield 1

 v.open_play('/Game/Course/Maps/L_04_Dodgeball');yield 2
 yield from v.ready()
 p=v.pawn();enemies=v.actors('/Game/Course/Dodgeball/BP_EnemyCharacter.BP_EnemyCharacter_C')
 for e in enemies:e.set_actor_tick_enabled(False)
 enemy=enemies[0];enemy.set_actor_location(unreal.Vector(0,0,100),False,True)
 p.set_actor_location(unreal.Vector(500,0,100),False,True)
 enemy.look_at_actor(p)
 before={b.get_name() for b in v.actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C')}
 enemy.throw_dodgeball()
 shot=next(b for b in v.actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C') if b.get_name() not in before)
 yield .8
 v.check('Dodgeball hit destroys projectile',not unreal.SystemLibrary.is_valid(shot))
 enemy.set_actor_location(unreal.Vector(0,0,2000),False,True)
 enemy.set_actor_rotation(unreal.Rotator(pitch=0, yaw=90, roll=0),False)
 before={b.get_name() for b in v.actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C')}
 enemy.throw_dodgeball()
 shot=next(b for b in v.actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C') if b.get_name() not in before)
 yield 5.3
 v.check('Dodgeball expires after five seconds',not unreal.SystemLibrary.is_valid(shot))
 del p,enemy,enemies,shot
 v.L.editor_request_end_play();yield 1
 v.L.load_level('/Game/Course/Maps/L_01_Shooter')
def start():v.start(steps,'extra-checks.json')
