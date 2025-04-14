# src/ui/analytics_view.py
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta, date
import calendar

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QTabWidget, QScrollArea, QFrame, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class MatplotlibCanvas(FigureCanvas):
    """Canvas for matplotlib plots."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # Set figure background to transparent
        self.fig.patch.set_alpha(0.0)
        
        # Apply some styling to plots
        plt.style.use('seaborn-v0_8-whitegrid')

class AnalyticsView(QWidget):
    """Analytics view showing statistics and charts."""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the analytics UI."""
        main_layout = QVBoxLayout(self)
        
        # Time range selector
        range_layout = QHBoxLayout()
        
        range_layout.addWidget(QLabel("Time Range:"))
        
        self.range_selector = QComboBox()
        self.range_selector.addItems(["Last 7 Days", "Last 30 Days", "Current Month", "All Time"])
        self.range_selector.currentIndexChanged.connect(self.refresh_analytics)
        range_layout.addWidget(self.range_selector)
        
        range_layout.addStretch()
        
        main_layout.addLayout(range_layout)
        
        # Tabs for different analytics views
        self.tabs = QTabWidget()
        
        # Screen time tab
        self.screen_time_tab = QWidget()
        self.setup_screen_time_tab()
        self.tabs.addTab(self.screen_time_tab, "Screen Time")
        
        # Breaks tab
        self.breaks_tab = QWidget()
        self.setup_breaks_tab()
        self.tabs.addTab(self.breaks_tab, "Breaks")
        
        # Streak tab
        self.streak_tab = QWidget()
        self.setup_streak_tab()
        self.tabs.addTab(self.streak_tab, "Streak")
        
        main_layout.addWidget(self.tabs)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_analytics)
        main_layout.addWidget(refresh_button)
        
        # Initial data load
        self.refresh_analytics()
    
    def setup_screen_time_tab(self):
        """Set up the screen time analytics tab."""
        layout = QVBoxLayout(self.screen_time_tab)
        
        # Summary statistics
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_layout = QGridLayout(summary_frame)
        
        # Labels for statistics
        summary_layout.addWidget(QLabel("Total Screen Time:"), 0, 0)
        self.total_screen_time = QLabel("0 hours")
        self.total_screen_time.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.total_screen_time, 0, 1)
        
        summary_layout.addWidget(QLabel("Daily Average:"), 1, 0)
        self.avg_screen_time = QLabel("0 hours")
        self.avg_screen_time.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.avg_screen_time, 1, 1)
        
        summary_layout.addWidget(QLabel("Longest Day:"), 2, 0)
        self.max_screen_time = QLabel("0 hours (N/A)")
        self.max_screen_time.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.max_screen_time, 2, 1)
        
        layout.addWidget(summary_frame)
        
        # Screen time chart
        self.screen_time_chart = MatplotlibCanvas(self, width=7, height=4)
        layout.addWidget(self.screen_time_chart)
    
    def setup_breaks_tab(self):
        """Set up the breaks analytics tab."""
        layout = QVBoxLayout(self.breaks_tab)
        
        # Summary statistics
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_layout = QGridLayout(summary_frame)
        
        # Labels for statistics
        summary_layout.addWidget(QLabel("Total Breaks:"), 0, 0)
        self.total_breaks = QLabel("0")
        self.total_breaks.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.total_breaks, 0, 1)
        
        summary_layout.addWidget(QLabel("Completed Breaks:"), 1, 0)
        self.completed_breaks = QLabel("0")
        self.completed_breaks.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.completed_breaks, 1, 1)
        
        summary_layout.addWidget(QLabel("Completion Rate:"), 2, 0)
        self.break_completion_rate = QLabel("0%")
        self.break_completion_rate.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.break_completion_rate, 2, 1)
        
        layout.addWidget(summary_frame)
        
        # Breaks chart
        self.breaks_chart = MatplotlibCanvas(self, width=7, height=4)
        layout.addWidget(self.breaks_chart)
    
    def setup_streak_tab(self):
        """Set up the streak analytics tab."""
        layout = QVBoxLayout(self.streak_tab)
        
        # Current streak info
        current_streak_frame = QFrame()
        current_streak_frame.setFrameShape(QFrame.Shape.StyledPanel)
        current_streak_layout = QVBoxLayout(current_streak_frame)
        
        self.current_streak_label = QLabel("Current Streak: 0 days")
        self.current_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_streak_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        current_streak_layout.addWidget(self.current_streak_label)
        
        self.longest_streak_label = QLabel("Longest Streak: 0 days")
        self.longest_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.longest_streak_label.setFont(QFont("Arial", 14))
        current_streak_layout.addWidget(self.longest_streak_label)
        
        layout.addWidget(current_streak_frame)
        
        # Calendar view (streak calendar)
        self.streak_calendar = MatplotlibCanvas(self, width=7, height=5)
        layout.addWidget(self.streak_calendar)
        
        # Streak history chart
        self.streak_chart = MatplotlibCanvas(self, width=7, height=4)
        layout.addWidget(self.streak_chart)
    
    def refresh_analytics(self):
        """Refresh all analytics data and charts."""
        try:
            # Get date range based on selection
            date_range = self._get_selected_date_range()
            
            # Get data from database
            stats_data = self.db.get_screen_time_stats(days=date_range)
            
            # Convert to pandas DataFrame for easier analysis
            if stats_data:
                df = pd.DataFrame([
                    {
                        'date': row['date'],
                        'screen_time': row['total_work_seconds'] / 3600.0,  # Convert to hours
                        'total_breaks': row['total_breaks'],
                        'completed_breaks': row['completed_breaks']
                    }
                    for row in stats_data
                ])
                
                # Sort by date
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Update screen time tab
                    self._update_screen_time_analytics(df)
                    
                    # Update breaks tab
                    self._update_breaks_analytics(df)
                    
                    # Get streak data and update streak tab
                    self._update_streak_analytics()
            else:
                # No data
                self._update_no_data_state()
                
        except Exception as e:
            print(f"Error refreshing analytics: {e}")
    
    def _get_selected_date_range(self):
        """Get the number of days to look back based on selection."""
        selection = self.range_selector.currentText()
        
        if selection == "Last 7 Days":
            return 7
        elif selection == "Last 30 Days":
            return 30
        elif selection == "Current Month":
            # Calculate days in current month
            today = datetime.now()
            _, days_in_month = calendar.monthrange(today.year, today.month)
            return days_in_month
        else:  # All Time
            return 365  # Just return a large number
    
    def _update_screen_time_analytics(self, df):
        """Update screen time analytics tab."""
        if df.empty:
            return
            
        # Calculate summary statistics
        total_hours = df['screen_time'].sum()
        avg_hours = df['screen_time'].mean()
        max_day_idx = df['screen_time'].idxmax() if len(df) > 0 else None
        
        # Update labels
        self.total_screen_time.setText(f"{total_hours:.1f} hours")
        self.avg_screen_time.setText(f"{avg_hours:.1f} hours per day")
        
        if max_day_idx is not None:
            max_date = df.loc[max_day_idx, 'date'].strftime('%Y-%m-%d')
            max_hours = df.loc[max_day_idx, 'screen_time']
            self.max_screen_time.setText(f"{max_hours:.1f} hours ({max_date})")
        
        # Update chart
        self.screen_time_chart.axes.clear()
        
        # Plot bar chart
        ax = self.screen_time_chart.axes
        ax.bar(df['date'], df['screen_time'], color='#3498db', alpha=0.7)
        ax.set_title('Daily Screen Time')
        ax.set_ylabel('Hours')
        ax.set_xlabel('Date')
        
        # Format x-axis dates
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ensure adequate spacing
        self.screen_time_chart.fig.tight_layout()
        self.screen_time_chart.draw()
    
    def _update_breaks_analytics(self, df):
        """Update breaks analytics tab."""
        if df.empty:
            return
            
        # Calculate summary statistics
        total_breaks = df['total_breaks'].sum()
        completed_breaks = df['completed_breaks'].sum()
        completion_rate = (completed_breaks / total_breaks * 100) if total_breaks > 0 else 0
        
        # Update labels
        self.total_breaks.setText(f"{total_breaks}")
        self.completed_breaks.setText(f"{completed_breaks}")
        self.break_completion_rate.setText(f"{completion_rate:.1f}%")
        
        # Update chart
        self.breaks_chart.axes.clear()
        
        # Plot stacked bar chart
        ax = self.breaks_chart.axes
        
        # Calculate skipped breaks
        df['skipped_breaks'] = df['total_breaks'] - df['completed_breaks']
        
        # Create stacked bar
        ax.bar(df['date'], df['completed_breaks'], color='#2ecc71', alpha=0.7, label='Completed')
        ax.bar(df['date'], df['skipped_breaks'], bottom=df['completed_breaks'], color='#e74c3c', alpha=0.7, label='Skipped')
        
        ax.set_title('Daily Breaks')
        ax.set_ylabel('Number of Breaks')
        ax.set_xlabel('Date')
        ax.legend()
        
        # Format x-axis dates
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ensure adequate spacing
        self.breaks_chart.fig.tight_layout()
        self.breaks_chart.draw()
    
    def _update_streak_analytics(self):
        """Update streak analytics tab."""
        # Get streak data
        streak_data = self.db.get_streak_data(days=90)  # Up to 90 days
        
        if not streak_data:
            return
            
        # Convert to pandas DataFrame
        df = pd.DataFrame([
            {
                'date': row['date'],
                'total_breaks': row['total_breaks'],
                'completed_breaks': row['completed_breaks'],
                'has_activity': row['total_breaks'] > 0
            }
            for row in streak_data
        ])
        
        # Sort by date
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate current streak
            current_streak, longest_streak = self._calculate_streaks(df)
            
            # Update streak labels
            self.current_streak_label.setText(f"Current Streak: {current_streak} days")
            self.longest_streak_label.setText(f"Longest Streak: {longest_streak} days")
            
            # Update streak calendar
            self._draw_streak_calendar(df)
            
            # Update streak chart
            self._draw_streak_chart(df)
    
    def _calculate_streaks(self, df):
        """Calculate current and longest streaks."""
        # A day is considered part of streak if user took at least one break
        df['in_streak'] = df['has_activity'] & (df['completed_breaks'] > 0)
        
        # Ensure data is sorted by date
        df = df.sort_values('date')
        
        # Fill in missing dates with False values
        if len(df) >= 2:
            date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
            df = df.set_index('date').reindex(date_range).fillna({'in_streak': False}).reset_index()
            df = df.rename(columns={'index': 'date'})
        
        # Calculate current streak
        current_streak = 0
        # Start from the most recent day and count backwards
        for i in range(len(df)-1, -1, -1):
            if df.iloc[i]['in_streak']:
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        streak_lengths = []
        current_length = 0
        
        for _, row in df.iterrows():
            if row['in_streak']:
                current_length += 1
            else:
                streak_lengths.append(current_length)
                current_length = 0
        
        # Add the last streak
        streak_lengths.append(current_length)
        
        longest_streak = max(streak_lengths) if streak_lengths else 0
        
        return current_streak, longest_streak
    
    def _draw_streak_calendar(self, df):
        """Draw a GitHub-style streak calendar."""
        self.streak_calendar.axes.clear()
        ax = self.streak_calendar.axes
        
        # Get today and find the start of the current week (Monday)
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())
        
        # Go back for a number of complete weeks
        num_weeks = 8  # 8 weeks history
        start_date = start_date - timedelta(weeks=num_weeks-1)
        
        # Create a range of dates
        dates = [start_date + timedelta(days=i) for i in range(num_weeks * 7)]
        
        # Create a 7x8 grid for weeks (y-axis) and days (x-axis)
        activity_grid = []
        
        for week in range(num_weeks):
            week_data = []
            for day in range(7):  # 0=Monday, 6=Sunday
                current_date = start_date + timedelta(weeks=week, days=day)
                
                # Check if this date is in our data
                date_str = current_date.strftime('%Y-%m-%d')
                
                matching_rows = df[df['date'].dt.strftime('%Y-%m-%d') == date_str]
                
                if not matching_rows.empty:
                    row = matching_rows.iloc[0]
                    if row['has_activity'] and row['completed_breaks'] > 0:
                        # Scale intensity based on break completion rate
                        completion_rate = row['completed_breaks'] / row['total_breaks'] if row['total_breaks'] > 0 else 0
                        intensity = 0.3 + 0.7 * completion_rate  # Scale from 0.3 to 1.0
                    else:
                        intensity = 0.1  # Low intensity for days with activity but no completed breaks
                else:
                    intensity = 0  # No activity
                
                week_data.append(intensity)
            activity_grid.append(week_data)
        
        # Plot as a heatmap
        # Transpose the grid to match the expected orientation
        activity_grid = list(map(list, zip(*activity_grid)))
        
        # Create the heatmap
        im = ax.imshow(activity_grid, cmap='YlGn', aspect='auto', vmin=0, vmax=1)
        
        # Configure axes
        ax.set_xticks(range(num_weeks))
        ax.set_xticklabels([f'W{w+1}' for w in range(num_weeks)])
        
        ax.set_yticks(range(7))
        ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        
        ax.set_title('Activity Streak Calendar')
        
        # Add grid lines
        ax.grid(which='major', color='w', linestyle='-', linewidth=1.5)
        
        # Ensure adequate spacing
        self.streak_calendar.fig.tight_layout()
        self.streak_calendar.draw()
    
    def _draw_streak_chart(self, df):
        """Draw a chart showing streak history."""
        self.streak_chart.axes.clear()
        ax = self.streak_chart.axes
        
        # Calculate daily streak values (how many consecutive days up to that point)
        streaks = []
        current_streak = 0
        
        # Ensure data is sorted by date
        df = df.sort_values('date')
        
        # Fill in missing dates
        if len(df) >= 2:
            date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
            filled_df = df.set_index('date').reindex(date_range).reset_index()
            filled_df = filled_df.rename(columns={'index': 'date'})
            filled_df['has_activity'] = filled_df['has_activity'].fillna(False)
            filled_df['completed_breaks'] = filled_df['completed_breaks'].fillna(0)
        else:
            filled_df = df
        
        # Calculate streak value for each day
        for _, row in filled_df.iterrows():
            if row['has_activity'] and row['completed_breaks'] > 0:
                current_streak += 1
            else:
                current_streak = 0
            streaks.append(current_streak)
        
        # Plot the streak values
        ax.plot(filled_df['date'], streaks, color='#27ae60', linewidth=2)
        ax.fill_between(filled_df['date'], streaks, alpha=0.3, color='#27ae60')
        
        ax.set_title('Streak History')
        ax.set_ylabel('Days')
        ax.set_xlabel('Date')
        
        # Format x-axis dates
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ensure adequate spacing
        self.streak_chart.fig.tight_layout()
        self.streak_chart.draw()
    
    def _update_no_data_state(self):
        """Update UI to show no data message."""
        # Screen time tab
        self.total_screen_time.setText("0 hours")
        self.avg_screen_time.setText("0 hours per day")
        self.max_screen_time.setText("0 hours (N/A)")
        
        self.screen_time_chart.axes.clear()
        self.screen_time_chart.axes.text(0.5, 0.5, "No data available", 
                                         horizontalalignment='center',
                                         verticalalignment='center',
                                         transform=self.screen_time_chart.axes.transAxes)
        self.screen_time_chart.draw()
        
        # Breaks tab
        self.total_breaks.setText("0")
        self.completed_breaks.setText("0")
        self.break_completion_rate.setText("0%")
        
        self.breaks_chart.axes.clear()
        self.breaks_chart.axes.text(0.5, 0.5, "No data available", 
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    transform=self.breaks_chart.axes.transAxes)
        self.breaks_chart.draw()
        
        # Streak tab
        self.current_streak_label.setText("Current Streak: 0 days")
        self.longest_streak_label.setText("Longest Streak: 0 days")
        
        self.streak_calendar.axes.clear()
        self.streak_calendar.axes.text(0.5, 0.5, "No data available", 
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       transform=self.streak_calendar.axes.transAxes)
        self.streak_calendar.draw()
        
        self.streak_chart.axes.clear()
        self.streak_chart.axes.text(0.5, 0.5, "No data available", 
                                    horizontalalignment='center',
                                    verticalalignment='center',
                                    transform=self.streak_chart.axes.transAxes)
        self.streak_chart.draw()


