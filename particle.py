import pygame
import random

# Класс - частица фейерверка
class Particle:
    # Инициализация
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color # От фейерверка зависит
        
        # У следующих атрибутов рандомные значения
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-5, 2)
        self.size = random.randint(1, 4)
        self.lifetime = random.randint(30, 90)
    
    # Обновление местоположения частицы и ее времени жизни
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.1 # 0.1 - гравиция (пока предположительная)
        self.lifetime -= 1
    
    # Проверка на время жизни частицы
    def is_alive(self):
        return self.lifetime > 0
    
    # Отрисовка частицы
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

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
        
        new_particle = Particle(random.randint(0, width), random.randint(0, height), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        particles.append(new_particle)
        
        for particle in particles[:]: # Испольуем копию списка, чтобы безопасно удалять частицы
            particle.update()
            particle.draw(screen)
            
            if not particle.is_alive():
                particles.remove(particle)
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()