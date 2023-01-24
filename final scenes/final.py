from manim import *
from manim_data_structures import *
from manim_physics import *

import numpy as np


# Chris Agrella (2023-01-24)
# Scenes: BubbleSort, InsertionSort, RainbowPendulum, SierpinskiTriangle

# How-to:
# pip install manim manim-physics manim-data-structures
# manim -qh --flush_cache -v WARNING final.py BubbleSort InsertionSort RainbowPendulum SierpinskiTriangle


class BubbleSort(Scene):
    def swap_bubbles(self, arr, index1, index2):
        arr_v = arr.fetch_arr()
        v1 = arr_v[index1]
        v2 = arr_v[index2]

        old_color = arr.fetch_mob_arr()[0][0].fill_color

        self.play(
            arr.animate_elem_square(index1).set_fill(color=RED),
            arr.animate_elem_square(index2).set_fill(color=GREEN),
            run_time=0.5,
        )

        arr.update_elem_value(index1, v2, update_anim_args={"run_time": 0.5})
        arr.update_elem_value(index2, v1, update_anim_args={"run_time": 0.5})

        self.play(
            arr.animate_elem_square(index1).set_fill(color=old_color),
            arr.animate_elem_square(index2).set_fill(color=old_color),
            run_time=0.5,
        )

    def move_elems(self, win, p, index):
        self.play(
            p.shift_to_elem(index, play_anim=False),
            win.shift_to_elem(index, play_anim=False),
            run_time=0.5,
        )

    def construct(self):
        arr = MArray(self, [5, 4, 3, 2, 1], label="Array").shift(LEFT * 2)
        self.play(Create(arr))
        n = len(arr.fetch_arr())

        window = MArraySlidingWindow(self, arr, 0, 2)
        self.play(Create(window))

        j_ptr = MArrayPointer(self, arr, 0, "j")
        i_ptr = MArrayPointer(self, arr, n - 1, "i")
        self.play(Create(j_ptr))

        t = Text("Bubble Sort", font_size=30, font="IBM Plex Mono").shift(UP * 2)

        self.play(Write(t))

        self.wait(1)

        swap_osc_var = Variable(
            0, Text("Swaps", font="IBM Plex Mono", font_size=28), var_type=Integer
        )
        swap_osc_var.shift(DOWN + LEFT * 4)
        swap_tracker = swap_osc_var.tracker
        self.play(Write(swap_osc_var))

        self.wait(10)

        for i in range(n - 1):
            if i == 1:
                self.play(Create(i_ptr))
            if i != 0:
                i_ptr.shift_to_elem(n - i)
            for j in range(0, n - i - 1):
                self.move_elems(window, j_ptr, j)
                a = arr.fetch_arr()
                if a[j] > a[j + 1]:
                    self.swap_bubbles(arr, j, j + 1)
                    self.play(swap_tracker.animate.increment_value(1), run_time=0.2)
            self.wait(3)

        self.play(FadeOut(j_ptr), FadeOut(window), FadeOut(i_ptr))

        self.wait(5)


class RainbowPendulum(SpaceScene):
    def construct(self):
        p = MultiPendulum(*[RIGHT * (i) + UP for i in range(1, 6)], pivot_point=UP * 3)
        self.add(p)
        self.make_rigid_body(p.bobs)
        p.start_swinging()
        for i, color in enumerate([BLUE, GREEN, YELLOW, ORANGE, RED][::-1]):
            self.add(TracedPath(p.bobs[i].get_center, stroke_color=color))

        self.wait(19)

        p.end_swinging()

        self.wait(3)


BASE_SIZE = 6
MAX_DEPTH = 6

DP_M_MAP = [[] for _ in range(MAX_DEPTH)]


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


