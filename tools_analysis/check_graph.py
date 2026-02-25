import json
from pathlib import Path
from rich.console import Console
from module.script import Script


colors = ["#00ff00", "#ff0000", "#0000ff", "#00e5ff"]


def main():
    console = Console()

    platform = "pc98"
    ws_num = 4
    base_dir = Path(f"c:/work_han/workspace{ws_num}")
    script_base_dir = base_dir / f"script-{platform}"

    inputs = ["43970=43975"]
    is_kor = True

    # Read a graph info
    graph_path = script_base_dir / "MAIN.EXE_con.json"
    if not graph_path.exists():
        return
    with open(graph_path, "r", encoding="utf-8") as f:
        graph_db = json.load(f)

    # Read a pair of scripts
    src_script = Script(str(script_base_dir / "MAIN.EXE_jpn.json"))
    dst_script = Script(str(script_base_dir / "MAIN.EXE_kor.json"))
    script = dst_script if is_kor else src_script

    for graph in graph_db:
        include = True
        for input in inputs:
            if input not in graph:
                include = False
                break
        if not include:
            continue

        text = ""
        for address in graph:
            if "=" not in address:
                sentence = address
            else:
                sentence = script.script[address]
            if address in inputs:
                idx = inputs.index(address) % 4
                sentence = f"[{colors[idx]}]{sentence}[/{colors[idx]}]"
            text += sentence
        console.print(text)

    graph_db.sort()
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_db, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
