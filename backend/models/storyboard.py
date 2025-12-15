# models/storyboard.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.shot import Shot

class Storyboard(BaseModel):
    """
    Collection of shots forming a sequence
    """
    
    # Identification
    storyboard_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    title: str
    description: Optional[str] = None
    
    # Shots
    shots: List[Shot] = Field(default_factory=list)
    
    # Script/source
    original_script: Optional[str] = None
    
    # Style consistency
    style_preset: Optional[str] = None  # "noir", "sci-fi", "horror", etc.
    color_grading: Optional[str] = None  # "warm", "cool", "desaturated"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    
    # Export settings
    export_format: str = "jpg"  # "jpg", "png", "exr", "tiff"
    target_fps: int = 24  # For video export
    
    def add_shot(self, shot: Shot):
        """Add shot to storyboard"""
        shot.shot_number = len(self.shots) + 1
        self.shots.append(shot)
        self.modified_at = datetime.now()
    
    def reorder_shots(self, new_order: List[int]):
        """Reorder shots by shot_number list"""
        if len(new_order) != len(self.shots):
            raise ValueError("new_order must match number of shots")
        
        # Create new list in specified order
        reordered = [None] * len(self.shots)
        for new_pos, old_pos in enumerate(new_order):
            if old_pos < len(self.shots):
                shot = self.shots[old_pos]
                shot.shot_number = new_pos + 1
                reordered[new_pos] = shot
        
        self.shots = [s for s in reordered if s is not None]
        self.modified_at = datetime.now()
    
    def get_shot(self, shot_number: int) -> Optional[Shot]:
        """Get shot by number"""
        for shot in self.shots:
            if shot.shot_number == shot_number:
                return shot
        return None
    
    class Config:
        json_schema_extra = {
            "example": {
                "storyboard_id": "20251216_150000",
                "title": "Mars Discovery Scene",
                "description": "Hero discovers ancient alien technology",
                "shots": []
            }
        }