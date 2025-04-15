import time
import threading
import datetime
from typing import Callable, Optional

class EyeCareTimer:
    """
    Core timer implementation for the 20-20-20 rule.
    Tracks work sessions and triggers breaks at specified intervals.
    """
    def __init__(
        self, 
        work_duration: int = 20 * 60,  # 20 minutes in seconds
        break_duration: int = 20,      # 20 seconds
        on_break_start: Optional[Callable] = None,
        on_break_end: Optional[Callable] = None
    ):
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.on_break_start = on_break_start
        self.on_break_end = on_break_end
        
        self.is_running = False
        self.is_paused = False
        self.is_in_break = False
        self.timer_thread = None
        self.work_start_time = None
        self.break_start_time = None
        self.elapsed_work_time = 0
        self.pause_time = None
        self.last_activity_time = time.time()
        self.inactivity_threshold = 5 * 60  # 5 minutes in seconds
        self.break_ended_manually = False  # New flag to track manual end
        self.breaks_taken = 0  # Track number of breaks taken
    
    def start(self):
        """Start the timer."""
        if self.is_running:
            return
            
        self.is_running = True
        self.is_paused = False
        self.work_start_time = time.time()
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
    def pause(self):
        """Pause the timer."""
        if not self.is_running or self.is_paused:
            return
            
        self.is_paused = True
        self.pause_time = time.time()
        
    def resume(self):
        """Resume the timer from a paused state."""
        if not self.is_running or not self.is_paused:
            return
            
        if self.pause_time:
            pause_duration = time.time() - self.pause_time
            self.work_start_time += pause_duration
            self.break_start_time = None if not self.is_in_break else self.break_start_time + pause_duration
            self.pause_time = None
            
        self.is_paused = False
        
    def stop(self):
        """Stop the timer completely."""
        self.is_running = False
        self.is_paused = False
        self.is_in_break = False
        self.work_start_time = None
        self.elapsed_work_time = 0
        if self.timer_thread:
            self.timer_thread.join(timeout=1.0)
        
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity_time = time.time()
        
        if self.is_running and self.is_paused and self._is_paused_due_to_inactivity():
            self.resume()
    
    def manually_pause(self):
        """Pause the timer manually (user initiated)."""
        self.pause()
        self._manual_pause = True
        
    def _is_paused_due_to_inactivity(self):
        """Check if the current pause is due to inactivity."""
        return self.is_paused and not getattr(self, '_manual_pause', False)
        
    def _check_inactivity(self):
        """Check if user has been inactive beyond the threshold."""
        if time.time() - self.last_activity_time > self.inactivity_threshold:
            if self.is_running and not self.is_paused:
                self.pause()
                if hasattr(self, '_manual_pause'):
                    self._manual_pause = False
                return True
        return False
    
    def get_remaining_work_time(self):
        """Get the remaining time until the next break."""
        if not self.is_running or self.is_in_break:
            return 0
            
        if self.is_paused:
            elapsed = self.pause_time - self.work_start_time
        else:
            elapsed = time.time() - self.work_start_time
            
        remaining = max(0, self.work_duration - elapsed)
        return int(remaining)
    
    def get_remaining_break_time(self):
        """Get the remaining time in the current break."""
        if not self.is_running or not self.is_in_break or not self.break_start_time:
            return 0
            
        if self.is_paused:
            elapsed = self.pause_time - self.break_start_time
        else:
            elapsed = time.time() - self.break_start_time
            
        remaining = max(0, self.break_duration - elapsed)
        return int(remaining)
    
    def _run_timer(self):
        """Main timer loop running in a separate thread."""
        try:
            while self.is_running:
                if self.is_paused:
                    time.sleep(1)
                    continue
                    
                self._check_inactivity()
                
                current_time = time.time()
                
                if not self.is_in_break:
                    if self.work_start_time and current_time - self.work_start_time >= self.work_duration:
                        self.is_in_break = True
                        self.break_start_time = current_time
                        self.breaks_taken += 1  # Increment break counter
                        if self.on_break_start:
                            self.on_break_start()
                else:
                    if self.break_start_time and current_time - self.break_start_time >= self.break_duration:
                        if not self.break_ended_manually:  # Only trigger if not ended manually
                            self.is_in_break = False
                            self.work_start_time = current_time
                            if self.on_break_end:
                                self.on_break_end()  # Let notification handle the rest
                        self.break_ended_manually = False  # Reset flag
                
                time.sleep(0.5)
        except Exception as e:
            print(f"Error in timer thread: {e}")
    
    def end_break(self):
        """End the break and resume work cycle."""
        print("Ending break in timer")
        if not self.is_in_break:
            print("Not in break, ignoring end_break call")
            return
            
        self.is_in_break = False
        self.break_ended_manually = True  # Mark as manually ended
        self.work_start_time = time.time()
        
        # Call on_break_end callback if provided
        if self.on_break_end:
            try:
                self.on_break_end()
            except Exception as e:
                print(f"Error in break end callback: {e}")
        
    def get_session_stats(self):
        """Get statistics about the current session."""
        if not self.work_start_time:
            return {
                "session_duration": 0,
                "breaks_taken": 0,
                "current_status": "stopped"
            }
        
        current_time = time.time() if not self.is_paused else self.pause_time
        if self.work_start_time:
            total_duration = current_time - self.work_start_time
        else:
            total_duration = 0
        
        status = "in_break" if self.is_in_break else "paused" if self.is_paused else "working"
        
        return {
            "session_duration": int(total_duration),
            "breaks_taken": self.breaks_taken,
            "current_status": status
        }