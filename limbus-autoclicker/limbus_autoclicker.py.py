import pyautogui
import keyboard
import time
import os
import io 
import sys
import psutil
from PIL import Image, ImageOps
from threading import Thread
import logging
import win32gui
import win32con

# settings)) ny a cho? 
DEBUG_MODE = True
CLICK_DELAY = 0.01
SCAN_INTERVAL = 0.05
CONFIDENCE = 0.5
RETRIES = 2
GAME_WINDOW_TITLE = "LimbusCompany"
MAX_IMAGE_WIDTH = 200  # Максимальная ширина изображений кнопок
USE_WIN32_API = True

# ======== UTF - 8 ЧТОБЫ РАБОТАЛ ЛАУНЧЕР) ========

# установка UTF-8 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# логированияе с UTF-8
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
handler.encoding = 'utf-8'
logging.basicConfig(handlers=[handler], level=logging.DEBUG)
# ======== UTF - 8 ЧТОБЫ РАБОТАЛ ЛАУНЧЕР) ========

# == тут будет попытка эмуляции виндовс апи / on there I wanna try get emulation windows API. THIS NOT WORKING, SORRY, MATE == 
if sys.platform == 'win32' and USE_WIN32_API:
    try:
        import win32gui
        import win32api
        import win32con
    except ImportError:
        logging.warning("Win32 API недоступен. Установите pywin32: pip install pywin32")
        USE_WIN32_API = False

def send_win32_click(self, hwnd, x, y):
    """Улучшенный клик через Windows API"""
    try:
        # Конвертируем координаты в клиентские координаты окна
        rect = win32gui.GetWindowRect(hwnd)
        client_x = x - rect[0]
        client_y = y - rect[1]
        
        # Отправляем сообщения о клике
        lparam = win32api.MAKELONG(client_x, client_y)
        
        # Последовательность событий для более реалистичного клика
        win32gui.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        time.sleep(0.05)  # Короткая пауза между нажатием и отпусканием
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
        
        return True
    except Exception as e:
        self.log(f"Win32 API клик не сработал: {e}", level=logging.ERROR)
        return False
# == тут будет попытка эмуляции виндовс апи / on there I wanna try get emulation windows API. THIS NOT WORKING, SORRY, MATE == 


