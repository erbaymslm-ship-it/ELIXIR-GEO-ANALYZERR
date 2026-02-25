"""
ELIXIR TECHNOLOGY
Dinamik 2D Isi Haritasi - Ekrana Otomatik Sigan
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel
import numpy as np


class HeatMapWidget(Widget):
    grid_data = ListProperty([])
    rows = NumericProperty(5)
    cols = NumericProperty(5)
    show_values = NumericProperty(0)
    highlight_row = NumericProperty(-1)
    highlight_col = NumericProperty(-1)

    def __init__(self, **kwargs):
        super(HeatMapWidget, self).__init__(**kwargs)
        self.data_matrix = np.zeros((5, 5))
        self.cell_tap_callback = None
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(grid_data=self.update_heatmap)
        self.bind(show_values=self.update_canvas)
        self.bind(rows=self._on_grid_change, cols=self._on_grid_change)
        self.bind(highlight_row=self.update_canvas, highlight_col=self.update_canvas)

    def _on_grid_change(self, *args):
        self.data_matrix = np.zeros((self.rows, self.cols))
        self.update_canvas()

    def update_heatmap(self, *args):
        if not self.grid_data:
            return

        matrix = np.zeros((self.rows, self.cols))
        for item in self.grid_data:
            row = item.get('row', 0)
            col = item.get('col', 0)
            value = item.get('value', 0)
            if row < self.rows and col < self.cols:
                matrix[row][col] = value

        if np.max(matrix) > np.min(matrix):
            normalized = (matrix - np.min(matrix)) / (np.max(matrix) - np.min(matrix)) * 255
        else:
            normalized = matrix * 255

        self.data_matrix = normalized.astype(np.uint8)
        self.update_canvas()

    def _get_color_for_value(self, value):
        if value < 0.25:
            t = value / 0.25
            return (0, int(80 * t), int(180 * (1 - t) + 50))
        elif value < 0.5:
            t = (value - 0.25) / 0.25
            return (0, int(80 + 175 * t), int(50 * (1 - t)))
        elif value < 0.75:
            t = (value - 0.5) / 0.25
            return (int(255 * t), int(215 - 50 * t), 0)
        else:
            t = (value - 0.75) / 0.25
            return (255, int(165 * (1 - t)), 0)

    def update_canvas(self, *args):
        if self.width <= 1 or self.height <= 1:
            return

        self.canvas.clear()

        with self.canvas:
            Color(*get_color_from_hex('#141414'))
            Rectangle(pos=self.pos, size=self.size)

            avail_w = self.width - 4
            avail_h = self.height - 4

            cell_w = avail_w / max(self.cols, 1)
            cell_h = avail_h / max(self.rows, 1)
            cell_size = min(cell_w, cell_h)

            total_w = cell_size * self.cols
            total_h = cell_size * self.rows
            offset_x = self.x + (self.width - total_w) / 2
            offset_y = self.y + (self.height - total_h) / 2

            font_size = max(7, min(14, int(cell_size * 0.35)))

            for row in range(self.rows):
                for col in range(self.cols):
                    if row < len(self.data_matrix) and col < len(self.data_matrix[0]):
                        value = self.data_matrix[row][col]
                        norm_value = value / 255.0 if value > 0 else 0
                        r, g, b = self._get_color_for_value(norm_value)
                        Color(r / 255, g / 255, b / 255, 0.85)
                    else:
                        Color(0.08, 0.08, 0.08, 1)

                    x = offset_x + col * cell_size
                    y = offset_y + (self.rows - 1 - row) * cell_size
                    gap = max(1, cell_size * 0.04)
                    Rectangle(pos=(x + gap, y + gap), size=(cell_size - gap * 2, cell_size - gap * 2))

                    if self.show_values == 1:
                        if row < len(self.data_matrix) and col < len(self.data_matrix[0]):
                            value = self.data_matrix[row][col]
                            Color(1, 1, 1, 0.9)
                            label = CoreLabel(text=f"{int(value)}", font_size=font_size)
                            label.refresh()
                            tex = label.texture
                            Rectangle(
                                texture=tex,
                                pos=(x + cell_size / 2 - tex.size[0] / 2,
                                     y + cell_size / 2 - tex.size[1] / 2),
                                size=tex.size
                            )

            Color(*get_color_from_hex('#3D3500'))
            for i in range(self.cols + 1):
                x = offset_x + i * cell_size
                Line(points=[x, offset_y, x, offset_y + total_h], width=0.8)
            for i in range(self.rows + 1):
                y = offset_y + i * cell_size
                Line(points=[offset_x, y, offset_x + total_w, y], width=0.8)

            if self.highlight_row >= 0 and self.highlight_col >= 0:
                hx = offset_x + self.highlight_col * cell_size
                hy = offset_y + (self.rows - 1 - self.highlight_row) * cell_size
                Color(1, 0.84, 0, 0.9)
                Line(rectangle=[hx, hy, cell_size, cell_size], width=2.5)
                Color(1, 1, 1, 0.15)
                Rectangle(pos=(hx, hy), size=(cell_size, cell_size))

        self._cell_layout = (offset_x, offset_y, cell_size, total_w, total_h)

    def _get_cell_from_touch(self, touch_x, touch_y):
        if not hasattr(self, '_cell_layout') or self._cell_layout is None:
            return None
        offset_x, offset_y, cell_size, total_w, total_h = self._cell_layout
        lx = touch_x - offset_x
        ly = touch_y - offset_y
        if lx < 0 or ly < 0 or lx >= total_w or ly >= total_h:
            return None
        col = int(lx / cell_size)
        row = self.rows - 1 - int(ly / cell_size)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col
        return None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            result = self._get_cell_from_touch(touch.x, touch.y)
            if result is not None:
                row, col = result
                value = 0
                if row < len(self.data_matrix) and col < len(self.data_matrix[0]):
                    value = float(self.data_matrix[row][col])
                self.highlight_row = row
                self.highlight_col = col
                if self.cell_tap_callback:
                    self.cell_tap_callback(row, col, value)
                return True
        return super().on_touch_down(touch)
