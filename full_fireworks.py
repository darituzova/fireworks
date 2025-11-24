import pygame
import random
import math
import json

# Класс - частица фейерверка
class Particle:
    # Инициализация
    def __init__(self, x, y, color, config=None):
        # Инициализация конфигурации
        if config is None:
            config = {}
        config_particle = config.get('particle', {})
        
        # Основные параметры частицы
        self.x = x
        self.y = y
        self.color = color # Цвет наследуется от фейерверка
        
        # Случайное направление движения по кругу
        angle = random.uniform(0, 2 * math.pi) # Случайный угол от 0 до 360 градусов
        speed_range = config_particle.get('speed_range', [1.5, 3])
        speed = random.uniform(speed_range[0], speed_range[1])
        
        # Разложение скорости на компоненты по осям
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        
        # Визуальные параметры
        size_range = config_particle.get('size_range', [2, 4])
        self.size = random.randint(size_range[0], size_range[1])
        
        # Время жизни частицы
        lifetime_range = config_particle.get('lifetime_range', [200, 220])
        self.lifetime = random.randint(lifetime_range[0], lifetime_range[1])
        self.max_lifetime = self.lifetime  # Сохраняем максимальное время жизни
        
        # Параметры следа частицы
        self.line = [] # Список точек следа (x, y, size, alpha)
        self.max_line_length = config_particle.get('line_max_length', 15)
        self.line_counter = 0 # Счетчик для создания точек
        self.line_spacing = config_particle.get('line_spacing', 2)
        self.line_fade_speed = config_particle.get('line_fade_speed', 6)
        self.base_size = config_particle.get('base_size', 2.5)
        
        # Физические параметры
        self.gravity = config_particle.get('gravity', 0.05)
        
        # Параметры затухания
        self.fading = False # Флаг начала затухания
        self.fade_alpha = 255  # Начальная прозрачность
        self.fade_start = config_particle.get('fade_start', 30) # Когда начинать затухание
    
    # Обновление состояния частицы на каждом кадре
    def update(self):
        # Сохраняем предыдущую позицию для создания плавного следа
        old_x, old_y = self.x, self.y
        
        # Обновление позиции с учетом гравитации
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity # Гравитация влияет только на вертикальную скорость
        self.lifetime -= 1 # Уменьшаем время жизни
        
        # Активация затухания, когда время жизни подходит к концу
        if self.lifetime <= self.fade_start and not self.fading:
            self.fading = True
        
        # Обновление прозрачности при затухании
        if self.fading:
            # Прогресс затухания от 0 до 1
            fade_progress = (self.fade_start - self.lifetime) / self.fade_start
            self.fade_alpha = max(0, 255 - int(255 * fade_progress))
        
        # Добавление новых точек следа
        self._add_line_point(old_x, old_y)
        
        # Обновление существующих точек следа
        self._update_line()
    
    # Добавление новой точки в след частицы
    def _add_line_point(self, old_x, old_y):
        self.line_counter += 1
        if self.line_counter >= self.line_spacing:
            # Длина следа зависит от текущей скорости
            speed_factor = min(1.0, (abs(self.speed_x) + abs(self.speed_y)) / 8)  # Чем быстрее движется частица, тем длиннее след
            current_line_length = self.max_line_length * (0.5 + 0.5 * speed_factor)
            
            # Используем среднюю точку между старым и новым положением для плавности
            mid_x = (old_x + self.x) / 2
            mid_y = (old_y + self.y) / 2
            
            # Прозрачность точек следа не превышает общую прозрачность частицы
            line_alpha = min(220, self.fade_alpha)
            self.line.append((mid_x, mid_y, current_line_length, line_alpha))
            self.line_counter = 0
    
    # Обновление точек следа (уменьшение альфа-канала)
    def _update_line(self):
        # Уменьшение альфа-канала всех точек с учетом общего затухания
        for i in range(len(self.line)):
            x, y, size, alpha = self.line[i]
            # Уменьшаем прозрачность, но не ниже 0
            new_alpha = max(0, alpha - self.line_fade_speed)
            # Учитываем общее затухание частицы
            if self.fading:
                new_alpha = min(new_alpha, self.fade_alpha)
            self.line[i] = (x, y, size, new_alpha)
        
        # Удаление полностью прозрачных точек
        self.line = [(x, y, size, alpha) for x, y, size, alpha in self.line if alpha > 0]
    
    # Проверка на время жизни частицы
    def is_alive(self):
        return self.lifetime > 0
    
    # Отрисовка частицы и ее следа
    def draw(self, screen):
        # Отрисовка следа
        self._draw_line(screen)
        
        # Отрисовка самой частицы (круг)
        if self.is_alive():
            # Используем fade_alpha для плавного затухания
            alpha = self.fade_alpha
            
            # Создание поверхности с альфа-каналом для частицы
            particle_surface = pygame.Surface((self.size * 2 + 2, self.size * 2 + 2), pygame.SRCALPHA)
            particle_color = (*self.color, alpha) # Цвет с учетом прозрачности
            
            # Отрисовка круглой частицы
            pygame.draw.circle(particle_surface, particle_color, (self.size + 1, self.size + 1), self.size)
            
            # Размещение частицы на экране
            screen.blit(particle_surface, (self.x - self.size - 1, self.y - self.size - 1))
    
    # Отрисовка следа
    def _draw_line(self, screen):
        for x, y, size, alpha in self.line:
            if alpha > 0: # Рисуем только видимые точки
                # Расчет размера точки следа
                circle_size = max(0.5, size / 8)
                
                # Создание поверхности с альфа-каналом
                max_surface_size = int(self.base_size * 2 + 2)
                circle_surface = pygame.Surface((max_surface_size, max_surface_size), pygame.SRCALPHA)
                circle_color = (*self.color, int(alpha)) # Цвет с учетом прозрачности
                
                # Отрисовка круглой точки следа
                center_x, center_y = max_surface_size // 2, max_surface_size // 2
                pygame.draw.circle(circle_surface, circle_color, (center_x, center_y), circle_size)
                
                # Размещение точки следа на экране
                screen.blit(circle_surface, (x - center_x, y - center_y))


