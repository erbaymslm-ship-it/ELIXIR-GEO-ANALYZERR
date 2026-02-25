"""
ELIXIR TECHNOLOGY
4D Voxel Goruntuleme Widget'i - Isosurface Rendering
"""

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, Line, Quad
from kivy.properties import (
    NumericProperty, ObjectProperty, BooleanProperty
)
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import numpy as np
import math


class VoxelRenderer(Widget):
    data_matrix = ObjectProperty(None, allownone=True)
    depth_data = ObjectProperty(None, allownone=True)
    rotation_x = NumericProperty(30)
    rotation_y = NumericProperty(45)
    zoom = NumericProperty(1.0)
    selected_layer = NumericProperty(-1)
    show_wireframe = BooleanProperty(False)
    num_layers = NumericProperty(5)
    threshold = NumericProperty(0.0)
    alpha_factor = NumericProperty(0.8)
    focus_row = NumericProperty(-1)
    focus_col = NumericProperty(-1)

    def __init__(self, **kwargs):
        super(VoxelRenderer, self).__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)
        self.bind(rotation_x=self._redraw, rotation_y=self._redraw)
        self.bind(zoom=self._redraw, selected_layer=self._redraw)
        self.bind(data_matrix=self._redraw, depth_data=self._redraw)
        self.bind(threshold=self._redraw, alpha_factor=self._redraw)
        self.bind(show_wireframe=self._redraw)
        self.bind(focus_row=self._redraw, focus_col=self._redraw)
        self._touch_prev = None
        Clock.schedule_once(self._redraw, 0)

    def _project_3d(self, x, y, z, cx, cy):
        rad_x = math.radians(self.rotation_x)
        rad_y = math.radians(self.rotation_y)

        y1 = y * math.cos(rad_x) - z * math.sin(rad_x)
        z1 = y * math.sin(rad_x) + z * math.cos(rad_x)

        x2 = x * math.cos(rad_y) + z1 * math.sin(rad_y)
        z2 = -x * math.sin(rad_y) + z1 * math.cos(rad_y)

        scale = self.zoom * min(self.width, self.height) * 0.28
        sx = cx + x2 * scale
        sy = cy + y1 * scale
        return sx, sy, z2

    def _get_color(self, norm):
        if norm < 0.25:
            t = norm / 0.25
            r, g, b = 0.0, 0.0 + t * 0.8, 0.6 + t * 0.4
        elif norm < 0.5:
            t = (norm - 0.25) / 0.25
            r, g, b = 0.0, 0.8 + t * 0.2, 1.0 - t * 0.6
        elif norm < 0.75:
            t = (norm - 0.5) / 0.25
            r, g, b = t * 1.0, 1.0, 0.4 - t * 0.4
        else:
            t = (norm - 0.75) / 0.25
            r, g, b = 1.0, 1.0 - t * 0.7, 0.0
        return r, g, b

    def _draw_cube_face(self, corners, r, g, b, a, brightness):
        br = min(1.0, brightness)
        fr, fg, fb = r * br, g * br, b * br
        with self.canvas:
            Color(fr, fg, fb, a)
            if len(corners) == 4:
                Quad(points=[
                    corners[0][0], corners[0][1],
                    corners[1][0], corners[1][1],
                    corners[2][0], corners[2][1],
                    corners[3][0], corners[3][1],
                ])
            if self.show_wireframe:
                Color(fr * 1.3, fg * 1.3, fb * 1.3, min(1.0, a * 0.8))
                pts = []
                for c in corners:
                    pts.extend([c[0], c[1]])
                pts.extend([corners[0][0], corners[0][1]])
                Line(points=pts, width=0.7)

    def _redraw(self, *args):
        for child in self.children[:]:
            if isinstance(child, Label):
                self.remove_widget(child)

        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return

        with self.canvas:
            Color(*get_color_from_hex('#0A0A0A'))
            Rectangle(pos=self.pos, size=self.size)

        if self.data_matrix is None:
            with self.canvas:
                Color(*get_color_from_hex('#666666'))
            return

        matrix = self.data_matrix
        rows, cols = matrix.shape
        layers = self.num_layers
        cx, cy = self.center_x, self.center_y

        half = 0.08
        faces_to_draw = []

        for layer in range(layers):
            for row in range(rows):
                for col in range(cols):
                    val = float(matrix[row][col])
                    norm = min(1.0, max(0.0, val / 255.0))

                    if norm < self.threshold:
                        continue

                    if val <= 0 and self.selected_layer < 0:
                        continue

                    depth_offset = 0
                    if self.depth_data and f"{row},{col}" in self.depth_data:
                        depth_offset = float(self.depth_data[f"{row},{col}"]) * 0.01

                    nx = (col - cols / 2.0) / max(cols, 1)
                    ny = (row - rows / 2.0) / max(rows, 1)
                    nz = -(layer / max(layers - 1, 1)) * 1.2 - depth_offset

                    layer_factor = 1.0 - (layer / max(layers - 1, 1)) * 0.5
                    effective_norm = norm * layer_factor

                    r, g, b = self._get_color(effective_norm)

                    alpha = self.alpha_factor * (0.3 + effective_norm * 0.7)
                    if self.selected_layer >= 0 and layer != self.selected_layer:
                        alpha *= 0.1

                    is_focused = (self.focus_row >= 0 and self.focus_col >= 0 and
                                  row == self.focus_row and col == self.focus_col)
                    if is_focused:
                        alpha = min(1.0, alpha * 1.5)
                        r = min(1.0, r + 0.3)
                        g = min(1.0, g + 0.3)
                        b = min(1.0, b + 0.3)

                    s = half * (0.7 + effective_norm * 0.5)

                    cube_corners_3d = [
                        (nx - s, nz - s, ny - s),
                        (nx + s, nz - s, ny - s),
                        (nx + s, nz + s, ny - s),
                        (nx - s, nz + s, ny - s),
                        (nx - s, nz - s, ny + s),
                        (nx + s, nz - s, ny + s),
                        (nx + s, nz + s, ny + s),
                        (nx - s, nz + s, ny + s),
                    ]

                    projected = []
                    for px, py, pz in cube_corners_3d:
                        sx, sy, sz = self._project_3d(px, py, pz, cx, cy)
                        projected.append((sx, sy, sz))

                    face_defs = [
                        ([0, 1, 2, 3], 0.7),
                        ([4, 5, 6, 7], 0.7),
                        ([3, 2, 6, 7], 1.15),
                        ([0, 1, 5, 4], 0.55),
                        ([0, 3, 7, 4], 0.8),
                        ([1, 2, 6, 5], 0.65),
                    ]

                    for indices, brightness in face_defs:
                        corners_2d = [(projected[i][0], projected[i][1]) for i in indices]
                        face_z = sum(projected[i][2] for i in indices) / 4.0
                        faces_to_draw.append((face_z, corners_2d, r, g, b, alpha, brightness, is_focused))

        faces_to_draw.sort(key=lambda f: f[0])

        for fz, corners, r, g, b, a, brightness, is_focused in faces_to_draw:
            self._draw_cube_face(corners, r, g, b, a, brightness)
            if is_focused:
                with self.canvas:
                    Color(1.0, 0.84, 0.0, 0.4)
                    pts = []
                    for c in corners:
                        pts.extend([c[0], c[1]])
                    pts.extend([corners[0][0], corners[0][1]])
                    Line(points=pts, width=1.5)

        self._draw_axes(cx, cy)

    def _draw_axes(self, cx, cy):
        axis_len = 0.7
        origin = self._project_3d(0, 0, 0, cx, cy)
        x_end = self._project_3d(axis_len, 0, 0, cx, cy)
        y_end = self._project_3d(0, -axis_len * 1.2, 0, cx, cy)
        z_end = self._project_3d(0, 0, axis_len, cx, cy)

        with self.canvas:
            Color(1.0, 0.3, 0.3, 0.6)
            Line(points=[origin[0], origin[1], x_end[0], x_end[1]], width=1.2)

            Color(0.3, 1.0, 0.3, 0.6)
            Line(points=[origin[0], origin[1], y_end[0], y_end[1]], width=1.2)

            Color(0.3, 0.5, 1.0, 0.6)
            Line(points=[origin[0], origin[1], z_end[0], z_end[1]], width=1.2)

        lbl_offset = 12
        self._draw_axis_label("X", x_end[0] + lbl_offset, x_end[1], (1.0, 0.3, 0.3, 0.9))
        self._draw_axis_label("Z/Derinlik", y_end[0] + lbl_offset, y_end[1], (0.3, 1.0, 0.3, 0.9))
        self._draw_axis_label("Y", z_end[0] + lbl_offset, z_end[1], (0.3, 0.5, 1.0, 0.9))

    def _draw_axis_label(self, text, x, y, color):
        lbl = Label(
            text=text,
            pos=(x - 20, y - 10),
            size=(40, 20),
            font_size='10sp',
            color=color,
            bold=True
        )
        self.add_widget(lbl)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_prev = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._touch_prev and self.collide_point(*touch.pos):
            dx = touch.x - self._touch_prev[0]
            dy = touch.y - self._touch_prev[1]
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.rotation_x = max(-89, min(89, self.rotation_x))
            self._touch_prev = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self._touch_prev = None
        return super().on_touch_up(touch)


