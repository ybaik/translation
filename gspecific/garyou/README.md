# garyou Python 스크립트

- `end_dat_to_png.py`: 게임 엔딩의 `END_S*.DAT` 파일을 RLE 해제하고 PC-98 4bpp 플래너 데이터를 변환해 640×400 PNG로 저장한다. `ENDPAL.GRG` 또는 `ENDPAL.BRG`에서 이미지 번호에 맞는 팔레트를 읽는다.
- `end_png_to_dat.py`: 640×400 한국어 PNG를 지정 팔레트의 인덱스로 변환한 뒤 플래너 형식과 게임의 RLE 형식으로 인코딩해 `*.kor.DAT`를 만든다. `--verify`를 사용하면 생성 파일을 다시 디코딩해 픽셀 인덱스를 검증한다.

두 스크립트 모두 `--workspace`를 필수로 받는다. 원본과 팔레트는 `jpn-pc98/`, 변환 자료는 파일별 `image-pc98/END_S*.DAT/`을 사용한다.
