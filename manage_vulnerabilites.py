#!/usr/bin/env python3
"""
Vulnerability Management Script for Instructors
Easily switch between secure and vulnerable versions for teaching
"""

import os
import sys
import shutil
import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path

class VulnerabilityManager:
    """Manage vulnerable and secure versions of the weather station"""
    
    def __init__(self, project_root='.'):
        self.project_root = Path(project_root)
        self.vulnerable_dir = self.project_root / 'vulnerable_version'
        self.secure_dir = self.project_root / 'secure_version'
        self.active_version_file = self.project_root / '.active_version'
        
        # Vulnerability categories for progressive disclosure
        self.vulnerability_levels = {
            'beginner': {
                'description': 'Basic vulnerabilities (hardcoded secrets, weak validation)',
                'vulns': list(range(1, 21))  # VULN-01 to VULN-20
            },
            'intermediate': {
                'description': 'Common web vulnerabilities (SQLi, XSS, path traversal)',
                'vulns': list(range(21, 51))  # VULN-21 to VULN-50
            },
            'advanced': {
                'description': 'Complex vulnerabilities (deserialization, race conditions)',
                'vulns': list(range(51, 77))  # VULN-51 to VULN-76
            }
        }
    
    def setup(self):
        """Initial setup of vulnerable and secure versions"""
        print("🔧 Setting up vulnerability management system...")
        
        # Create directories
        self.vulnerable_dir.mkdir(exist_ok=True)
        self.secure_dir.mkdir(exist_ok=True)
        
        # Copy current (secure) version to secure_version
        src_dir = self.project_root / 'src'
        if src_dir.exists():
            print("📁 Backing up secure version...")
            shutil.copytree(src_dir, self.secure_dir / 'src', dirs_exist_ok=True)
        
        # Copy vulnerable version to vulnerable_version
        vulnerable_file = self.project_root / 'src' / 'vulnerable_weather_station.py'
        if vulnerable_file.exists():
            print("📁 Setting up vulnerable version...")
            shutil.copy(vulnerable_file, self.vulnerable_dir / 'weather_station.py')
        
        # Create version tracking file
        self.save_active_version('secure')
        
        print("✅ Setup complete!")
    
    def switch_version(self, version='secure', level=None):
        """Switch between secure and vulnerable versions"""
        if version not in ['secure', 'vulnerable']:
            print("❌ Version must be 'secure' or 'vulnerable'")
            return
        
        print(f"🔄 Switching to {version} version...")
        
        # Backup current version
        self.backup_current()
        
        if version == 'secure':
            # Restore secure version
            src = self.secure_dir / 'src'
            dst = self.project_root / 'src'
            
            if src.exists():
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
                print("✅ Switched to SECURE version")
            else:
                print("❌ Secure version not found. Run setup first.")
                return
                
        else:  # vulnerable
            # Apply vulnerable version with optional filtering
            self.apply_vulnerable_version(level)
            print(f"✅ Switched to VULNERABLE version" + 
                  (f" (level: {level})" if level else ""))
        
        # Update tracking
        self.save_active_version(version, level)
    
    def apply_vulnerable_version(self, level=None):
        """Apply vulnerable version with optional filtering by level"""
        vulnerable_file = self.vulnerable_dir / 'weather_station.py'
        
        if not vulnerable_file.exists():
            vulnerable_file = self.project_root / 'src' / 'vulnerable_weather_station.py'
        
        if not vulnerable_file.exists():
            print("❌ Vulnerable version not found")
            return
        
        # Read vulnerable code
        with open(vulnerable_file, 'r') as f:
            content = f.read()
        
        if level and level in self.vulnerability_levels:
            # Filter vulnerabilities by level
            content = self.filter_vulnerabilities(content, level)
        else:
            # Remove VULN comments for student version
            content = self.remove_vuln_comments(content)
        
        # Save to main weather_station.py
        target = self.project_root / 'src' / 'weather_station.py'
        with open(target, 'w') as f:
            f.write(content)
    
    def filter_vulnerabilities(self, content, level):
        """Include only vulnerabilities up to specified level"""
        lines = content.split('\n')
        filtered_lines = []
        
        # Get vulnerability numbers to include
        include_vulns = set()
        if level == 'beginner':
            include_vulns = set(self.vulnerability_levels['beginner']['vulns'])
        elif level == 'intermediate':
            include_vulns.update(self.vulnerability_levels['beginner']['vulns'])
            include_vulns.update(self.vulnerability_levels['intermediate']['vulns'])
        elif level == 'advanced':
            # Include all
            for lvl in self.vulnerability_levels.values():
                include_vulns.update(lvl['vulns'])
        
        for line in lines:
            # Check if line has a VULN comment
            if '# VULN-' in line:
                # Extract vulnerability number
                vuln_num = self.extract_vuln_number(line)
                if vuln_num and vuln_num not in include_vulns:
                    # Skip this vulnerability (use secure version)
                    # This is a simplified approach - in practice,
                    # you'd replace with the secure implementation
                    continue
            
            # Remove VULN comments for student version
            filtered_lines.append(self.remove_vuln_comments(line))
        
        return '\n'.join(filtered_lines)
    
    def extract_vuln_number(self, line):
        """Extract vulnerability number from comment"""
        import re
        match = re.search(r'VULN-(\d+)', line)
        if match:
            return int(match.group(1))
        return None
    
    def remove_vuln_comments(self, content):
        """Remove VULN-XX comments for student version"""
        import re
        # Remove inline VULN comments
        content = re.sub(r'\s*#\s*VULN-\d+[^]*', '', content)
        return content
    
    def backup_current(self):
        """Backup current version before switching"""
        backup_dir = self.project_root / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'backup_{timestamp}'
        
        src_dir = self.project_root / 'src'
        if src_dir.exists():
            shutil.copytree(src_dir, backup_path / 'src')
            print(f"📦 Backup created: {backup_path}")
    
    def create_student_version(self, output_dir='student_version'):
        """Create a clean version for students without solutions"""
        print("📚 Creating student version...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Copy project structure
        for item in ['docs', 'setup', 'tests', 'requirements.txt', 'README.md']:
            src = self.project_root / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, output_path / item, dirs_exist_ok=True)
                else:
                    shutil.copy(src, output_path / item)
        
        # Copy vulnerable version without VULN comments
        src_dir = output_path / 'src'
        src_dir.mkdir(exist_ok=True)
        
        # Process vulnerable file
        vulnerable_file = self.project_root / 'src' / 'vulnerable_weather_station.py'
        if vulnerable_file.exists():
            with open(vulnerable_file, 'r') as f:
                content = f.read()
            
            # Remove all VULN comments and instructor notes
            content = self.remove_vuln_comments(content)
            content = content.replace('# INSTRUCTOR NOTE:', '')
            content = content.replace('DO NOT USE IN PRODUCTION!', 
                                    'Security Assessment Version')
            
            # Save as weather_station.py for students
            with open(src_dir / 'weather_station.py', 'w') as f:
                f.write(content)
        
        # Remove instructor-only documents
        instructor_docs = [
            'VULNERABILITY_LAB_INSTRUCTOR.md',
            'INSTRUCTOR_GUIDE.md'
        ]
        
        for doc in instructor_docs:
            doc_path = output_path / 'docs' / doc
            if doc_path.exists():
                doc_path.unlink()
        
        print(f"✅ Student version created in: {output_path}")
    
    def generate_report(self):
        """Generate a report of all vulnerabilities"""
        print("\n📊 VULNERABILITY REPORT")
        print("=" * 50)
        
        vulnerable_file = self.project_root / 'src' / 'vulnerable_weather_station.py'
        if not vulnerable_file.exists():
            print("❌ Vulnerable version not found")
            return
        
        with open(vulnerable_file, 'r') as f:
            content = f.read()
        
        # Extract all vulnerabilities
        import re
        vulns = re.findall(r'# VULN-(\d+): ([^]+)', content)
        
        # Categorize vulnerabilities
        categorized = {
            'beginner': [],
            'intermediate': [],
            'advanced': []
        }
        
        for vuln_num, description in vulns:
            vuln_num = int(vuln_num)
            for level, info in self.vulnerability_levels.items():
                if vuln_num in info['vulns']:
                    categorized[level].append(f"VULN-{vuln_num:02d}: {description}")
                    break
        
        # Print report
        for level, vulns in categorized.items():
            print(f"\n{level.upper()} ({len(vulns)} vulnerabilities)")
            print(f"{self.vulnerability_levels[level]['description']}")
            print("-" * 40)
            for vuln in vulns[:5]:  # Show first 5
                print(f"  • {vuln}")
            if len(vulns) > 5:
                print(f"  ... and {len(vulns) - 5} more")
        
        print(f"\nTotal vulnerabilities: {sum(len(v) for v in categorized.values())}")
    
    def save_active_version(self, version, level=None):
        """Save the currently active version"""
        data = {
            'version': version,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.active_version_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_active_version(self):
        """Get the currently active version"""
        if self.active_version_file.exists():
            with open(self.active_version_file, 'r') as f:
                return json.load(f)
        return {'version': 'unknown', 'level': None}
    
    def verify_installation(self):
        """Verify the current installation integrity"""
        print("\n🔍 Verifying installation...")
        
        current = self.get_active_version()
        print(f"Active version: {current['version']}")
        if current['level']:
            print(f"Vulnerability level: {current['level']}")
        
        # Check for important files
        checks = {
            'Main application': self.project_root / 'src' / 'weather_station.py',
            'Sensor module': self.project_root / 'src' / 'sensor_module.py',
            'Security module': self.project_root / 'src' / 'security' / '__init__.py',
            'Student guide': self.project_root / 'docs' / 'STUDENT_GUIDE.md'
        }
        
        all_good = True
        for name, path in checks.items():
            if path.exists():
                print(f"✅ {name}: Found")
            else:
                print(f"❌ {name}: Missing")
                all_good = False
        
        if all_good:
            print("\n✅ Installation verified successfully!")
        else:
            print("\n⚠️  Some files are missing. Run setup to fix.")
    

def main():
    parser = argparse.ArgumentParser(
        description='Manage vulnerable and secure versions for teaching'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Initial setup')
    
    # Switch command
    switch_parser = subparsers.add_parser('switch', help='Switch versions')
    switch_parser.add_argument('version', choices=['secure', 'vulnerable'])
    switch_parser.add_argument('--level', choices=['beginner', 'intermediate', 'advanced'],
                              help='Vulnerability level for progressive disclosure')
    
    # Create student version
    student_parser = subparsers.add_parser('student', help='Create student version')
    student_parser.add_argument('--output', default='student_version',
                               help='Output directory')
    
    # Report command
    subparsers.add_parser('report', help='Generate vulnerability report')
    
    # Verify command
    subparsers.add_parser('verify', help='Verify installation')
    
    # Status command
    subparsers.add_parser('status', help='Show current version status')
    
    args = parser.parse_args()
    
    manager = VulnerabilityManager()
    
    if args.command == 'setup':
        manager.setup()
    elif args.command == 'switch':
        manager.switch_version(args.version, args.level)
    elif args.command == 'student':
        manager.create_student_version(args.output)
    elif args.command == 'report':
        manager.generate_report()
    elif args.command == 'verify':
        manager.verify_installation()
    elif args.command == 'status':
        status = manager.get_active_version()
        print(f"Current version: {status['version']}")
        if status['level']:
            print(f"Level: {status['level']}")
        print(f"Last changed: {status.get('timestamp', 'unknown')}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()