"""
Enhanced Error Dialog with User-Friendly API Error Messages
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QCheckBox, QProgressBar, QFrame,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon

class ErrorSolution:
    """Container for error solutions"""
    
    def __init__(self, title: str, description: str, action: Optional[callable] = None, 
                 action_text: str = "Fix Now"):
        self.title = title
        self.description = description
        self.action = action
        self.action_text = action_text

class APIErrorHandler:
    """Handles API-specific error analysis and solutions"""
    
    @staticmethod
    def analyze_error(error_message: str, error_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze API error and provide user-friendly information"""
        
        error_lower = error_message.lower()
        
        # API Key Issues
        if any(keyword in error_lower for keyword in ['api_key', 'authentication', 'unauthorized', '401']):
            return {
                'title': 'API Authentication Problem',
                'friendly_message': 'There\'s an issue with your OpenAI API key.',
                'icon': '🔐',
                'severity': 'high',
                'solutions': [
                    ErrorSolution(
                        'Check API Key Format',
                        'Ensure your API key starts with "sk-" and is correctly entered without extra spaces.',
                        action=APIErrorHandler._show_api_key_help,
                        action_text='Show API Key Help'
                    ),
                    ErrorSolution(
                        'Verify API Key Validity',
                        'Your API key might be expired, invalid, or have insufficient permissions.',
                        action=APIErrorHandler._open_openai_account,
                        action_text='Open OpenAI Account'
                    ),
                    ErrorSolution(
                        'Use Offline Mode',
                        'Continue practicing without AI features while you resolve the API issue.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Switch to Offline'
                    )
                ]
            }
        
        # Rate Limiting
        elif any(keyword in error_lower for keyword in ['rate_limit', '429', 'too many requests']):
            return {
                'title': 'API Rate Limit Exceeded',
                'friendly_message': 'You\'ve made too many requests. Please wait a moment before trying again.',
                'icon': '⏱️',
                'severity': 'medium',
                'solutions': [
                    ErrorSolution(
                        'Wait and Retry',
                        'Rate limits reset automatically. Try again in a few minutes.',
                        action=None,
                        action_text='OK'
                    ),
                    ErrorSolution(
                        'Use Offline Mode Temporarily',
                        'Practice with local exercises while waiting for rate limit reset.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Use Offline Mode'
                    ),
                    ErrorSolution(
                        'Check Usage Limits',
                        'Review your OpenAI account usage and billing information.',
                        action=APIErrorHandler._open_openai_usage,
                        action_text='Check Usage'
                    )
                ]
            }
        
        # Billing/Payment Issues
        elif any(keyword in error_lower for keyword in ['billing', 'payment', 'quota', 'insufficient', 'credits']):
            return {
                'title': 'Billing or Quota Issue',
                'friendly_message': 'There\'s an issue with your OpenAI account billing or usage quota.',
                'icon': '💳',
                'severity': 'high',
                'solutions': [
                    ErrorSolution(
                        'Check Billing Status',
                        'Verify your payment method and account balance in your OpenAI dashboard.',
                        action=APIErrorHandler._open_openai_billing,
                        action_text='Open Billing'
                    ),
                    ErrorSolution(
                        'Review Usage Quota',
                        'You may have exceeded your monthly usage limit.',
                        action=APIErrorHandler._open_openai_usage,
                        action_text='Check Usage'
                    ),
                    ErrorSolution(
                        'Continue Offline',
                        'Use the app in offline mode while resolving billing issues.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Go Offline'
                    )
                ]
            }
        
        # Network/Connection Issues
        elif any(keyword in error_lower for keyword in ['network', 'connection', 'timeout', '502', '503', '504']):
            return {
                'title': 'Connection Problem',
                'friendly_message': 'Unable to connect to OpenAI servers. This might be a temporary network issue.',
                'icon': '🌐',
                'severity': 'medium',
                'solutions': [
                    ErrorSolution(
                        'Check Internet Connection',
                        'Ensure you have a stable internet connection.',
                        action=None,
                        action_text='OK'
                    ),
                    ErrorSolution(
                        'Retry Request',
                        'The issue might be temporary. Try your request again.',
                        action=None,
                        action_text='OK'
                    ),
                    ErrorSolution(
                        'Use Offline Mode',
                        'Continue practicing offline until connectivity is restored.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Go Offline'
                    )
                ]
            }
        
        # Server Errors
        elif any(keyword in error_lower for keyword in ['server', '500', '502', '503']):
            return {
                'title': 'Server Error',
                'friendly_message': 'OpenAI\'s servers are experiencing issues. This is temporary.',
                'icon': '🔧',
                'severity': 'low',
                'solutions': [
                    ErrorSolution(
                        'Wait and Retry',
                        'Server issues are usually resolved quickly. Try again in a few minutes.',
                        action=None,
                        action_text='OK'
                    ),
                    ErrorSolution(
                        'Use Offline Mode',
                        'Continue your Spanish practice offline while servers recover.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Go Offline'
                    ),
                    ErrorSolution(
                        'Check Status',
                        'Visit OpenAI\'s status page for real-time server information.',
                        action=APIErrorHandler._open_openai_status,
                        action_text='Check Status'
                    )
                ]
            }
        
        # Generic/Unknown Errors
        else:
            return {
                'title': 'Unexpected Error',
                'friendly_message': 'An unexpected error occurred while communicating with the AI service.',
                'icon': '⚠️',
                'severity': 'medium',
                'solutions': [
                    ErrorSolution(
                        'Try Again',
                        'The error might be temporary. Try your request again.',
                        action=None,
                        action_text='OK'
                    ),
                    ErrorSolution(
                        'Use Offline Mode',
                        'Continue practicing with local exercises.',
                        action=APIErrorHandler._enable_offline_mode,
                        action_text='Go Offline'
                    ),
                    ErrorSolution(
                        'Report Issue',
                        'If the problem persists, consider reporting it for assistance.',
                        action=APIErrorHandler._show_contact_info,
                        action_text='Get Help'
                    )
                ]
            }
    
    @staticmethod
    def _show_api_key_help():
        """Show API key help information"""
        QMessageBox.information(
            None, "API Key Help",
            "Your OpenAI API Key:\n\n"
            "1. Should start with 'sk-'\n"
            "2. Is about 51 characters long\n"
            "3. Can be found at: https://platform.openai.com/api-keys\n"
            "4. Should be kept secret and not shared\n\n"
            "To set your API key:\n"
            "• Go to Settings → API & AI tab\n"
            "• Enter your key and test the connection\n"
            "• Or create a .env file with OPENAI_API_KEY=your_key"
        )
    
    @staticmethod
    def _enable_offline_mode():
        """Signal to enable offline mode"""
        # This would be connected to the main app's offline mode toggle
        QMessageBox.information(
            None, "Offline Mode",
            "Switching to offline mode...\n\n"
            "In offline mode you can:\n"
            "• Practice verb conjugations\n"
            "• Use built-in exercises\n"
            "• Track your progress\n"
            "• Review mistakes\n\n"
            "You can switch back to online mode anytime from the toolbar."
        )
    
    @staticmethod
    def _open_openai_account():
        """Open OpenAI account page"""
        import webbrowser
        webbrowser.open("https://platform.openai.com/account/api-keys")
    
    @staticmethod
    def _open_openai_billing():
        """Open OpenAI billing page"""
        import webbrowser
        webbrowser.open("https://platform.openai.com/account/billing")
    
    @staticmethod
    def _open_openai_usage():
        """Open OpenAI usage page"""
        import webbrowser
        webbrowser.open("https://platform.openai.com/account/usage")
    
    @staticmethod
    def _open_openai_status():
        """Open OpenAI status page"""
        import webbrowser
        webbrowser.open("https://status.openai.com/")
    
    @staticmethod
    def _show_contact_info():
        """Show contact information for support"""
        QMessageBox.information(
            None, "Get Help",
            "Need help? Here are your options:\n\n"
            "1. Check the built-in documentation\n"
            "2. Review the troubleshooting guide\n"
            "3. Visit the project repository for updates\n"
            "4. Search online forums for similar issues\n\n"
            "Remember: Most API issues are resolved by:\n"
            "• Checking your API key\n"
            "• Verifying your billing status\n"
            "• Using offline mode temporarily"
        )

