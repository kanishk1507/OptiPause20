from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont

class NotificationWindow(QWidget):
    """Simplified notification overlay for break reminders."""
    
    closed = pyqtSignal()
    break_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.WindowStaysOnTopHint)
        
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            self.setScreen(screen)
        
        self.setup_ui()
        
        self.countdown_timer = QTimer(self)
        self.countdown_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.countdown_timer.moveToThread(QThread.currentThread())
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_seconds = 20
        
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
        self.skip_button.setStyleSheet("background-color: red; color: white; padding: 8px;")
        self.skip_button.clicked.connect(self.on_break_end)
        
        self.done_button = QPushButton("Done")
        self.done_button.setStyleSheet("background-color: green; color: white; padding: 8px;")
        self.done_button.clicked.connect(self.on_break_end)
        
        buttons_layout.addWidget(self.skip_button)
        buttons_layout.addWidget(self.done_button)
        
        container_layout.addLayout(buttons_layout)
        
        layout.addWidget(container)
        self.setLayout(layout)
        
        self.setFixedSize(300, 200)
        
    def start_countdown(self, seconds=20):
        print("Starting countdown")
        self.countdown_seconds = seconds
        self.countdown_label.setText(str(seconds))
        self.countdown_timer.start(1000)
        
    def update_countdown(self):
        print(f"Updating countdown: {self.countdown_seconds}")
        if self.countdown_seconds > 0:
            self.countdown_seconds -= 1
            self.countdown_label.setText(str(self.countdown_seconds))
        else:
            print("Countdown reached 0, preparing to close")
            self.countdown_timer.stop()
            self.on_break_end()
            print("Break end signal emitted, closing initiated")
            
    def show_for_duration(self, seconds=20):
        print(f"Showing notification for {seconds} seconds")
        try:
            self.start_countdown(seconds)
            
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
                print(f"Notification positioned at x={x}, y={y}")
            else:
                self.move(100, 100)
                print("Using fallback position at 100, 100")
            
            self.show()
            print("Notification shown")
            self.raise_()
            self.activateWindow()
            print("Notification activated")
            from PyQt6.QtCore import QEventLoop
            loop = QEventLoop()
            QTimer.singleShot(1000, loop.quit)  # 1000ms delay
            loop.exec()
            print("Delay completed, window should be visible")
            # Hack to keep window visible
            self.setWindowModality(Qt.WindowModality.ApplicationModal)  # Force visibility
        except Exception as e:
            print(f"Error displaying notification: {e}")
            self.close()
        
    def on_break_end(self):
        """Handle break end (manual or countdown finish)."""
        print("Break ended manually or by countdown")
        if self.countdown_timer.isActive() and QThread.currentThread() == self.thread():
            self.countdown_timer.stop()
            print("Countdown timer stopped")
        self.break_ended.emit()
        self.close()
        print("Notification closed")
        
    def closeEvent(self, event):
        print("Closing notification event triggered")
        try:
            if self.countdown_timer.isActive() and QThread.currentThread() == self.thread():
                self.countdown_timer.stop()
                print("Countdown timer stopped in closeEvent")
            self.closed.emit()
            print("Closed signal emitted")
        except Exception as e:
            print(f"Error in closeEvent: {e}")
        super().closeEvent(event)