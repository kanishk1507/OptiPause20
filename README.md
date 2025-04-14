# 👁️ OptiPause20 – Eye Care Reminder App

**OptiPause20** is a desktop productivity and wellness application based on the **20-20-20 rule** in ophthalmology:  

The rule says : *Every 20 minutes, look at something 20 feet away for 20 seconds.*

It helps reduce digital eye strain by prompting users to take smart, non-intrusive breaks, while also tracking screen time, inactivity, and healthy usage habits.

---

## Features

- ⚡ **Minimal & Distraction-Free**: Dynamic break popups—no annoying sounds by default  
- 📊 **Screen Time Analytics**: Track your daily and weekly screen usage  
- 🔁 **Streak Tracking**: Build habits with daily usage streaks  
- 🔉 **Optional Focus Sounds**: Ambient audio (nature, white noise, etc.) to improve focus  
- 🖱️ **Activity-Based Timing**: Automatically pauses the countdown if no mouse/keyboard input is detected for 5+ minutes  
- 🔒 **System-Aware**: Detects when screen is locked or in screensaver mode to pause the timer  
- 🎬 **Focus Mode**: Temporarily disable breaks for movies, deep work, or full-screen apps  

---

## 🛠️ Tech Stack

| Feature                 | Technology |
|-------------------------|------------|
| UI & Notifications      | PyQt6 (or PySide6) |
| Data Storage            | SQLite + SQLAlchemy |
| Activity Monitoring     | Pynput |
| System Monitoring       | psutil + platform-specific APIs |
| Audio Playback          | PyAudio / pygame |
| Packaging               | PyInstaller |

---

## 📁 Project Structure

![image](https://github.com/user-attachments/assets/95686471-c967-435b-bc77-0afddcf14913)

 
## Run the app:

python src/main.py
