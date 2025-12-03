# 🚀 Setup & Management Guide
## Quick Setup, Reset, and Management Tools

---

## For Students: One-Line Setup

### The Fastest Way to Start

SSH into your Raspberry Pi and run:

```bash
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```

That's it! This will:
- ✅ Clone the repository
- ✅ Install all dependencies  
- ✅ Configure the environment
- ✅ Set up security certificates
- ✅ Create all necessary directories
- ✅ Run tests to verify installation

### After Installation

1. **Personalize your setup:**
```bash
cd ~/LabM4_weather_station
./setup/student_onboard.sh
```

2. **Start the weather station:**
```bash
./start_weather_station.sh
```

3. **Test without sensors:**
```bash
./test_simulation.sh
```

---

## For Instructors: Lab Management

### Initial Setup for All Raspberry Pis

#### Option 1: Setup Multiple Pis Simultaneously
Create this script on your computer:

```bash
#!/bin/bash
# setup_all_pis.sh

# List your Pi IP addresses
PI_IPS="192.168.1.101 192.168.1.102 192.168.1.103 192.168.1.104"
PASSWORD="raspberry"  # Default password

for IP in $PI_IPS; do
    echo "Setting up Pi at $IP..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no pi@$IP \
        "curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash"
done

echo "All Pis configured!"
```

#### Option 2: Use Ansible (Advanced)
```yaml
# setup_weather_stations.yml
- hosts: all_pis
  become: yes
  tasks:
    - name: Install Weather Station Lab
      shell: curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
      become_user: pi
```

### Reset Between Students

#### Soft Reset (Recommended - Keeps Installation)
Clears student data while preserving the installation:

```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh soft
```

Or directly:
```bash
./reset_lab.sh soft --backup  # Creates backup first
```

This will:
- Clear all logs
- Remove student data
- Reset databases
- Generate new credentials
- Reset Git repository
- Keep the installation intact

#### Hard Reset (Complete Removal)
Completely removes everything:

```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh hard
```

**Warning:** This deletes the entire project!

#### Quick Clean (Between Classes)
Just clean temporary files:

```bash
./reset_lab.sh clean
```

### Interactive Reset Menu
For a user-friendly interface:

```bash
cd ~/LabM4_weather_station/setup
./reset_lab.sh
```

Shows menu with options:
1. Soft Reset - For next student
2. Hard Reset - Complete removal
3. Clean Temp - Quick cleanup
4. Backup - Save student work
5. Setup Vulnerable - Switch versions

---

## Management Scripts Overview

### 📁 `/setup` Directory Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `quick_setup.sh` | Full installation | `./setup/quick_setup.sh` |
| `reset_lab.sh` | Reset environment | `./reset_lab.sh [soft\|hard]` |
| `student_onboard.sh` | Personalize for student | `./student_onboard.sh` |

### 📁 `/scripts` Directory Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| `manage_vulnerabilities.py` | Switch versions | `python manage_vulnerabilities.py switch vulnerable` |
| `test_simulation.py` | Test sensor simulation | `python test_simulation.py` |

---

## Bulk Operations for Multiple Pis

### Reset All Pis at Once
```bash
#!/bin/bash
# reset_all_pis.sh

PI_IPS="192.168.1.101 192.168.1.102 192.168.1.103"

for IP in $PI_IPS; do
    echo "Resetting Pi at $IP..."
    ssh pi@$IP "cd ~/LabM4_weather_station/setup && ./reset_lab.sh soft"
done
```

### Check Status of All Pis
```bash
#!/bin/bash
# check_all_pis.sh

PI_IPS="192.168.1.101 192.168.1.102 192.168.1.103"

for IP in $PI_IPS; do
    echo "=== Pi at $IP ==="
    ssh pi@$IP "cd ~/LabM4_weather_station && git status && echo 'Last activity:' && tail -1 logs/weather_station.log 2>/dev/null"
    echo
done
```

### Deploy Updates to All Pis
```bash
#!/bin/bash
# update_all_pis.sh

PI_IPS="192.168.1.101 192.168.1.102 192.168.1.103"

for IP in $PI_IPS; do
    echo "Updating Pi at $IP..."
    ssh pi@$IP "cd ~/LabM4_weather_station && git pull && pip install -r requirements.txt"
done
```

---

## Workflow Timeline

### Before Class
```bash
# On all Pis
./reset_lab.sh soft
```

### Start of Class
Students run:
```bash
# One-time setup (if not done)
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash

# Then personalize
cd ~/LabM4_weather_station
./setup/student_onboard.sh
```

### During Class
Students work on the lab:
```bash
# Start application
./start_weather_station.sh

# Test security
./test_security.sh
```

### End of Class
```bash
# Students can backup their work
cd ~/LabM4_weather_station
tar -czf ~/my_work.tar.gz student_work/

# Instructor resets
./setup/reset_lab.sh soft
```

---

## Troubleshooting

### Installation Fails
```bash
# Check internet connection
ping -c 3 github.com

# Try manual clone
git clone https://github.com/kodkal/LabM4_weather_station.git
cd LabM4_weather_station
./setup/quick_setup.sh
```

### Reset Script Fails
```bash
# Force clean
rm -rf ~/LabM4_weather_station
# Reinstall
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash
```

### Permission Issues
```bash
# Fix permissions
cd ~/LabM4_weather_station
chmod +x setup/*.sh
chmod +x *.sh
chmod 700 keys/
```

### Can't SSH to Pi
```bash
# On Pi (with monitor)
sudo systemctl enable ssh
sudo systemctl start ssh
hostname -I  # Get IP address
```

---

## Advanced Features

### Switch to Vulnerable Version
For security testing labs:
```bash
cd ~/LabM4_weather_station
python scripts/manage_vulnerabilities.py switch vulnerable
```

### Create Student Distribution
Remove instructor materials:
```bash
python scripts/manage_vulnerabilities.py student --output student_version
```

### Automated Grading
```bash
# Collect test results from all Pis
for IP in $PI_IPS; do
    echo "=== Results for $IP ==="
    ssh pi@$IP "cd ~/LabM4_weather_station && python tests/test_security.py"
done > lab_results.txt
```

---

## Quick Reference Card

### Essential Commands
```bash
# Setup
curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/install.sh | bash

# Start
cd ~/LabM4_weather_station && ./start_weather_station.sh

# Test
./test_security.sh

# Reset (soft)
./setup/reset_lab.sh soft

# Reset (hard)  
./setup/reset_lab.sh hard

# Switch to vulnerable
python scripts/manage_vulnerabilities.py switch vulnerable

# Switch to secure
python scripts/manage_vulnerabilities.py switch secure
```

---

## Tips for Instructors

1. **Pre-Setup**: Run installation on all Pis before class
2. **Use Soft Reset**: Between students (faster, preserves setup)
3. **Enable Simulation**: For students without sensors
4. **Monitor Progress**: Check logs in `logs/` directory
5. **Backup Work**: Use `--backup` flag when resetting

---

## Support

- **Repository**: https://github.com/kodkal/LabM4_weather_station
- **Issues**: https://github.com/kodkal/LabM4_weather_station/issues
- **Documentation**: See `/docs` directory

---

*Setup & Management Guide v1.0 | UVU IoT Security Lab*