"""Checks for copied template maps and real gameplay at saved placements."""
import unreal
import course_runtime_verification as v

def steps():
    for path,expected in [
        ('/Game/Course/Maps/L_03_ThirdPerson','BP_MyTPC_C'),
        ('/Game/Course/ThirdPerson/L_03_MixamoAdam','BP_MyTPC_Adam_C'),
        ('/Game/Course/Basics/L_02_GanfaultAnimation','BP_Ganfault_C'),
        ('/Game/Course/Basics/L_02_Framework','BP_MyPawn_C'),
    ]:
        v.open_play(path);yield 2
        yield from v.ready()
        p=v.G.get_player_pawn(v.world(),0)
        v.check(expected+' possessed',p.get_class().get_name()==expected)
        v.check(expected+' template PlayerStart',abs(p.get_actor_location().x)<5 and abs(p.get_actor_location().y)<5)
        if isinstance(p,unreal.Character):
            r=p.mesh.get_editor_property('relative_rotation')
            v.check(expected+' upright mesh',abs(r.pitch)<.1 and abs(r.roll)<.1 and abs(r.yaw+90)<.1,str(r))
            v.check(expected+' animation',p.mesh.get_anim_instance() is not None)
            start=p.get_actor_location();v.key('W');yield .4
            v.key('W',False);yield .2
            end=p.get_actor_location()
            v.check(expected+' movement',(end-start).length()>50)
            v.key('SpaceBar');yield .15
            v.check(expected+' jump',p.character_movement.is_falling() and p.get_velocity().z>0)
            v.key('SpaceBar',False)
            if expected=='BP_MyTPC_C':
                speed=p.character_movement.max_walk_speed
                v.key('LeftShift');yield .2
                v.check('Third person walk .4',abs(p.character_movement.max_walk_speed-speed*.4)<.1)
                v.key('LeftShift',False)
        del p
        v.L.editor_request_end_play();yield 1

    v.open_play('/Game/Course/Maps/L_02_Basics');yield 2
    yield from v.ready()
    p=v.pawn();gm=v.G.get_game_mode(v.world())
    v.check('Basics game mode','BP_GameModeWithScore' in gm.get_class().get_name())
    item=v.actors('/Game/BP_Collectable.BP_Collectable_C')[0]
    score=gm.get_editor_property('GameScore')
    p.set_actor_location(item.get_actor_location()+unreal.Vector(0,0,50),False,True);yield .4
    v.check('Basics collectable reference',gm.get_editor_property('GameScore')==score+50)
    sparks=v.actors('/Game/BP_Platform_Sparks.BP_Platform_Sparks_C')[0]
    platform=sparks.get_editor_property('BP_Platform')
    v.check('Basics dispatcher actor reference',platform is not None)
    del p,gm,item,sparks,platform
    v.L.editor_request_end_play();yield 1

    yield from dodge_steps()

def dodge_steps():
    v.open_play('/Game/Course/Maps/L_04_Dodgeball');yield 2
    yield from v.ready()
    p=v.pawn();enemy=v.actors('/Game/Course/Dodgeball/BP_EnemyCharacter.BP_EnemyCharacter_C')[0]
    v.check('One enemy in saved layout',len(v.actors('/Game/Course/Dodgeball/BP_EnemyCharacter.BP_EnemyCharacter_C'))==1)
    v.check('Dodgeball pawn',p.get_class().get_name()=='BP_DodgeballCharacter_C')
    r=p.mesh.get_editor_property('relative_rotation')
    v.check('Dodgeball character upright',abs(r.pitch)<.1 and abs(r.yaw+90)<.1,str(r))
    v.check('Enemy stays at saved position',(enemy.get_actor_location()-unreal.Vector(1100,1070,100)).length()<10)
    ghost=v.actors('/Game/Course/Dodgeball/BP_GhostWall.BP_GhostWall_C')[0]
    r=ghost.get_actor_rotation()
    v.check('Ghost wall upright yaw 90',abs(r.pitch)<.1 and abs(r.roll)<.1 and abs(r.yaw-90)<.1,str(r))
    v.check('Initial cover occludes enemy',not enemy.can_see_actor(p))
    unreal.SystemLibrary.execute_console_command(v.world(),'shot showui',v.G.get_player_controller(v.world(),0));yield .5
    # Move only the player in PIE; the enemy/walls/obstacles retain saved poses.
    p.set_actor_location(unreal.Vector(1100,600,100),False,True);yield .5
    v.check('Saved steel wall blocks enemy sight',not enemy.can_see_actor(p))
    p.set_actor_location(unreal.Vector(650,1070,100),False,True);yield .2
    v.check('Saved ghost wall permits enemy sight',enemy.can_see_actor(p))
    seen=False
    for i in range(12):
        yield .1
        balls=v.actors('/Game/Course/Dodgeball/BP_DodgeballProjectile.BP_DodgeballProjectile_C')
        if balls:
            seen=True
            v.check('Deferred throw speed 2200',balls[0].get_component_by_class(unreal.ProjectileMovementComponent).initial_speed==2200)
            break
    v.check('Enemy throws from saved position',seen)
    p.set_actor_location(unreal.Vector(650,1070,100),False,True)
    pc=v.G.get_player_controller(v.world(),0)
    pc.set_control_rotation(unreal.Rotator(pitch=0,yaw=0,roll=0))
    v.key('W');yield .5
    v.key('W',False);yield .2
    v.check('Ghost wall blocks walking player',695<p.get_actor_location().x<785,p.get_actor_location().to_tuple())
    camera=p.get_component_by_class(unreal.CameraComponent)
    v.check('Camera keeps topdown distance at cover',(camera.get_world_location()-p.get_actor_location()).length()>850)
    unreal.SystemLibrary.execute_console_command(v.world(),'shot showui',pc);yield .5
    p.set_actor_location(unreal.Vector(1450,850,100),False,True)
    start=p.get_actor_location();v.key('S');yield .3
    v.key('S',False);yield .2
    v.check('Dodgeball open ground movement',(p.get_actor_location()-start).length()>50)
    victory=v.actors('/Game/Course/Dodgeball/BP_VictoryBox.BP_VictoryBox_C')[0]
    p.set_actor_location(victory.get_actor_location()+unreal.Vector(0,0,115),False,True);yield 1
    v.check('Victory ends PIE',not v.L.is_in_play_in_editor())

def start():v.start(steps,'template-runtime.json')
