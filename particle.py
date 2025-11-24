import pygame
import random
import math

# Класс - частица фейерверка
class Particle:
    # Инициализация
    def __init__(self, x, y, color, config=None):
        if config is None:
            config = {}
        
        # Получаем настройки для частиц
        config_particle = config.get('particle', {})
        
        self.x = x
        self.y = y
        self.color = color # От фейерверка зависит
        
        # Создаем круговой взрыв с увеличенной скоростью и радиусом
        angle = random.uniform(0, 2 * math.pi)  # Случайный угол
        speed_range = config_particle.get('speed_range', [1.5, 3])
        speed = random.uniform(speed_range[0], speed_range[1])
        
        # Равномерное распределение по кругу
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        
        size_range = config_particle.get('size_range', [2, 4])
        self.size = random.randint(size_range[0], size_range[1])
        
        lifetime_range = config_particle.get('lifetime_range', [200, 220])
        self.lifetime = random.randint(lifetime_range[0], lifetime_range[1])
        self.max_lifetime = self.lifetime  # Сохраняем максимальное время жизни
        
        # Параметры следа
        self.line = [] # Список для линии следа (x, y, size, alpha)
        self.max_line_length = config_particle.get('line_max_length', 15)
        self.line_counter = 0 # Таймер между созданиями точек
        self.line_spacing = config_particle.get('line_spacing', 2)
        self.line_fade_speed = config_particle.get('line_fade_speed', 6)
        self.base_size = config_particle.get('base_size', 2.5)
        
        # Физические параметры
        self.gravity = config_particle.get('gravity', 0.05)
        
        # Флаг для плавного затухания
        self.fading = False
        self.fade_alpha = 255  # Начальная прозрачность
        self.fade_start = config_particle.get('fade_start', 30)
    
    # Обновление местоположения частицы и ее времени жизни
    def update(self):
        # Сохраняем позицию до обновления
        old_x, old_y = self.x, self.y
        
        # Обновляем позицию с учетом гравитации
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.lifetime -= 1
        
        # Начинаем затухание когда время жизни подходит к концу
        if self.lifetime <= self.fade_start and not self.fading:
            self.fading = True
        
        # Обновляем прозрачность при затухании
        if self.fading:
            fade_progress = (self.fade_start - self.lifetime) / self.fade_start
            self.fade_alpha = max(0, 255 - int(255 * fade_progress))
        
        # Добавляем точки следа
        self._add_line_point(old_x, old_y)
        
        # Обновляем существующие точки следа
        self._update_line()
    
    # Добавление новой точки в след
    def _add_line_point(self, old_x, old_y):
        self.line_counter += 1
        if self.line_counter >= self.line_spacing:
            # Длина следа зависит от текущей скорости
            speed_factor = min(1.0, (abs(self.speed_x) + abs(self.speed_y)) / 8)
            current_line_length = self.max_line_length * (0.5 + 0.5 * speed_factor)
            
            # Добавляем точку между старой и новой позицией для плавности
            mid_x = (old_x + self.x) / 2
            mid_y = (old_y + self.y) / 2
            
            # Используем текущую прозрачность для точек следа
            line_alpha = min(220, self.fade_alpha)
            self.line.append((mid_x, mid_y, current_line_length, line_alpha))
            self.line_counter = 0
    
    # Обновление точек следа (уменьшение альфа-канала)
    def _update_line(self):
        # Уменьшение альфа-канала всех точек с учетом общего затухания
        for i in range(len(self.line)):
            x, y, size, alpha = self.line[i]
            # Учитываем общую прозрачность при затухании
            new_alpha = max(0, alpha - self.line_fade_speed)
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
            particle_color = (*self.color, alpha)
            
            # Отрисовка круглой частицы
            pygame.draw.circle(particle_surface, particle_color, 
                            (self.size + 1, self.size + 1), self.size)
            screen.blit(particle_surface, (self.x - self.size - 1, self.y - self.size - 1))
    
    # Отрисовка следа
    def _draw_line(self, screen):
        for x, y, size, alpha in self.line:
            if alpha > 0:
                # Расчет размера точки следа
                circle_size = max(0.5, size / 8)
                
                # Создание поверхности с альфа-каналом
                max_surface_size = int(self.base_size * 2 + 2)
                circle_surface = pygame.Surface((max_surface_size, max_surface_size), pygame.SRCALPHA)
                circle_color = (*self.color, int(alpha))
                
                # Отрисовка круглой точки следа
                center_x, center_y = max_surface_size // 2, max_surface_size // 2
                pygame.draw.circle(circle_surface, circle_color, (center_x, center_y), circle_size)
                screen.blit(circle_surface, (x - center_x, y - center_y))

if __name__ == "__main__":
    # Экран
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Частица')
    background = (0, 0, 0)
    clock = pygame.time.Clock()

    # Список всех частиц
    particles = []

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
        
        # Создаем частицы группами для одновременного исчезновения
        if len(particles) == 0 or random.random() < 0.05:
            group_size = random.randint(8, 20)
            group_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            base_x = random.randint(0, width)
            base_y = random.randint(0, height)
            group_lifetime = random.randint(60, 100)
            
            for _ in range(group_size):
                particle = Particle(base_x, base_y, group_color)
                particle.lifetime = group_lifetime
                particle.max_lifetime = group_lifetime
                particles.append(particle)
        
        for particle in particles[:]: # Испольуем копию списка, чтобы безопасно удалять частицы
            particle.update()
            particle.draw(screen)
            
            if not particle.is_alive():
                particles.remove(particle)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()