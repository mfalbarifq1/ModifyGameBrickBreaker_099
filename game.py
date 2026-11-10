import tkinter as tk  # library GUI bawaan Python, dipakai untuk window dan canvas


# ============================================================
# KELAS INDUK: semua benda di game (bola, paddle, brick) turunan dari sini
# ============================================================
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas  # canvas tempat benda digambar
        self.item = item      # ID gambar benda di canvas (dipakai untuk geser/hapus)

    def get_position(self):
        # mengembalikan [x1, y1, x2, y2] = pojok kiri atas & kanan bawah benda
        return self.canvas.coords(self.item)

    def move(self, x, y):
        # menggeser benda sejauh x (horizontal) dan y (vertikal)
        self.canvas.move(self.item, x, y)

    def delete(self):
        # menghapus benda dari canvas
        self.canvas.delete(self.item)


