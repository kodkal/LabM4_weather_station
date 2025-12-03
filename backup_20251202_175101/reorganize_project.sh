#!/bin/bash
# ===========================================
# LAB M4 Project Reorganization Script
# Safe migration with backup and rollback
# macOS and Linux compatible
# ===========================================

set -e  # Exit on any error

PROJECT_DIR="${1:-.}"
BACKUP_DIR="${PROJECT_DIR}/backup_$(date +%Y%m%d_%H%M%S)"

echo "============================================"
echo "  LAB M4 Project Reorganization"
echo "============================================"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Backup directory:  $BACKUP_DIR"
echo ""

# ===========================================
# Step 1: Create Backup
# ===========================================
echo "📦 Step 1: Creating backup..."
mkdir -p "$BACKUP_DIR"

# Backup all Python files
for file in "$PROJECT_DIR"/*.py; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  ✓ Backed up $(basename "$file")"
    fi
done

# Backup all shell scripts
for file in "$PROJECT_DIR"/*.sh; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  ✓ Backed up $(basename "$file")"
    fi
done

# Backup .env files
for file in "$PROJECT_DIR"/.env*; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  ✓ Backed up $(basename "$file")"
    fi
done

echo "  Backup created at: $BACKUP_DIR"
echo ""

# ===========================================
# Step 2: Create New Directory Structure
# ===========================================
echo "📁 Step 2: Creating new directory structure..."

mkdir -p "$PROJECT_DIR/security"
mkdir -p "$PROJECT_DIR/config"
mkdir -p "$PROJECT_DIR/setup"
mkdir -p "$PROJECT_DIR/tests"
mkdir -p "$PROJECT_DIR/scripts"

echo "  ✓ Created security/"
echo "  ✓ Created config/"
echo "  ✓ Created setup/"
echo "  ✓ Created tests/"
echo "  ✓ Created scripts/"
echo ""

# ===========================================
# Step 3: Create __init__.py Files
# ===========================================
echo "📝 Step 3: Creating package __init__.py files..."

# Security package __init__.py
cat > "$PROJECT_DIR/security/__init__.py" << 'EOF'
"""
Security Module for Secure Weather Station
Contains authentication, encryption, validation, and credential management.
"""

from .auth import JWTManager
from .encryption import SecureDataTransmission
from .validation import InputValidator
from .credentials import SecureCredentialStore

__all__ = [
    'JWTManager',
    'SecureDataTransmission', 
    'InputValidator',
    'SecureCredentialStore'
]
EOF
echo "  ✓ Created security/__init__.py"

# Config package __init__.py
cat > "$PROJECT_DIR/config/__init__.py" << 'EOF'
"""
Configuration Module for Secure Weather Station
"""

from .settings import *

__all__ = [
    'SENSOR_TYPE',
    'SENSOR_PIN',
    'SENSOR_SIMULATION',
    'SIMULATION_CONFIG',
    'SECRET_KEY',
    'JWT_SECRET',
    'DEVICE_ID',
    'LOCATION',
    'API_PORT',
    'API_HOST',
    'DEBUG',
    'CERT_FILE',
    'PRIVATE_KEY_FILE',
    'DB_PATH',
    'CREDENTIAL_DB',
    'LOG_LEVEL',
    'LOG_FILE',
    'KEY_FILE',
    'validate_configuration',
    'print_configuration'
]
EOF
echo "  ✓ Created config/__init__.py"

# Tests package __init__.py
cat > "$PROJECT_DIR/tests/__init__.py" << 'EOF'
"""
Test Suite for Secure Weather Station
"""
EOF
echo "  ✓ Created tests/__init__.py"

# Scripts package
cat > "$PROJECT_DIR/scripts/__init__.py" << 'EOF'
"""
Utility Scripts for Secure Weather Station
"""
EOF
echo "  ✓ Created scripts/__init__.py"
echo ""

# ===========================================
# Step 4: Move Files to New Locations
# ===========================================
echo "🚚 Step 4: Moving files to new locations..."

# Security modules
for file in auth.py encryption.py validation.py credentials.py; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/security/"
        echo "  ✓ Moved $file → security/"
    fi
done

# Config modules
if [ -f "$PROJECT_DIR/settings.py" ]; then
    mv "$PROJECT_DIR/settings.py" "$PROJECT_DIR/config/"
    echo "  ✓ Moved settings.py → config/"
fi

# Setup scripts
for file in install.sh quick_setup.sh reset_lab.sh student_onboard.sh apply_runtime_fixes.sh; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/setup/"
        echo "  ✓ Moved $file → setup/"
    fi
done

# Test files
for file in test_security.py test_simulation.py; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        mv "$PROJECT_DIR/$file" "$PROJECT_DIR/tests/"
        echo "  ✓ Moved $file → tests/"
    fi
done

# Utility scripts
if [ -f "$PROJECT_DIR/manage_vulnerabilities.py" ]; then
    mv "$PROJECT_DIR/manage_vulnerabilities.py" "$PROJECT_DIR/scripts/"
    echo "  ✓ Moved manage_vulnerabilities.py → scripts/"
fi
echo ""

# ===========================================
# Step 5: Update Import Statements
# ===========================================
echo "🔧 Step 5: Updating import statements..."

# Function to update imports in a file
update_imports() {
    local filepath="$1"
    if [ -f "$filepath" ]; then
        # Use sed to update imports (macOS compatible with -i '')
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' 's/^from auth import/from security.auth import/g' "$filepath"
            sed -i '' 's/^from encryption import/from security.encryption import/g' "$filepath"
            sed -i '' 's/^from validation import/from security.validation import/g' "$filepath"
            sed -i '' 's/^from credentials import/from security.credentials import/g' "$filepath"
            sed -i '' 's/^import settings$/from config import settings/g' "$filepath"
            sed -i '' 's/^from settings import/from config.settings import/g' "$filepath"
        else
            # Linux
            sed -i 's/^from auth import/from security.auth import/g' "$filepath"
            sed -i 's/^from encryption import/from security.encryption import/g' "$filepath"
            sed -i 's/^from validation import/from security.validation import/g' "$filepath"
            sed -i 's/^from credentials import/from security.credentials import/g' "$filepath"
            sed -i 's/^import settings$/from config import settings/g' "$filepath"
            sed -i 's/^from settings import/from config.settings import/g' "$filepath"
        fi
        echo "  ✓ Updated imports in $(basename "$filepath")"
    fi
}

# Update main files
update_imports "$PROJECT_DIR/weather_station.py"
update_imports "$PROJECT_DIR/vulnerable_weather_station.py"
update_imports "$PROJECT_DIR/sensor_module.py"

# Update test files
update_imports "$PROJECT_DIR/tests/test_security.py"
update_imports "$PROJECT_DIR/tests/test_simulation.py"

# Add path setup to config/settings.py for sensor_module access
if [ -f "$PROJECT_DIR/config/settings.py" ]; then
    # Check if sys.path.insert is already there
    if ! grep -q "sys.path.insert" "$PROJECT_DIR/config/settings.py"; then
        # Create a temp file with the path setup added
        # This is a more reliable cross-platform approach
        python3 -c "
import re
filepath = '$PROJECT_DIR/config/settings.py'
with open(filepath, 'r') as f:
    content = f.read()

# Add 'import sys' after 'from pathlib import Path' if not present
if 'import sys' not in content:
    content = re.sub(
        r'(from pathlib import Path)',
        r'\1\nimport sys',
        content
    )

# Add sys.path.insert after BASE_DIR line
if 'sys.path.insert' not in content:
    content = re.sub(
        r'(BASE_DIR = Path\(__file__\)\.resolve\(\)\.parent\.parent)',
        r'\1\n\n# Add project root to path for sensor_module access\nsys.path.insert(0, str(BASE_DIR))',
        content
    )

with open(filepath, 'w') as f:
    f.write(content)
"
        echo "  ✓ Added path setup to config/settings.py"
    fi
fi

# Add path setup to test files
for testfile in "$PROJECT_DIR/tests/test_security.py" "$PROJECT_DIR/tests/test_simulation.py"; do
    if [ -f "$testfile" ]; then
        if ! grep -q "sys.path.insert" "$testfile"; then
            # Create temp file with path setup prepended
            {
                echo 'import sys'
                echo 'import os'
                echo 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
                echo ''
                cat "$testfile"
            } > "$testfile.tmp" && mv "$testfile.tmp" "$testfile"
            echo "  ✓ Added path setup to $(basename "$testfile")"
        fi
    fi
done

echo ""

# ===========================================
# Step 6: Update Root __init__.py
# ===========================================
echo "📝 Step 6: Updating root __init__.py..."

cat > "$PROJECT_DIR/__init__.py" << 'EOF'
"""
Secure Weather Station - IoT Security Project
Utah Valley University

This package provides a comprehensive IoT security education project.
"""

__version__ = '1.0.0'
__author__ = 'UVU IoT Security Lab'

# Make key modules easily importable
from security import JWTManager, SecureDataTransmission, InputValidator, SecureCredentialStore
from config import settings

__all__ = [
    'JWTManager',
    'SecureDataTransmission',
    'InputValidator', 
    'SecureCredentialStore',
    'settings'
]
EOF
echo "  ✓ Updated __init__.py"
echo ""

# ===========================================
# Step 7: Verify Structure
# ===========================================
echo "✅ Step 7: Verifying new structure..."
echo ""
echo "New project structure:"
echo "─────────────────────"

# Display structure
echo ""
echo "├── security/"
ls -1 "$PROJECT_DIR/security/" 2>/dev/null | sed 's/^/│   ├── /'
echo "├── config/"
ls -1 "$PROJECT_DIR/config/" 2>/dev/null | sed 's/^/│   ├── /'
echo "├── setup/"
ls -1 "$PROJECT_DIR/setup/" 2>/dev/null | sed 's/^/│   ├── /'
echo "├── tests/"
ls -1 "$PROJECT_DIR/tests/" 2>/dev/null | sed 's/^/│   ├── /'
echo "├── scripts/"
ls -1 "$PROJECT_DIR/scripts/" 2>/dev/null | sed 's/^/│   ├── /'
echo "├── docs/"
echo "│   └── (documentation files)"
echo "├── weather_station.py"
echo "├── vulnerable_weather_station.py"
echo "├── sensor_module.py"
echo "└── (other root files)"

echo ""
echo "============================================"
echo "  Reorganization Complete!"
echo "============================================"
echo ""
echo "📋 Next Steps:"
echo "  1. Test the application: python weather_station.py"
echo "  2. Run tests: python -m pytest tests/"
echo "  3. If everything works, commit the changes"
echo "  4. If issues arise, restore from: $BACKUP_DIR"
echo ""
echo "🔄 To rollback (if needed):"
echo "  cp $BACKUP_DIR/*.py ."
echo "  cp $BACKUP_DIR/*.sh ."
echo "  rm -rf security config setup tests scripts"
echo ""