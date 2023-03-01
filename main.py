from random import randint  # Импортируем randint из модуля random


# Создаем общий класс
class BoardException(Exception):
    pass


# Создаем класс исключений если игрок выстрели за пределы игрового поля
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы игрового поля!"


# Создаем класс исключний если игрок повторно стреляет в точку
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


# Создаем класс корретного размещения кораблей
class BoardWrongShipException(BoardException):
    pass


# Создаем класс для работы с точками
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Создаем метод для обмена информацией о точках на поле
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Создаем метод для вывода точек в консоль
    def __repr__(self):
        return f"({self.x}, {self.y})"


# Создаем класс кораблей
class Ship:
    def __init__(self, point, l, o):
        self.point = point
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = [] #Создаем список точек корабля
        for i in range(self.l):
            cur_x = self.point.x
            cur_y = self.point.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    # Создаем метод для определения попадания в корабль
    def shooten(self, shot):
        return shot in self.dots


# Создаем класс поля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    # Создаем метод для размещения кораблей на игровом поле
    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "▉"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Создаем метод для опредления контура корабля
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # Создаем метод для записи игрового поля
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("▉", "O")
        return res

    # Создаем метод для проверки положения точки в пределах игрового поля
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Создаем метод для выстрелов
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


# Создаем общий класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# Создаем класс ИИ
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# Создаем класс игрока
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Создаем класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем Вас \n    в игре \n  ~Морской бой~ ")
        print("-------------------")
        print(" формат ввода: X, Y ")
        print("  где X - номер строки  ")
        print("  а Y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Пользователь выиграл!!! 👍 ")
                break

            if self.us.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Компьютер выиграл 👎 ")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

