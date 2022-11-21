import math
import svgwrite
from typing import TypeVar, List, Tuple


T = TypeVar("T")


def pairs(l: List[T]) -> List[Tuple[T, T]]:
    return list(zip(l, l[1:] + l[:1]))


def line_to_poligon(
    start: Tuple[float, float], end: Tuple[float, float], width: float
) -> List[Tuple[float, float]]:
    x1, y1 = start
    x2, y2 = end
    angle = math.atan((y2 - y1) / (x2 - x1))
    radius = width / 2

    dx1 = radius * math.cos(-1 * (math.pi / 2 - angle))
    dy1 = radius * math.sin(-1 * (math.pi / 2 - angle))

    dx2 = radius * math.cos(math.pi / 2 + angle)
    dy2 = radius * math.sin(math.pi / 2 + angle)

    return [
        (x1 + dx1, y1 + dy1),
        (x2 + dx1, y2 + dy1),
        (x2 + dx2, y2 + dy2),
        (x1 + dx2, y1 + dy2),
    ]


def main() -> None:

    size = 400
    radius = 160
    dot_radius = 35
    dot_radian = math.pi / 3
    color = "blue"
    stroke_width = 16.6

    drawing = svgwrite.Drawing(viewBox=f"0 0 {size} {size}", x="0px", y="0px")

    clip = drawing.defs.add(drawing.clipPath(id="clip"))

    # outter_dots_group = drawing.add(drawing.g(id="outer_dots"))
    clip.translate(radius + dot_radius + 5, radius + dot_radius + 5)

    coordinates = [
        (
            radius * math.cos(d * dot_radian),
            radius * math.sin(d * dot_radian),
        )
        for d in [0, 1, 2, 3, 4, 5]
    ]

    for c1, c2 in pairs(coordinates):
        clip.add(drawing.circle(center=c1, r=dot_radius))
        clip.add(drawing.polygon(line_to_poligon( start=c1, end=c2, width=16.6)))

    for c1, c2 in pairs(coordinates[::2]):
        clip.add(drawing.polygon(line_to_poligon( start=c1, end=c2, width=16.6)))

    gradient = drawing.defs.add(
        drawing.linearGradient(
            id="gradient",
            start=(0, 0),
            end=(size , 0),
            gradientUnits="userSpaceOnUse",
        )
    )

    gradient.add_stop_color(offset=0, color="#2f38c2")
    gradient.add_stop_color(offset=0.09090909090909091, color="#2f33c3")
    gradient.add_stop_color(offset=0.18181818181818182, color="#3930c5")
    gradient.add_stop_color(offset=0.2727272727272727, color="#4d30c8")
    gradient.add_stop_color(offset=0.36363636363636365, color="#6831cd")
    gradient.add_stop_color(offset=0.4545454545454546, color="#8832d1")
    gradient.add_stop_color(offset=0.5454545454545454, color="#aa33d6")
    gradient.add_stop_color(offset=0.6363636363636364, color="#cc33da")
    gradient.add_stop_color(offset=0.7272727272727273, color="#df34d2")
    gradient.add_stop_color(offset=0.8181818181818182, color="#e235be")
    gradient.add_stop_color(offset=0.9090909090909092, color="#e435b0")
    gradient.add_stop_color(offset=1, color="#e535ab")

    drawing.add(
        drawing.rect(
            insert=(0, 0),
            size=(400, 400),
            fill="url(#gradient)",
            clip_path="url(#clip)",
        )
    )

    drawing.saveas(filename="logo.svg", pretty=True)

if __name__ == "__main__" :
    main()