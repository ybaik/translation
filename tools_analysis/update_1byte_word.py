import json
import re
from pathlib import Path
from typing import Any


WORD_PATTERN = re.compile(r"\{([^{}]+)\}")
SPACE_BEFORE_NULL_PATTERN = re.compile(r"\|_(?=(?:\|)?␀)")


def rewrite_word(word: str, custom_words: dict[str, str]) -> str | None:
    """{word}를 1바이트 조합으로 바꿀 수 있으면 바꾼 문자열을 반환한다."""
    if word in custom_words:
        return None

    # 이미 1바이트 조합이 들어간 케이스는 건드리지 않는다.
    if "|" in word:
        return None

    prefix = ""
    suffix = ""
    core = word

    if core.startswith("_"):
        prefix = "|_"
        core = core[1:]

    if core.endswith("_"):
        suffix = "|_"
        core = core[:-1]

    if not core:
        return None

    pieces: list[str] = []
    for character in core:
        one_byte_key = f"|{character}"
        if one_byte_key not in custom_words:
            return None
        pieces.append(f"{{{one_byte_key}}}")

    return prefix + "".join(pieces) + suffix


def rewrite_sentence(sentence: str, custom_words: dict[str, str]) -> tuple[str, int]:
    """문장 내 custom word를 1바이트 조합으로 치환한다."""
    changes = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changes
        word = match.group(1)
        rewritten = rewrite_word(word, custom_words)
        if rewritten is None or rewritten == match.group(0):
            return match.group(0)
        if (
            word.endswith("_")
            and match.end() == len(sentence)
            and rewritten.endswith("|_")
        ):
            rewritten = rewritten[:-2] + "|␀"
        changes += 1
        return rewritten

    rewritten_sentence = WORD_PATTERN.sub(replace, sentence)
    rewritten_sentence, null_changes = SPACE_BEFORE_NULL_PATTERN.subn(
        "|␀", rewritten_sentence
    )
    changes += null_changes
    return rewritten_sentence, changes


def walk_and_rewrite(value: Any, custom_words: dict[str, str]) -> tuple[Any, int]:
    """JSON 구조를 유지한 채 문자열만 재작성한다."""
    changes = 0
    if isinstance(value, str):
        rewritten, count = rewrite_sentence(value, custom_words)
        return rewritten, count
    if isinstance(value, list):
        rewritten_list = []
        for item in value:
            rewritten_item, count = walk_and_rewrite(item, custom_words)
            rewritten_list.append(rewritten_item)
            changes += count
        return rewritten_list, changes
    if isinstance(value, dict):
        rewritten_dict = {}
        for key, item in value.items():
            rewritten_item, count = walk_and_rewrite(item, custom_words)
            rewritten_dict[key] = rewritten_item
            changes += count
        return rewritten_dict, changes
    return value, 0


def main() -> None:
    ws_num = 1
    platform = "pc98"
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    if not base_dir.exists():
        # WSL에서 실행할 때의 C: 드라이브 경로
        base_dir = Path(f"/mnt/c/work_han/workspace{ws_num}")
    script_base_dir = base_dir / f"script-{platform}"

    custom_word_path = script_base_dir / "custom_word.json"
    with custom_word_path.open("r", encoding="utf-8") as f:
        custom_words = json.load(f)

    if not isinstance(custom_words, dict):
        raise ValueError(f"{custom_word_path}의 최상위 값은 객체여야 합니다.")

    kor_files = sorted(script_base_dir.glob("*_kor.json"))
    changed_files = 0
    changed_words = 0

    for kor_path in kor_files:
        with kor_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        rewritten_data, changes = walk_and_rewrite(data, custom_words)
        if changes:
            changed_files += 1
            changed_words += changes
            with kor_path.open("w", encoding="utf-8") as f:
                json.dump(rewritten_data, f, ensure_ascii=False, indent=4)

    print(f"대상 파일: {len(kor_files)}개")
    print(f"수정된 파일: {changed_files}개")
    print(f"치환된 블록/공백: {changed_words}개")


if __name__ == "__main__":
    main()
