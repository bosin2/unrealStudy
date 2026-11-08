using UnrealBuildTool;
public class Study_Unreal_Shooter : ModuleRules {
 public Study_Unreal_Shooter(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput" });
 }
}
