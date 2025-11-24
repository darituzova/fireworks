from game import Game
import json
import os

def load_config(name):
    config_file = name
    
    # Проверяем существование файла
    if not os.path.exists(config_file):
        print(f'Файл {config_file} не найден. Используются значения по умолчанию.')
        return None
    
    try:
        with open(config_file, 'r', encoding='UTF-8') as f:
            config = json.load(f)
        print(f'Конфигурация загружена из {config_file}')
        return config
    except Exception as e:
        print(f'Неожиданная ошибка при чтении {config_file}: {e}')
        print('Используются значения по умолчанию.')
        return None

# Загрузка конфигурации
name = 'config/config_base.json'
config = load_config(name)

# Создание игры с параметрами из конфигурации или значениями по умолчанию
if config:
    game = Game(width=config.get('width', 1000),
                height=config.get('height', 800),
                background=tuple(config.get('background', [0, 0, 0])),
                firework_interval=config.get('firework_interval', 30),
                diagonal=config.get('diagonal', False),
                margin_x=config.get('margin_x', 20),
                fps=config.get('fps', 60),
                config=config)
else:
    # Если конфиг не загружен, используем все значения по умолчанию
    game = Game()

game.run()