class ErrorDialog(QDialog):
    """Professional error dialog with solutions"""
    
    retry_requested = pyqtSignal()
    offline_mode_requested = pyqtSignal()
    
    def __init__(self, error_info: Dict[str, Any], technical_details: str = "", parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self.technical_details = technical_details
        
        self.setWindowTitle("Error - Spanish Conjugation Trainer")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Dialog | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        
        self.initUI()
        self.applyProfessionalStyling()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with icon and title
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Error icon
        icon_label = QLabel(self.error_info['icon'])
        icon_label.setFont(QFont("Arial", 24))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title and message
        title_layout = QVBoxLayout()
        
        title_label = QLabel(self.error_info['title'])
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title_label)
        
        message_label = QLabel(self.error_info['friendly_message'])
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #34495e; font-size: 12px;")
        title_layout.addWidget(message_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Solutions section
        solutions_group = QGroupBox("💡 How to Fix This")
        solutions_layout = QVBoxLayout(solutions_group)
        
        for i, solution in enumerate(self.error_info['solutions']):
            solution_frame = QFrame()
            solution_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                    background-color: #f8f9fa;
                    padding: 5px;
                }
            """)
            
            solution_layout = QVBoxLayout(solution_frame)
            solution_layout.setContentsMargins(10, 8, 10, 8)
            
            # Solution title
            title_label = QLabel(f"{i+1}. {solution.title}")
            title_label.setFont(QFont("Arial", 11, QFont.Bold))
            title_label.setStyleSheet("color: #2c3e50;")
            solution_layout.addWidget(title_label)
            
            # Solution description
            desc_label = QLabel(solution.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #5a6c7d; font-size: 10px; margin-left: 15px;")
            solution_layout.addWidget(desc_label)
            
            # Action button
            if solution.action:
                action_btn = QPushButton(solution.action_text)
                action_btn.clicked.connect(solution.action)
                action_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 10px;
                        margin-left: 15px;
                        margin-top: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                action_btn.setMaximumWidth(120)
                solution_layout.addWidget(action_btn, 0, Qt.AlignLeft)
            
            solutions_layout.addWidget(solution_frame)
        
        layout.addWidget(solutions_group)
        
        # Technical details (collapsible)
        if self.technical_details:
            self.show_details_checkbox = QCheckBox("Show technical details")
            self.show_details_checkbox.toggled.connect(self.toggleDetails)
            layout.addWidget(self.show_details_checkbox)
            
            self.details_text = QTextEdit()
            self.details_text.setPlainText(self.technical_details)
            self.details_text.setMaximumHeight(100)
            self.details_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    border: 1px solid #34495e;
                    border-radius: 4px;
                }
            """)
            self.details_text.setVisible(False)
            layout.addWidget(self.details_text)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Retry button for certain error types
        if self.error_info['severity'] in ['medium', 'low']:
            retry_btn = QPushButton("Try Again")
            retry_btn.clicked.connect(self.retry)
            button_layout.addWidget(retry_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def toggleDetails(self, checked: bool):
        """Toggle technical details visibility"""
        if hasattr(self, 'details_text'):
            self.details_text.setVisible(checked)
            if checked:
                self.resize(self.width(), self.height() + 100)
            else:
                self.resize(self.width(), self.height() - 100)
    
    def retry(self):
        """Emit retry signal and close dialog"""
        self.retry_requested.emit()
        self.accept()
    
    def applyProfessionalStyling(self):
        """Apply professional styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:default {
                background-color: #3498db;
            }
            QPushButton:default:hover {
                background-color: #2980b9;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #bdc3c7;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
    
    @staticmethod
    def show_api_error(error_message: str, technical_details: str = "", parent=None):
        """Static method to show API error dialog"""
        error_info = APIErrorHandler.analyze_error(error_message)
        dialog = ErrorDialog(error_info, technical_details, parent)
        return dialog.exec_() == QDialog.Accepted
    
    @staticmethod
    def show_generic_error(title: str, message: str, technical_details: str = "", parent=None):
        """Static method to show generic error dialog"""
        error_info = {
            'title': title,
            'friendly_message': message,
            'icon': '⚠️',
            'severity': 'medium',
            'solutions': [
                ErrorSolution(
                    'Try Again',
                    'The error might be temporary. Try your action again.',
                    action=None,
                    action_text='OK'
                ),
                ErrorSolution(
                    'Restart Application',
                    'If the problem persists, try restarting the application.',
                    action=None,
                    action_text='OK'
                )
            ]
        }
        dialog = ErrorDialog(error_info, technical_details, parent)
        return dialog.exec_() == QDialog.Accepted