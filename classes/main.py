from game import Game
import json

# Загружает конфигурацию из JSON файла
def load_config(name):
    try:
        # Попытка открыть и прочитать конфигурационный файл
        with open(name, 'r', encoding='UTF-8') as f:
            config = json.load(f)
        print(f'Конфигурация загружена из {name}')
        return config
    except FileNotFoundError:
        # Обработка случая, когда файл не найден
        print(f'Файл {name} не найден. Используются значения по умолчанию.')
        return None
    except Exception as e:
        # Обработка всех других ошибок (невалидный JSON, и т.д.)
        print(f'Ошибка при чтении {name}: {e}')
        print('Используются значения по умолчанию.')
        return None

# Загрузка конфигурации из файла
config = load_config('config/config_base.json')

# Создание экземпляра игры с параметрами из конфигурации или значениями по умолчанию
if config:
    # Если конфигурация загружена, используем значения из нее (учитываем, что может не оказаться ключа в json)
    game = Game(width=config.get('width', 1000),
                height=config.get('height', 800),
                background=tuple(config.get('background', [0, 0, 0])),
                firework_interval=config.get('firework_interval', 30),
                diagonal=config.get('diagonal', False),
                margin_x=config.get('margin_x', 20),
                fps=config.get('fps', 60),
                config=config)
else:
    # Если конфигурация не загружена, используем все значения по умолчанию
    game = Game()

# Запуск основного цикла игры
game.run()