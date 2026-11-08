using UnrealBuildTool;
public class Study_Unreal_ShooterEditorTarget : TargetRules {
 public Study_Unreal_ShooterEditorTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Editor;
  DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
  ExtraModuleNames.Add("Study_Unreal_Shooter");
 }
}

