from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

class NotificationWindow(QWidget):
    """Simplified notification overlay for break reminders."""
    
    closed = pyqtSignal()
    break_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(None, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        
        # Set window flags to ensure it stays on top and has no frame
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.Tool)
        
        self.setup_ui()
        
        # Setup countdown timer
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_seconds = 20
        
        # Setup auto-close timer
        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.on_break_end)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        container = QWidget()
        container.setStyleSheet("background-color: #34495e; border: 2px solid white;")
        
        container_layout = QVBoxLayout(container)
        
        self.title_label = QLabel("Time for an Eye Break!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        container_layout.addWidget(self.title_label)
        
        self.countdown_label = QLabel("20")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")
        container_layout.addWidget(self.countdown_label)
        
        buttons_layout = QHBoxLayout()
        
        self.skip_button = QPushButton("Skip")
        self.skip_button.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
        self.skip_button.clicked.connect(self.on_break_end)
        
        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px;")
        self.done_button.clicked.connect(self.on_break_end)
        
        buttons_layout.addWidget(self.skip_button)
        buttons_layout.addWidget(self.done_button)
        
        container_layout.addLayout(buttons_layout)
        
        layout.addWidget(container)
        self.setLayout(layout)
        
        self.setFixedSize(300, 200)
        
    def start_countdown(self, seconds=20):
        """Start the countdown timer."""
        print("Starting countdown")
        self.countdown_seconds = seconds
        self.countdown_label.setText(str(seconds))
        self.countdown_timer.start(1000)
        
        # Also start the auto-close timer as a backup
        self.close_timer.start((seconds + 1) * 1000)  # Add 1 second buffer
        
    def update_countdown(self):
        """Update the countdown display."""
        if self.countdown_seconds > 0:
            self.countdown_seconds -= 1
            self.countdown_label.setText(str(self.countdown_seconds))
        else:
            self.countdown_timer.stop()
            # Use QTimer.singleShot to ensure on_break_end is called in the event loop
            QTimer.singleShot(0, self.on_break_end)
        
    def show_for_duration(self, seconds=20):
        """Show the notification for the specified duration."""
        print(f"Showing notification for {seconds} seconds")
        try:
            # Position in center of screen
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            
            # Start countdown and show window
            self.start_countdown(seconds)
            self.show()
            self.raise_()
            self.activateWindow()
        except Exception as e:
            print(f"Error displaying notification: {e}")
            self.close()
        
    def on_break_end(self):
        """Handle break end (manual or countdown finish)."""
        print("Break ended, closing notification")
        # Stop timers
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        if self.close_timer.isActive():
            self.close_timer.stop()
            
        # Emit signal before closing
        try:
            self.break_ended.emit()
        except RuntimeError as e:
            print(f"Error emitting break_ended signal: {e}")
        
        # Close window using singleShot to avoid recursion
        QTimer.singleShot(0, self.close)
        
    def closeEvent(self, event):
        """Handle window close event."""
        print("Notification close event triggered")
        # Stop timers
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        if self.close_timer.isActive():
            self.close_timer.stop()
            
        # Emit signal
        try:
            self.closed.emit()
        except RuntimeError as e:
            print(f"Error emitting closed signal: {e}")
        
        # Accept the close event
        event.accept()