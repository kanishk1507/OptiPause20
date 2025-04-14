# src/ui/notification.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class NotificationWindow(QWidget):
    """Transparent notification overlay for break reminders."""
    
    closed = pyqtSignal()
    
    # Modify the NotificationWindow initialization
    def __init__(self, parent=None):
        # Use fewer window flags to reduce chance of issues
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    
        # Reduce transparency if that might be causing issues
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
        # Add safety check for screen availability
        if self.screen() is None:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                self.setScreen(screen)
    
        # Set up the layout
        self.setup_ui()
    
        # Initialize timer for auto-close
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close)
    
        # Timer for countdown display
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_seconds = 20  # Default
        
    def setup_ui(self):
        """Set up the notification UI."""
        layout = QVBoxLayout()
        
        # Main content container with background
        container = QWidget()
        container.setObjectName("notificationContainer")
        container.setStyleSheet("""
            #notificationContainer {
                background-color: rgba(52, 73, 94, 0.9);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        container_layout = QVBoxLayout(container)
        
        # Title
        self.title_label = QLabel("Time for an Eye Break!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        container_layout.addWidget(self.title_label)
        
        # Instruction
        self.instruction_label = QLabel(
            "Look at something 20 feet away for 20 seconds"
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet("""
            color: white;
            font-size: 14px;
        """)
        container_layout.addWidget(self.instruction_label)
        
        # Countdown
        self.countdown_label = QLabel("20")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            margin: 15px 0;
        """)
        container_layout.addWidget(self.countdown_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.skip_button = QPushButton("Skip")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.8);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(231, 76, 60, 1.0);
            }
        """)
        self.skip_button.clicked.connect(self.close)
        
        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(46, 204, 113, 0.8);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(46, 204, 113, 1.0);
            }
        """)
        self.done_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.skip_button)
        buttons_layout.addWidget(self.done_button)
        
        container_layout.addLayout(buttons_layout)
        
        # Add container to main layout
        layout.addWidget(container)
        self.setLayout(layout)
        
        # Set fixed size
        self.setFixedSize(300, 200)
        
    def start_countdown(self, seconds=20):
        """Start the countdown timer."""
        self.countdown_seconds = seconds
        self.countdown_label.setText(str(seconds))
        self.countdown_timer.start(1000)  # 1 second interval
        
    def update_countdown(self):
        """Update the countdown display."""
        self.countdown_seconds -= 1
        self.countdown_label.setText(str(self.countdown_seconds))
        
        if self.countdown_seconds <= 0:
            self.countdown_timer.stop()
            self.close()
            
    # In notification.py, modify show_for_duration method
    def show_for_duration(self, seconds=20):
        """Show the notification for the specified duration."""
        try:
            self.start_countdown(seconds)
        
            # Center on primary screen
            screen_geometry = self.screen().geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2  # Center vertically instead of fixed 100px
            self.move(x, y)
        
            # Show the notification
            self.show()
            self.activateWindow()  # Make sure window gets focus
        except Exception as e:
            print(f"Error displaying notification: {e}")
            self.close()  # Close on error to prevent further issues
        
    def closeEvent(self, event):
        """Handle close event."""
        self.countdown_timer.stop()
        self.closed.emit()
        super().closeEvent(event)