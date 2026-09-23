from typing import Any


def reconstruct_lines(words: list[dict[str, Any]], tolerance: float = 3.0) -> list[dict[str, Any]]:
	lines: list[dict[str, Any]] = []
	for word in sorted(words, key=lambda item: (float(item.get("top", 0)), float(item.get("x0", 0)))):
		target = next((line for line in lines if abs(line["top"] - float(word.get("top", 0))) <= tolerance), None)
		if target is None:
			lines.append({"top": float(word.get("top", 0)), "bottom": float(word.get("bottom", 0)), "words": [word]})
		else:
			target["words"].append(word)
			target["bottom"] = max(target["bottom"], float(word.get("bottom", 0)))
	for line in lines:
		line["words"].sort(key=lambda item: float(item.get("x0", 0)))
		line["text"] = " ".join(str(item.get("text", "")) for item in line["words"]).strip()
		line["bbox"] = [float(line["words"][0].get("x0", 0)), line["top"], float(line["words"][-1].get("x1", 0)), line["bottom"]]
	return lines
