import pygame
import random
from firework import Firework

class Game:
    def __init__(self, width=800, height=600, background=(0, 0, 0), firework_interval=30):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Фейерверки')
        self.background = background
        self.clock = pygame.time.Clock()
        
        self.fireworks = []
        # Таймер для фейерверков
        self.firework_timer = 0
        self.firework_interval = firework_interval
        
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Клавища ESC - выход
                    self.running = False
    
    def spawn_random_firework(self):
        new_firework = Firework(random.randint(20, self.width - 20), self.height)
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
            self.clock.tick(60) 
        
        pygame.quit()

if __name__ == "__main__":   
    game = Game()
    game.run()