from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

Pointer = tuple[int, int]
# Направления движения:
UP: Pointer = (0, -1)
DOWN: Pointer = (0, 1)
LEFT: Pointer = (-1, 0)
RIGHT: Pointer = (1, 0)

Color = tuple[int, int, int]
# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Color = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR: Color = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: Color = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: Color = (0, 255, 0)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, body_color: Color | None = None) -> None:
        """Инициализирует игровой объект с позицией по цетру окна."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw(self) -> None:
        """Абстрактный метод для отрисовки объекта."""
        raise NotImplementedError(
            'Метод draw() должен быть реализован в дочернем классе')


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self, body_color=APPLE_COLOR, taking_position: list[Pointer] = None) -> None:
        """Инициализирует яблоко в случайном метсте."""
        super().__init__(body_color=body_color)
        self.position: Pointer = self.randomize_position(taking_position or [])

    def draw(self) -> None:
        """Отрисовка яблока."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, taking_position: list[Pointer]) -> Pointer:
        """Возврощает рандомные координаты яблока."""
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if position not in taking_position:
                return position


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self, body_color: Color = SNAKE_COLOR) -> None:
        super().__init__(body_color=body_color)
        """Задаем начальные параметры змейки."""
        self.reset()

    def update_direction(self) -> None:
        """Обновляем напрвление змейки, на основе ввода пользовотеля."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Перемещает змейку в текущем направлении.

        Добавляет новую голову и при необходимости удаляет хвост.
        Обесперчивает телепортацию, при выходе за границу карты.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

        self.last = (self.positions.pop() if len(
            self.positions) > self.length else None)

    def draw(self) -> None:
        """Отрисовывает змейку."""
        for position in self.positions[:-1]:
            rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> Pointer:
        """Возвращает координаты головы."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывыет параметры змейки в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None


def handle_keys(game_object) -> None:
    """Обрабатывает нажатия клавиш от пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Основная функция игры, содержащая главные игровой цикл."""
    pg.init()
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        screen.fill(BOARD_BACKGROUND_COLOR)

        snake.update_direction()
        snake.move()
        snake.draw()
        apple.draw()

        # Проверка на съедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.position = apple.randomize_position(snake.positions)
        # Проверка столкновения с самим собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        pg.display.update()


if __name__ == '__main__':
    main()
