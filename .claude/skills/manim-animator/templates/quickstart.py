"""Minimal ManimCE starter with two cooperating Scenes.

Copy this file, expand into more Scene classes, and render with:

    python3 scripts/render_scenes.py --code quickstart.py --out output/

Follows the write-system hard rules:
  - One Scene per class, no aggregator.
  - Each Scene has a title at the top edge.
  - No external files, no config mutation, no third-party imports beyond
    manim + numpy + standard library.
"""

from manim import *


class TitleScene(Scene):
    def construct(self):
        title = Text("Manim Quickstart", font_size=56, color=BLUE).to_edge(UP)
        subtitle = Text(
            "A minimal starting point for the manim-animator skill",
            font_size=28,
            color=GRAY_B,
        ).next_to(title, DOWN, buff=0.5)

        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(subtitle), run_time=0.6)
        self.wait(0.3)


class ShapeTransformScene(Scene):
    def construct(self):
        title = Text("Transforming Shapes", font_size=48, color=BLUE).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        circle = Circle(radius=1.4, color=YELLOW).shift(DOWN * 0.8)
        square = Square(side_length=2.4, color=GREEN).shift(DOWN * 0.8)

        self.play(Create(circle), run_time=1.0)
        self.wait(0.4)
        self.play(Transform(circle, square), run_time=1.2)
        self.play(circle.animate.rotate(PI / 4).set_color(RED), run_time=1.0)
        self.wait(0.8)
        self.play(FadeOut(circle), FadeOut(title), run_time=0.6)
        self.wait(0.3)
