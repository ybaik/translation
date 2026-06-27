import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator


def iter_strings(value: Any) -> Iterator[str]:
    """JSON 값에서 모든 문자열을 재귀적으로 꺼낸다."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)


def is_left_only_key(key: str, all_keys: set[str]) -> bool:
    """_* 키 중 같은 *가 *_ 키로도 쓰이는 경우는 제외한다."""
    if not key.startswith("_") or len(key) <= 1:
        return False

    word = key[1:]
    return f"{word}_" not in all_keys


def main() -> None:
    ws_num = 4
    platform = "pc98"
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    if not base_dir.exists():
        # WSL에서 실행할 때의 C: 드라이브 경로
        base_dir = Path(f"/mnt/c/work_han/workspace{ws_num}")
    script_base_dir = base_dir / f"script-{platform}"

    custom_word_path = script_base_dir / "custom_word_kor.json"
    with custom_word_path.open("r", encoding="utf-8") as f:
        custom_words = json.load(f)

    if not isinstance(custom_words, dict):
        raise ValueError(f"{custom_word_path}의 최상위 값은 객체여야 합니다.")

    all_keys = set(custom_words)
    target_keys = [key for key in custom_words if is_left_only_key(key, all_keys)]

    occurrence_counts: Counter[str] = Counter()
    sentence_counts: Counter[str] = Counter()
    file_counts: Counter[str] = Counter()

    kor_files = sorted(script_base_dir.glob("*_kor.json"))
    for kor_path in kor_files:
        with kor_path.open("r", encoding="utf-8") as f:
            sentences = list(iter_strings(json.load(f)))

        keys_used_in_file: set[str] = set()
        for sentence in sentences:
            for key in target_keys:
                placeholder = "{" + key + "}"
                count = sentence.count(placeholder)
                if count:
                    occurrence_counts[key] += count
                    sentence_counts[key] += 1
                    keys_used_in_file.add(key)

        for key in keys_used_in_file:
            file_counts[key] += 1

    sorted_keys = sorted(
        target_keys,
        key=lambda key: (-occurrence_counts[key], -sentence_counts[key], key),
    )

    print(f"대상 파일: {len(kor_files)}개")
    print(f"custom_word 키: {len(custom_words)}개")
    print(f'체크 대상 "_*" 키: {len(target_keys)}개')
    print("키\t등장 횟수\t문장 수\t파일 수")
    for key in sorted_keys:
        print(f"{key}\t{occurrence_counts[key]}\t{sentence_counts[key]}\t{file_counts[key]}")


if __name__ == "__main__":
    main()
