#!/bin/bash
# =====================================================
# Reset Script for Weather Station Lab
# Instructor tool to reset environment between students
# =====================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$HOME/LabM4_weather_station"
BACKUP_DIR="$HOME/lab_backups"

# Functions
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Banner
show_banner() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║            Weather Station Lab Reset Tool               ║"
    echo "║                    INSTRUCTOR USE                       ║"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo -e "${NC}"
}

# Soft Reset - Reset for next student
soft_reset() {
    echo -e "${YELLOW}=== SOFT RESET ===${NC}"
    echo "This will reset the environment for the next student while keeping the installation."
    echo
    read -p "Are you sure you want to soft reset? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Soft reset cancelled"
        return 0
    fi
    
    cd "$PROJECT_DIR" 2>/dev/null || {
        print_error "Project directory not found!"
        return 1
    }
    
    # 1. Backup student work (optional)
    if [ "$1" == "--backup" ]; then
        backup_student_work
    fi
    
    # 2. Clear logs
    print_status "Clearing log files..."
    rm -rf logs/*
    touch logs/.gitkeep
    print_success "Logs cleared"
    
    # 3. Clear data files
    print_status "Clearing data files..."
    rm -rf data/*
    rm -rf data_backup/*
    touch data/.gitkeep
    touch data_backup/.gitkeep
    print_success "Data files cleared"
    
    # 4. Reset database
    print_status "Resetting databases..."
    rm -f data/*.db
    rm -f data/*.sqlite
    print_success "Databases reset"
    
    # 5. Reset credentials and keys (keep certificates)
    print_status "Resetting credentials..."
    rm -f keys/master.key
    rm -f keys/fernet.key
    rm -f keys/aes.key
    rm -f .env
    
    # Recreate .env from template
    if [ -f .env.example ]; then
        cp .env.example .env
        
        # Generate new secure keys
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        
        # Update .env
        sed -i "s/change-this-to-a-secure-random-key/$SECRET_KEY/g" .env
        sed -i "s/change-this-to-another-secure-key/$JWT_SECRET/g" .env
        
        chmod 600 .env
        print_success "New credentials generated"
    fi
    
    # 6. Reset Git repository (remove student commits)
    print_status "Resetting Git repository..."
    git stash > /dev/null 2>&1 || true
    git checkout main > /dev/null 2>&1 || git checkout master > /dev/null 2>&1 || true
    git reset --hard HEAD > /dev/null 2>&1
    git clean -fd > /dev/null 2>&1
    print_success "Repository reset to original state"
    
    # 7. Clear Python cache
    print_status "Clearing Python cache..."
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    print_success "Python cache cleared"
    
    # 8. Reset file permissions
    print_status "Resetting file permissions..."
    chmod 700 keys
    chmod 755 logs data data_backup
    chmod 644 requirements.txt README.md
    chmod 755 setup/*.sh scripts/*.sh 2>/dev/null || true
    print_success "File permissions reset"
    
    # 9. Clear any running processes
    print_status "Stopping any running processes..."
    pkill -f "weather_station.py" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    print_success "Processes stopped"
    
    # 10. Reset systemd service if exists
    if systemctl list-units --full -all | grep -Fq "weather-station.service"; then
        print_status "Resetting systemd service..."
        sudo systemctl stop weather-station 2>/dev/null || true
        sudo systemctl disable weather-station 2>/dev/null || true
        print_success "Service reset"
    fi
    
    echo
    print_success "Soft reset complete! Environment ready for next student."
    echo
    echo -e "${YELLOW}Next student should run:${NC}"
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  ./start_weather_station.sh"
}

# Hard Reset - Complete removal
hard_reset() {
    echo -e "${RED}=== HARD RESET ===${NC}"
    echo "This will COMPLETELY REMOVE the weather station project!"
    echo "All files, data, and configurations will be deleted."
    echo
    read -p "Are you sure you want to hard reset? Type 'DELETE' to confirm: " confirmation
    
    if [ "$confirmation" != "DELETE" ]; then
        print_warning "Hard reset cancelled"
        return 0
    fi
    
    # Final confirmation
    echo
    echo -e "${RED}FINAL WARNING: This action cannot be undone!${NC}"
    read -p "Really delete everything? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Hard reset cancelled"
        return 0
    fi
    
    # Backup before deletion (optional)
    if [ "$1" == "--backup" ]; then
        backup_student_work
    fi
    
    # 1. Stop all processes
    print_status "Stopping all processes..."
    pkill -f "weather_station" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    print_success "Processes stopped"
    
    # 2. Remove systemd service
    if systemctl list-units --full -all | grep -Fq "weather-station.service"; then
        print_status "Removing systemd service..."
        sudo systemctl stop weather-station 2>/dev/null || true
        sudo systemctl disable weather-station 2>/dev/null || true
        sudo rm -f /etc/systemd/system/weather-station.service
        sudo systemctl daemon-reload
        print_success "Service removed"
    fi
    
    # 3. Remove firewall rules
    if command -v ufw &> /dev/null; then
        print_status "Removing firewall rules..."
        sudo ufw delete allow 8443/tcp 2>/dev/null || true
        print_success "Firewall rules removed"
    fi
    
    # 4. Remove project directory
    print_status "Removing project directory..."
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
        print_success "Project directory removed"
    else
        print_warning "Project directory not found"
    fi
    
    # 5. Remove any global Python packages installed
    print_status "Cleaning Python packages..."
    pip3 uninstall -y flask jwt cryptography 2>/dev/null || true
    print_success "Python cleanup complete"
    
    # 6. Remove user from groups (optional)
    read -p "Remove user from gpio/i2c groups? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo deluser $USER gpio 2>/dev/null || true
        sudo deluser $USER i2c 2>/dev/null || true
        sudo deluser $USER spi 2>/dev/null || true
        print_success "User removed from hardware groups"
    fi
    
    # 7. Clear bash history related to project
    print_status "Clearing command history..."
    history -d $(history | grep weather_station | awk '{print $1}') 2>/dev/null || true
    print_success "History cleared"
    
    echo
    print_success "Hard reset complete! All project files removed."
    echo
    echo -e "${YELLOW}To reinstall, run:${NC}"
    echo "  curl -sSL https://raw.githubusercontent.com/kodkal/LabM4_weather_station/main/quick_setup.sh | bash"
}

# Backup student work
backup_student_work() {
    print_status "Backing up student work..."
    
    mkdir -p "$BACKUP_DIR"
    
    STUDENT_NAME=$(whoami)
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/student_${STUDENT_NAME}_${TIMESTAMP}.tar.gz"
    
    # Create backup
    tar -czf "$BACKUP_FILE" \
        -C "$PROJECT_DIR" \
        src/ \
        logs/ \
        data/ \
        .env \
        2>/dev/null || true
    
    print_success "Student work backed up to: $BACKUP_FILE"
}

# Clean temporary files only
clean_temp() {
    echo -e "${BLUE}=== CLEAN TEMPORARY FILES ===${NC}"
    echo "This will only remove temporary files and cache."
    echo
    
    cd "$PROJECT_DIR" 2>/dev/null || {
        print_error "Project directory not found!"
        return 1
    }
    
    print_status "Cleaning temporary files..."
    
    # Python cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Temp files
    find . -type f -name "*.tmp" -delete 2>/dev/null || true
    find . -type f -name "*.log" -delete 2>/dev/null || true
    find . -type f -name ".DS_Store" -delete 2>/dev/null || true
    
    # Old backups
    find data_backup -type f -mtime +7 -delete 2>/dev/null || true
    
    print_success "Temporary files cleaned"
}

# Reset to vulnerable version for testing
setup_vulnerable() {
    echo -e "${YELLOW}=== SETUP VULNERABLE VERSION ===${NC}"
    echo "This will switch to the vulnerable version for security testing."
    echo
    
    cd "$PROJECT_DIR" 2>/dev/null || {
        print_error "Project directory not found!"
        return 1
    }
    
    if [ -f "scripts/manage_vulnerabilities.py" ]; then
        print_status "Switching to vulnerable version..."
        python3 scripts/manage_vulnerabilities.py switch vulnerable
        print_success "Vulnerable version activated"
        
        echo
        print_warning "WARNING: System now contains security vulnerabilities!"
        print_warning "DO NOT expose to internet or use with real data!"
        echo
        echo -e "${YELLOW}Students can now test for vulnerabilities using:${NC}"
        echo "  python tests/test_security.py"
    else
        print_error "Vulnerability management script not found"
    fi
}

# Main menu
show_menu() {
    show_banner
    
    echo "Select reset option:"
    echo
    echo "  1) Soft Reset - Reset for next student (keeps installation)"
    echo "  2) Hard Reset - Complete removal (deletes everything)"
    echo "  3) Clean Temp - Remove temporary files only"
    echo "  4) Backup Only - Backup current student work"
    echo "  5) Setup Vulnerable - Switch to vulnerable version"
    echo "  6) Exit"
    echo
    read -p "Enter choice [1-6]: " choice
    
    case $choice in
        1)
            soft_reset "--backup"
            ;;
        2)
            hard_reset "--backup"
            ;;
        3)
            clean_temp
            ;;
        4)
            backup_student_work
            ;;
        5)
            setup_vulnerable
            ;;
        6)
            echo "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice!"
            sleep 2
            show_menu
            ;;
    esac
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments, show menu
    show_menu
else
    # Direct command
    case "$1" in
        soft)
            soft_reset "$2"
            ;;
        hard)
            hard_reset "$2"
            ;;
        clean)
            clean_temp
            ;;
        backup)
            backup_student_work
            ;;
        vulnerable)
            setup_vulnerable
            ;;
        --help|-h)
            echo "Usage: $0 [command] [options]"
            echo
            echo "Commands:"
            echo "  soft       - Soft reset (keeps installation)"
            echo "  hard       - Hard reset (removes everything)"
            echo "  clean      - Clean temporary files"
            echo "  backup     - Backup student work"
            echo "  vulnerable - Setup vulnerable version"
            echo
            echo "Options:"
            echo "  --backup   - Create backup before reset"
            echo
            echo "Examples:"
            echo "  $0              # Show interactive menu"
            echo "  $0 soft         # Soft reset"
            echo "  $0 hard --backup # Hard reset with backup"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
fi