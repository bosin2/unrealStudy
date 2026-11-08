"""Copy actual Third Person template levels without replacing their geometry."""
import json
import pathlib
import unreal
E = unreal.EditorAssetLibrary
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
AS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
UE = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
TEMPLATE = '/Game/ThirdPerson/Lvl_ThirdPerson'
STAGES = [
    ('Maps/L_03_ThirdPerson', 'ThirdPerson/BP_ThirdPersonGameMode'),
    ('ThirdPerson/L_03_MixamoAdam', 'ThirdPerson/BP_AdamGameMode'),
    ('Basics/L_02_GanfaultAnimation', 'ThirdPerson/BP_GanfaultGameMode'),
    ('Basics/L_02_Framework', 'Basics/BP_MyGameMode'),
    ('Maps/L_04_Dodgeball', 'Dodgeball/BP_DodgeballGameMode'),
]

def xyz(v):
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]

def template_snapshot():
    """Compare geometry, materials, transforms, lighting and PlayerStart."""
    records = []
    for a in AS.get_all_level_actors():
        if a.get_class().get_name() in ('WorldDataLayers', 'WorldPartitionMiniMap'):
            continue
        r = a.get_actor_rotation()
        record = dict(label=a.get_actor_label(), cls=a.get_class().get_name(),
                      location=xyz(a.get_actor_location()), scale=xyz(a.get_actor_scale3d()),
                      rotation=[round(r.pitch, 3), round(r.yaw, 3), round(r.roll, 3)])
        if isinstance(a, unreal.StaticMeshActor):
            c = a.static_mesh_component
            assert c.static_mesh, a.get_actor_label()
            record['mesh'] = c.static_mesh.get_path_name()
            record['materials'] = [m.get_path_name() if m else None for m in c.get_materials()]
            record['collision'] = str(c.get_collision_profile_name())
        records.append(record)
    return sorted(records, key=lambda r: r['label'])

def replace_from_template(dest, source):
    assert dest.startswith('/Game/Course/'), dest
    assert L.load_level('/Engine/Maps/Entry')
    if E.does_asset_exist(dest):
        assert E.delete_asset(dest), dest
    if E.does_asset_exist(dest + '_BuiltData'):
        assert E.delete_asset(dest + '_BuiltData')
    assert L.new_level_from_template(dest, source), dest

def build(stage, gm, baseline):
    path = '/Game/Course/' + stage
    replace_from_template(path, TEMPLATE)
    assert template_snapshot() == baseline, 'Template copy changed actors: ' + path
    UE.get_editor_world().get_world_settings().set_editor_property(
        'default_game_mode', E.load_blueprint_class('/Game/Course/' + gm))
    if 'Dodgeball' in stage:
        # UE 5.8 has different geometry than the lecture's UE 5.0 map.
        # Keep its geometry intact. One enemy uses the north-east obstacle;
        # adjacent normal/ghost walls reproduce the L-shaped cover exercise.
        entries = [
            ('BP_EnemyCharacter', (1100, 1070, 100), (0, -130, 0), 'Enemy_01'),
            ('BP_Wall', (1000, 850, 0), (0, 0, 0), 'Wall'),
            ('BP_GhostWall', (800, 1050, 0), (0, 90, 0), 'GhostWall'),
            ('BP_VictoryBox', (1550, 650, 0), (0, 0, 0), 'VictoryBox'),
        ]
        for name, loc, rot, label in entries:
            a = AS.spawn_actor_from_class(E.load_blueprint_class('/Game/Course/Dodgeball/' + name),
                                         unreal.Vector(*loc), unreal.Rotator(pitch=rot[0], yaw=rot[1], roll=rot[2]))
            assert a, name
            a.set_actor_label(label)
    assert L.save_current_level()
    assert L.load_level('/Engine/Maps/Entry')
    assert L.load_level(path)
    actual = template_snapshot()
    by_label = {r['label']: r for r in actual}
    assert all(by_label.get(r['label']) == r for r in baseline), path
    assert not any(r['label'] == 'PracticeFloor' or r['label'].startswith('JumpStep_') for r in actual)
    return dict(map=path, template=TEMPLATE, preserved_template_actors=len(baseline),
                added_actors=[r for r in actual if r['label'] not in {b['label'] for b in baseline}])

assert not L.is_in_play_in_editor(), 'Stop PIE before rebuilding levels'
assert L.load_level(TEMPLATE)
baseline = template_snapshot()
assert len([r for r in baseline if r['cls'] == 'StaticMeshActor']) > 20
report = [build(stage, gm, baseline) for stage, gm in STAGES]
# This published lesson map is itself a Third Person template copy. Copy it
# whole to preserve its Level Blueprint dispatcher references.
replace_from_template('/Game/Course/Maps/L_02_Basics', '/Game/ThirdPersonBP/Maps/ThirdPersonExampleMap')
UE.get_editor_world().get_world_settings().set_editor_property(
    'default_game_mode', E.load_blueprint_class('/Game/BP_GameModeWithScore'))
a = AS.spawn_actor_from_class(E.load_blueprint_class('/Game/TestActor'), unreal.Vector(300, 500, 100))
a.set_actor_label('Cpp01_TestActor')
del a
assert L.save_current_level()
report.append(dict(map='/Game/Course/Maps/L_02_Basics', template='/Game/ThirdPersonBP/Maps/ThirdPersonExampleMap'))
out = pathlib.Path(unreal.Paths.project_saved_dir()) / 'CourseVerification/template-layout.json'
out.write_text(json.dumps(dict(baseline=baseline, levels=report), indent=2), encoding='utf-8')
assert L.load_level('/Game/Course/Maps/L_04_Dodgeball')
result = report
