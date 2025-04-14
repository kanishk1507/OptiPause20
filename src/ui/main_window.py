# src/ui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSystemTrayIcon, QMenu,
    QTabWidget, QGridLayout, QSlider, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QAction

import os 
from PyQt6.QtGui import QIcon


from .notification import NotificationWindow

class MainWindow(QMainWindow):
    """Main application window with settings and dashboard."""
    
    def __init__(self, app_controller):
        super().__init__()
        
        self.app_controller = app_controller
        self.notification = None
        
        self.setWindowTitle("OptiPause20")
        self.setMinimumSize(600, 400)
        
        # Step 1: Create tray_icon BEFORE using it
        self.tray_icon = QSystemTrayIcon(self)

        # Step 2: Set icon path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, 'resources', 'icons', 'app_icon.png')

        if not os.path.exists(icon_path):
            print(f"[ERROR] Icon file not found at: {icon_path}")
        else:
            icon = QIcon(icon_path)
            self.setWindowIcon(icon)
            self.tray_icon.setIcon(icon)

        # Step 3: Set window and tray icon
        self.setWindowIcon(QIcon(icon_path))
        self.tray_icon.setIcon(QIcon(icon_path))

        # Set up UI
        self.setup_ui()
        
        # Set up system tray
        self.setup_tray()
        
        # Update timer for UI refresh
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Set up the main window UI."""
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # Timer display
        timer_layout = QHBoxLayout()
        
        self.status_label = QLabel("Working")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        timer_layout.addWidget(self.status_label)
        
        self.time_label = QLabel("20:00")
        self.time_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.time_label, 1)
        
        dashboard_layout.addLayout(timer_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_pause_button = QPushButton("Pause")
        self.start_pause_button.clicked.connect(self.toggle_timer)
        control_layout.addWidget(self.start_pause_button)
        
      
        dashboard_layout.addLayout(control_layout)
        
        # Focus sound player
        sound_layout = QHBoxLayout()
        sound_layout.addWidget(QLabel("Focus Sounds:"))
        
        self.sound_selector = QComboBox()
        self.sound_selector.addItem("None")
        self.sound_selector.addItem("White Noise")
        self.sound_selector.addItem("Nature Sounds")
        self.sound_selector.addItem("Ambient Music")
        sound_layout.addWidget(self.sound_selector, 1)
        
        self.play_sound_button = QPushButton("Play")
        sound_layout.addWidget(self.play_sound_button)
        
        dashboard_layout.addLayout(sound_layout)
        
        # Daily stats
        dashboard_layout.addWidget(QLabel("Today's Statistics"))
            
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Screen Time:"), 0, 0)
        self.screen_time_label = QLabel("0 hours")
        stats_layout.addWidget(self.screen_time_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Breaks Taken:"), 1, 0)
        self.breaks_taken_label = QLabel("0")
        stats_layout.addWidget(self.breaks_taken_label, 1, 1)
        
        stats_layout.addWidget(QLabel("Current Streak:"), 2, 0)
        self.streak_label = QLabel("0 days")
        stats_layout.addWidget(self.streak_label, 2, 1)
        
        dashboard_layout.addLayout(stats_layout)
        
        # Add spacer to push everything up
        dashboard_layout.addStretch()
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Work duration setting
        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel("Work Duration:"))
        
        self.work_slider = QSlider(Qt.Orientation.Horizontal)
        self.work_slider.setMinimum(5)
        self.work_slider.setMaximum(60)
        self.work_slider.setValue(20)
        self.work_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.work_slider.setTickInterval(5)
        work_layout.addWidget(self.work_slider, 1)
        
        self.work_value_label = QLabel("20 minutes")
        work_layout.addWidget(self.work_value_label)
        
        settings_layout.addLayout(work_layout)
        
        # Break duration setting
        break_layout = QHBoxLayout()
        break_layout.addWidget(QLabel("Break Duration:"))
        
        self.break_slider = QSlider(Qt.Orientation.Horizontal)
        self.break_slider.setMinimum(5)
        self.break_slider.setMaximum(60)
        self.break_slider.setValue(20)
        self.break_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.break_slider.setTickInterval(5)
        break_layout.addWidget(self.break_slider, 1)
        
        self.break_value_label = QLabel("20 seconds")
        break_layout.addWidget(self.break_value_label)
        
        settings_layout.addLayout(break_layout)
        
        # Inactivity threshold
        inactivity_layout = QHBoxLayout()
        inactivity_layout.addWidget(QLabel("Inactivity Threshold:"))
        
        self.inactivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.inactivity_slider.setMinimum(1)
        self.inactivity_slider.setMaximum(15)
        self.inactivity_slider.setValue(5)
        self.inactivity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.inactivity_slider.setTickInterval(1)
        inactivity_layout.addWidget(self.inactivity_slider, 1)
        
        self.inactivity_value_label = QLabel("5 minutes")
        inactivity_layout.addWidget(self.inactivity_value_label)
        
        settings_layout.addLayout(inactivity_layout)
        
        # Other settings
        self.start_with_system = QCheckBox("Start with system")
        settings_layout.addWidget(self.start_with_system)
        
        self.minimize_to_tray = QCheckBox("Minimize to tray")
        self.minimize_to_tray.setChecked(True)
        settings_layout.addWidget(self.minimize_to_tray)
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_button)
        
        # Add spacer
        settings_layout.addStretch()
        
        # Add tabs to tab widget
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(settings_tab, "Settings")
        
        # Analytics tab (to be implemented)
        analytics_tab = QWidget()
        tabs.addTab(analytics_tab, "Analytics")
        
        # Add tab widget to main layout
        main_layout.addWidget(tabs)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Connect slider signals
        self.work_slider.valueChanged.connect(self.update_work_label)
        self.break_slider.valueChanged.connect(self.update_break_label)
        self.inactivity_slider.valueChanged.connect(self.update_inactivity_label)
    
    def setup_tray(self):
        """Set up system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Eye Care - 20-20-20 Rule")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        self.pause_action = QAction("Pause", self)
        self.pause_action.triggered.connect(self.toggle_timer)
        tray_menu.addAction(self.pause_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def update_work_label(self):
        """Update the work duration label when slider changes."""
        value = self.work_slider.value()
        self.work_value_label.setText(f"{value} minutes")
    
    def update_break_label(self):
        """Update the break duration label when slider changes."""
        value = self.break_slider.value()
        self.break_value_label.setText(f"{value} seconds")
    
    def update_inactivity_label(self):
        """Update the inactivity threshold label when slider changes."""
        value = self.inactivity_slider.value()
        self.inactivity_value_label.setText(f"{value} minutes")
    
    def toggle_timer(self):
        """Toggle between paused and running states."""
        if self.app_controller.timer.is_running:
            if self.app_controller.timer.is_paused:
                self.app_controller.resume_timer()
                self.start_pause_button.setText("Pause")
                self.pause_action.setText("Pause")
            else:
                self.app_controller.pause_timer()
                self.start_pause_button.setText("Resume")
                self.pause_action.setText("Resume")
        else:
            self.app_controller.start_timer()
            self.start_pause_button.setText("Pause")
            self.pause_action.setText("Pause")
    
    def save_settings(self):
        """Save the current settings."""
        # Get values
        work_duration = self.work_slider.value() * 60  # Convert to seconds
        break_duration = self.break_slider.value()
        inactivity_threshold = self.inactivity_slider.value() * 60  # Convert to seconds
        
        # Update database
        db = self.app_controller.db
        db.set_setting('work_duration', work_duration)
        db.set_setting('break_duration', break_duration)
        db.set_setting('inactivity_threshold', inactivity_threshold)
        db.set_setting('start_with_system', str(self.start_with_system.isChecked()).lower())
        db.set_setting('minimize_to_tray', str(self.minimize_to_tray.isChecked()).lower())
        
        # Update timer
        self.app_controller.timer.work_duration = work_duration
        self.app_controller.timer.break_duration = break_duration
        self.app_controller.timer.inactivity_threshold = inactivity_threshold
    
    def update_ui(self):
        """Update UI elements with current state."""
        timer = self.app_controller.timer
        
        # Update time display
        if timer.is_running:
            if timer.is_in_break:
                remaining = timer.get_remaining_break_time()
                self.status_label.setText("Break")
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            else:
                remaining = timer.get_remaining_work_time()
                if timer.is_paused:
                    self.status_label.setText("Paused")
                    self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
                else:
                    self.status_label.setText("Working")
                    self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            
            # Format time as MM:SS
            minutes = remaining // 60
            seconds = remaining % 60
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.status_label.setText("Stopped")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
            self.time_label.setText("--:--")
            
        # TODO: Update statistics
    
    def show_break_notification(self):
        """Show the break notification window."""
        try:
            # First, close existing notification if any
            if self.notification and self.notification.isVisible():
                self.notification.close()
                self.notification = None
        
            # Create new notification with proper parent
            self.notification = NotificationWindow(parent=self)
            self.notification.closed.connect(self.on_notification_closed)
        
            # Get break duration
            break_duration = self.app_controller.timer.break_duration
        
            # Show notification
            self.notification.show_for_duration(break_duration)
        
        except Exception as e:
            print(f"Error showing notification: {e}")

        # Ensure timer continues even if notification fails
        if self.app_controller and self.app_controller.timer:
            self.app_controller.timer.is_in_break = True

    def hide_break_notification(self):
        """Hide the break notification window."""
        if self.notification:
            if self.notification.isVisible():
                self.notification.close()
                self.notification = None
    
    def on_notification_closed(self):
        """Handle notification window close event."""
        # This is called when the user manually closes the notification
        # or when the automatic timer expires
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.minimize_to_tray.isChecked():
            event.ignore()
            self.hide()
        else:
            self.tray_icon.hide()
            event.accept()