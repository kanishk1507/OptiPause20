import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core.timer import EyeCareTimer
from core.activity_tracker import ActivityTracker
from core.system_monitor import SystemMonitor
from data.database import Database
from ui.main_window import MainWindow

class EyeCareApp:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        # Initialize database
        self.db = Database()
        
        # Load settings
        work_duration = int(self.db.get_setting('work_duration', 1200))
        break_duration = int(self.db.get_setting('break_duration', 20))
        inactivity_threshold = int(self.db.get_setting('inactivity_threshold', 300))
        
        # Initialize core components
        self.timer = EyeCareTimer(
            work_duration=work_duration,
            break_duration=break_duration,
            on_break_start=self.on_break_start,
            on_break_end=self.on_break_end
        )
        
        # Set inactivity threshold
        self.timer.inactivity_threshold = inactivity_threshold
        
        # Initialize activity tracker
        self.activity_tracker = ActivityTracker(on_activity=self.on_user_activity)
        
        # Initialize system monitor
        self.system_monitor = SystemMonitor(
            on_system_idle=self.on_system_idle,
            on_system_active=self.on_system_active
        )
        
        # Initialize UI
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self)
        
        # Current session tracking
        self.current_session_id = None
        self.current_break_id = None
        
    def start(self):
        """Start the application."""
        # Start core components
        self.activity_tracker.start()
        self.system_monitor.start()
        
        # Show main window
        self.main_window.show()
        
        # Start with timer running
        self.start_timer()
        
        # Start application event loop
        return self.app.exec()
    
    def start_timer(self):
        """Start the eye care timer and record a new session."""
        if not self.timer.is_running:
            self.timer.start()
            import datetime
            # Record session start
            self.current_session_id = self.db.start_session(
                datetime.datetime.now().isoformat()
            )
            print(f"Started new session: {self.current_session_id}")
        
            # Start tracking screen time immediately
            today = datetime.date.today().isoformat()
            self.db.update_daily_stats(
                today,
                0,  # Will be updated when session ends
                0,  # Will be updated when breaks occur
                0,  # Will be updated when breaks complete
                0   # Will be updated when session ends
            )
    
    def stop_timer(self):
        """Stop the eye care timer and record session end."""
        if self.timer.is_running:
            stats = self.timer.get_session_stats()
            self.timer.stop()
            
            if self.current_session_id:
                import datetime
                # Record session end
                self.db.end_session(
                    self.current_session_id,
                    datetime.datetime.now().isoformat(),
                    stats['session_duration'],
                    stats['breaks_taken']
                )
                
                # Update daily stats
                today = datetime.date.today().isoformat()
                self.db.update_daily_stats(
                    today,
                    stats['session_duration'],
                    stats['breaks_taken'],
                    stats['breaks_taken'],  # Simplification, assuming all breaks completed
                    stats['session_duration']
                )
                
                self.current_session_id = None
    
    def pause_timer(self):
        """Pause the eye care timer."""
        if self.timer.is_running and not self.timer.is_paused:
            self.timer.manually_pause()
    
    def resume_timer(self):
        """Resume the eye care timer."""
        if self.timer.is_running and self.timer.is_paused:
            self.timer.resume()
    
    def on_break_start(self):
        """Handler for when a break starts."""
        print("Break started")
        try:
            import datetime

            # Record break start
            if self.current_session_id and not self.current_break_id:
                self.current_break_id = self.db.record_break(
                    self.current_session_id,
                    datetime.datetime.now().isoformat()
                )
            
            # Trigger notification via signal
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.trigger_break_notification()
        except Exception as e:
            print(f"Error on break start: {e}")

    def on_break_end(self):
        """Handler for when a break ends."""
        print("Break ended")
        try:
            import datetime
        
            # Record break completion in database
            if self.current_break_id:
                self.db.complete_break(
                    self.current_break_id,
                    self.timer.break_duration
                )
                
                # Calculate work time since last break
                work_time = 0
                if self.timer.work_start_time:
                    work_time = int(datetime.datetime.now().timestamp() - self.timer.work_start_time)
                
                # Update daily stats for completed break and work time
                today = datetime.date.today().isoformat()
                self.db.update_daily_stats(
                    today,
                    work_time,  # Add work time since last break
                    1,  # One break taken
                    1,  # One completed break
                    work_time  # Update longest session if applicable
                )
                
                self.current_break_id = None
                print(f"Break completion recorded with {work_time} seconds of work time")
            
            # Hide notification if it exists
            if hasattr(self, 'main_window') and self.main_window:
                # Use QTimer.singleShot to avoid potential recursion
                QTimer.singleShot(0, self.main_window.hide_break_notification)
                print("Break notification hide scheduled")
        
            # End break in timer if still in break
            if self.timer.is_in_break:
                self.timer.is_in_break = False
                self.timer.work_start_time = datetime.datetime.now().timestamp()
                print("Break ended in timer")
        except Exception as e:
            print(f"Error on break end: {e}")

    def on_user_activity(self):
        """Handler for user activity events."""
        self.timer.update_activity()
    
    def on_system_idle(self):
        """Handler for when system becomes idle."""
        print("System idle detected")
        if self.timer.is_running and not self.timer.is_paused:
            self.timer.pause()
    
    def on_system_active(self):
        """Handler for when system becomes active again."""
        print("System active detected")
        if self.timer.is_running and self.timer.is_paused:
            # Only resume if the pause wasn't manual
            if not getattr(self.timer, '_manual_pause', False):
                self.timer.resume()
    
    def cleanup(self):
        """Clean up resources before exit."""
        self.stop_timer()
        self.activity_tracker.stop()
        self.system_monitor.stop()
        self.db.close()

if __name__ == "__main__":
    app = EyeCareApp()
    try:
        sys.exit(app.start())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        app.cleanup()