class SierpinskiTriangle(Scene):
    def play_animation_by_depth(self, klass, longest, dec, reverse=False):
        iterator = DP_M_MAP
        if reverse:
            iterator = DP_M_MAP[::-1]
        for ii, depth in enumerate(iterator):
            if len(depth) == 1:
                self.play(klass(depth[0]), runtime=longest)
                continue

            rt = max(longest - dec * ii, 0.05)
            if reverse:
                rt = dec * (ii + 1)

            chunks = list(split(depth, 3))
            for i in range(len(chunks[0])):
                animations = [klass(chunks[x][i]) for x in range(3)]
                self.play(*animations, run_time=rt)

    def draw_triangle(self, center, size):
        side = size
        height = (np.sqrt(3) / 2) * side
        bottom_left = center + (-side / 2, -(height / 2), 0)
        bottom_right = center + (side / 2, -(height / 2), 0)
        top = (0, height / 2, 0)

        t = Polygon(bottom_left, bottom_right, top, fill_color=BLUE, fill_opacity=1.0)

        self.add(t)

        return t

    def recursive_triangle(self, center, depth, t):
        if depth == MAX_DEPTH:
            return

        # step one: big triangle
        # area = sqrt(3)/4 (side)^2
        # height = sqrt(3)/4 * side

        side = BASE_SIZE * ((1 / 2) ** depth)
        height = (np.sqrt(3) / 2) * side

        # step two: middle triangle (empty out)
        new_height = height / 2
        new_side = side / 2
        p = Polygon(
            center + (new_side / 2, 0, 0),
            center + (-new_side / 2, 0, 0),
            center + (0, -new_height, 0),
            stroke_opacity=0.0,
            fill_opacity=1.0,
            fill_color=BLACK,
        )
        DP_M_MAP[depth].append(p)
        # self.play(FadeIn(p), run_time=0.05)

        # Up
        self.recursive_triangle(center + (UP * new_height / 2), depth + 1, t)
        # Left-Down
        self.recursive_triangle(
            center + (DOWN * new_height / 2) + (LEFT * new_side / 2), depth + 1, t
        )
        # Right-Down
        self.recursive_triangle(
            center + (DOWN * new_height / 2) + (RIGHT * new_side / 2), depth + 1, t
        )

    def create_triangle(self, center, size):
        t = self.draw_triangle(center, size)

        self.recursive_triangle(np.array([0, 0, 0]), 0, t)

        # fade in
        self.play_animation_by_depth(Create, 1, 0.2)

        self.wait(3)

        # fade out
        self.play_animation_by_depth(Uncreate, 1, 0.1, reverse=True)

    def construct(self):

        t = Text("Sierpiński triangle", font_size=16, font="IBM Plex Mono").shift(
            LEFT * 3 + UP * 2
        )
        t2 = Text(
            "A Sierpiński triangle is an equilateral\ntriangle that is recursively divided\ninto smaller triangles.",
            font_size=14,
            font="IBM Plex Mono",
        ).shift(LEFT * 3.5 + UP * 1.5)

        self.add(t, t2)

        self.create_triangle(ORIGIN, BASE_SIZE)
        self.wait(5)


class InsertionSort(Scene):
    def swap_bubbles(self, arr, index1, index2):
        arr_v = arr.fetch_arr()
        v1 = arr_v[index1]
        v2 = arr_v[index2]

        old_color = arr.fetch_mob_arr()[0][0].fill_color

        self.play(
            arr.animate_elem_square(index1).set_fill(color=RED),
            arr.animate_elem_square(index2).set_fill(color=GREEN),
            run_time=0.5,
        )

        arr.update_elem_value(index1, v2, update_anim_args={"run_time": 0.5})
        arr.update_elem_value(index2, v1, update_anim_args={"run_time": 0.5})

        self.play(
            arr.animate_elem_square(index1).set_fill(color=old_color),
            arr.animate_elem_square(index2).set_fill(color=old_color),
            self.swap_tracker.animate.increment_value(1),
            run_time=0.5,
        )

    def shift_pointer(self, pointer, idx):
        self.play(pointer.shift_to_elem(idx, play_anim=False), run_time=0.25)

    def run_insertion_sort(self, arr):
        n = len(arr.fetch_arr())

        window = MArraySlidingWindow(self, arr, 0, 1)
        self.play(Create(window))

        t = Text("Insertion Sort", font_size=30, font="IBM Plex Mono").shift(
            UP * 3 + LEFT * 4.5
        )

        self.play(Write(t))

        self.wait(1)

        swap_osc_var = Variable(
            0, Text("Swaps", font="IBM Plex Mono", font_size=30), var_type=Integer
        )
        swap_osc_var.shift(UP * 2 + LEFT * 5)
        self.swap_tracker = swap_osc_var.tracker
        self.play(Write(swap_osc_var))

        i_ptr = MArrayPointer(self, arr, 1, label="i")
        self.play(Create(i_ptr))
        j_ptr = MArrayPointer(
            self, arr, 1, label="j", pointer_pos=MArrayDirection.UP, arrow_gap=1
        )
        j_created = False

        self.wait(3)

        i = 1
        while i < n:
            if not j_created:
                j_created = True
                self.play(Create(j_ptr))
            j = i
            self.shift_pointer(j_ptr, j)
            while j > 0 and (arr.fetch_arr()[j - 1] > arr.fetch_arr()[j]):
                self.swap_bubbles(arr, j - 1, j)
                j -= 1
                self.shift_pointer(j_ptr, j)
            i += 1
            if i < n:
                window.resize_window(i)
                self.shift_pointer(i_ptr, i)
            self.wait(3)

        self.play(FadeOut(j_ptr), FadeOut(window), FadeOut(i_ptr))

    def construct(self):
        arr = MArray(self, [8, 7, 6, 5, 4, 1], label="Array").shift(LEFT * 2)
        self.play(Create(arr))

        self.wait(8)

        self.run_insertion_sort(arr)

        self.wait(5)
