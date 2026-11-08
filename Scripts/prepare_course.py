from pathlib import Path
import json, shutil, re
R=Path(__file__).resolve().parents[1]
S=R/'Source/Study_Unreal_Shooter';S.mkdir(parents=True,exist_ok=True)
origin=R/'tmp/official/cpp'
sources={
 'MyThirdPersonChar.h':'Chapter04/Activity4.01/MyThirdPersonChar.h',
 'MyThirdPersonChar.cpp':'Chapter04/Activity4.01/MyThirdPersonChar.cpp',
 'DodgeballCharacter.h':'Chapter05/Exercise5.01/DodgeballCharacter.h',
 'DodgeballCharacter.cpp':'Chapter05/Exercise5.01/DodgeballCharacter.cpp',
 'EnemyCharacter.h':'Chapter06/Exercise6.03/EnemyCharacter.h',
 'EnemyCharacter.cpp':'Chapter06/Exercise6.03/EnemyCharacter.cpp',
 'DodgeballProjectile.h':'Chapter06/Exercise6.06/DodgeballProjectile.h',
 'DodgeballProjectile.cpp':'Chapter06/Exercise6.03/DodgeballProjectile.cpp',
 'Wall.h':'Chapter06/Exercise6.04/Wall.h',
 'Wall.cpp':'Chapter06/Exercise6.04/Wall.cpp',
 'VictoryBox.h':'Chapter06/Exercise6.05/VictoryBox.h',
 'VictoryBox.cpp':'Chapter06/Exercise6.05/VictoryBox.cpp',
}
for dst,src in sources.items():
 t=(origin/src).read_text(encoding='utf-8-sig').replace('MYTHIRDPERSON_API','STUDY_UNREAL_SHOOTER_API').replace('DODGEBALL_API','STUDY_UNREAL_SHOOTER_API')
 t=t.replace('#include "DodgeballCharacter.h "','#include "DodgeballCharacter.h"')
 if dst=='DodgeballCharacter.cpp':
  t=t.replace('\tHealthComponent = CreateDefaultSubobject<UHealthComponent>(TEXT("Health Component"));','')
  # The published source contains an unrelated chapter-7 line; the lecture has no health component.
  t=t.replace('\tJump();','').replace('\tStopJumping();','')
  t=t.replace('\tcheck(PlayerInputComponent);','\tSuper::SetupPlayerInputComponent(PlayerInputComponent);\n\tcheck(PlayerInputComponent);')
 if dst in ['MyThirdPersonChar.cpp','DodgeballCharacter.cpp']:
  t=t.replace('EnhancedSubsystem != nullptr','EnhancedSubsystem != nullptr && IC_Character != nullptr')
 if dst=='EnemyCharacter.cpp':
  t=t.replace('ECC_GameTraceChannel1','ECC_GameTraceChannel2')
  t=t.replace('bool AEnemyCharacter::CanSeeActor(AActor * TargetActor)','bool AEnemyCharacter::CanSeeActor(const AActor * TargetActor) const')
  t=t.replace('SightSource->SetupAttachment(RootComponent);','SightSource->SetupAttachment(RootComponent);\n\tSightSource->SetRelativeLocation(FVector(10.f, 0.f, 80.f));')
  t=t.replace('#include "DodgeballProjectile.h"','#include "DodgeballProjectile.h"\n#include "GameFramework/ProjectileMovementComponent.h"\n#include "Components/SceneComponent.h"')
  t=t.replace('GetWorld()->SpawnActor<ADodgeballProjectile>(DodgeballClass, SpawnLocation, GetActorRotation());', '''FTransform SpawnTransform(GetActorRotation(), SpawnLocation);
    ADodgeballProjectile* Projectile = GetWorld()->SpawnActorDeferred<ADodgeballProjectile>(DodgeballClass, SpawnTransform);
    if (Projectile)
    {
        Projectile->GetProjectileMovementComponent()->InitialSpeed = 2200.f;
        Projectile->FinishSpawning(SpawnTransform);
    }''')
 if dst=='EnemyCharacter.h':
  t=t.replace('protected:','public:')
  t=t.replace('bool CanSeeActor(AActor* TargetActor);','UFUNCTION(BlueprintCallable, Category="LookAt")\n\tbool CanSeeActor(const AActor* TargetActor) const;')
  t=t.replace('bool LookAtActor(AActor* TargetActor);','UFUNCTION(BlueprintCallable, Category="LookAt")\n\tbool LookAtActor(AActor* TargetActor);')
  t=t.replace('void ThrowDodgeball();','UFUNCTION(BlueprintCallable, Category="Dodgeball")\n\tvoid ThrowDodgeball();')
 if dst=='DodgeballProjectile.cpp':t=t.replace('InitialSpeed = 2200.f','InitialSpeed = 1500.f')
 if dst in ['Wall.cpp','VictoryBox.cpp']:t=t.replace('#include "'+dst.replace('.cpp','.h')+'"','#include "'+dst.replace('.cpp','.h')+'"\n#include "Components/SceneComponent.h"')
 (S/dst).write_text(t,encoding='utf-8')