# Класс - фейерверк
class Firework:
    # Инициализация
    def __init__(self, x, y, diagonal=False, config=None):
        # Инициализация конфигурации
        if config is None:
            config = {}
        config_firework = config.get('firework', {})
        
        # Позиция и движение
        self.x = x
        self.y = y
        self.initial_y = y  # Сохраняем начальную позицию Y для расчета прогресса
        self.initial_x = x  # Сохраняем начальную позицию X для диагональных фейерверков
        
        # Списки для визуальных эффектов
        self.particles = [] # Список частиц (объектов класса Particle)
        self.line = []  # След фейерверка (x, y, size, alpha)
        
        # Параметры следа
        self.max_line_length = config_firework.get('line_max_length', 30) # Максимальная длина хвоста
        self.line_counter = 0 # Счетчик для создания новых точек следа
        self.line_spacing = config_firework.get('line_spacing', 2.5) # Интервал между точками следа
        self.line_fade_speed = config_firework.get('line_fade_speed', 8) # Скорость исчезновения точек
        self.base_size = config_firework.get('base_size', 2.6) # Базовый размер точек следа
        
        # Физические параметры
        initial_speed_y_range = config_firework.get('initial_speed_y_range', [-7, -2])
        self.initial_speed_y = random.uniform(initial_speed_y_range[0], initial_speed_y_range[1])
        self.speed_y = self.initial_speed_y
        
        # Для диагональных фейерверков - движение под углом
        self.diagonal = diagonal
        if self.diagonal:
            # Случайное направление: влево (-1) или вправо (1)
            self.direction = random.choice([-1, 1])
            diagonal_speed_x_range = config_firework.get('diagonal_speed_x_range', [1, 3])
            self.initial_speed_x = random.uniform(diagonal_speed_x_range[0], diagonal_speed_x_range[1]) * self.direction
            self.speed_x = self.initial_speed_x # Горизонтальная скорость для диагонального движения
        else:
            # Вертикальные фейерверки - движение только вверх
            self.speed_x = 0
        
        # Определение высоты взрыва
        min_explosion_height = config_firework.get('min_explosion_height', 50) # Минимальная высота взрыва
        max_explosion_height_offset = config_firework.get('max_explosion_height_offset', 50) # Отступ от верха
        max_explosion_height = self.initial_y - max_explosion_height_offset # Максимальная высота взрыва

        # Если исходная позиция слишком низкая, то взрываемся посередине
        if max_explosion_height < min_explosion_height:

            self.explosion_height = (min_explosion_height + self.initial_y) // 2
        else:
            # Случайная высота взрыва в допустимом диапазоне
            self.explosion_height = random.randint(min_explosion_height, max_explosion_height)
            
        # Визуальные параметры
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.exploded = False # Флаг на взрыв
        self.config = config # Полная конфигурация
        self.config_firework = config_firework # Конфигурация конкретно для фейерверков
    
    # Основное обновление состояния фейерверка на каждом кадре
    def update(self):
        if not self.exploded:
            # Обновление полета до взрыва
            self._update_flying()
        else:
            # Обновление взрыва и частиц
            self._update_explosion()
            
    # Обновление полета (до взрыва)
    def _update_flying(self):
        # Расчет прогресса полета от начальной позиции до точки взрыва
        total_distance = self.initial_y - self.explosion_height
        current_distance = self.initial_y - self.y
        progress = current_distance / total_distance
        
        # Замедление скорости на последних 40% пути для эффекта "торможения перед взрывом"
        if progress > 0.6:
            slowdown_factor = 1 - (progress - 0.6) / 0.4  # От 1 до 0
            self.speed_y = self.initial_speed_y * (0.5 + 0.5 * slowdown_factor) # Это гарантирует, что скорость никогда не упадет ниже 50% от начальной
            if self.diagonal:
                self.speed_x = self.initial_speed_x * (0.5 + 0.5 * slowdown_factor) # Это гарантирует, что скорость никогда не упадет ниже 50% от начальной
        
        self._add_line_point() # Добавление новой точки следа
        self._update_line() # Обновление существующих точек следа (уменьшение прозрачности)
        self.y += self.speed_y # Перемещение фейерверка
        if self.diagonal:
            self.x += self.speed_x # Перемещение по X для диагональных фейерверков
        
        # Проверка достижения точки взрыва
        if self.y <= self.explosion_height:
            self.explode()
    
    # Добавление новой точки в след
    def _add_line_point(self):
        self.line_counter += 1
        # Создаем новую точку следа через определенные интервалы
        if self.line_counter >= self.line_spacing:
            # Длина следа зависит от текущей скорости - чем быстрее, тем длиннее хвост
            if self.diagonal:
                speed_factor = (abs(self.speed_y) + abs(self.speed_x)) / (abs(self.initial_speed_y) + abs(self.initial_speed_x))
            else:
                speed_factor = abs(self.speed_y / self.initial_speed_y)
            
            # Текущая длина хвоста с учетом скорости
            current_line_length = self.max_line_length * (0.6 + 0.4 * speed_factor) # гарантирует, что хвост никогда не исчезнет полностью
            self.line.append((self.x, self.y, current_line_length, 255))  # Новая точка с максимальной альфой
            self.line_counter = 0 # Сбрасываем счетчик
    
    # Обновление точек следа - уменьшение прозрачности и удаление невидимых точек
    def _update_line(self):
        # Уменьшение альфа-канала всех точек
        for i in range(len(self.line)):
            x, y, size, alpha = self.line[i]
            # Уменьшаем прозрачность, но не ниже 0
            self.line[i] = (x, y, size, max(0, alpha - self.line_fade_speed))
        
        # Удаление полностью прозрачных точек (альфа = 0)
        self.line = [(x, y, size, alpha) for x, y, size, alpha in self.line if alpha > 0]
    
    # Обновление взрыва (после детонации)
    def _update_explosion(self):
        for particle in self.particles[:]: # Проходим по копии списка частиц для безопасного удаления
            particle.update()
            
            # Удаляем "мертвые" частицы (у которых закончилось время жизни)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    # Взрыв
    def explode(self):
        self.exploded = True
        
        # Выбираем кол-во частиц
        particles_count_range = self.config_firework.get('particles_count_range', [100, 200])
        number_particles = random.randint(particles_count_range[0], particles_count_range[1])
        
        # Создание частиц взрыва с одинаковым временем жизни
        particles_lifetime_range = self.config_firework.get('particles_lifetime_range', [40, 80])
        particle_lifetime = random.randint(particles_lifetime_range[0], particles_lifetime_range[1])
        
        # Создаем указанное количество частиц
        for _ in range(number_particles):
            # Передаем полный конфиг, Particle сам выберет нужные настройки
            particle = Particle(self.x, self.y, self.color, self.config)
            # Устанавливаем одинаковое время жизни для всех частиц этого взрыва
            particle.lifetime = particle_lifetime
            particle.max_lifetime = particle_lifetime
            self.particles.append(particle)
        
    # Проверка "жив" ли фейерверк
    def is_alive(self):
        return not self.exploded or len(self.particles) > 0
    
    # Основной метод отрисовки фейерверка
    def draw(self, screen):
        if not self.exploded:
            # Рисуем след полета
            self._draw_line(screen)
        else:
            # Рисуем взрыв
            self._draw_explosion(screen)
    
    # Отрисовка следа (хвоста) фейерверка
    def _draw_line(self, screen):
        for x, y, size, alpha in self.line:
            if alpha > 0: # Рисуем только видимые точки
                # Расчет размера и прозрачности точки
                circle_size = max(1, size / 8)
                
                # Создание поверхности с альфа-каналом для прозрачности
                max_surface_size = int(self.base_size * 2 + 2)
                circle_surface = pygame.Surface((max_surface_size, max_surface_size), pygame.SRCALPHA)
                # Цвет точки с учетом текущей прозрачности
                circle_color = (*self.color, int(alpha))
                
                # Отрисовка точки на временной поверхности
                center_x, center_y = max_surface_size // 2, max_surface_size // 2
                pygame.draw.circle(circle_surface, circle_color, (center_x, center_y), circle_size)
                # Копируем точку на основной экран с правильными координатами
                screen.blit(circle_surface, (x - center_x, y - center_y))
    
    # Отрисовка взрыва - отрисовка всех частиц
    def _draw_explosion(self, screen):
        for particle in self.particles:
            particle.draw(screen)