class VoxelViewWidget(BoxLayout):
    def __init__(self, data_matrix=None, depth_data=None, focus_row=-1, focus_col=-1, **kwargs):
        super(VoxelViewWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [5, 5]
        self.spacing = 5

        self.renderer = VoxelRenderer(
            data_matrix=data_matrix,
            depth_data=depth_data,
            focus_row=focus_row,
            focus_col=focus_col,
        )
        self.add_widget(self.renderer)

        controls_top = BoxLayout(
            size_hint_y=None, height=36, spacing=8, padding=[10, 0]
        )

        lbl_layer = Label(
            text="Katman: Tumu",
            size_hint_x=0.25,
            color=get_color_from_hex('#FFD700'),
            font_size='10sp'
        )
        self._layer_label = lbl_layer
        controls_top.add_widget(lbl_layer)

        layer_slider = Slider(
            min=-1, max=4, value=-1, step=1, size_hint_x=0.35
        )
        layer_slider.bind(value=self._on_layer_change)
        controls_top.add_widget(layer_slider)

        lbl_zoom = Label(
            text="Zoom",
            size_hint_x=0.15,
            color=get_color_from_hex('#B8860B'),
            font_size='10sp'
        )
        controls_top.add_widget(lbl_zoom)

        zoom_slider = Slider(
            min=0.5, max=3.0, value=1.0, step=0.1, size_hint_x=0.25
        )
        zoom_slider.bind(value=self._on_zoom_change)
        controls_top.add_widget(zoom_slider)

        self.add_widget(controls_top)

        controls_mid = BoxLayout(
            size_hint_y=None, height=36, spacing=8, padding=[10, 0]
        )

        lbl_thresh = Label(
            text="Esik: 0%",
            size_hint_x=0.25,
            color=get_color_from_hex('#FFD700'),
            font_size='10sp'
        )
        self._thresh_label = lbl_thresh
        controls_mid.add_widget(lbl_thresh)

        thresh_slider = Slider(
            min=0.0, max=1.0, value=0.0, step=0.05, size_hint_x=0.35
        )
        thresh_slider.bind(value=self._on_threshold_change)
        controls_mid.add_widget(thresh_slider)

        lbl_alpha = Label(
            text="Seffaflik",
            size_hint_x=0.15,
            color=get_color_from_hex('#B8860B'),
            font_size='10sp'
        )
        controls_mid.add_widget(lbl_alpha)

        alpha_slider = Slider(
            min=0.1, max=1.0, value=0.8, step=0.05, size_hint_x=0.25
        )
        alpha_slider.bind(value=self._on_alpha_change)
        controls_mid.add_widget(alpha_slider)

        self.add_widget(controls_mid)

        controls_bottom = BoxLayout(
            size_hint_y=None, height=36, spacing=8, padding=[10, 0]
        )

        self._wireframe_btn = Button(
            text="Wireframe: Kapali",
            size_hint_x=0.5,
            background_normal='',
            background_color=get_color_from_hex('#1A1A00'),
            color=get_color_from_hex('#FFD700'),
            font_size='10sp'
        )
        self._wireframe_btn.bind(on_press=self._toggle_wireframe)
        controls_bottom.add_widget(self._wireframe_btn)

        controls_bottom.add_widget(Label(size_hint_x=0.5))

        self.add_widget(controls_bottom)

    def _on_layer_change(self, slider, value):
        self.renderer.selected_layer = int(value)
        if int(value) < 0:
            self._layer_label.text = "Katman: Tumu"
        else:
            self._layer_label.text = f"Katman: {int(value) + 1}"

    def _on_zoom_change(self, slider, value):
        self.renderer.zoom = value

    def _on_threshold_change(self, slider, value):
        self.renderer.threshold = value
        self._thresh_label.text = f"Esik: {int(value * 100)}%"

    def _on_alpha_change(self, slider, value):
        self.renderer.alpha_factor = value

    def _toggle_wireframe(self, btn):
        self.renderer.show_wireframe = not self.renderer.show_wireframe
        if self.renderer.show_wireframe:
            self._wireframe_btn.text = "Wireframe: Acik"
        else:
            self._wireframe_btn.text = "Wireframe: Kapali"

    def update_data(self, data_matrix, depth_data=None):
        self.renderer.data_matrix = data_matrix
        self.renderer.depth_data = depth_data
