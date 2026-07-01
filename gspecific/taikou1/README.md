# taikou1 Python 스크립트

- `pc98_image_codec.py`: PC-98 인덱스/플래너 이미지 변환, 게임 전용 RLE/LZ 압축·해제, 매니페스트 읽기와 HTML 미리보기 생성을 제공하는 공용 모듈이다.
- `decode_raw_planar.py`: 코드에 정의된 원본 파일의 고정 크기 플래너 이미지 블록을 PNG로 추출하고 JSON/HTML 인덱스를 만든다. 포함된 파일의 일부 주소 범위도 처리한다.
- `encode_raw_planar.py`: 디코딩 결과에 대응하는 `.kor` 폴더의 오프셋명 PNG를 원본 크기의 플래너 블록으로 재인코딩하고 `encode_index.json`을 기록한다.
- `decode_rle_lz.py`: 코드에 정의된 이미지 아카이브를 순회하며 RLE/LZ 프레임을 PNG로 추출하고 JSON/HTML 보고서를 만든다. `--intermediate`로 플래너 및 픽셀 중간 파일도 저장할 수 있다.
- `encode_rle_lz.py`: `.kor` 폴더의 오프셋명 PNG를 삽입 가능한 RLE/LZ 블록으로 만든다. 기본적으로 원본 압축 크기까지 널 패딩하며 `--no-padding`으로 끌 수 있다.
- `gen_font_from_db_taiko1.py`: Taikou 1 인명과 고정 지명·문구에 필요한 글꼴을 기존 BMP 캔버스에 배치해 새 폰트 BMP와 `custom_word.json`을 생성한다.
- `set_code_from_db_taiko1.py`: `TBS.DAT`와 `MAIN.EXE`의 성/이름 항목을 `NameDB`의 한국어 이름 토큰으로 바꾸고 일본어/한국어 스크립트 JSON의 길이와 주소를 함께 조정한다.

이미지 변환 대상 목록과 폰트·작업 공간 경로는 각 스크립트 내부 상수로 정의되어 있다.
