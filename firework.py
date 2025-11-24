import pygame
import random
from particle import Particle

# Класс - фейерверк
class Firework:
    # Инициализация
    def __init__(self, x, y, diagonal=False):
        # Позиция фейерверка
        self.x = x
        self.y = y
        self.initial_y = y  # Сохраняем начальную позицию Y для расчета прогресса
        self.initial_x = x  # Сохраняем начальную позицию X для диагональных фейерверков
        
        self.particles = [] # Список частиц (объектов класса Particle)
        
        # Параметры следа
        self.line = [] # Список для линии взрыва (x, y, size, alpha)
        self.max_line_length = 30 # Максимальная длина следа
        self.line_counter = 0 # Таймер между созданиями точек
        self.line_spacing = 2.5  # Интервал между созданием новых точек
        self.base_size = 2.6 # Базовый размер для центрирования
        
        # Физические параметры
        self.initial_speed_y = random.uniform(-7, -2)  # Начальная скорость (отрицательная - движение вверх)
        self.speed_y = self.initial_speed_y
        
        # Для диагональных фейерверков
        self.diagonal = diagonal
        if self.diagonal:
            # Случайное направление: влево или вправо
            self.direction = random.choice([-1, 1])
            self.initial_speed_x = random.uniform(1, 3) * self.direction
            self.speed_x = self.initial_speed_x
            # Точка взрыва - всегда выше текущей позиции с отступами от краев
            min_explosion_height = 50  # Минимальный отступ от верхнего края
            max_explosion_height = self.initial_y - 50  # Минимальный отступ от исходной позиции

            # Если исходная позиция слишком низкая (меньше 100px от верха), 
            # то взрываемся посередине между верхним краем и исходной позицией
            if max_explosion_height < min_explosion_height:
                self.explosion_height = (min_explosion_height + self.initial_y) // 2
            else:
                self.explosion_height = random.randint(min_explosion_height, max_explosion_height)
        
        # Визуальные параметры
        else:
            # Вертикальные фейерверки
            self.speed_x = 0
            # Точка взрыва - всегда выше текущей позиции с отступами от краев
            min_explosion_height = 50  # Минимальный отступ от верхнего края
            max_explosion_height = self.initial_y - 50  # Минимальный отступ от исходной позиции

            # Если исходная позиция слишком низкая (меньше 100px от верха), 
            # то взрываемся посередине между верхним краем и исходной позицией
            if max_explosion_height < min_explosion_height:
                self.explosion_height = (min_explosion_height + self.initial_y) // 2
            else:
                self.explosion_height = random.randint(min_explosion_height, max_explosion_height)    
        # Визуальные параметры
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.exploded = False # Флаг на взрыв
    
    # Обновление состояния фейерверка
    def update(self):
        if not self.exploded:
            self._update_flying()
        else:
            self._update_explosion()
            
    # Обновление полета (до взрыва)
    def _update_flying(self):
        if self.diagonal:
            # Для диагональных фейерверков
            total_distance = self.initial_y - self.explosion_height
            current_distance = self.initial_y - self.y
            progress = current_distance / total_distance
            
            # Замедление скорости на последних 40% пути
            if progress > 0.6:
                slowdown_factor = 1 - (progress - 0.6) / 0.4
                self.speed_y = self.initial_speed_y * (0.5 + 0.5 * slowdown_factor)
                self.speed_x = self.initial_speed_x * (0.5 + 0.5 * slowdown_factor)
        else:
            # Для вертикальных фейерверков
            total_distance = self.initial_y - self.explosion_height
            current_distance = self.initial_y - self.y
            progress = current_distance / total_distance
            
            # Замедление скорости на последних 40% пути
            if progress > 0.6:
                slowdown_factor = 1 - (progress - 0.6) / 0.4
                self.speed_y = self.initial_speed_y * (0.5 + 0.5 * slowdown_factor)
        
        self._add_line_point() # Добавление новой точки следа
        self._update_line() # Обновление существующих точек следа
        self.y += self.speed_y # Перемещение фейерверка
        if self.diagonal:
            self.x += self.speed_x # Перемещение по X для диагональных фейерверков
        
        # Проверка достижения точки взрыва
        if self.y <= self.explosion_height:
            self.explode()
    
    # Добавление новой точки в след
    def _add_line_point(self):
        self.line_counter += 1
        if self.line_counter >= self.line_spacing:
            # Длина следа зависит от текущей скорости
            if self.diagonal:
                speed_factor = (abs(self.speed_y) + abs(self.speed_x)) / (abs(self.initial_speed_y) + abs(self.initial_speed_x))
            else:
                speed_factor = abs(self.speed_y / self.initial_speed_y)
                
            current_line_length = self.max_line_length * (0.6 + 0.4 * speed_factor)
            self.line.append((self.x, self.y, current_line_length, 255))  # Новая точка с максимальной альфой
            self.line_counter = 0
    
    # Обновление точек следа (уменьшение альфа-канала)
    def _update_line(self):
        # Уменьшение альфа-канала всех точек
        for i in range(len(self.line)):
            x, y, size, alpha = self.line[i]
            self.line[i] = (x, y, size, max(0, alpha - 8))  # Медленное затухание
        
        # Удаление полностью прозрачных точек
        self.line = [(x, y, size, alpha) for x, y, size, alpha in self.line if alpha > 0]
    
    # Обновление взрыва (после детонации)
    def _update_explosion(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
    
    # Взрыв
    def explode(self):
        self.exploded = True
        
        # Создание частиц взрыва с одинаковым временем жизни
        number_particles = random.randint(100, 200)
        particle_lifetime = random.randint(40, 80)  # Общее время жизни для всех частиц
        
        for _ in range(number_particles):
            particle = Particle(self.x, self.y, self.color)
            particle.lifetime = particle_lifetime  # Устанавливаем одинаковое время жизни
            particle.max_lifetime = particle_lifetime  # И максимальное время жизни тоже одинаковое
            self.particles.append(particle)
        
    # Проверка на то, что или фейерверк еще не взорвался или он пока взрывется и его частицы живы
    def is_alive(self):
        return not self.exploded or len(self.particles) > 0
    
    # Отрисовка фейерверка
    def draw(self, screen):
        if not self.exploded:
            self._draw_line(screen)
        else:
            self._draw_explosion(screen)
    
    # Отрисовка следа
    def _draw_line(self, screen):
        for x, y, size, alpha in self.line:
            if alpha > 0:
                # Расчет размера и прозрачности точки
                circle_size = max(1, size / 8)
                
                # Создание поверхности с альфа-каналом
                max_surface_size = int(self.base_size * 2 + 2)
                circle_surface = pygame.Surface((max_surface_size, max_surface_size), pygame.SRCALPHA)
                circle_color = (*self.color, int(alpha))
                
                # Отрисовка точки
                center_x, center_y = max_surface_size // 2, max_surface_size // 2
                pygame.draw.circle(circle_surface, circle_color, (center_x, center_y), circle_size)
                screen.blit(circle_surface, (x - center_x, y - center_y))
    
    # Отрисовка взрыва
    def _draw_explosion(self, screen):
        for particle in self.particles:
            particle.draw(screen)

if __name__ == "__main__":        
    # Экран
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Фейерверк')
    background = (0, 0, 0)
    clock = pygame.time.Clock()

    # Список всех фейерверков
    fireworks = []

    # Таймер для фейерверков
    firework_timer = 0
    firework_interval = 30

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
        
        firework_timer += 1
        if firework_timer >= firework_interval:
            # Случайно выбираем тип фейерверка
            diagonal = random.choice([True, False])
            new_firework = Firework(random.randint(20, width - 20), height, diagonal)
            fireworks.append(new_firework)
            firework_timer = 0
            
        for firework in fireworks[:]: # Испольуем копию списка, чтобы безопасно удалять фейерверки
            firework.update()
            firework.draw(screen)
                
            if not firework.is_alive():
                fireworks.remove(firework)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()