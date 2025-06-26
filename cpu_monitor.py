import sys
import subprocess
import time
import wmi
import winreg
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QPoint, QTimer

OHM_EXE_PATH = r"C:\OpenHardwareMonitor\OpenHardwareMonitor.exe"
OHM_NAMESPACE = "root\\OpenHardwareMonitor"

def detect_windows_theme():
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if value == 1 else "dark"
    except:
        return "dark"

def launch_ohm():
    try:
        tasks = subprocess.check_output('tasklist').decode()
        if "OpenHardwareMonitor.exe" in tasks:
            return
        subprocess.run([
            "powershell",
            "-Command",
            f'Start-Process \\"{OHM_EXE_PATH}\\" -WindowStyle Minimized -Verb runAs'
        ])
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] Failed to launch OHM: {e}")

class CustomCPUMonitorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini CPU Monitor")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 110)

        # Theme
        self.theme = detect_windows_theme()
        if self.theme == "dark":
            self.bg_color = QColor(255, 255, 255, 220)
            self.info_color = QColor(230, 230, 230, 200)
            self.text_color = "black"
        else:
            self.bg_color = QColor(40, 40, 40, 185)
            self.info_color = QColor(70, 70, 70, 185)
            self.text_color = "white"

        # Title
        self.cpu_label = QLabel("CPU", self)
        self.cpu_label.setGeometry(110, 5, 80, 25)
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.cpu_label.setStyleSheet("color: rgb(19,132,242); background-color: transparent;")

        # Info labels
        self.temp_label = QLabel("--°C", self)
        self.load_label = QLabel("--%", self)
        self.power_label = QLabel("--W", self)
        self.freq_label = QLabel("-- GHz", self)

        label_style = f"color: {self.text_color}; font: 10pt 'Segoe UI'; font-weight: bold; background-color: transparent;"
        for label in [self.temp_label, self.load_label, self.power_label, self.freq_label]:
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignCenter)

        self.temp_label.setGeometry(25, 42, 60, 25)
        self.load_label.setGeometry(115, 42, 60, 25)
        self.power_label.setGeometry(205, 42, 60, 25)
        self.freq_label.setGeometry(105, 78, 80, 18)

        # Minimize button
        self.min_btn = QPushButton("—", self)
        self.min_btn.setGeometry(245, 13, 18, 18)
        self.min_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(100,100,100,200);
                font-size: 6pt;
                border: none;
                border-radius: 2px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                background-color: rgba(200,200,200,100);
                border-radius: 2px;
            }
        """)
        self.min_btn.clicked.connect(self.showMinimized)

        # Close button
        self.close_btn = QPushButton("×", self)
        self.close_btn.setGeometry(267, 13, 18, 18)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: red;
                background-color: rgba(100,100,100,200);
                font-size:11pt;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255,0,0,60);
                border-radius: 2px;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        # WMI init
        try:
            self.w = wmi.WMI(namespace=OHM_NAMESPACE)
        except Exception as e:
            print("[ERROR] WMI init failed:", e)
            self.w = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(3000)
        self.update_info()

        self.old_pos = self.pos()

    def update_info(self):
        if not self.w:
            return

        try:
            sensors = self.w.Sensor()
            cpu_temps = []
            cpu_load = "--"
            cpu_power = "--"
            cpu_clock = "--"

            for s in sensors:
                if s.SensorType == 'Temperature' and 'CPU Core' in s.Name:
                    cpu_temps.append(s.Value)
                elif s.SensorType == 'Load' and 'CPU Total' in s.Name:
                    cpu_load = f"{s.Value:.0f}"
                elif s.SensorType == 'Power' and 'CPU Package' in s.Name:
                    cpu_power = f"{s.Value:.0f}"
                elif s.SensorType == 'Clock' and 'CPU Core #1' in s.Name:
                    cpu_clock = f"{s.Value/1000:.2f}"

            avg_temp = f"{(sum(cpu_temps)/len(cpu_temps)):.0f}" if cpu_temps else "--"

            self.temp_label.setText(f"🌡 {avg_temp}°C")
            self.load_label.setText(f"⚙ {cpu_load}%")
            self.power_label.setText(f"🔋 {cpu_power}W")
            self.freq_label.setText(f"🧠 {cpu_clock} GHz")

        except Exception as e:
            self.temp_label.setText("ERR")
            self.load_label.setText("--")
            self.power_label.setText("--")
            self.freq_label.setText("-- GHz")
            print(f"[ERROR] {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # Top center trapezium
        painter.setBrush(self.bg_color)
        path = QPainterPath()
        path.moveTo(66.5, 10)
        path.lineTo(233.5, 10)
        path.lineTo(218, 26)
        path.lineTo(82, 26)
        path.closeSubpath()
        painter.drawPath(path)

        # Top left trapezium
        path_left = QPainterPath()

        # top border
        painter.setPen(QPen(QColor(QColor(19,132,242)), 2))  # Border color and thickness
        painter.drawLine(QPoint(10, 10), QPoint(60, 10))  # top line of trapezium

        path_left.moveTo(10, 10)
        path_left.lineTo(60.5, 10)

        # top border end
        painter.setPen(Qt.NoPen)

        path_left.lineTo(80, 30)
        path_left.lineTo(10, 30)
        path_left.closeSubpath()
        painter.drawPath(path_left)

        # Top right trapezium
        path_right = QPainterPath()

        # top border
        painter.setPen(QPen(QColor(QColor(19,132,242)), 2))  # Border color and thickness
        painter.drawLine(QPoint(239, 10), QPoint(290, 10))  # top line of trapezium

        path_right.moveTo(239.5, 10)
        path_right.lineTo(290, 10)

        # top border end
        painter.setPen(Qt.NoPen)
        
        path_right.lineTo(290, 30)
        path_right.lineTo(220, 30)
        path_right.closeSubpath()
        painter.drawPath(path_right)

        # Main body
        painter.setBrush(self.bg_color)
        body_path = QPainterPath()
        body_path.addRoundedRect(10, 30, 280, 50, 0, 0)
        painter.drawPath(body_path)

        # Bottom trapezium
        trap_path = QPainterPath()
        trap_path.moveTo(80, 80)
        trap_path.lineTo(210, 80)

        # top border
        painter.setPen(QPen(QColor(QColor(19,132,242)), 2))  # Border color and thickness
        painter.drawLine(QPoint(185, 100), QPoint(110, 100))  # top line of trapezium

        trap_path.lineTo(185, 100)
        trap_path.lineTo(110, 100)

        # top border end
        painter.setPen(Qt.NoPen)

        trap_path.closeSubpath()
        painter.drawPath(trap_path)

        # Info boxes
        painter.setBrush(self.info_color)
        for i in range(3):
            x = 20 + i * 90
            painter.drawRoundedRect(x, 40, 70, 30, 6, 6)

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()


if __name__ == "__main__":
    launch_ohm()
    app = QApplication(sys.argv)
    window = CustomCPUMonitorUI()
    window.show()
    sys.exit(app.exec_())
