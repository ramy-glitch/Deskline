"""Count leak-test words across the three corpus sections."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"
SECTIONS = ("appointments", "referrals_waiting", "records_results")
WORDS = ("appointment", "referral", "result", "waiting", "patient", "gp", "hospital")


def main() -> None:
    files = {}
    for section in SECTIONS:
        found = sorted((CORPUS / section).glob("*.txt"))
        if not found:
            raise SystemExit(f"no text files in data/corpus/{section}")
        files[section] = found

    print(f"{'word':<14}" + "".join(f"{section:<22}" for section in SECTIONS) + "sections")
    failed = []
    for word in WORDS:
        counts = []
        for section in SECTIONS:
            total = 0
            for path in files[section]:
                total += path.read_text(encoding="utf-8").lower().count(word)
            counts.append(total)
        present = sum(1 for n in counts if n > 0)
        if present < 2:
            failed.append(word)
        print(f"{word:<14}" + "".join(f"{n:<22}" for n in counts) + str(present))

    print()
    if failed:
        print("missing from two sections:", ", ".join(failed))
    else:
        print("every word appears in more than one section")


if __name__ == "__main__":
    main()