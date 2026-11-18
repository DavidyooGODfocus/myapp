"""검증된 장면 자료를 Manim 영상으로 변환합니다. LaTeX는 사용하지 않습니다."""
import json
from pathlib import Path

import numpy as np
from manim import (
    Axes, Circle, Create, DOWN, FadeIn, FadeOut, LEFT, Polygon,
    Scene, Square, Text, UP, VGroup, WHITE, YELLOW, BLUE,
)
from manimpango import list_fonts


class MathVideo(Scene):
    def construct(self):
        plan = json.loads(Path(__file__).with_name("scene.json").read_text(encoding="utf-8"))
        installed = set(list_fonts())
        font = next((f for f in ("NanumGothic", "AppleGothic", "Malgun Gothic", "Noto Sans CJK KR") if f in installed), "sans-serif")

        def label(value, size=30, width=12):
            obj = Text(value, font=font, font_size=size, color=WHITE)
            if obj.width > width:
                obj.scale_to_fit_width(width)
            return obj

        title = label(plan["title"], 38).to_edge(UP)
        self.play(FadeIn(title), run_time=0.5)
        for step in plan["steps"]:
            caption = label(step["text"], 27).to_edge(DOWN)
            kind = step["kind"]
            if kind == "graph":
                axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1], x_length=9, y_length=4.5, tips=False)
                coefficients = step["coefficients"]
                # 표시 영역 밖으로 크게 벗어나는 다항식 부분은 그리지 않습니다.
                points = []
                segments = VGroup()
                for x in np.linspace(-5, 5, 401):
                    y = float(np.polyval(coefficients, x))
                    if -5 <= y <= 5:
                        points.append(axes.c2p(x, y))
                    else:
                        if len(points) > 1:
                            from manim import VMobject
                            segments.add(VMobject(color=YELLOW).set_points_as_corners(points))
                        points = []
                if len(points) > 1:
                    from manim import VMobject
                    segments.add(VMobject(color=YELLOW).set_points_as_corners(points))
                content = VGroup(axes, segments)
            elif kind == "shape":
                shapes = {
                    "circle": lambda: Circle(radius=1.5, color=BLUE),
                    "square": lambda: Square(side_length=3, color=BLUE),
                    "triangle": lambda: Polygon(LEFT * 2 + DOWN, UP * 1.7, -LEFT * 2 + DOWN, color=BLUE),
                }
                content = shapes[step["shape"]]()
            else:
                content = label(step["formula"] or step["text"], 44)
            self.play(Create(content), FadeIn(caption), run_time=1)
            self.wait(step["seconds"])
            self.play(FadeOut(content), FadeOut(caption), run_time=0.5)
        self.wait(0.5)
