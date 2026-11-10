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


# ============================================================
# BRICK (balok)
# ============================================================
class Brick(GameObject):
    # kamus: sisa hit -> warna. Warna berubah tiap brick kena pukul
    COLORS = {1: '#e74c3c', 2: '#3498db', 3: '#2ecc71'}  # MODIF: hits 3 jadi hijau (sebelumnya #222222)

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits                 # berapa kali brick harus dipukul
        color = Brick.COLORS[hits]       # warna awal sesuai jumlah hit
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')  # tag dipakai untuk menghitung sisa brick
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()  # hit habis -> brick hilang
        else:
            # masih ada sisa hit -> ganti warna sesuai sisa hit
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


# ============================================================
# GAME (kelas utama)
# ============================================================
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 5      # MODIF: nyawa (sebelumnya 3)
        self.score = 0      # MODIF: skor awal
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#1a1a2e',  # MODIF: background gelap (sebelumnya #aaaaff)
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}   # kamus: ID canvas -> objek (dipakai untuk mencari objek saat tabrakan)
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        # menyusun brick: 3 baris, tiap baris diulang ke kanan
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)  # MODIF: baris atas 3 hit (sebelumnya 2)
            self.add_brick(x + 37.5, 70, 2)  # MODIF: baris tengah 2 hit (sebelumnya 1)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None        # teks nyawa (dibuat nanti)
        self.score_hud = None  # MODIF: teks skor (dibuat nanti)
        self.setup_game()
        self.canvas.focus_set()  # agar canvas bisa menerima input keyboard
        # tombol panah menggerakkan paddle
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-20))  # MODIF: -20 (sebelumnya -10)
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(20))   # MODIF: 20 (sebelumnya 10)

    def setup_game(self):
        # menyiapkan satu ronde (dipanggil di awal & setiap kehilangan nyawa)
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()  # MODIF: tampilkan skor
        self.text = self.draw_text(300, 200,
                                   'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        # hapus bola lama (kalau ada), lalu buat bola baru di atas tengah paddle
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)  # tempelkan bola ke paddle

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick  # daftarkan ke kamus agar bisa dicari saat tabrakan

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='white')  # MODIF: teks putih

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)  # pertama kali: buat teks
        else:
            self.canvas.itemconfig(self.hud, text=text)  # selanjutnya: ubah isinya saja

    def update_score_text(self):  # MODIF: method baru untuk menampilkan skor
        text = 'Score: %s' % self.score
        if self.score_hud is None:
            self.score_hud = self.draw_text(550, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')   # spasi tidak dipakai lagi
        self.canvas.delete(self.text)   # hapus tulisan "Press Space to start"
        self.paddle.ball = None         # lepas bola dari paddle
        self.game_loop()                # mulai perulangan game

    def game_loop(self):
        # jantung game, dipanggil berulang tiap beberapa milidetik
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))  # hitung sisa brick
        if num_bricks == 0:
            # semua brick habis -> menang
            self.ball.speed = None
            self.draw_text(300, 200, 'You win!')
        elif self.ball.get_position()[3] >= self.height:
            # bola jatuh melewati bawah layar -> nyawa berkurang
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                # NOTE: karena pakai < 0, pemain dapat lives+1 kesempatan.
                # Kalau mau pas 5, ganti jadi: self.lives <= 0
                self.draw_text(300, 200, 'You Lose!!! Game Over!')
            else:
                self.after(1000, self.setup_game)  # ronde baru setelah 1 detik
        else:
            # game lanjut: gerakkan bola lalu ulangi loop
            self.ball.update()
            self.after(40, self.game_loop)  # MODIF: 40 ms (sebelumnya 50) -> lebih cepat

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        # cari semua benda yang tumpang tindih dengan bola
        items = self.canvas.find_overlapping(*ball_coords)
        # ubah ID canvas menjadi objek game (paddle/brick)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:  # MODIF: tambah skor tiap kena brick
            if isinstance(obj, Brick):
                self.score += 10
        self.update_score_text()


# program mulai dari sini (hanya jalan kalau file dijalankan langsung)
if __name__ == '__main__':
    root = tk.Tk()                  # window utama
    root.title('Brick Breaker')     # MODIF: judul window (sebelumnya 'Hello, Jarvis!')
    game = Game(root)               # buat game di dalam window
    game.mainloop()                 # window terus tampil menunggu input