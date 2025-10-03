#!/usr/bin/env python3
# ================================================================
# wire/height_controller.py
"""Wire height adjustment controller."""

class HeightController:
    """Manages wire height adjustments and offsets."""
    
    def __init__(self, initial_offset: float = 0.0, step_size: float = 0.5):
        """Initialize height controller."""
        self.height_offset = initial_offset
        self.step_size = step_size
        self.original_offset = initial_offset
        self.history = [initial_offset]
        
    def adjust_height(self, delta: float):
        """Adjust wire height by delta amount."""
        self.height_offset += delta
        self.history.append(self.height_offset)
        print(f"Height adjusted by {delta:.2f}mm (total: {self.height_offset:.2f}mm)")
    
    def set_height(self, new_height: float):
        """Set absolute height offset."""
        self.height_offset = new_height
        self.history.append(new_height)
    
    def reset_height(self):
        """Reset height to original position."""
        self.height_offset = self.original_offset
        self.history.append(self.original_offset)
        print(f"Height reset to {self.original_offset:.2f}mm")
    
    def get_height_offset(self) -> float:
        """Get current height offset."""
        return self.height_offset
    
    def get_step_size(self) -> float:
        """Get current step size."""
        return self.step_size
    
    def set_step_size(self, step: float):
        """Set height adjustment step size."""
        self.step_size = max(0.1, min(5.0, step))  # Clamp between 0.1 and 5.0mm
    
    def get_history(self) -> list:
        """Get height adjustment history."""
        return self.history.copy()
    
    def undo_last_adjustment(self):
        """Undo the last height adjustment."""
        if len(self.history) > 1:
            self.history.pop()  # Remove current
            self.height_offset = self.history[-1]  # Set to previous
            print(f"Height adjustment undone, now: {self.height_offset:.2f}mm")
        else:
            print("No height adjustments to undo")

