# CPU_Monitor

A lightweight, always-on-top CPU monitoring widget built with **PyQt5**, designed for Windows desktops. It displays real-time CPU temperature, usage, power, and frequency using data fetched from **OpenHardwareMonitor**.

![image](https://github.com/user-attachments/assets/a07f3f87-cadf-422b-8215-76f22c6bf505)

## 💡 Features

- 🌡 Real-time CPU Temperature
- ⚙ CPU Load Percentage
- 🔋 Power Consumption (Watts)
- 🧠 CPU Clock Speed (GHz)
- 🎨 Auto Light/Dark theme detection based on Windows settings
- 🪟 Frameless, draggable, always-on-top window
- 🎨 Custom-shaped UI with trapezium decorations
- ❌ Minimize and Close buttons embedded in UI

## 🚀 Requirements

- Python 3.6+
- Windows OS
- [OpenHardwareMonitor](https://openhardwaremonitor.org/) (must be extracted to `C:\OpenHardwareMonitor\`)

## 🛠 Installation

## 1. Clone the repository:
   ```bash
   git clone https://github.com/SudoRV/CPU_Monitor.git
   cd CPU_Monitor

## 2. Install dependencies
   ```bash
   pip install -r requirements.txt

## 3. Ensure OpenHardwareMonitor is installed and placed in:
   ```bash
   C:\OpenHardwareMonitor\OpenHardwareMonitor.exe

## ▶️ Usage
    ```bash
    python cpu_monitor.py

