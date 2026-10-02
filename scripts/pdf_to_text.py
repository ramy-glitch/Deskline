"""Turn the referral leaflet PDF into a plain-text corpus file."""

from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "corpus" / "referrals_waiting" / "patient-referal-easy-read.pdf"
OUT = PDF.with_suffix(".txt")


def page_text(reader: PdfReader) -> str:
    lines = []
    for page in reader.pages:
        raw = page.extract_text() or ""
        for line in raw.replace("\x0c", "\n").splitlines():
            line = line.strip()
            if line:
                lines.append(line)
    return "\n".join(lines)


def main() -> None:
    if not PDF.is_file():
        raise SystemExit(f"missing {PDF.relative_to(ROOT)}")

    text = page_text(PdfReader(str(PDF)))
    if len(text) < 400:
        raise SystemExit(
            f"extract is only {len(text)} characters. "
            "The PDF may be pictures rather than text."
        )

    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"saved     {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()