import pygame
import random
from firework import Firework

class Game:
    def __init__(self, width=1000, height=800, caption='Фейерверки', background=(0, 0, 0), firework_interval=30, diagonal=False, margin_x=20, fps=60, config=None):
        if config is None:
            config = {}  
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(caption)
        self.background = background
        self.clock = pygame.time.Clock()
        
        self.fireworks = []
        # Таймер для фейерверков
        self.firework_timer = 0
        self.firework_interval = firework_interval
        self.diagonal = diagonal  # Флаг для диагональных фейерверков
        
        self.running = True
        
        self.margin_x = margin_x
        self.fps = fps
        self.config = config
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Клавища ESC - выход
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # Добавляем обработку клика мыши
                if event.button == 1:  # Левая кнопка мыши
                    self.create_firework_at_pos(event.pos)
    
    def create_firework_at_pos(self, pos):
        # Создаем фейерверк в позиции клика
        x, y = pos
        new_firework = Firework(x, y, self.diagonal, self.config)
        self.fireworks.append(new_firework)
    
    def spawn_random_firework(self):
        # Если diagonal=True, создаем диагональные фейерверки, иначе вертикальные
        new_firework = Firework(
            random.randint(self.margin_x, self.width - self.margin_x), 
            self.height, 
            self.diagonal, 
            self.config)
        self.fireworks.append(new_firework)
    
    def update(self):
        self.firework_timer += 1
        if self.firework_timer >= self.firework_interval:
            self.spawn_random_firework()
            self.firework_timer = 0
        
        for firework in self.fireworks[:]: # Испольуем копию списка, чтобы безопасно удалять фейерверки
            firework.update()
            
            if not firework.is_alive():
                    self.fireworks.remove(firework)
    
    def draw(self):
        self.screen.fill((self.background))
        
        for firework in self.fireworks:
            firework.draw(self.screen)
            
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps) 
        
        pygame.quit()

if __name__ == "__main__":   
    game = Game()
    game.run()