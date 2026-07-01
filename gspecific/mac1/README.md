# mac1 Python 스크립트

- `decode.py`: Macintosh 게임의 커스텀 `.IMG` 헤더와 Delta+RLE 데이터를 해제하고, 4bpp 플래너 이미지를 회색조 BMP로 저장한다. 현재 예제 입력은 `customized/mac1/examples/MG09.IMG`로 고정되어 있다.
- `codec.py`: `.IMG`용 열 우선 순회 순서를 만들고 Delta+RLE 압축을 수행하는 공용 함수가 들어 있다. 직접 실행하면 `MG09.PLA`를 압축해 참조 `MG09.IMG`의 페이로드와 비교한다.
- `make_kor_img.py`: 원본 `.IMG`의 헤더와 크기를 유지하면서 대응하는 `_Kor.bmp`를 플래너 데이터로 변환·압축해 `_Kor.IMG`를 생성한다. 처리할 파일명과 경로는 `main()`에 지정되어 있다.

`__init__.py`는 이 폴더를 Python 패키지로 표시하며 별도의 처리 로직은 없다.
