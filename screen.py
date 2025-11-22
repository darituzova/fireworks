import pygame

# Экран
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Частица')
background = (0, 0, 0)
clock = pygame.time.Clock()

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
    
    
    