class LimbusAutoClicker:
    def __init__(self):
        self.is_running = False
        self.stop_flag = False
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.game_window_rect = None
        self.is_windows = sys.platform == 'win32'
        self.setup_logging()
        
        # Инициализация Windows API
        if self.is_windows:
            try:
                import win32gui
                self.win32gui = win32gui
            except ImportError:
                self.log("Для Windows требуется pywin32! Установите: pip install pywin32", level=logging.WARNING)
                self.is_windows = False
        
        # Загрузка и оптимизация изображений
        self.winrate_img = self.load_optimized_image("winrate_button.png")
        self.chainstart_img = self.load_optimized_image("chainstart_button.png")
        
        if not all([self.winrate_img, self.chainstart_img]):
            self.log("Ошибка: Не найдены необходимые изображения кнопок!", level=logging.ERROR)
            exit(1)

    def setup_logging(self):
        """u know this"""
        logging.basicConfig(
            level=logging.DEBUG if DEBUG_MODE else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.script_dir, 'autoclicker.log')),
                logging.StreamHandler()
            ]
        )
    
    def log(self, message, level=logging.INFO):
        """JUST LOG))))"""
        logging.log(level, message)

    def load_optimized_image(self, filename):
        """LOAD AND OPTIMIZED IMAGE"""
        path = os.path.join(self.script_dir, filename)
        if not os.path.exists(path):
            self.log(f"Файл не найден: {filename}", level=logging.ERROR)
            return None
            
        try:
            img = Image.open(path)
            
            if 'icc_profile' in img.info:
                del img.info['icc_profile']
            
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (0, 0, 0))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            if img.width > MAX_IMAGE_WIDTH:
                ratio = MAX_IMAGE_WIDTH / float(img.width)
                new_height = int(float(img.height) * ratio)
                img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.LANCZOS)
            
            optimized_path = path.replace('.png', '_optimized.png')
            img.save(optimized_path, quality=95, optimize=True)
            
            self.log(f"Оптимизировано {filename}: {img.size[0]}x{img.size[1]}", level=logging.DEBUG)
            
            return {
                'path': optimized_path,
                'width': img.width,
                'height': img.height,
                'original_path': path
            }
        except Exception as e:
            self.log(f"Ошибка обработки {filename}: {e}", level=logging.ERROR)
            return None

    def get_game_window_rect(self):
        """rect game"""
        try:
            if self.is_windows:
                hwnd = self.win32gui.FindWindow(None, GAME_WINDOW_TITLE)
                if hwnd:
                    client_rect = self.win32gui.GetClientRect(hwnd)
                    client_left, client_top, client_right, client_bottom = client_rect
                    
                    point_left_top = self.win32gui.ClientToScreen(hwnd, (client_left, client_top))
                    point_right_bottom = self.win32gui.ClientToScreen(hwnd, (client_right, client_bottom))
                    
                    width = point_right_bottom[0] - point_left_top[0]
                    height = point_right_bottom[1] - point_left_top[1]
                    
                    if width > 100 and height > 100:
                        return (*point_left_top, width, height)
            
            screen_width, screen_height = pyautogui.size()
            return (0, 0, max(screen_width, 100), max(screen_height, 100))
        except Exception as e:
            self.log(f"Ошибка получения размеров окна: {e}", level=logging.DEBUG)
            return (0, 0, *pyautogui.size())

    def is_game_window_active(self):
        """game window activity"""
        try:
            if self.is_windows:
                active_window = self.win32gui.GetWindowText(self.win32gui.GetForegroundWindow())
                if GAME_WINDOW_TITLE not in active_window:
                    return False
            
            self.game_window_rect = self.get_game_window_rect()
            return True
        except Exception as e:
            self.log(f"Ошибка проверки окна: {e}", level=logging.DEBUG)
            return False

    def validate_search_area(self, img_data, region):
        """check validate picture area"""
        if not img_data or not region:
            self.log("Нет данных изображения или региона поиска", level=logging.DEBUG)
            return False
            
        img_w, img_h = img_data['width'], img_data['height']
        region_w, region_h = region[2], region[3]
        
        if region_w <= 10 or region_h <= 10:
            self.log(f"Регион поиска слишком мал: {region_w}x{region_h}", level=logging.DEBUG)
            return False
        
        if img_w > region_w or img_h > region_h:
            self.log(f"Изображение {img_w}x{img_h} слишком большое для региона {region_w}x{region_h}", level=logging.DEBUG)
            try:
                scale_factor = min(region_w/img_w, region_h/img_h)
                new_width = int(img_w * scale_factor * 0.9)
                new_height = int(img_h * scale_factor * 0.9)
                self.dynamically_resize_image(img_data, new_width, new_height)
                return True
            except Exception as e:
                self.log(f"Ошибка масштабирования: {e}", level=logging.DEBUG)
                return False
        return True

    def dynamically_resize_image(self, img_data, new_width, new_height):
        """change resize"""
        original_path = img_data['original_path']
        
        try:
            img = Image.open(original_path)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (0, 0, 0))
                background.paste(img, mask=img.split()[3])
                img = background
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            optimized_path = img_data['path']
            img.save(optimized_path, quality=95, optimize=True)
            
            img_data['width'] = new_width
            img_data['height'] = new_height
            
            self.log(f"Изображение масштабировано до {new_width}x{new_height}", level=logging.DEBUG)
        except Exception as e:
            self.log(f"Ошибка динамического масштабирования: {e}", level=logging.ERROR)
            raise

    def find_button_center(self, img_data):
        if not img_data or not self.is_game_window_active() or not self.game_window_rect:
            return None
            
        left, top, width, height = self.game_window_rect
        region = (left, top, width, height)
        
        if not self.validate_search_area(img_data, region):
            return None

        for _ in range(RETRIES):
            try:
                location = pyautogui.locateOnScreen(
                    img_data['path'],
                    confidence=CONFIDENCE,
                    grayscale=True,
                    region=region
                )
                if location:
                    center_x = location.left + location.width // 2
                    center_y = location.top + location.height // 2
                    return (center_x, center_y)
            except pyautogui.ImageNotFoundException:
                self.log(f"Изображение не найдено: {os.path.basename(img_data['path'])}", level=logging.DEBUG)
            except Exception as e:
                self.log(f"Ошибка при поиске кнопки: {e}", level=logging.DEBUG)
            time.sleep(0.5)
        return None

    def click_button(self, img_data):
        """click on button. First trying PyAutoGUI, after Win32 API """
        button_center = self.find_button_center(img_data)
        if not button_center:
            return False

        x, y = button_center
            
        # 1. if Limbus active trying default click (meh,... not working)
        try:
            pyautogui.moveTo(x, y, duration=0)
            pyautogui.click()
            self.log(f"Обычный клик: {x}, {y}", level=logging.DEBUG)
            return True
        except Exception as e:
            self.log(f"Ошибка обычного клика: {e}", level=logging.DEBUG)
        
        # 2. if not working and Win32 API turn onn, trying win 32
        if USE_WIN32_API and self.is_windows:
            hwnd = win32gui.FindWindow(None, GAME_WINDOW_TITLE)
            if hwnd:
                # Recalculation of coordinates relative to the window
                left, top = win32gui.ClientToScreen(hwnd, (0, 0))
                rel_x = x - left
                rel_y = y - top
                
                if send_win32_click(hwnd, rel_x, rel_y):
                    self.log(f"Win32 API клик: {rel_x}, {rel_y}", level=logging.DEBUG)
                    return True
        
        return False

    def auto_battle(self):
        """сам цикл автобоя"""
        self.log("Автобой запущен! Для остановки нажмите F8", level=logging.INFO)
        self.log("Автобой запущен (Win32 API + Ускоренный режим)!", level=logging.INFO)
                
        while not self.stop_flag:
            if not self.is_game_window_active():
                time.sleep(0.5)
                continue
            
            # Быстрые клики без лишних задержек
            self.click_button(self.winrate_img)
            self.click_button(self.chainstart_img)
            time.sleep(SCAN_INTERVAL)

        
        while not self.stop_flag:
            if not self.is_game_window_active():
                self.log("Окно игры не активно, ожидание...", level=logging.DEBUG)
                time.sleep(1)
                continue
            
                 # Клик по Win Rate
            if self.click_button(self.winrate_img):
                self.log("Win Rate clicked!", level=logging.DEBUG)
                time.sleep(CLICK_DELAY)
            
                # Клик по Chain Start
            if self.click_button(self.chainstart_img):
                self.log("Chain Start clicked!", level=logging.DEBUG)
                time.sleep(CLICK_DELAY)
                
            time.sleep(SCAN_INTERVAL)
                
        self.log("Автобой остановлен", level=logging.INFO)

    def toggle_script(self):
        if self.is_running:
            self.stop_flag = True
            self.is_running = False
            self.log("Остановка...", level=logging.INFO)
        else:
            self.is_running = True
            self.stop_flag = False
            Thread(target=self.auto_battle, daemon=True).start()
            self.log("Запуск...", level=logging.INFO)

 #   if not any("limbuscompany" in p.name().lower() for p in psutil.process_iter()): exit()  # дабы работало в ЛИМБЕ КОМПАНЕ)) 

if __name__ == "__main__":
    print("""
    Limbus Company Autoclicker
    ========================
    Управление:
    - F8: Включить/выключить автокликер
    - Esc: Выйти из программы
    
    Требования:
    1. Файлы winrate_button.png и chainstart_button.png в той же папке
    2. Игра в оконном режиме
    3. Установите зависимости:
       pip install pillow pyautogui keyboard
       Для Windows: pip install pywin32
    """)
    
    clicker = LimbusAutoClicker()
    keyboard.add_hotkey('F8', clicker.toggle_script)
    keyboard.wait('esc')