(S/'Study_Unreal_Shooter.cpp').write_text('#include "Modules/ModuleManager.h"\nIMPLEMENT_PRIMARY_GAME_MODULE(FDefaultGameModuleImpl, Study_Unreal_Shooter, "Study_Unreal_Shooter");\n')
(S/'Study_Unreal_Shooter.Build.cs').write_text('''using UnrealBuildTool;
public class Study_Unreal_Shooter : ModuleRules {
 public Study_Unreal_Shooter(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput" });
 }
}
''')
for kind in ['','Editor']:
 (R/'Source'/f'Study_Unreal_Shooter{kind}.Target.cs').write_text('''using UnrealBuildTool;
public class Study_Unreal_Shooter%sTarget : TargetRules {
 public Study_Unreal_Shooter%sTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.%s;
  DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
  ExtraModuleNames.Add("Study_Unreal_Shooter");
 }
}
'''%(kind,kind,kind or 'Game'))
p=R/'Study_Unreal_Shooter.uproject';data=json.loads(p.read_text())
data['Modules']=[{'Name':'Study_Unreal_Shooter','Type':'Runtime','LoadingPhase':'Default'}]
for name in ['EnhancedInput','PythonScriptPlugin','EditorScriptingUtilities','EditorToolset','ModelContextProtocol']:
 if not any(x['Name']==name for x in data['Plugins']):data['Plugins'].append({'Name':name,'Enabled':True})
p.write_text(json.dumps(data,indent=2)+'\n')
engine=R/'Config/DefaultEngine.ini';t=engine.read_text(encoding='utf-8-sig')
if 'Name="EnemySight"' not in t:
 t=t.replace('[/Script/Engine.CollisionProfile]', '''[/Script/Engine.CollisionProfile]
+DefaultChannelResponses=(Channel=ECC_GameTraceChannel2,DefaultResponse=ECR_Block,bTraceType=True,bStaticObject=False,Name="EnemySight")
+DefaultChannelResponses=(Channel=ECC_GameTraceChannel3,DefaultResponse=ECR_Block,bTraceType=False,bStaticObject=False,Name="Dodgeball")
+Profiles=(Name="Dodgeball",CollisionEnabled=QueryAndPhysics,ObjectTypeName="Dodgeball",CustomResponses=((Channel="Camera",Response=ECR_Ignore),(Channel="EnemySight",Response=ECR_Ignore)),HelpMessage="GSD2 6.01",bCanModify=True)''')
 t+='\n[CoreRedirects]\n'
 for cls in ['MyThirdPersonChar','DodgeballCharacter','EnemyCharacter','DodgeballProjectile','Wall','VictoryBox']:
  old='MyThirdPerson' if cls=='MyThirdPersonChar' else 'Dodgeball'
  t+=f'+ClassRedirects=(OldName="/Script/{old}.{cls}",NewName="/Script/Study_Unreal_Shooter.{cls}")\n'
engine.write_text(t,encoding='utf-8')
# Preserve current input mappings; append only the legacy mappings used by the course Blueprint examples.
inp=R/'Config/DefaultInput.ini';t=inp.read_text(encoding='utf-8-sig')
legacy=(R/'tmp/official/blue/Chapter07/Config/DefaultInput.ini').read_text(encoding='utf-8-sig')
extra=[l for l in legacy.splitlines() if l.startswith(('+ActionMappings=','+AxisMappings=')) and l not in t]
if extra:t+='\n[/Script/Engine.InputSettings]\n'+'\n'.join(extra)+'\n'
inp.write_text(t,encoding='utf-8')
lic=R/'Docs/Licenses';lic.mkdir(parents=True,exist_ok=True)
for folder in ['blue','cpp']:shutil.copy2(R/'tmp/official'/folder/'LICENSE',lic/f'Packt-{folder}-MIT.txt')
print('Course C++ module, input mappings, collision channels and license notices prepared.')

