class Content:
    def __init__(self, address: str = None, sentence: str = None, text="", desc="") -> None:
        if address is not None:
            start, end = address.split("=")
            self.addr_start = int(start, 16)
            self.addr_end = int(end, 16)

        if sentence is not None:
            parts = sentence.split("#", 1)
            self.text = parts[0].strip()
            self.desc = parts[1].strip() if len(parts) > 1 else ""
        else:
            self.text = text
            self.desc = desc

    def __str__(self) -> str:
        return self.text + ("" if not self.desc else "#" + self.desc)
