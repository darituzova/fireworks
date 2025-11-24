import pygame
import random
from firework import Firework

# Класс - Игрв
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

if __name__ == "__main__":   
    game = Game()
    game.run()