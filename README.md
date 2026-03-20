# Dell G5 SE (AMD) Fan Control

A lightweight, single-file fan control utility designed specifically for the **Dell G5 SE 5505**. This tool gives you an easy-to-use graphical interface to control your system fans in just two clicks, consuming **0 MB background RAM** when not in use.

## Highlights
- **G-Mode (Full Speed)**: Maximize cooling (100% fan speed) instantly.
- **Medium Speed**: Moderate cooling profile.
- **Auto / Stopped**: Return control back to the laptop's hardware.
- **Zero Overhead**: The app completely exits the moment a profile is selected, freeing up all memory.

## Prerequisites
Because this is built for Linux (Ubuntu/Debian-based), make sure you have python3 and the GTK dependencies installed (they are usually pre-installed on most Ubuntu systems):
```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0
```

## Installation

**1. Clone or Download the repository**
Download this repository to your computer and extract it, or clone it via terminal:
```bash
git clone https://github.com/YOUR_USERNAME/dell-fan-control.git
cd dell-fan-control
```

**2. Make the script executable & Install Sudoers**
The fan controllers in Linux require root access to change hardware states. To prevent the script from asking for your password every time you click a button, run the built-in installer:
```bash
chmod +x dell_fan_control.py
sudo ./dell_fan_control.py install
```
*(This adds a safe, single-file exception to your sudoers list so the fan GUI can run seamlessly).*

**3. Install Desktop Shortcut (Optional)**
If you want to launch it easily from your Application Menu without opening a terminal:
```bash
mkdir -p ~/.local/share/applications/
cp dell-fan-control.desktop ~/.local/share/applications/
```
You can now search for "Dell Fan Control" in your app menu!

## Usage

You can launch the tool from your app menu (if you added the shortcut) or run it directly from terminal:
```bash
./dell_fan_control.py
```

### Advanced (Command Line)
If you prefer terminal commands or want to bind fan speeds to keyboard shortcuts, you can interact with the script directly:
```bash
sudo ./dell_fan_control.py set-fans max     # 100% Speed
sudo ./dell_fan_control.py set-fans med     # ~50% Speed
sudo ./dell_fan_control.py set-fans auto    # Hardware Control
sudo ./dell_fan_control.py set-fans toggle  # Toggles between Auto and Max
```

## Note for other Laptops
This specifically writes to the `dell_smm` hwmon driver (`pwm1` and `pwm3`). It was tested on the Dell G5 SE 5505 but might work on other Dell machines supporting `dell-smm-hwmon`.