# src/ui/streak_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCalendarWidget, 
    QProgressBar, QFrame, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QPalette, QFont, QTextCharFormat

from datetime import datetime, timedelta

class StreakView(QWidget):
    """Widget for displaying user's streak information."""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the streak view UI."""
        layout = QVBoxLayout(self)
        
        # Current streak display
        streak_frame = QFrame()
        streak_frame.setFrameShape(QFrame.Shape.StyledPanel)
        streak_layout = QVBoxLayout(streak_frame)
        
        self.streak_label = QLabel("Current Streak: 0 days")
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.streak_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        streak_layout.addWidget(self.streak_label)
        
        self.streak_desc = QLabel("Keep using the app daily and taking breaks!")
        self.streak_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        streak_layout.addWidget(self.streak_desc)
        
        layout.addWidget(streak_frame)
        
        # Progress to next milestone
        milestone_frame = QFrame()
        milestone_layout = QVBoxLayout(milestone_frame)
        
        milestone_layout.addWidget(QLabel("Progress to next milestone:"))
        
        self.milestone_progress = QProgressBar()
        self.milestone_progress.setMinimum(0)
        self.milestone_progress.setMaximum(100)
        self.milestone_progress.setValue(0)
        milestone_layout.addWidget(self.milestone_progress)
        
        self.milestone_label = QLabel("0/7 days")
        self.milestone_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        milestone_layout.addWidget(self.milestone_label)
        
        layout.addWidget(milestone_frame)
        
        # Calendar view
        calendar_frame = QFrame()
        calendar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        calendar_layout = QVBoxLayout(calendar_frame)
        
        calendar_layout.addWidget(QLabel("Your Activity Calendar:"))
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        calendar_layout.addWidget(self.calendar)
        
        layout.addWidget(calendar_frame)
        
        # Streak statistics
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout(stats_frame)
        
        # Longest streak
        longest_streak_layout = QVBoxLayout()
        self.longest_streak_value = QLabel("0")
        self.longest_streak_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.longest_streak_value.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        longest_streak_layout.addWidget(self.longest_streak_value)
        
        longest_streak_label = QLabel("Longest Streak")
        longest_streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        longest_streak_layout.addWidget(longest_streak_label)
        
        stats_layout.addLayout(longest_streak_layout)
        
        # Total active days
        active_days_layout = QVBoxLayout()
        self.active_days_value = QLabel("0")
        self.active_days_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_days_value.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        active_days_layout.addWidget(self.active_days_value)
        
        active_days_label = QLabel("Total Active Days")
        active_days_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        active_days_layout.addWidget(active_days_label)
        
        stats_layout.addLayout(active_days_layout)
        
        # Perfect days (all breaks taken)
        perfect_days_layout = QVBoxLayout()
        self.perfect_days_value = QLabel("0")
        self.perfect_days_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.perfect_days_value.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        perfect_days_layout.addWidget(self.perfect_days_value)
        
        perfect_days_label = QLabel("Perfect Days")
        perfect_days_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        perfect_days_layout.addWidget(perfect_days_label)
        
        stats_layout.addLayout(perfect_days_layout)
        
        layout.addWidget(stats_frame)
        
        # Load current streak data
        self.update_streak_data()
    
    def update_streak_data(self):
        """Update streak data and UI."""
        try:
            # Get streak data from database
            streak_data = self.db.get_streak_data(days=60)  # Get last 60 days
            
            if not streak_data:
                return
                
            # Calculate streak metrics
            current_streak, longest_streak, active_days, perfect_days = self._calculate_streak_metrics(streak_data)
            
            # Update UI
            self.streak_label.setText(f"Current Streak: {current_streak} days")
            
            # Update streak description
            if current_streak == 0:
                self.streak_desc.setText("Start your streak by taking breaks today!")
            elif current_streak < 3:
                self.streak_desc.setText("Keep going! Your streak is just beginning.")
            elif current_streak < 7:
                self.streak_desc.setText("Great job! You're building a healthy habit.")
            elif current_streak < 14:
                self.streak_desc.setText("Fantastic! You're consistent with your eye care.")
            elif current_streak < 30:
                self.streak_desc.setText("Impressive streak! Your eyes thank you.")
            else:
                self.streak_desc.setText("Amazing dedication to eye care! Keep it up!")
            
            # Update next milestone progress
            milestone_days = self._get_next_milestone(current_streak)
            current_progress = current_streak % milestone_days if milestone_days > 0 else 0
            progress_percentage = (current_progress / milestone_days) * 100 if milestone_days > 0 else 0
            
            self.milestone_progress.setValue(int(progress_percentage))
            self.milestone_label.setText(f"{current_progress}/{milestone_days} days")
            
            # Update calendar with activity data
            self._update_calendar(streak_data)
            
            # Update streak statistics
            self.longest_streak_value.setText(str(longest_streak))
            self.active_days_value.setText(str(active_days))
            self.perfect_days_value.setText(str(perfect_days))
            
        except Exception as e:
            print(f"Error updating streak data: {e}")
    
    def _calculate_streak_metrics(self, streak_data):
        """Calculate streak metrics from database data."""
        # Convert to dictionary with date as key for easier lookup
        activity_dict = {row['date']: row for row in streak_data}
        
        # Get dates sorted in descending order (newest first)
        dates = sorted(activity_dict.keys(), reverse=True)
        
        # Calculate current streak (consecutive days with activity)
        current_streak = 0
        today = datetime.now().date().isoformat()
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat

       
    # Check if user has activity today
        if today in activity_dict and activity_dict[today]['completed_breaks'] > 0:
            current_streak = 1
        
            # Look back through previous days
            current_date = yesterday
            day_offset = 2
        
            while current_date in activity_dict:
                if activity_dict[current_date]['completed_breaks'] > 0:
                    current_streak += 1
                    current_date = (datetime.now().date() - timedelta(days=day_offset)).isoformat()
                    day_offset += 1
                else:
                    break
        elif yesterday in activity_dict and activity_dict[yesterday]['completed_breaks'] > 0:
            # If no activity today but had activity yesterday, count from yesterday
            current_streak = 1
        
            # Look back through previous days
            day_offset = 2
            current_date = (datetime.now().date() - timedelta(days=day_offset)).isoformat()
        
            while current_date in activity_dict:
                if activity_dict[current_date]['completed_breaks'] > 0:
                    current_streak += 1
                    day_offset += 1
                    current_date = (datetime.now().date() - timedelta(days=day_offset)).isoformat()
                else:
                    break
    
        # Calculate longest streak
        longest_streak = 0
        current_run = 0
        previous_date = None
    
        for date_str in sorted(activity_dict.keys()):  # Sort in ascending order for this calculation
            date_obj = datetime.fromisoformat(date_str).date()
        
            # Check if day had completed breaks
            if activity_dict[date_str]['completed_breaks'] > 0:
                # Check if this is consecutive with previous date
                if previous_date is not None and (date_obj - previous_date).days == 1:
                    current_run += 1
                else:
                    current_run = 1
                
                # Update longest streak if current run is longer
                longest_streak = max(longest_streak, current_run)
                previous_date = date_obj
            else:
                # Break in streak
                current_run = 0
                previous_date = None
        
        # Calculate total active days (days with at least one completed break)
        active_days = sum(1 for date in activity_dict if activity_dict[date]['completed_breaks'] > 0)
        
        # Calculate perfect days (all scheduled breaks were completed)
        perfect_days = sum(1 for date in activity_dict 
                        if activity_dict[date]['total_breaks'] > 0 
                        and activity_dict[date]['completed_breaks'] == activity_dict[date]['total_breaks'])
        
        return current_streak, longest_streak, active_days, perfect_days

    def _get_next_milestone(self, current_streak):
        """Get the next milestone based on current streak."""
        milestones = [3, 7, 14, 30, 60, 90, 180, 365]
        
        for milestone in milestones:
            if current_streak < milestone:
                return milestone
        
        # If beyond all milestones, set next milestone 100 days away
        return ((current_streak // 100) + 1) * 100

    def _update_calendar(self, streak_data):
        """Update calendar with activity data."""
        # Create a format for days with activity
        active_format = QTextCharFormat()
        active_format.setBackground(QColor(46, 204, 113, 100))  # Light green background
        
        # Create a format for perfect days
        perfect_format = QTextCharFormat()
        perfect_format.setBackground(QColor(46, 204, 113, 220))  # Darker green background
        
        # Create a format for days with activity but missed breaks
        partial_format = QTextCharFormat()
        partial_format.setBackground(QColor(241, 196, 15, 100))  # Light yellow background
        
        # Reset all date formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Apply formatting to days based on activity
        for row in streak_data:
            date_obj = datetime.fromisoformat(row['date']).date()
            qt_date = QDate(date_obj.year, date_obj.month, date_obj.day)
            
            if row['completed_breaks'] > 0:
                if row['completed_breaks'] == row['total_breaks'] and row['total_breaks'] > 0:
                    # Perfect day (all breaks taken)
                    self.calendar.setDateTextFormat(qt_date, perfect_format)
                else:
                    # Partial day (some breaks taken)
                    self.calendar.setDateTextFormat(qt_date, partial_format)
            elif row['total_breaks'] > 0:
                # Day with activity but no breaks taken
                self.calendar.setDateTextFormat(qt_date, active_format)