# Класс - Игра
class Game:
    # Инициализация параметров игры
    def __init__(self, width=1000, height=800, caption='Фейерверки', background=(0, 0, 0), firework_interval=30, diagonal=False, margin_x=20, fps=60, config=None):
        # Устанавливаем конфиг по умолчанию если не передан
        if config is None:
            config = {} 
        
        # Инициализация pygame
        pygame.init()
        
        # Настройки графического окна
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(caption)
        self.background = background
        self.clock = pygame.time.Clock()
        
        # Список активных фейерверков
        self.fireworks = []
        
        # Таймер для фейерверков
        self.firework_timer = 0
        self.firework_interval = firework_interval
        
        # Режим движения фейерверков (диагональный или вертикальный)
        self.diagonal = diagonal
        
        # Флаг работы главного цикла
        self.running = True
        
        # Дополнительные настройки
        self.margin_x = margin_x
        self.fps = fps
        self.config = config # Конфигурация из файл
    
    # Обработка всех событий
    def handle_events(self):
        for event in pygame.event.get():
            # Закрытие окна (крестик)
            if event.type == pygame.QUIT:
                self.running = False
            
            # Нажатие клавиши на клавиатуре
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Клавища ESC - выход
                    self.running = False
            
            # Нажатие кнопки мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.create_firework_at_pos(event.pos)
    
    # Создание фейерверка в указанной позиции
    def create_firework_at_pos(self, pos):
        x, y = pos
        new_firework = Firework(x, y, self.diagonal, self.config)
        self.fireworks.append(new_firework)
    
    # Создание случайного фейерверка
    def spawn_random_firework(self):
        new_firework = Firework(random.randint(self.margin_x, self.width - self.margin_x), self.height, self.diagonal, self.config)
        self.fireworks.append(new_firework)
    
    # Обновление состояния игры на каждом кадре
    def update(self):
        # Увеличиваем таймер и создаем фейерверк при достижении интервала
        self.firework_timer += 1
        if self.firework_timer >= self.firework_interval:
            self.spawn_random_firework()
            self.firework_timer = 0 # Сбрасываем таймер
        
        # Обновляем все фейерверки и удаляем "мертвые"
        for firework in self.fireworks[:]: # Испольуем копию списка, чтобы безопасно удалять фейерверки
            firework.update()
            
            if not firework.is_alive():
                self.fireworks.remove(firework)
    
    # Отрисовка всех элементов игры на экране
    def draw(self):
        # Заливаем фон
        self.screen.fill((self.background))
        
        # Отрисовываем все активные фейерверки
        for firework in self.fireworks:
            firework.draw(self.screen)
        
        # Обновляем дисплей
        pygame.display.flip()
    
    # Главный игровой цикл
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps) 
        
        # Завершение работы pygame при выходе из цикла
        pygame.quit()


