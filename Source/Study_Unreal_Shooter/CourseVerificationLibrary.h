#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "CourseVerificationLibrary.generated.h"

// Development-only input injection for repeatable PIE checks of the real input bindings.
UCLASS()
class STUDY_UNREAL_SHOOTER_API UCourseVerificationLibrary : public UBlueprintFunctionLibrary
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable, meta=(DevelopmentOnly), Category="Course|Verification")
 static bool InjectKey(APlayerController* Controller, FName KeyName, bool Pressed);
};
