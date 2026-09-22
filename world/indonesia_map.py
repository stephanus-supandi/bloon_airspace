"""
INDONESIA MAP (STYLIZED / FICTIONAL)
-------------------------------------
These polygons are NOT geographic data.
They are vibes. Approximate vibes.
If you tried to navigate with these, you would have a bad time.
"""
from typing import List, Tuple

Polygon = List[Tuple[float, float]]


# Each island is a list of (x, y) points in world coords.
# World space: roughly 0..2000 x, 0..900 y.
# Oriented so that north is +y, east is +x.

SUMATRA: Polygon = [
    (150, 250), (230, 220), (310, 260), (380, 330),
    (430, 420), (460, 520), (440, 600), (380, 640),
    (300, 620), (230, 560), (180, 470), (150, 370),
]

JAVA: Polygon = [
    (560, 720), (620, 705), (700, 710), (780, 720),
    (800, 745), (740, 760), (650, 760), (580, 750),
]

BALI: Polygon = [
    (815, 725), (835, 720), (845, 735), (830, 745), (815, 740),
]

LOMBOK: Polygon = [
    (860, 730), (880, 725), (890, 740), (870, 748),
]

SUMBAWA: Polygon = [
    (905, 735), (955, 730), (970, 745), (920, 750),
]

FLORES: Polygon = [
    (990, 740), (1080, 735), (1100, 750), (1010, 755),
]

TIMOR: Polygon = [
    (1120, 745), (1180, 740), (1195, 755), (1135, 760),
]

KALIMANTAN: Polygon = [
    (620, 200), (720, 180), (830, 200), (880, 280),
    (890, 380), (860, 470), (790, 510), (700, 500),
    (640, 440), (610, 350), (605, 270),
]

SULAWESI: Polygon = [
    # K-shape. Approximate.
    (980, 280), (1030, 260), (1060, 300), (1040, 360),
    (1080, 390), (1110, 440), (1090, 490), (1040, 480),
    (1020, 430), (990, 460), (960, 430), (980, 380),
    (960, 330),
]

MALUKU: Polygon = [
    (1220, 420), (1260, 410), (1290, 440), (1280, 490),
    (1240, 510), (1210, 480),
]

MALUKU_SMALL: Polygon = [
    (1310, 520), (1340, 515), (1350, 540), (1320, 548),
]

PAPUA: Polygon = [
    (1400, 300), (1500, 280), (1620, 300), (1720, 340),
    (1780, 400), (1790, 470), (1740, 530), (1650, 560),
    (1550, 550), (1470, 510), (1420, 450), (1400, 380),
]

# Grouped for iteration
ISLANDS = {
    "Sumatra": SUMATRA,
    "Java": JAVA,
    "Bali": BALI,
    "Lombok": LOMBOK,
    "Sumbawa": SUMBAWA,
    "Flores": FLORES,
    "Timor": TIMOR,
    "Kalimantan": KALIMANTAN,
    "Sulawesi": SULAWESI,
    "Maluku": MALUKU,
    "Maluku Small": MALUKU_SMALL,
    "Papua": PAPUA,
}


class IndonesiaMap:
    """Holds the stylized polygons. No GIS. No claims of accuracy."""

    def __init__(self):
        self.islands = ISLANDS

    def all_polygons(self):
        return list(self.islands.items())