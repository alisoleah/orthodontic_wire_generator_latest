"""
Animation utilities for smooth UI transitions
"""

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class FadeAnimation:
    """Fade in/out animation for widgets"""
    
    @staticmethod
    def fade_in(widget, duration_ms=300):
        """Fade in a widget"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration_ms)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # Store reference to prevent garbage collection
        widget._fade_animation = animation
        
    @staticmethod
    def fade_out(widget, duration_ms=300, callback=None):
        """Fade out a widget"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration_ms)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        
        # Store reference to prevent garbage collection
        widget._fade_animation = animation


class PulseAnimation:
    """Pulse animation for completion effects"""
    
    @staticmethod
    def pulse(widget, duration_ms=500):
        """Create a pulse effect"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration_ms)
        animation.setStartValue(1.0)
        animation.setKeyValueAt(0.5, 0.5)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        
        # Store reference
        widget._pulse_animation = animation


class ProgressAnimation:
    """Animated progress bar with shimmer effect"""
    
    @staticmethod
    def animate_progress(progress_bar, target_value, duration_ms=1000):
        """Animate progress bar to target value"""
        current_value = progress_bar.value()
        
        animation = QPropertyAnimation(progress_bar, b"value")
        animation.setDuration(duration_ms)
        animation.setStartValue(current_value)
        animation.setEndValue(target_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # Store reference
        progress_bar._progress_animation = animation


class StatusMessageAnimation:
    """Animated status messages with auto-hide"""
    
    @staticmethod
    def show_temporary_message(status_bar, message, duration_ms=3000, success=True):
        """Show a temporary status message with fade effect"""
        # Set message
        status_bar.showMessage(message)
        
        # Apply color based on success/error
        if success:
            status_bar.setStyleSheet("QStatusBar { color: #28a745; }")
        else:
            status_bar.setStyleSheet("QStatusBar { color: #dc3545; }")
        
        # Auto-clear after duration
        def clear_message():
            status_bar.clearMessage()
            status_bar.setStyleSheet("")  # Reset style
        
        QTimer.singleShot(duration_ms, clear_message)
