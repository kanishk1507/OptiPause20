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

## Some screeenshots of application (with a basic gui):

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/197bd827-84da-428b-a657-1e7436613bd3" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/893fc310-aa86-424b-89f6-56b7aefa104e" width="400"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/90e88de5-a86a-428e-9408-8e92bdce6525" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/8bc739d0-c339-4f4f-b1ff-82860aabceed" width="400"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/f5bbeb5f-265e-4bbf-a292-ea6b83f03ea4" width="400"/></td>
    <td><img src="https://github.com/user-attachments/assets/077d6f10-aeeb-4ced-96ac-dcf8fa83f6bd" width="400"/></td>
  </tr>
</table>



P.S. : The GUI is created with AI Tools! 
