# nobu2 Python 스크립트

- `gen_font_from_db_nobu2.py`: `NameDB`의 NB2 인명과 고정 단어·지명을 모아 한국어 폰트 BMP를 구성하고, 문자열과 코드의 대응표인 `custom_word.json`을 생성한다.
- `set_code_from_db_nobu2.py`: `DATA17.DAT`, `DATA50.DAT`, `ODAMAIN.EXE`의 스크립트 JSON에서 성명 배열을 읽어 `NameDB`의 한국어 이름으로 변환하고 길이와 주소를 맞춘다. 기본값 `save = False`에서는 변경 예정 내용만 출력하므로 실제 저장 시 값을 명시적으로 바꿔야 한다.

두 스크립트 모두 `C:/work_han/...` 경로와 작업 공간 번호를 내부 설정으로 사용한다.
