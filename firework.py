import pygame
import random
from particle import Particle

# Класс - фейерверк
class Firework:
    # Инициализация
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        self.particles = [] # Список частиц (объектов класса Particle)
        self.line = [] # Список для линии взрыва
        self.speed_y = random.uniform(-7, -2) # Скорость отрицательная, так как по коордиантам идем вверх
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.exploded = False # Флаг на взрыв
        self.explosion_height = random.randint(50, pygame.display.get_surface().get_height() - 50) # Рандомная точка взрыва
        self.size_line = random.randint(1, 2)
    
    # Обновление позиций линии фейерверка или его частиц
    def update(self):
        if not self.exploded: # Если еще не было взрыва
            self.line.append((self.x, self.y)) # Максимум точек в следе 10
            if len(self.line) > 10:
                self.line.pop(0)
            
            self.y += self.speed_y
            if self.y < self.explosion_height: # Знак <, так как работаем в координтной плоскости
                self.explode()
        
        else: # Произошел взрыв
            for particle in self.particles[:]: # Испольуем копию списка, чтобы безопасно удалять частицы
                particle.update()
                if not particle.is_alive():
                    self.particles.remove(particle) 
    
    # Взрыв
    def explode(self):
        self.exploded = True
        
        number_particles = random.randint(100, 200)
        for _ in range(number_particles):
            self.particles.append(Particle(self.x, self.y, self.color))
    
    # Проверка на то, что или фейерверк еще не взорвался или он пока взрывется и его частицы живы
    def is_alive(self):
        return not self.exploded or len(self.particles) > 0
    
    # Отрисовка линии фейерверка или частиц через класс
    def draw(self, screen):
        if not self.exploded: # Если еще не было взрыва
            # Рисуем линию из точек следа
            if len(self.line) > 1:
                for i in range(len(self.line) - 1):
                    start_pos = (self.line[i][0], self.line[i][1])
                    end_pos = (self.line[i + 1][0], self.line[i + 1][1])
                    pygame.draw.line(screen, self.color, start_pos, end_pos, self.size_line)
            
        else: # Произошел взрыв
            for particle in self.particles:
                particle.draw(screen)   
        
# Экран
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Фейерверк')
background = (0, 0, 0)
clock = pygame.time.Clock()

# Создаем один фейерверк
firework = Firework(random.randint(20, height - 20), height)

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
    
    if firework.is_alive():
        firework.update()
        firework.draw(screen)
    else:
        firework = Firework(random.randint(20, height - 20),  height )
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()