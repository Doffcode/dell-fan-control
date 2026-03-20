#!/usr/bin/env python3
import gi
import subprocess
import sys
import os
import glob

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# -------------------------------------------------------------------------------------------------
# Backend: Write fan speed directly to hwmon (requires root)
# -------------------------------------------------------------------------------------------------
def set_fans(speed_arg):
    speed = 0
    if speed_arg == "max": speed = 255
    elif speed_arg == "med": speed = 128
    elif speed_arg == "auto" or speed_arg == "off": speed = 0
    elif speed_arg == "toggle":
        # Toggle logic: Auto -> Max -> Med -> Max (simulating the bash logic)
        try:
            with open("/tmp/dell_fan_state", "r") as f:
                state = int(f.read().strip())
        except:
            state = 0
            
        if state == 255: speed = 0      # From Max -> Auto
        elif state == 128: speed = 255  # From Med -> Max
        else: speed = 255               # From Auto -> Max
    else:
        print("Usage: ./dell_fan_control.py set-fans {max|med|auto|toggle}")
        sys.exit(1)

    hwmon_dir = None
    for p in glob.glob("/sys/class/hwmon/hwmon*/name"):
        try:
            with open(p, "r") as f:
                if "dell_smm" in f.read():
                    hwmon_dir = os.path.dirname(p)
                    break
        except Exception:
            pass
            
    if not hwmon_dir or not os.path.exists(os.path.join(hwmon_dir, "pwm1")):
        print("Error: Dell SMM fan controller not found!")
        sys.exit(1)
        
    try:
        with open(os.path.join(hwmon_dir, "pwm1"), "w") as f: f.write(str(speed))
        with open(os.path.join(hwmon_dir, "pwm3"), "w") as f: f.write(str(speed))
        with open("/tmp/dell_fan_state", "w") as f: f.write(str(speed))
        print(f"Fan speed set to {speed}.")
    except PermissionError:
        print("Permission denied. You must run this command via sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    sys.exit(0)


# -------------------------------------------------------------------------------------------------
# Installer: Set passwordless sudo (requires root)
# -------------------------------------------------------------------------------------------------
def install_sudoers():
    if os.geteuid() != 0:
        print("Please run this initial setup with sudo: sudo ./dell_fan_control.py install")
        sys.exit(1)
        
    print("Configuring sudoers to allow running fan control without password...")
    script_path = os.path.abspath(__file__)
    # Add a rule for this specific python script allowing passwordless 'set-fans' execution
    rule = f"ALL ALL=(ALL) NOPASSWD: {script_path} set-fans *\n"
    
    with open("/etc/sudoers.d/dell_fans", "w") as f:
        f.write(rule)
        
    os.chmod("/etc/sudoers.d/dell_fans", 0o440)
    print("Installation complete! You can now run the GUI without sudo password prompts.")
    sys.exit(0)


# -------------------------------------------------------------------------------------------------
# GUI: Lightweight GTK Frontend
# -------------------------------------------------------------------------------------------------
class FanControlWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Dell G5 Fan Control")
        self.set_border_width(15)
        self.set_default_size(250, 150)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        
        # Disable resize to keep it compact
        self.set_resizable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        lbl = Gtk.Label(label="Control System Fans")
        lbl.set_markup("<b>Control System Fans</b>")
        vbox.pack_start(lbl, False, False, 5)

        # Full Speed Button
        btn_max = Gtk.Button(label="🚀 G-Mode (Full Speed)")
        btn_max.get_style_context().add_class("suggested-action")
        btn_max.connect("clicked", self.set_fan_and_exit, "max")
        vbox.pack_start(btn_max, True, True, 0)

        # Med Speed Button
        btn_med = Gtk.Button(label="🔥 Medium Speed")
        btn_med.connect("clicked", self.set_fan_and_exit, "med")
        vbox.pack_start(btn_med, True, True, 0)

        # Auto Button
        btn_auto = Gtk.Button(label="❄️ Auto / Stopped")
        btn_auto.connect("clicked", self.set_fan_and_exit, "auto")
        vbox.pack_start(btn_auto, True, True, 0)

    def set_fan_and_exit(self, widget, speed):
        script_path = os.path.abspath(__file__)
        try:
            # We call ourselves via sudo with the "set-fans" argument.
            # Thanks to our install.sh logic, this should NOT prompt for password.
            subprocess.run(["sudo", "-n", script_path, "set-fans", speed], check=True)
            print(f"Successfully applied profile: {speed}")
        except subprocess.CalledProcessError:
            # If 'sudo -n' fails, it means passwordless sudo isn't set. We fallback to pkexec to prompt gracefully.
            try:
                subprocess.run(["pkexec", script_path, "set-fans", speed], check=True)
                print(f"Successfully applied profile: {speed}")
            except Exception as e:
                print(f"Error applying profile: {e}")
        except Exception as e:
            print(f"Error applying profile: {e}")
            
        # Exit immediately to keep background RAM at 0 when not actively making a choice!
        Gtk.main_quit()

if __name__ == '__main__':
    # CLI Router
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_sudoers()
        elif sys.argv[1] == "set-fans" and len(sys.argv) == 3:
            set_fans(sys.argv[2])
        else:
            print("Usage: ")
            print("  GUI view : ./dell_fan_control.py")
            print("  Install  : sudo ./dell_fan_control.py install")
            print("  CLI set  : sudo ./dell_fan_control.py set-fans {max|med|auto|toggle}")
            sys.exit(1)
    else:
        # Launch GUI if no arguments are provided
        win = FanControlWindow()
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        Gtk.main()
