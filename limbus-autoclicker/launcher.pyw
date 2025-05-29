import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
import keyboard
import pyautogui
import time

# Автокликер (встроенный прямо в лаунчер)
class Autoclicker:
    def __init__(self, log_callback):
        self.is_running = False
        self.log = log_callback
        self.timer = QTimer()
        self.timer.timeout.connect(self.click_loop)

    def start(self):
        if self.is_running:
            self.log("Autoclicker уже запущен!")
            return
        
        self.is_running = True
        self.timer.start(100)  # Интервал 100 мс
        self.log("Autoclicker запущен. Нажмите F8 для остановки.")

    def stop(self):
        self.is_running = False
        self.timer.stop()
        self.log("Autoclicker остановлен.")

    def click_loop(self):
        if keyboard.is_pressed('f8'):  # Остановка по F8
            self.stop()
            return
        
        pyautogui.click()  # Левый клик
        time.sleep(0.1)    # Задержка между кликами

# Основное окно лаунчера
class LimbusLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limbus Autoclicker Launcher")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon("icon.ico"))  # Можно заменить на свой иконку
        
        self.autoclicker = Autoclicker(self.log)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Готов")
        layout.addWidget(self.status_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.start_btn = QPushButton("Start Autoclicker")
        self.start_btn.clicked.connect(self.start_autoclicker)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Autoclicker")
        self.stop_btn.clicked.connect(self.stop_autoclicker)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Горячая клавиша F7 для старта
        keyboard.add_hotkey('f7', self.start_autoclicker)

    def start_autoclicker(self):
        try:
            self.autoclicker.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Работает")
        except Exception as e:
            self.log(f"Ошибка: {str(e)}", error=True)

    def stop_autoclicker(self):
        self.autoclicker.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Готов")

    def log(self, message, error=False):
        color = "red" if error else "black"
        self.log_output.append(f'<span style="color:{color}">{message}</span>')

    def closeEvent(self, event):
        self.autoclicker.stop()
        event.accept()

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        launcher = LimbusLauncher()
        launcher.show()
        
        # Проверка зависимостей
        try:
            import keyboard
            import pyautogui
        except ImportError:
            QMessageBox.critical(None, "Ошибка", 
                               "Установите зависимости:\npip install keyboard pyautogui PyQt5")
            sys.exit(1)
            
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        input("Нажмите Enter для выхода...")