# Загружает конфигурацию из JSON файла
def load_config(name):
    try:
        # Попытка открыть и прочитать конфигурационный файл
        with open(name, 'r', encoding='UTF-8') as f:
            config = json.load(f)
        print(f'Конфигурация загружена из {name}')
        return config
    except FileNotFoundError:
        # Обработка случая, когда файл не найден
        print(f'Файл {name} не найден. Используются значения по умолчанию.')
        return None
    except Exception as e:
        # Обработка всех других ошибок (невалидный JSON, и т.д.)
        print(f'Ошибка при чтении {name}: {e}')
        print('Используются значения по умолчанию.')
        return None

# Загрузка конфигурации из файла
config = load_config('config/config_base.json')

# Создание экземпляра игры с параметрами из конфигурации или значениями по умолчанию
if config:
    # Если конфигурация загружена, используем значения из нее (учитываем, что может не оказаться ключа в json)
    game = Game(width=config.get('width', 1000),
                height=config.get('height', 800),
                background=tuple(config.get('background', [0, 0, 0])),
                firework_interval=config.get('firework_interval', 30),
                diagonal=config.get('diagonal', False),
                margin_x=config.get('margin_x', 20),
                fps=config.get('fps', 60),
                config=config)
else:
    # Если конфигурация не загружена, используем все значения по умолчанию
    game = Game()

# Запуск основного цикла игры
game.run()