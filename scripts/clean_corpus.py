"""Drop scraper leftovers from the corpus text files."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"
TRAILERS = {
    "more in",
    "help with appointments in the nhs app",
    "gps",
    "help with your profile in the nhs app",
    "related guidance",
    "related guidance and support",
    "find out more about tests and treatments",
    "view more information about conditions",
    "get help in:",
}


def clean(text: str) -> str:
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "-" or stripped.lower() in TRAILERS:
            continue
        if stripped == ".":
            if kept and kept[-1] != "" and not kept[-1].endswith("."):
                kept[-1] += "."
            continue
        kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def main() -> None:
    paths = sorted(CORPUS.glob("*/*.txt"))
    if not paths:
        raise SystemExit("no text files under data/corpus")
    for path in paths:
        original = path.read_text(encoding="utf-8")
        cleaned = clean(original)
        if cleaned == original:
            print(f"unchanged {path.relative_to(ROOT)}")
            continue
        path.write_text(cleaned, encoding="utf-8")
        print(f"cleaned   {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()