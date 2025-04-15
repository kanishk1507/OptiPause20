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
        
        # Eye Health tab (new)
        self.eye_health_tab = self.setup_eye_health_tab()
        
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
    
    def setup_eye_health_tab(self):
        """Set up the eye health analytics tab."""
        # Create a new tab for eye health metrics
        eye_health_tab = QWidget()
        layout = QVBoxLayout(eye_health_tab)
        
        # Summary statistics
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_layout = QGridLayout(summary_frame)
        
        # Labels for statistics
        summary_layout.addWidget(QLabel("Eye Health Score:"), 0, 0)
        self.eye_health_score = QLabel("0%")
        self.eye_health_score.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.eye_health_score, 0, 1)
        
        summary_layout.addWidget(QLabel("Break Compliance:"), 1, 0)
        self.break_compliance = QLabel("0%")
        self.break_compliance.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.break_compliance, 1, 1)
        
        summary_layout.addWidget(QLabel("Recommended Daily Breaks:"), 2, 0)
        self.recommended_breaks = QLabel("0")
        self.recommended_breaks.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        summary_layout.addWidget(self.recommended_breaks, 2, 1)
        
        layout.addWidget(summary_frame)
        
        # Eye strain risk chart
        self.eye_strain_chart = MatplotlibCanvas(self, width=7, height=4)
        layout.addWidget(self.eye_strain_chart)
        
        # Recommendations section
        recommendations_frame = QFrame()
        recommendations_frame.setFrameShape(QFrame.Shape.StyledPanel)
        recommendations_layout = QVBoxLayout(recommendations_frame)
        
        recommendations_layout.addWidget(QLabel("Eye Health Recommendations:"))
        
        self.recommendations_text = QLabel("Start taking regular breaks to improve your eye health.")
        self.recommendations_text.setWordWrap(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        layout.addWidget(recommendations_frame)
        
        # Add the tab
        self.tabs.addTab(eye_health_tab, "Eye Health")
        
        return eye_health_tab
    
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
                    
                    # Update eye health tab
                    self._update_eye_health_analytics(df)
            else:
                # No data
                self._update_no_data_state()
                
        except Exception as e:
            print(f"Error refreshing analytics: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def _update_eye_health_analytics(self, df):
        """Update eye health analytics tab."""
        if df.empty:
            return
            
        # Calculate eye health metrics
        total_screen_time = df['screen_time'].sum()
        total_breaks = df['total_breaks'].sum()
        completed_breaks = df['completed_breaks'].sum()
        
        # Calculate break compliance
        compliance_rate = (completed_breaks / total_breaks * 100) if total_breaks > 0 else 0
        
        # Calculate eye health score (simple algorithm)
        # Higher compliance and more breaks relative to screen time = better score
        breaks_per_hour = completed_breaks / total_screen_time if total_screen_time > 0 else 0
        ideal_breaks_per_hour = 3  # Ideally 3 breaks per hour (20-20-20 rule)
        breaks_ratio = min(breaks_per_hour / ideal_breaks_per_hour, 1) if ideal_breaks_per_hour > 0 else 0
        
        health_score = (compliance_rate * 0.6) + (breaks_ratio * 40)  # 60% weight on compliance, 40% on break frequency
        health_score = min(health_score, 100)  # Cap at 100%
        
        # Update labels
        self.eye_health_score.setText(f"{health_score:.1f}%")
        self.break_compliance.setText(f"{compliance_rate:.1f}%")
        
        # Calculate recommended breaks
        avg_daily_screen_time = df['screen_time'].mean()
        recommended_daily_breaks = max(3, int(avg_daily_screen_time * ideal_breaks_per_hour))
        self.recommended_breaks.setText(f"{recommended_daily_breaks}")
        
        # Update recommendations based on metrics
        if health_score < 40:
            self.recommendations_text.setText(
                "Your eye health score is low. Try to take more regular breaks and complete the full 20 seconds "
                "for each break. Remember the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds."
            )
        elif health_score < 70:
            self.recommendations_text.setText(
                "You're doing okay, but could improve your eye health by taking more consistent breaks. "
                "Try to complete all scheduled breaks and consider reducing continuous screen time."
            )
        else:
            self.recommendations_text.setText(
                "Great job! You're maintaining good eye health habits. Keep up the good work and "
                "remember to blink frequently and stay hydrated for optimal eye health."
            )
        
        # Update eye strain risk chart
        self.eye_strain_chart.axes.clear()
        
        # Calculate daily eye strain risk based on screen time and breaks
        df['strain_risk'] = df['screen_time'] / (df['completed_breaks'] + 1) * 3
        df['strain_risk'] = df['strain_risk'].clip(0, 10)  # Scale from 0-10
        
        # Plot line chart
        ax = self.eye_strain_chart.axes
        ax.plot(df['date'], df['strain_risk'], color='#e74c3c', linewidth=2, marker='o')
        
        ax.set_title('Daily Eye Strain Risk (0-10)')
        ax.set_ylabel('Risk Level')
        ax.set_xlabel('Date')
        ax.set_ylim(0, 10)
        
        # Add a horizontal line for moderate risk
        ax.axhline(y=5, color='#f39c12', linestyle='--', alpha=0.7)
        
        # Add a horizontal line for high risk
        ax.axhline(y=7.5, color='#c0392b', linestyle='--', alpha=0.7)
        
        # Format x-axis dates
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ensure adequate spacing
        self.eye_strain_chart.fig.tight_layout()
        self.eye_strain_chart.draw()
    
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
        
        # Eye health tab
        self.eye_health_score.setText("0%")
        self.break_compliance.setText("0%")
        self.recommended_breaks.setText("0")
        
        self.eye_strain_chart.axes.clear()
        self.eye_strain_chart.axes.text(0.5, 0.5, "No data available", 
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       transform=self.eye_strain_chart.axes.transAxes)
        self.eye_strain_chart.draw()