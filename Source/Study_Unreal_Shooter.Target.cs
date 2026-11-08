using UnrealBuildTool;
public class Study_Unreal_ShooterTarget : TargetRules {
 public Study_Unreal_ShooterTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Game;
  DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
  ExtraModuleNames.Add("Study_Unreal_Shooter");
 }
}

