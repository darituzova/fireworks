import pygame
import random
from particle import Particle

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

if __name__ == "__main__":        
    # Инициализация pygame и создание окна
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Фейерверк')
    background = (0, 0, 0)
    clock = pygame.time.Clock()

    # Список всех активных фейерверков
    fireworks = []

    # Таймер для автоматического создания фейерверков
    firework_timer = 0
    firework_interval = 30  # Интервал между авто-фейерверками в кадрах
    
    # Основной цикл
    running = True

    while running:
        screen.fill((background))
        
        # Обработчик событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Клавища ESC - выход
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # Добавляем обработку клика мыши
                if event.button == 1:  # Левая кнопка мыши
                    # Создаем фейерверк в позиции клика
                    x, y = event.pos
                    diagonal = random.choice([True, False])
                    new_firework = Firework(x, y, diagonal)
                    fireworks.append(new_firework)
        
        # Автоматическое создание фейерверков через интервалы
        firework_timer += 1
        if firework_timer >= firework_interval:
            # Случайно выбираем тип фейерверка и позицию
            diagonal = random.choice([True, False])
            new_firework = Firework(random.randint(20, width - 20), height, diagonal)
            fireworks.append(new_firework)
            firework_timer = 0
        
        # Обновление и отрисовка всех фейерверков
        for firework in fireworks[:]: # Испольуем копию списка, чтобы безопасно удалять фейерверки
            firework.update()
            firework.draw(screen)
            
            # Удаление "мертвых" фейерверков
            if not firework.is_alive():
                fireworks.remove(firework)
        
        # Обновление дисплея
        pygame.display.flip()
        clock.tick(60)
    
    # Завершение работы pygame
    pygame.quit()