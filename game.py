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


# ============================================================
# BOLA
# ============================================================
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10          # jari-jari bola
        self.direction = [1, -1]  # [horizontal, vertikal]: 1=kanan/bawah, -1=kiri/atas
        self.speed = 10           # jarak gerak bola per frame
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='orange')  # MODIF: warna bola (sebelumnya white)
        super(Ball, self).__init__(canvas, item)  # panggil __init__ milik GameObject

    def update(self):
        # dipanggil tiap frame untuk menggerakkan bola
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # kena dinding kiri atau kanan -> balik arah horizontal
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # kena atap -> balik arah vertikal
        if coords[1] <= 0:
            self.direction[1] *= -1
        # jarak geser = arah x kecepatan
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        # dipanggil saat bola menyentuh benda lain (paddle/brick)
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5  # titik tengah bola secara horizontal
        if len(game_objects) > 1:
            # kena 2 benda sekaligus -> pantul vertikal saja
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:      # bola di kanan benda -> pantul ke kanan
                self.direction[0] = 1
            elif x < coords[0]:    # bola di kiri benda -> pantul ke kiri
                self.direction[0] = -1
            else:                  # bola tepat di atas/bawah benda -> pantul vertikal
                self.direction[1] *= -1

        # kalau benda yang kena adalah Brick, kurangi hit-nya
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


# ============================================================
# PADDLE (papan pemukul)
# ============================================================
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100   # MODIF: lebih lebar (sebelumnya 80)
        self.height = 10
        self.ball = None   # bola yang menempel di paddle sebelum game mulai
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='cyan')  # MODIF: warna paddle (sebelumnya yellow)
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        # menyimpan bola agar ikut bergerak bersama paddle
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # hanya bergerak kalau tidak keluar dari layar
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)  # geser paddle (horizontal saja)
            if self.ball is not None:
                self.ball.move(offset, 0)        # bola ikut bergeser kalau masih menempel


