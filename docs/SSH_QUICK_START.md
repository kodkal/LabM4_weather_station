# 🚀 Quick Start Guide - Weather Station Lab
## SSH Setup and One-Command Installation

---

## Step 1: SSH into Your Raspberry Pi

### Find Your Pi's IP Address
First, you need to find your Raspberry Pi's IP address:

**Option A: If you have a monitor connected:**
```bash
hostname -I
```

**Option B: From another computer on the same network:**
```bash
# On Windows (Command Prompt)
arp -a

# On Mac/Linux
arp -a | grep raspberry
# or
sudo nmap -sn 192.168.1.0/24 | grep -B 2 "Raspberry"
```

### SSH Connection

**From Windows (PowerShell/Terminal):**
```bash
ssh pi@<IP_ADDRESS>
# Example: ssh pi@192.168.1.100
```

**From Mac/Linux:**
```bash
ssh pi@<IP_ADDRESS>
# Example: ssh pi@192.168.1.100
```

**Default Password:** `raspberry` (change it immediately!)

### First Time SSH Setup

If SSH is not enabled on your Pi:

1. **With Monitor/Keyboard:**
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → SSH → Enable
   ```

2. **Headless Setup (no monitor):**
   - Add empty file named `ssh` to boot partition of SD card
   - The Pi will enable SSH on first boot

---

## Step 2: One-Command Installation

Once you're connected via SSH, run this single command to set up everything:

```bash
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/setup/quick_setup.sh | bash
```

**Alternative (if curl fails):**
```bash
wget -qO- https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/setup/quick_setup.sh | bash
```

This command will:
- ✅ Update system packages
- ✅ Install all prerequisites
- ✅ Clone the project repository
- ✅ Set up Python environment
- ✅ Configure hardware interfaces
- ✅ Generate SSL certificates
- ✅ Create secure credentials
- ✅ Configure firewall
- ✅ Run installation tests

**Installation takes about 5-10 minutes.**

---

## Step 3: Start the Weather Station

After installation completes:

```bash
cd ~/LabM4_weather_station
./start_weather_station.sh
```

Or manually:
```bash
cd ~/LabM4_weather_station
source venv/bin/activate
python weather_station.py
```

---

## 🎮 Quick Commands

### Test Without Sensors (Simulation Mode)
```bash
cd ~/LabM4_weather_station
./test_simulation.sh
```

### Run Security Tests
```bash
cd ~/LabM4_weather_station
./test_security.sh
```

### Check Installation
```bash
cd ~/LabM4_weather_station
source venv/bin/activate
python -c "from src.sensor_module import SensorReader; print('✓ Installation OK')"
```

---

## 🔧 Troubleshooting SSH

### "Connection Refused" Error
```bash
# On the Pi (with monitor):
sudo systemctl start ssh
sudo systemctl enable ssh
```

### "Host Key Verification Failed"
```bash
# On your computer:
ssh-keygen -R <IP_ADDRESS>
# Then try SSH again
```

### "Permission Denied"
- Check you're using correct username (usually `pi`)
- Check password (default: `raspberry`)
- Try with sudo: `ssh pi@<IP_ADDRESS> -o PreferredAuthentications=password`

### Can't Find Pi's IP
```bash
# Try these ranges:
ping 192.168.1.1-254
ping 192.168.0.1-254
ping 10.0.0.1-254
```

---

## 🔐 SSH Security (After First Login)

### Change Default Password
```bash
passwd
# Enter current password: raspberry
# Enter new password: [your-secure-password]
```

### Set Up SSH Keys (Recommended)
On your computer:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096

# Copy key to Pi
ssh-copy-id pi@<IP_ADDRESS>

# Now you can SSH without password
ssh pi@<IP_ADDRESS>
```

### Disable Password Login (After Setting Up Keys)
On the Pi:
```bash
sudo nano /etc/ssh/sshd_config
# Change: PasswordAuthentication no
# Save and exit

sudo systemctl restart ssh
```

---

## 📱 SSH from Mobile

### iOS
- App: **Termius** or **Prompt**
- Enter Pi's IP, username: `pi`, password

### Android
- App: **JuiceSSH** or **Termux**
- Add new connection with Pi's details

---

## 👨‍🏫 For Instructors

### Reset for Next Student
```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh soft  # Keeps installation, clears data
```

### Complete Removal
```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh hard  # Removes everything
```

### Setup All Pis at Once
Create a script on your computer:
```bash
#!/bin/bash
# setup_all_pis.sh

PI_IPS="192.168.1.101 192.168.1.102 192.168.1.103"

for IP in $PI_IPS; do
    echo "Setting up Pi at $IP..."
    ssh pi@$IP "curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/setup/quick_setup.sh | bash"
done
```

---

## 🚨 Common Issues & Solutions

### Issue: "No Space Left on Device"
```bash
# Clean up space
sudo apt-get clean
sudo apt-get autoremove
df -h  # Check disk usage
```

### Issue: "Module Not Found" Errors
```bash
# Reinstall requirements
cd ~/LabM4_weather_station
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Hardware Not Detected (But That's OK!)
```bash
# Use simulation mode - no sensors needed!
export SENSOR_SIMULATION=true
python weather_station.py
```

---

## 📋 Installation Verification Checklist

After installation, verify everything works:

```bash
# 1. Check project exists
ls ~/LabM4_weather_station

# 2. Check Python environment
source ~/LabM4_weather_station/venv/bin/activate
python --version  # Should be 3.9+

# 3. Check required packages
pip list | grep -E "flask|jwt|cryptography"

# 4. Check certificates
ls ~/LabM4_weather_station/keys/

# 5. Run simulation test
cd ~/LabM4_weather_station
export SENSOR_SIMULATION=true
python -c "from src.sensor_module import SensorReader; s=SensorReader('SIMULATED'); print(s.read_sensor())"
```

If all checks pass, you're ready to start the lab!

---

## 📚 Next Steps

1. **Read the Student Guide:**
   ```bash
   less ~/LabM4_weather_station/docs/STUDENT_GUIDE.md
   ```

2. **Start Coding:**
   ```bash
   cd ~/LabM4_weather_station/src
   nano weather_station.py
   ```

3. **Test Your Security:**
   ```bash
   python ~/LabM4_weather_station/tests/test_security.py
   ```

---

## 🆘 Get Help

- **Instructor:** [Your contact info]
- **Documentation:** `~/LabM4_weather_station/docs/`
- **Project Issues:** https://github.com/kodkal/LabM4_weather_station/issues

---

**Remember:** You can complete this entire lab in simulation mode - no physical sensors required!

---

*Quick Start Guide v1.0 | Utah Valley University*