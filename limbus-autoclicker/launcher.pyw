import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, Qt

class LimbusLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limbus Autobot Launcher")
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon("icon.ico"))  # Замените на свой .ico файл
        
        self.process = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.start_btn = QPushButton("Start Autobot (F7)")
        self.start_btn.clicked.connect(self.start_script)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Autobot (F8)")
        self.stop_btn.clicked.connect(self.stop_script)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start_script(self):
        if self.process and self.process.state() == QProcess.Running:
            self.log("Autobot is already running!")
            return
            
        script_path = os.path.join(os.path.dirname(__file__), "limbus_autoclicker.py")
        if not os.path.exists(script_path):
            self.log(f"ERROR: File 'limbus_autoclicker.py' not found in:\n{script_path}", error=True)
            QMessageBox.critical(self, "Error", f"File 'limbus_autoclicker.py' not found!")
            return
            
        try:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_output)
            self.process.readyReadStandardError.connect(self.handle_error)
            self.process.finished.connect(self.script_finished)
            
            # Для Windows используем 'python', для Linux/Mac - 'python3'
            python_cmd = "python3" if sys.platform != "win32" else "python"
            self.process.start(python_cmd, [script_path])
            
            if not self.process.waitForStarted(3000):
                self.log("Failed to start script!", error=True)
                return
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Running")
            self.log("Autobot started successfully! Press F8 to stop.")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}", error=True)
            QMessageBox.critical(self, "Error", f"Failed to start: {str(e)}")

    def stop_script(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
            self.log("Autobot stopped by user")
        
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

if __name__ == "__main__":
    # Проверка зависимостей перед запуском
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        print("ERROR: Install PyQt5 first:\npip install PyQt5")
        input("Press Enter to exit...")
        sys.exit(1)

    app = QApplication(sys.argv)
    launcher = LimbusLauncher()
    launcher.show()
    sys.exit(app.exec_())
