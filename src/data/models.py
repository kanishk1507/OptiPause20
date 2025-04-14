from datetime import datetime, date
from typing import List, Dict, Any, Optional

class Session:
    """Represents a work session."""
    def __init__(
        self,
        id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        duration_seconds: Optional[int] = None,
        breaks_taken: int = 0
    ):
        self.id = id
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.duration_seconds = duration_seconds
        self.breaks_taken = breaks_taken
        
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Session':
        """Create a Session object from a database row."""
        return cls(
            id=row['id'],
            start_time=datetime.fromisoformat(row['start_time']),
            end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
            duration_seconds=row['duration_seconds'],
            breaks_taken=row['breaks_taken']
        )

class Break:
    """Represents a break during a work session."""
    def __init__(
        self,
        id: Optional[int] = None,
        session_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        duration_seconds: Optional[int] = None,
        completed: bool = False
    ):
        self.id = id
        self.session_id = session_id
        self.start_time = start_time or datetime.now()
        self.duration_seconds = duration_seconds
        self.completed = completed
        
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Break':
        """Create a Break object from a database row."""
        return cls(
            id=row['id'],
            session_id=row['session_id'],
            start_time=datetime.fromisoformat(row['start_time']),
            duration_seconds=row['duration_seconds'],
            completed=bool(row['completed'])
        )

class DailyStats:
    """Represents aggregated statistics for a single day."""
    def __init__(
        self,
        date: date,
        total_work_seconds: int = 0,
        total_breaks: int = 0,
        completed_breaks: int = 0,
        longest_session_seconds: int = 0
    ):
        self.date = date
        self.total_work_seconds = total_work_seconds
        self.total_breaks = total_breaks
        self.completed_breaks = completed_breaks
        self.longest_session_seconds = longest_session_seconds
        
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'DailyStats':
        """Create a DailyStats object from a database row."""
        return cls(
            date=date.fromisoformat(row['date']),
            total_work_seconds=row['total_work_seconds'],
            total_breaks=row['total_breaks'],
            completed_breaks=row['completed_breaks'],
            longest_session_seconds=row['longest_session_seconds']
        )
        
    @property
    def total_work_hours(self) -> float:
        """Convert total work seconds to hours."""
        return self.total_work_seconds / 3600.0
        
    @property
    def break_completion_rate(self) -> float:
        """Calculate the percentage of breaks that were completed."""
        if self.total_breaks == 0:
            return 0.0
        return (self.completed_breaks / self.total_breaks) * 100.0

class Settings:
    """Application settings."""
    def __init__(
        self,
        work_duration: int = 1200,  # 20 minutes in seconds
        break_duration: int = 20,   # 20 seconds
        inactivity_threshold: int = 300,  # 5 minutes in seconds
        notification_style: str = "center",
        sound_enabled: bool = False,
        selected_sound: str = "none"
    ):
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.inactivity_threshold = inactivity_threshold
        self.notification_style = notification_style
        self.sound_enabled = sound_enabled
        self.selected_sound = selected_sound
        
    @classmethod
    def from_dict(cls, settings_dict: Dict[str, str]) -> 'Settings':
        """Create a Settings object from a dictionary of settings."""
        return cls(
            work_duration=int(settings_dict.get('work_duration', 1200)),
            break_duration=int(settings_dict.get('break_duration', 20)),
            inactivity_threshold=int(settings_dict.get('inactivity_threshold', 300)),
            notification_style=settings_dict.get('notification_style', 'center'),
            sound_enabled=settings_dict.get('sound_enabled', 'false').lower() == 'true',
            selected_sound=settings_dict.get('selected_sound', 'none')
        )
        
    def to_dict(self) -> Dict[str, str]:
        """Convert the Settings object to a dictionary."""
        return {
            'work_duration': str(self.work_duration),
            'break_duration': str(self.break_duration),
            'inactivity_threshold': str(self.inactivity_threshold),
            'notification_style': self.notification_style,
            'sound_enabled': str(self.sound_enabled).lower(),
            'selected_sound': self.selected_sound
        }