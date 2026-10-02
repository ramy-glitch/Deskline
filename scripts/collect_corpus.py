"""Collect the Alpha corpus pages. One known URL at a time."""

import json
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"
METADATA = ROOT / "data" / "metadata"
TODAY = date.today().isoformat()

PAGES = [
    {
        "section": "appointments",
        "title": "Hospital referrals and appointments",
        "url": "https://www.nhs.uk/nhs-app/help/appointments/hospital-and-other-appointments/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "appointments",
        "title": "GP surgery appointments",
        "url": "https://www.nhs.uk/nhs-app/help/appointments/gp-surgery-appointments/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "appointments",
        "title": "Managing your GP appointments",
        "url": "https://www.nhs.uk/nhs-app/help/appointments/managing-gp-appointments/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "appointments",
        "title": "Book an appointment using the NHS e-Referral Service",
        "url": "https://www.nhs.uk/nhs-services/hospitals/book-an-appointment/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "appointments",
        "title": "Your choices in the NHS",
        "url": "https://www.nhs.uk/using-the-nhs/about-the-nhs/your-choices-in-the-nhs/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "appointments",
        "title": "About NHS hospital services",
        "url": "https://www.nhs.uk/nhs-services/hospitals/about-nhs-hospital-services/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "referrals_waiting",
        "title": "Referrals for specialist care",
        "url": "https://www.nhs.uk/nhs-services/hospitals/referrals-for-specialist-care/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "referrals_waiting",
        "title": "Guide to NHS waiting times in England",
        "url": "https://www.nhs.uk/nhs-services/hospitals/guide-to-nhs-waiting-times-in-england/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "referrals_waiting",
        "title": "Viewing waiting lists",
        "url": "https://www.nhs.uk/nhs-app/help/appointments/view-waiting-lists/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "referrals_waiting",
        "title": "What happens when your doctor asks you to see a specialist",
        "url": "https://www.england.nhs.uk/wp-content/uploads/2018/08/patient-referal-easy-read.pdf",
        "publisher": "NHS England",
        "kind": "pdf",
    },
    {
        "section": "referrals_waiting",
        "title": "Choice",
        "url": "https://www.england.nhs.uk/personalisedcare/choice/",
        "publisher": "NHS England",
        "kind": "html",
    },
    {
        "section": "referrals_waiting",
        "title": "The NHS Choice Framework",
        "url": "https://www.gov.uk/government/publications/the-nhs-choice-framework/the-nhs-choice-framework-what-choices-are-available-to-me-in-the-nhs",
        "publisher": "GOV.UK",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "View your test results",
        "url": "https://www.nhs.uk/nhs-services/gps/view-your-test-results/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Viewing test results",
        "url": "https://www.nhs.uk/nhs-app/help/test-results/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "How to log in",
        "url": "https://www.nhs.uk/nhs-app/help/logging-in/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Documents",
        "url": "https://www.nhs.uk/nhs-app/help/documents/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Messages",
        "url": "https://www.nhs.uk/nhs-app/help/messages/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Family and carer access",
        "url": "https://www.nhs.uk/nhs-app/help/profile/family-and-carer-access/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Abbreviations",
        "url": "https://www.nhs.uk/nhs-app/help/understanding-abbreviations/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Contact the NHS App team",
        "url": "https://www.nhs.uk/contact-us/nhs-app-contact-us/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Get help for mental health now",
        "url": "https://www.nhs.uk/mental-health/get-urgent-help-for-mental-health/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Get urgent medical help now",
        "url": "https://111.nhs.uk/",
        "publisher": "NHS website",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Subject access requests for patients and service users",
        "url": "https://digital.nhs.uk/data-and-information/information-governance/guidance/subject-access-requests/guidance-for-patients-and-service-users",
        "publisher": "NHS England Digital",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "Getting copies of medical records",
        "url": "https://www.england.nhs.uk/contact-us/common-questions/how-do-i-get-a-copy-of-my-health-medical-records/",
        "publisher": "NHS England",
        "kind": "html",
    },
    {
        "section": "records_results",
        "title": "How to access your personal information",
        "url": "https://www.england.nhs.uk/contact-us/privacy-notice/find-out-how-to-access-your-personal-information-or-make-a-request-in-relation-to-other-rights/",
        "publisher": "NHS England",
        "kind": "html",
    },
]


def slug(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".pdf"):
        name = name[: -len(".pdf")]
    return name


def article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("script, style, nav, header, footer, noscript"):
        tag.decompose()
    node = (
        soup.select_one(".govuk-govspeak")
        or soup.select_one(".entry-content")
        or soup.select_one("main")
        or soup.select_one("article")
    )
    if node is None:
        raise RuntimeError("no article element found")
    text = node.get_text("\n", strip=True)
    if len(text) < 400:
        raise RuntimeError(f"extract is only {len(text)} characters")
    return text


def write_metadata(page: dict, name: str) -> None:
    row = {
        "section": page["section"],
        "title": page["title"],
        "url": page["url"],
        "publisher": page["publisher"],
        "retrieved_at": TODAY,
        "document_type": "guidance",
    }
    path = METADATA / f"{page['section']}-{name}.json"
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(f"metadata  {path.relative_to(ROOT)}")


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = "Deskline local corpus (personal study copy)"

    for page in PAGES:
        name = slug(page["url"])
        folder = CORPUS / page["section"]
        folder.mkdir(parents=True, exist_ok=True)
        response = session.get(page["url"], timeout=30)
        response.raise_for_status()

        if page["kind"] == "pdf":
            path = folder / f"{name}.pdf"
            path.write_bytes(response.content)
        else:
            path = folder / f"{name}.txt"
            path.write_text(article_text(response.text), encoding="utf-8")

        print(f"saved     {path.relative_to(ROOT)}")
        write_metadata(page, name)
        time.sleep(2)


if __name__ == "__main__":
    main()