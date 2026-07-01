# Workspace 구조

이 문서는 `/mnt/c/work_han` 아래에 있는 `workspace*` 디렉터리의 공통 구조와 각 경로의 역할을 설명한다.

디렉터리 이름의 `pc98`은 대상 플랫폼을 나타낸다. 자동화 스크립트에서는 이를 `platform` 값으로 구성하므로, 다른 플랫폼을 사용하면 같은 위치에 `jpn-dos`, `script-dos`, `kor-dos`와 같은 이름을 사용할 수 있다.

## 작업 흐름

```text
jpn-pc98/
  원본 일본어 바이너리
       │
       ▼ extract_script_auto.py
script_init-pc98/
  자동 추출한 일본어 JSON
       │
       ▼ 대상 선택, 복사 및 번역
script-pc98/
  편집 중인 *_jpn.json + *_kor.json
  custom_char.json / custom_word.json
       │
       │    binary_inputs-pc98/
       │      이미지, 압축 블록 등의 교체 데이터
       │             │
       └─────────────┴──▶ write_script_auto.py
                             │
                             ▼
kor-pc98/
  번역문을 기록한 한국어 바이너리
       │
       ▼ 복사 및 패키징
kor-pc98-dosbox-x/
  에뮬레이터 실행용 전체 게임 디렉터리
```

`script_init-pc98`는 전체 원본에서 자동 추출한 초기 자료이고, `script-pc98`는 실제 번역 대상으로 선별·편집하는 자료이다. 따라서 두 폴더의 파일 수가 달라도 이상이 아니다. `kor-pc98` 역시 수정된 파일만 담을 수 있어 `jpn-pc98`보다 파일 수가 적을 수 있다.

원본 바이너리의 하위 디렉터리는 이후 단계에서도 유지한다. 예를 들어 `jpn-pc98/BTL/FILE.DAT`에서 추출한 파일은 `script_init-pc98/BTL/FILE.DAT_jpn.json`이 되고, 최종 결과는 `kor-pc98/BTL/FILE.DAT`에 기록된다.

## 디렉터리와 파일 설명

| 경로 | 용도 |
| --- | --- |
| `jpn-pc98/` | 패치의 기준이 되는 일본어 원본 바이너리. 쓰기 단계에서 이 파일을 복사해 번역문을 반영한다. |
| `script_init-pc98/` | 원본 바이너리에서 자동 추출한 `*_jpn.json`. 번역 대상을 정하기 전의 초기 결과이다. |
| `script-pc98/` | 실제 작업본. 일반적으로 원본용 `*_jpn.json`과 번역용 `*_kor.json`을 함께 둔다. |
| `kor-pc98/` | `script-pc98`의 번역을 원본 바이너리에 기록한 결과물. |
| `binary_inputs-pc98/` | JSON 문자열만으로 넣을 수 없는 이미지, 압축 블록, 원시 플래너 데이터 등 바이너리 교체 자료. |
| `kor-pc98-dosbox-x/` | DOSBox-X에서 바로 실행하기 위한 전체 한국어판 파일 트리. 작업 공간에 따라 이름 끝에 `_`가 붙거나 별도 복사본이 존재한다. |
| `reverse/` | 디스어셈블 결과, 포맷 분석 코드, 디코딩 이미지 등 역공학 자료. |
| `capture/` | 실행 화면 캡처 및 확인 자료. |
| `dictionary.json` | 일본어 문장별 번역 후보와 사용 횟수를 모은 대사 사전. |
| `annoying.json` | 동일 일본어에 여러 번역이 사용되는 등 별도 확인이 필요한 문장 목록. |
| `info.txt` | 주소, 용어, 파일 포맷 등 작업 중 발견한 수동 메모. |
| `*.pkl` | 폰트 테이블과 커스텀 문자 조합으로 만든 캐시. 원본 데이터가 아니라 재생성 가능한 가속용 파일이다. |
| `*.bmp` | 한국어 글꼴 캔버스 또는 에뮬레이터용 글꼴 이미지. |
| `*.bat`, `*.conf` | 게임 실행용 배치 파일과 DOSBox-X 설정. |

`script-pc98/custom_char.json`은 기본 폰트 테이블에 없는 문자 매핑을, `custom_word.json`은 여러 글자를 하나의 게임 코드로 취급하는 커스텀 단어 매핑을 제공한다.

## 스크립트 파일 규칙

- `<파일명>_jpn.json`: 원본 바이너리에서 추출한 일본어 문자열과 주소 범위이다. 바이너리 검증과 한국어 기록의 기준으로 사용한다.
- `<파일명>_kor.json`: 같은 주소에 기록할 한국어 번역이다. 대응하는 `_jpn.json`과 한 쌍으로 관리한다.
- JSON 파일의 상대 경로와 `_jpn` 또는 `_kor` 앞의 파일명은 원본 바이너리의 상대 경로 및 파일명과 같아야 한다.
- `script_init-pc98`는 재추출 가능한 초기 산출물이고, 실제 번역 작업의 기준은 `script-pc98`이다.

## 수동 편집 대상과 생성물

| 구분 | 경로 |
| --- | --- |
| 보존할 원본 | `jpn-pc98/` |
| 주로 수동 편집 | `script-pc98/*_kor.json`, `custom_char.json`, `custom_word.json`, `binary_inputs-pc98/` |
| 원문·주소 조정 시 함께 편집 | `script-pc98/*_jpn.json` |
| 자동 생성 가능 | `script_init-pc98/`, `kor-pc98/`, 폰트 테이블 캐시 `*.pkl` |
| 실행 테스트용 | `kor-pc98-dosbox-x/` |
| 배포용 패치 | `kor-pc98/` |

## 작업 시 주의사항

- 자동화 스크립트의 `ws_num`, `platform` 값이 코드에 고정된 경우가 많다. 실행 전에 대상 workspace와 `pc98`/`dos` 설정을 확인해야 한다.
- `script-pc98`에서 `*_kor.json`만 수정하더라도 같은 이름의 `*_jpn.json` 주소 범위가 기준이 되므로 두 파일을 쌍으로 관리해야 한다.
- `write_script_auto.py`는 `jpn-pc98`의 원본을 읽어 `kor-pc98`에 쓴다. `kor-pc98`의 기존 파일을 원본처럼 사용하지 않는다.
- `binary_inputs-pc98`의 파일명과 상대 경로는 스크립트 토큰에서 참조될 수 있으므로 임의로 바꾸지 않는다.
- `script_init-pc98`, `reverse`, 배포 압축 파일은 목적이 서로 다르다. 번역 작업본은 `script-pc98`, 생성 결과는 `kor-pc98`을 기준으로 판단한다.
- 생성 스크립트를 다시 실행하면 `script_init-pc98`와 `kor-pc98`의 기존 파일을 덮어쓸 수 있으므로, 수동 수정 사항을 생성물에만 남기지 않는다.
