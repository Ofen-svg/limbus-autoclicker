import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, Qt

# Установка UTF-8 для корректного вывода в консоли Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

class LimbusLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limbus Autobot Start F8")
        self.setGeometry(100, 100, 500, 400)
        
        self.process = None
        self.tray_icon = None
        
        self.init_ui()
        self.init_tray()
    
    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        btn_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("Start Autobot")
        self.start_btn.clicked.connect(self.start_script)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Autobot")
        self.stop_btn.clicked.connect(self.stop_script)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("system-run"))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.start_script)
        tray_menu.addAction(start_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_script)
        tray_menu.addAction(stop_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def start_script(self):
        if self.process and self.process.state() == QProcess.Running:
            self.log("Autobot is already running!")
            return
            
        script_path = os.path.join(os.path.dirname(__file__), "limbus_autoclicker.py")
        if not os.path.exists(script_path):
            self.log(f"Error: Script not found at {script_path}")
            return
            
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.script_finished)
        
        # Запуск скрипта
        self.process.start("python", [script_path])
        
        if not self.process.waitForStarted(3000):
            self.log("Failed to start the script!")
            return
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.log("Autobot started successfully!")
        
        if self.tray_icon:
            self.tray_icon.showMessage("Limbus Autobot", "Script started", QSystemTrayIcon.Information, 2000)
    
    def stop_script(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
            self.log("Autobot stopped")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Ready")
    
    def handle_output(self):
        data = self.process.readAllStandardOutput()
        text = data.data().decode("utf-8", errors="replace").strip()
        if text:
            self.log(text)
    
    def handle_error(self):
        data = self.process.readAllStandardError()
        text = data.data().decode("utf-8", errors="replace").strip()
        if text:
            self.log(f"ERROR: {text}", error=True)
    
    def script_finished(self, exit_code, exit_status):
        self.log(f"Script finished with code {exit_code}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Ready")
    
    def log(self, message, error=False):
        color = "red" if error else "black"
        self.log_output.append(f'<span style="color:{color}">{message}</span>')
    
    def closeEvent(self, event):
        if self.tray_icon and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Limbus Autobot", 
                "The app is running in the tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    launcher = LimbusLauncher()
    launcher.show()
    sys.exit(app.exec_())