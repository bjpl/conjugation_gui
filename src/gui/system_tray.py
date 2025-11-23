"""
Professional System Tray Integration
"""

import os
import sys
from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap

class SystemTrayManager(QObject):
    """Professional system tray integration manager"""
    
    # Signals
    show_main_window = pyqtSignal()
    hide_main_window = pyqtSignal()
    new_exercise_requested = pyqtSignal()
    speed_mode_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.tray_icon = None
        self.is_enabled = True
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Initialize the system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available on this system")
            self.is_enabled = False
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        
        # Set icon (try to load from resources, fallback to default)
        icon = self.load_tray_icon()
        self.tray_icon.setIcon(icon)
        
        # Set tooltip
        self.tray_icon.setToolTip("Spanish Conjugation Trainer")
        
        # Create context menu
        self.create_context_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Show tray icon
        self.tray_icon.show()
        
        # Show startup notification
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                "Spanish Conjugation Trainer",
                "Application started successfully. Click the tray icon to access features.",
                QSystemTrayIcon.Information,
                3000
            )
    
    def load_tray_icon(self) -> QIcon:
        """Load system tray icon"""
        icon_paths = [
            "src/resources/app_icon.ico",
            "src/resources/icon_32.png",
            "src/resources/icon_16.png",
        ]
        
        # Try to load custom icon
        for path in icon_paths:
            if os.path.exists(path):
                return QIcon(path)
        
        # Fallback: create a simple icon programmatically
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        from PyQt5.QtGui import QPainter, QBrush, QColor
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a simple circular icon
        painter.setBrush(QBrush(QColor(52, 152, 219)))  # Blue color
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, 14, 14)
        
        # Draw "ES" text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(painter.font())
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "ES")
        painter.end()
        
        return QIcon(pixmap)
    
    def create_context_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()
        
        # Main actions
        show_action = QAction("🏠 Show Main Window", self)
        show_action.triggered.connect(self.show_main_window.emit)
        menu.addAction(show_action)
        
        hide_action = QAction("📍 Hide to Tray", self)
        hide_action.triggered.connect(self.hide_main_window.emit)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        # Quick actions
        quick_menu = menu.addMenu("⚡ Quick Actions")
        
        new_exercise_action = QAction("📝 New Exercise", self)
        new_exercise_action.triggered.connect(self.new_exercise_requested.emit)
        quick_menu.addAction(new_exercise_action)
        
        speed_mode_action = QAction("🏃 Speed Mode", self)
        speed_mode_action.triggered.connect(self.speed_mode_requested.emit)
        quick_menu.addAction(speed_mode_action)
        
        # Practice modes submenu
        practice_menu = menu.addMenu("📚 Practice Modes")
        
        grammar_action = QAction("📖 Grammar Drills", self)
        grammar_action.triggered.connect(lambda: self.request_practice_mode("grammar"))
        practice_menu.addAction(grammar_action)
        
        task_action = QAction("🎯 Task Mode", self)
        task_action.triggered.connect(lambda: self.request_practice_mode("task"))
        practice_menu.addAction(task_action)
        
        story_action = QAction("📜 Story Mode", self)
        story_action.triggered.connect(lambda: self.request_practice_mode("story"))
        practice_menu.addAction(story_action)
        
        menu.addSeparator()
        
        # Statistics and progress
        stats_action = QAction("📊 View Statistics", self)
        stats_action.triggered.connect(lambda: self.request_feature("statistics"))
        menu.addAction(stats_action)
        
        progress_action = QAction("📈 Export Progress", self)
        progress_action.triggered.connect(lambda: self.request_feature("export"))
        menu.addAction(progress_action)
        
        menu.addSeparator()
        
        # Settings and about
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(lambda: self.request_feature("about"))
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Exit
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click shows/hides main window
            if self.main_window and self.main_window.isVisible():
                self.hide_main_window.emit()
            else:
                self.show_main_window.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click on some systems
            if self.main_window and not self.main_window.isVisible():
                self.show_main_window.emit()
    
    def request_practice_mode(self, mode: str):
        """Request a specific practice mode"""
        # Show main window first
        self.show_main_window.emit()
        
        # Trigger specific mode (would need to be connected to main window)
        if self.main_window and hasattr(self.main_window, 'start_practice_mode'):
            self.main_window.start_practice_mode(mode)
    
    def request_feature(self, feature: str):
        """Request a specific feature"""
        # Show main window first
        self.show_main_window.emit()
        
        # Trigger specific feature
        if self.main_window:
            if feature == "statistics" and hasattr(self.main_window, 'showStatistics'):
                self.main_window.showStatistics()
            elif feature == "export" and hasattr(self.main_window, 'exportProgress'):
                self.main_window.exportProgress()
            elif feature == "about" and hasattr(self.main_window, 'show_about'):
                self.main_window.show_about()
    
    def show_message(self, title: str, message: str, icon_type=QSystemTrayIcon.Information, duration: int = 3000):
        """Show system tray notification"""
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon_type, duration)
    
    def show_progress_notification(self, correct: int, total: int):
        """Show progress notification"""
        if total > 0:
            accuracy = (correct / total) * 100
            message = f"Session Complete!\n{correct}/{total} correct ({accuracy:.1f}%)"
            self.show_message("Practice Session", message, QSystemTrayIcon.Information)
    
    def show_achievement_notification(self, achievement: str):
        """Show achievement notification"""
        message = f"Achievement Unlocked: {achievement}!"
        self.show_message("Great Job!", message, QSystemTrayIcon.Information)
    
    def show_reminder_notification(self):
        """Show practice reminder"""
        message = "Time for Spanish practice! Keep your streak going."
        self.show_message("Practice Reminder", message, QSystemTrayIcon.Information)
    
    def update_tooltip(self, session_info: str = ""):
        """Update tray icon tooltip with session info"""
        if self.tray_icon:
            base_tooltip = "Spanish Conjugation Trainer"
            if session_info:
                full_tooltip = f"{base_tooltip}\n{session_info}"
            else:
                full_tooltip = base_tooltip
            
            self.tray_icon.setToolTip(full_tooltip)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable system tray functionality"""
        self.is_enabled = enabled
        if self.tray_icon:
            self.tray_icon.setVisible(enabled)
    
    def cleanup(self):
        """Clean up system tray resources"""
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon = None
    
    @staticmethod
    def is_available() -> bool:
        """Check if system tray is available"""
        return QSystemTrayIcon.isSystemTrayAvailable()

class TrayNotificationManager(QObject):
    """Manages different types of system tray notifications"""
    
    def __init__(self, tray_manager: SystemTrayManager):
        super().__init__()
        self.tray_manager = tray_manager
        self.notification_settings = {
            "session_complete": True,
            "achievements": True,
            "reminders": False,  # Disabled by default
            "errors": True
        }
    
    def set_notification_enabled(self, notification_type: str, enabled: bool):
        """Enable/disable specific notification types"""
        if notification_type in self.notification_settings:
            self.notification_settings[notification_type] = enabled
    
    def notify_session_complete(self, stats: dict):
        """Notify about session completion"""
        if not self.notification_settings.get("session_complete", True):
            return
        
        correct = stats.get("correct", 0)
        total = stats.get("total", 0)
        
        if total > 0:
            accuracy = (correct / total) * 100
            
            # Choose message based on performance
            if accuracy >= 90:
                message = f"Excellent! {correct}/{total} correct ({accuracy:.1f}%)\nYou're mastering Spanish!"
                icon = QSystemTrayIcon.Information
            elif accuracy >= 70:
                message = f"Good work! {correct}/{total} correct ({accuracy:.1f}%)\nKeep practicing!"
                icon = QSystemTrayIcon.Information
            else:
                message = f"Keep going! {correct}/{total} correct ({accuracy:.1f}%)\nPractice makes perfect!"
                icon = QSystemTrayIcon.Warning
            
            self.tray_manager.show_message("Practice Session Complete", message, icon)
    
    def notify_achievement(self, achievement: str, description: str = ""):
        """Notify about achievements"""
        if not self.notification_settings.get("achievements", True):
            return
        
        message = f"{achievement}"
        if description:
            message += f"\n{description}"
        
        self.tray_manager.show_message("Achievement Unlocked! 🏆", message, QSystemTrayIcon.Information)
    
    def notify_error(self, error_title: str, error_message: str):
        """Notify about errors"""
        if not self.notification_settings.get("errors", True):
            return
        
        # Keep error messages brief for tray notifications
        brief_message = error_message[:100] + "..." if len(error_message) > 100 else error_message
        self.tray_manager.show_message(f"Error: {error_title}", brief_message, QSystemTrayIcon.Critical)
    
    def notify_milestone(self, milestone: str):
        """Notify about learning milestones"""
        if not self.notification_settings.get("achievements", True):
            return
        
        message = f"Milestone reached: {milestone}"
        self.tray_manager.show_message("Learning Progress 📈", message, QSystemTrayIcon.Information)
    
    def schedule_reminder(self, hours: int = 24):
        """Schedule a practice reminder (would need QTimer implementation)"""
        # This would typically use QTimer to schedule reminders
        # For now, just a placeholder
        pass