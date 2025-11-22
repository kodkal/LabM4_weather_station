# Student Quick Start - Weather Station Lab

## 🆘 Got Errors? Start Here!

### Error 1: Setup Script Exits Early
```
[!] Not running on Raspberry Pi - some features may not work
teacher@ubuntu:~$    <--- Script stopped!
```

**Fix:** Get the updated setup script from your instructor.

---

### Error 2: Can't Start Weather Station
```
xargs: unmatched single quote
export: --: invalid option
RuntimeError: This module can only be run on a Raspberry Pi!
```

**Fix (10 seconds):**
```bash
cd ~/LabM4_weather_station
./apply_runtime_fixes.sh
```

Then try: `./start_weather_station.sh` again

**Alternative (if above fails):**
```bash
cd ~/LabM4_weather_station
export SENSOR_SIMULATION=true
python src/weather_station.py
```

---

## ✅ Fresh Installation (No Errors Yet)

### Step 1: Run Setup
```bash
./quick_setup.sh
```

Wait for it to complete. Should take 5-10 minutes.

---

### Step 2: Run Onboarding
```bash
./student_onboarding.sh
```

Answer the questions:
- Your name
- Experience level
- (It will auto-detect your platform - don't worry about sensor choice on Ubuntu!)

---

### Step 3: Start the Weather Station
```bash
./start_weather_station.sh
```

Should see:
```
======================================
  Weather Station - Starting
======================================
Platform: Ubuntu 20.04.1 LTS
Simulation Mode: true
API URL: https://localhost:8443
======================================
```

---

### Step 4: Access the API

Open your browser:
```
https://localhost:8443
```

**Note:** You'll see a security warning (self-signed certificate). This is expected!
- Chrome: Click "Advanced" → "Proceed to localhost"
- Firefox: Click "Advanced" → "Accept the Risk"

---

## 🎯 Starting Your Security Work

### Quick Commands

```bash
# Start the station
./start_weather_station.sh

# Run security tests
./test_security.sh

# Check your setup
./check_environment.sh

# View your quick reference
cat student_work/quick_reference.txt
```

---

### Finding Vulnerabilities

**Beginner students:**
```bash
# See hints
cat student_work/hints.txt

# Search for obvious issues
grep -r "password" src/
grep -r "admin" src/
```

**All students:**
```bash
# Review your checklist
cat student_work/security_checklist.md

# Track your progress
nano student_work/progress.md
```

---

## 📚 Important Files

| File | What It Is |
|------|-----------|
| `src/weather_station.py` | Main application code |
| `.env` | Configuration (secrets here!) |
| `student_work/` | Your personal workspace |
| `logs/weather_station.log` | Application logs |
| `PLATFORM_SETUP.md` | Platform-specific info |

---

## 🔍 Common Questions

**Q: Do I need a Raspberry Pi?**  
A: No! The lab works perfectly on Ubuntu in simulation mode. All vulnerabilities can be found.

**Q: What's simulation mode?**  
A: Generates fake sensor data so you don't need hardware. Security features work exactly the same.

**Q: I'm on Ubuntu, can I complete the lab?**  
A: YES! 100% of the lab objectives can be achieved in simulation mode.

**Q: How do I know if I'm in simulation mode?**  
A: Check your `.env` file: `SENSOR_SIMULATION=true` means simulation mode.

**Q: The API won't start, port 8443 in use?**  
A: Kill the existing process:
```bash
sudo lsof -i :8443
# Note the PID, then:
sudo kill <PID>
```

**Q: Where do I find the vulnerabilities?**  
A: Start in `src/weather_station.py` and look for:
- Hardcoded passwords
- SQL queries that might be injectable
- Weak encryption/secrets
- Missing input validation
- Debug mode enabled

**Q: I found a vulnerability, now what?**  
A:
1. Document it in `student_work/progress.md`
2. Fix it in the code
3. Test with `./test_security.sh`
4. Verify it's actually fixed!

---

## 🆘 Still Having Issues?

### Try These Steps:

1. **Check you're in the right directory:**
   ```bash
   pwd
   # Should show: /home/yourusername/LabM4_weather_station
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Check Python packages:**
   ```bash
   pip list | grep -E "flask|jwt"
   ```

4. **View error logs:**
   ```bash
   tail -20 logs/weather_station.log
   ```

5. **Run the fix script:**
   ```bash
   ./apply_runtime_fixes.sh
   ```

---

### Get Help

1. Read the error message carefully
2. Check `RUNTIME_FIXES.md` for known issues
3. Ask your instructor or TA
4. Post in the course forum

**Include in your help request:**
- The exact error message
- What you were trying to do
- Your platform (Ubuntu version or Raspberry Pi model)
- Output of: `./check_environment.sh`

---

## 📖 Documentation

**For setup issues:**
- `PLATFORM_SETUP.md` - Your specific platform setup
- `RUNTIME_FIX_SUMMARY.md` - Runtime error solutions

**For the lab:**
- `docs/` folder - Lab guides
- `student_work/hints.txt` - Beginner hints (if applicable)
- `student_work/quick_reference.txt` - Your command reference

**For security concepts:**
- Review lecture materials
- Check OWASP Top 10
- Read about IoT security best practices

---

## ✅ Success Checklist

Before starting the security work:

- [ ] Setup script completed without errors
- [ ] Onboarding completed
- [ ] Weather station starts successfully
- [ ] Can access https://localhost:8443
- [ ] API responds to requests
- [ ] No Python import errors
- [ ] Simulation mode is working (if on Ubuntu)

If all checked, you're ready to begin!

---

## 🎉 You're Ready!

**Your goal:** Find and fix security vulnerabilities in the IoT weather station.

**Remember:**
- Take your time
- Document everything
- Test your fixes
- Ask for help when stuck
- Learn from each vulnerability

**Good luck!** 🚀

---

**Quick Links:**
- Errors? → `./apply_runtime_fixes.sh`
- Start app → `./start_weather_station.sh`
- Run tests → `./test_security.sh`
- Your hints → `cat student_work/hints.txt` (beginners)
- Your checklist → `cat student_work/security_checklist.md`

**The most important thing: Learn and have fun! 😊**