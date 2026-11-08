#include "CourseVerificationLibrary.h"
#include "GameFramework/PlayerController.h"
#include "InputKeyEventArgs.h"

bool UCourseVerificationLibrary::InjectKey(APlayerController* Controller, FName KeyName, bool Pressed)
{
#if WITH_EDITOR
 if (Controller)
 {
  return Controller->InputKey(FInputKeyEventArgs::CreateSimulated(
   FKey(KeyName), Pressed ? IE_Pressed : IE_Released, Pressed ? 1.f : 0.f));
 }
#endif
 return false;
}
