# unrealStudy

Unreal Engine **5.8**로 진행한 블루프린트·C++ 실습 프로젝트입니다.
하나의 `Study_Unreal_Shooter.uproject` 안에서 레벨별로 실습을 구분합니다.

## 실행

Windows에 Unreal Engine 5.8, Unreal C++ 빌드 도구가 포함된 Visual Studio, Git LFS를 설치합니다.

```powershell
git lfs install
git clone https://github.com/bosin2/unrealStudy.git
cd unrealStudy
git lfs pull
```

`Study_Unreal_Shooter.uproject`를 열고 C++ 모듈 빌드 요청을 진행합니다.
필요하면 `.uproject`의 우클릭 메뉴에서 Visual Studio 프로젝트 파일을 생성한 뒤
`Development Editor / Win64`로 빌드합니다.

에셋은 Git LFS로 관리하므로 **Git LFS를 사용한 clone**을 권장합니다.
빌드 결과, 캐시, 개인 설정, 임시 다운로드, 강의 PDF는 저장소에 포함하지 않습니다.

## 실습 레벨

| 경로 (`Content/` 기준) | 내용 |
| --- | --- |
| `Course/Maps/L_01_Shooter` | 1인칭 슈터, 표적, 달리기, 줌, HUD |
| `Course/Maps/L_02_Basics` | 블루프린트 통신, 조명, 점수, 플랫폼, TestActor |
| `Course/Maps/L_03_ThirdPerson` | C++ 삼인칭 캐릭터, 애니메이션, Enhanced Input |
| `Course/Maps/L_04_Dodgeball` | 탑다운 이동, 적 시야, 공 투척, 일반·투과 벽, 승리 영역 |
| `Course/Basics/L_02_Framework` | Pawn·PlayerController·GameMode 기초 |
| `Course/Basics/L_02_GanfaultAnimation` | Ganfault 애니메이션 |
| `Course/ThirdPerson/L_03_MixamoAdam` | Mixamo Adam 캐릭터 |

자세한 조작과 자료별 구현 내용은 [실습 레벨 안내](Docs/실습_레벨_안내.md)를 참고하세요.
삼인칭 실습은 기본 템플릿 맵의 지형을 보존합니다. UE 5.8과 강의의 구버전은 기본 맵 지형이 다릅니다.

## 구성과 출처

- `Source/`: 게임 C++ 코드
- `Content/`: 맵·블루프린트·애니메이션·메시 등 프로젝트 에셋
- `Config/`: 공유 프로젝트 설정
- `Scripts/`: 에디터 자동화 및 실습 검증 코드. 일반 플레이에는 실행할 필요가 없습니다.
- `Docs/`: 실습 안내 및 원본 코드 라이선스

출판사 예제 코드의 라이선스는 [Docs/Licenses](Docs/Licenses)에 보관했습니다.
Unreal Engine 템플릿·Starter Content 및 외부 캐릭터 에셋에는 각 원본의 이용 조건이 적용됩니다.
