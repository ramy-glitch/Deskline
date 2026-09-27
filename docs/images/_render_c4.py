"""Render the Alpha context and container diagrams to PNG."""

from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/segoeui.ttf"
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"

PERSON = ("#08427B", "#ffffff")
SYSTEM = ("#1168BD", "#ffffff")
EXTERNAL = ("#999999", "#ffffff")
CONTAINER = ("#438DD5", "#ffffff")
BOUNDARY = ("#1168BD", "#ffffff")
ARROW = "#444444"
BG = "#ffffff"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def wrap(draw, text, face, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else f"{current} {word}"
        if draw.textlength(trial, font=face) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rounded(draw, box, fill, outline, radius=12, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def centered(draw, lines, face, box, fill, top):
    x0, y0, x1, y1 = box
    line_h = face.size + 6
    y = top
    for line in lines:
        w = draw.textlength(line, font=face)
        draw.text(((x0 + x1 - w) / 2, y), line, font=face, fill=fill)
        y += line_h
    return y


def card(draw, box, fill, title, body, tech=None):
    color, ink = fill
    rounded(draw, box, color, color, radius=14)
    title_face = font(22, bold=True)
    body_face = font(16)
    tech_face = font(15)
    pad = 18
    y = box[1] + pad
    y = centered(draw, wrap(draw, title, title_face, box[2] - box[0] - 2 * pad), title_face, box, ink, y)
    if tech:
        y += 4
        y = centered(draw, wrap(draw, tech, tech_face, box[2] - box[0] - 2 * pad), tech_face, box, ink, y)
    y += 8
    centered(draw, wrap(draw, body, body_face, box[2] - box[0] - 2 * pad), body_face, box, ink, y)


def person(draw, box, title, body):
    card(draw, box, PERSON, title, body)
    # Small person mark in the top-left of the card.
    x, y = box[0] + 16, box[1] + 14
    draw.ellipse((x, y, x + 14, y + 14), outline="#ffffff", width=2)
    draw.arc((x - 4, y + 16, x + 18, y + 34), 200, 340, fill="#ffffff", width=2)


def arrow(draw, start, end, label, label_xy):
    x0, y0 = start
    x1, y1 = end
    draw.line((x0, y0, x1, y1), fill=ARROW, width=3)
    import math

    angle = math.atan2(y1 - y0, x1 - x0)
    length = 14
    spread = 0.45
    p1 = (x1 - length * math.cos(angle - spread), y1 - length * math.sin(angle - spread))
    p2 = (x1 - length * math.cos(angle + spread), y1 - length * math.sin(angle + spread))
    draw.polygon([end, p1, p2], fill=ARROW)
    face = font(15)
    lx, ly = label_xy
    tw = draw.textlength(label, font=face)
    draw.rectangle((lx - 4, ly - 2, lx + tw + 4, ly + face.size + 4), fill=BG)
    draw.text((lx, ly), label, font=face, fill="#222222")


def context():
    image = Image.new("RGB", (2100, 1040), BG)
    draw = ImageDraw.Draw(image)
    draw.text((48, 36), "System context for Deskline", font=font(32, bold=True), fill="#1a1a1a")

    person(draw, (60, 180, 420, 430), "Customer", "Asks a question and does not choose a section.")
    person(draw, (60, 560, 420, 810), "Section staff", "Reads a ticket and the reason it was opened.")
    card(
        draw,
        (760, 300, 1360, 700),
        SYSTEM,
        "Deskline",
        "Routes a question to Returns, Warranties, or Repairs, then cites that section or opens a ticket.",
    )
    card(
        draw,
        (1660, 150, 2060, 430),
        EXTERNAL,
        "Halfords website",
        "Publishes the returns, warranty, and terms pages. Copyright stays with Halfords.",
    )
    card(
        draw,
        (1660, 580, 2060, 860),
        EXTERNAL,
        "Model provider",
        "Supplies the chat model and the embedding model. The provider can be replaced.",
    )

    arrow(draw, (420, 260), (760, 380), "Asks a question", (470, 250))
    arrow(draw, (760, 520), (420, 400), "Answer, question, or ticket", (450, 450))
    arrow(draw, (420, 690), (760, 620), "Reads tickets", (470, 640))
    arrow(draw, (1360, 400), (1660, 290), "Scrapes the listed pages once", (1380, 310))
    arrow(draw, (1360, 600), (1660, 700), "Routes, grades, drafts, checks", (1380, 640))

    image.save("docs/images/context.png", "PNG")


def containers():
    image = Image.new("RGB", (2100, 1320), BG)
    draw = ImageDraw.Draw(image)
    draw.text((48, 32), "Containers for the Deskline Alpha", font=font(32, bold=True), fill="#1a1a1a")

    boundary = (560, 150, 1560, 1180)
    rounded(draw, boundary, "#ffffff", BOUNDARY[0], radius=16, width=3)
    draw.text((584, 168), "Deskline, local", font=font(20, bold=True), fill=BOUNDARY[0])

    person(draw, (40, 200, 400, 430), "Customer", "Asks a question.")
    person(draw, (40, 520, 400, 750), "Section staff", "Reads tickets.")
    card(
        draw,
        (40, 900, 420, 1160),
        EXTERNAL,
        "Local corpus",
        "One unmodified scrape of the listed Halfords pages. Gitignored JSON. Stays on this machine.",
        tech="JSON files",
    )
    card(
        draw,
        (1680, 480, 2060, 780),
        EXTERNAL,
        "Model provider",
        "Chat and embedding models. The provider can be replaced.",
    )

    card(
        draw,
        (700, 240, 1420, 430),
        CONTAINER,
        "API",
        "Accepts a question and returns an answer, a clarifying question, or a ticket.",
        tech="Python",
    )
    card(
        draw,
        (700, 500, 1420, 720),
        CONTAINER,
        "LangGraph application",
        "Routes, asks once, retrieves, checks, and escalates. Runs inside the API process.",
        tech="Python, LangGraph, LangChain",
    )
    card(
        draw,
        (640, 820, 1020, 1080),
        CONTAINER,
        "PostgreSQL",
        "Holds sections, chunks, and tickets. Filtered by section id.",
        tech="PostgreSQL, pgvector",
    )
    card(
        draw,
        (1100, 820, 1480, 1080),
        CONTAINER,
        "Eval runner",
        "Scores the frozen golden set. Run by hand. Not on the customer path.",
        tech="Python, RAGAS",
    )

    arrow(draw, (400, 300), (700, 320), "Sends a question", (430, 250))
    arrow(draw, (400, 630), (700, 600), "Reads a ticket", (430, 580))
    arrow(draw, (1060, 430), (1060, 500), "Runs one turn", (1076, 446))
    arrow(draw, (900, 720), (830, 820), "Reads chunks, writes tickets", (620, 740))
    arrow(draw, (1420, 560), (1680, 620), "Uses the model", (1430, 520))
    arrow(draw, (420, 1040), (640, 1000), "Ingested once into chunks", (430, 980))
    arrow(draw, (1360, 820), (1360, 720), "Runs the golden set", (1376, 752))

    image.save("docs/images/containers.png", "PNG")


if __name__ == "__main__":
    context()
    containers()
