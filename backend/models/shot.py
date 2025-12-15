# models/shot.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ShotType(str, Enum):
    """Standard cinematography shot types"""
    EXTREME_WIDE = "extreme wide shot"
    WIDE = "wide shot"
    MEDIUM_WIDE = "medium wide shot"
    MEDIUM = "medium shot"
    MEDIUM_CLOSE = "medium close-up"
    CLOSE_UP = "close-up"
    EXTREME_CLOSE = "extreme close-up"

class CameraAngle(str, Enum):
    """Standard camera angles"""
    EYE_LEVEL = "eye-level"
    LOW_ANGLE = "low-angle"
    HIGH_ANGLE = "high-angle"
    OVERHEAD = "overhead"
    DUTCH = "dutch angle"
    POV = "point of view"

class Shot(BaseModel):
    """
    Complete shot specification for FIBO Cinematics Studio
    """
    
    # Identification
    shot_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    shot_number: Optional[int] = None
    shot_name: Optional[str] = None
    
    # Scene info
    scene_description: str
    shot_type: str = "medium shot"
    purpose: Optional[str] = None  # "establishing", "reaction", "detail", etc.
    
    # FIBO data
    structured_prompt: Dict[str, Any]
    simple_prompt: str
    seed: Optional[int] = None
    
    # Generated outputs
    image_url: Optional[str] = None
    image_local_path: Optional[str] = None
    
    # HDR outputs
    hdr_16bit_path: Optional[str] = None
    hdr_comparison_path: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Generation settings
    aspect_ratio: str = "16:9"
    steps: int = 50
    guidance_scale: float = 5.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "shot_id": "20251216_143022",
                "shot_number": 1,
                "scene_description": "Astronaut discovers alien artifact",
                "shot_type": "wide shot",
                "simple_prompt": "Wide cinematic shot of astronaut on Mars...",
                "aspect_ratio": "16:9"
            }
        }