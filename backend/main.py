# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import json
import asyncio
from datetime import datetime
import uuid

# Import our modules
from api.bria_client import BriaFIBOClient
from agents.cinema_crew import CinemaCrew
from utils.hdr_pipeline import CinematicHDR
from models.shot import Shot
from models.storyboard import Storyboard

# Initialize FastAPI
app = FastAPI(
    title="FIBO Cinematics Studio API",
    description="Professional cinematic image generation with multi-agent AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
bria_client = BriaFIBOClient()
cinema_crew = CinemaCrew()
hdr_pipeline = CinematicHDR()

# In-memory storage (use database in production)
shots_db: Dict[str, Shot] = {}
storyboards_db: Dict[str, Storyboard] = {}

# Ensure directories exist
os.makedirs("outputs/shots", exist_ok=True)
os.makedirs("outputs/storyboards", exist_ok=True)
os.makedirs("outputs/hdr", exist_ok=True)

# Mount outputs for file serving
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateShotRequest(BaseModel):
    scene_description: str
    shot_type: str = "medium shot"
    aspect_ratio: str = "16:9"
    apply_hdr: bool = True
    hdr_preset: str = "neutral"
    hdr_settings: Optional[Dict[str, float]] = {
        "exposure": 0.0,
        "contrast": 1.0,
        "saturation": 1.0,
        "temperature": 0.0
    }

class RefineshotRequest(BaseModel):
    shot_id: str
    refinement_prompt: str
    apply_hdr: bool = True

class CreateStoryboardRequest(BaseModel):
    title: str
    script: str
    num_shots: int = 5
    aspect_ratio: str = "16:9"
    style_preset: Optional[str] = None

class ModifyParameterRequest(BaseModel):
    shot_id: str
    parameter: str  # "camera_angle", "lens_focal_length", etc.
    value: str
    
class ApplyPresetRequest(BaseModel):
    shot_id: str
    preset_name: str

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "FIBO Cinematics Studio API",
        "version": "1.0.0",
        "status": "operational",
        "services": {
            "bria_client": "connected",
            "cinema_crew": "ready",
            "hdr_pipeline": "ready"
        }
    }

@app.post("/api/shots/create")
async def create_shot(request: CreateShotRequest, background_tasks: BackgroundTasks):
    """
    Create a single cinematic shot
    
    Flow:
    1. Cinema Crew creates structured prompt
    2. Bria API generates image
    3. Optional: HDR processing
    """
    try:
        print(f"\n{'='*80}")
        print(f"🎬 NEW SHOT REQUEST")
        print(f"{'='*80}")
        
        shot_id = f"shot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Step 1: Cinema Crew creates shot
        print(f"\n🤖 STEP 1: Cinema Crew creating shot...")
        crew_result = cinema_crew.create_single_shot(
            scene_description=request.scene_description,
            shot_type=request.shot_type
        )
        
        structured_prompt = crew_result["structured_prompt"]
        simple_prompt = crew_result["simple_prompt"]
        
        # Step 2: Generate with Bria FIBO
        print(f"\n🎨 STEP 2: Generating with FIBO...")
        fibo_result = bria_client.generate_image(
            structured_prompt=structured_prompt,
            aspect_ratio=request.aspect_ratio,
            sync=False  # Async
        )
        
        image_url = fibo_result["image_url"]
        seed = fibo_result["seed"]
        
        # Create Shot object
        shot = Shot(
            shot_id=shot_id,
            scene_description=request.scene_description,
            shot_type=request.shot_type,
            structured_prompt=structured_prompt,
            simple_prompt=simple_prompt,
            seed=seed,
            image_url=image_url,
            aspect_ratio=request.aspect_ratio
        )
        
        # Step 3: HDR processing (async in background)
        if request.apply_hdr:
            print(f"\n🎨 STEP 3: Scheduling HDR processing...")
            
            def process_hdr():
                hdr_paths = hdr_pipeline.process_shot(
                    image_url=image_url,
                    shot_id=shot_id,
                    preset=request.hdr_preset,
                    **request.hdr_settings
                )
                
                # Update shot with HDR paths
                shot.hdr_16bit_path = hdr_paths.get('tiff_16bit')
                shot.hdr_comparison_path = hdr_paths.get('comparison')
                
                print(f"✅ HDR processing complete for {shot_id}")
            
            background_tasks.add_task(process_hdr)
        
        # Save to database
        shots_db[shot_id] = shot
        
        # Save to disk
        shot_file = f"outputs/shots/{shot_id}.json"
        with open(shot_file, 'w') as f:
            json.dump(shot.dict(), f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print(f"✅ SHOT CREATED: {shot_id}")
        print(f"{'='*80}\n")
        
       # Convert datetime fields for JSON serialization
        shot_dict = shot.dict(exclude={'structured_prompt'})
        shot_dict['created_at'] = shot.created_at.isoformat()
        shot_dict['modified_at'] = shot.modified_at.isoformat() if shot.modified_at else None
        
        return JSONResponse(content={
            "success": True,
            "shot_id": shot_id,
            "shot": shot_dict,
            "image_url": image_url,
            "message": "Shot created successfully. HDR processing in progress."
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=f"Shot creation failed: {str(e)}")

@app.get("/api/shots/{shot_id}")
async def get_shot(shot_id: str):
    """Get shot details"""
    if shot_id not in shots_db:
        raise HTTPException(status_code=404, detail="Shot not found")
    
    shot = shots_db[shot_id]
    shot_dict = shot.dict()
    shot_dict['created_at'] = shot.created_at.isoformat()
    shot_dict['modified_at'] = shot.modified_at.isoformat() if shot.modified_at else None
    
    return JSONResponse(content={"shot": shot_dict})

@app.get("/api/shots")
async def list_shots():
    """List all shots"""
    shots = [
        {
            "shot_id": shot.shot_id,
            "shot_type": shot.shot_type,
            "scene_description": shot.scene_description[:100],
            "created_at": shot.created_at.isoformat(),
            "image_url": shot.image_url
        }
        for shot in shots_db.values()
    ]
    
    return JSONResponse(content={"shots": shots, "total": len(shots)})

@app.post("/api/shots/{shot_id}/refine")
async def refine_shot(shot_id: str, request: RefineshotRequest):  
    """Refine existing shot with new instructions"""
    try:
        if shot_id not in shots_db:
            raise HTTPException(status_code=404, detail="Shot not found")
        
        original_shot = shots_db[shot_id]
        
        print(f"\n🎨 Refining shot {shot_id}...")
        print(f"   Refinement: {request.refinement_prompt}")
        
        # Refine with Bria
        result = bria_client.refine_image(
            structured_prompt=original_shot.structured_prompt,
            refinement_prompt=request.refinement_prompt,
            seed=original_shot.seed,
            aspect_ratio=original_shot.aspect_ratio
        )
        
        # Create new shot (refined version)
        new_shot_id = f"{shot_id}_refined_{datetime.now().strftime('%H%M%S')}"
        
        refined_shot = Shot(
            shot_id=new_shot_id,
            scene_description=f"{original_shot.scene_description} (refined: {request.refinement_prompt})",
            shot_type=original_shot.shot_type,
            structured_prompt=result["structured_prompt"],
            simple_prompt=original_shot.simple_prompt,
            seed=result["seed"],
            image_url=result["image_url"],
            aspect_ratio=original_shot.aspect_ratio,
            notes=f"Refined from {shot_id}"
        )
        
        shots_db[new_shot_id] = refined_shot
        
        # Convert datetime for JSON
        refined_dict = refined_shot.dict(exclude={'structured_prompt'})
        refined_dict['created_at'] = refined_shot.created_at.isoformat()
        refined_dict['modified_at'] = refined_shot.modified_at.isoformat() if refined_shot.modified_at else None
        
        return JSONResponse(content={
            "success": True,
            "original_shot_id": shot_id,
            "refined_shot_id": new_shot_id,
            "shot": refined_dict,
            "image_url": refined_shot.image_url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shots/{shot_id}/modify")
async def modify_parameter(shot_id: str, request: ModifyParameterRequest):
    """
    Modify single parameter while keeping others constant
    Demonstrates FIBO's disentanglement!
    """
    try:
        if shot_id not in shots_db:
            raise HTTPException(status_code=404, detail="Shot not found")
        
        original_shot = shots_db[shot_id]
        
        # Clone structured prompt
        modified_prompt = original_shot.structured_prompt.copy()
        
        print(f"\n📷 Modifying parameter: {request.parameter} = {request.value}")
        
        # Apply modification based on parameter type
        if request.parameter == "camera_angle":
            modified_prompt["photographic_characteristics"]["camera_angle"] = request.value
        
        elif request.parameter == "lens_focal_length":
            modified_prompt["photographic_characteristics"]["lens_focal_length"] = request.value
        
        elif request.parameter == "depth_of_field":
            modified_prompt["photographic_characteristics"]["depth_of_field"] = request.value
        
        elif request.parameter == "lighting_direction":
            modified_prompt["lighting"]["direction"] = request.value
        
        elif request.parameter == "color_scheme":
            modified_prompt["aesthetics"]["color_scheme"] = request.value
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown parameter: {request.parameter}")
        
        # Generate with modified prompt
        result = bria_client.generate_image(
            structured_prompt=modified_prompt,
            seed=original_shot.seed,  # Keep same seed!
            aspect_ratio=original_shot.aspect_ratio,
            sync=False
        )
        
        # Create new shot
        new_shot_id = f"{shot_id}_mod_{request.parameter}_{datetime.now().strftime('%H%M%S')}"
        
        modified_shot = Shot(
            shot_id=new_shot_id,
            scene_description=original_shot.scene_description,
            shot_type=original_shot.shot_type,
            structured_prompt=modified_prompt,
            simple_prompt=original_shot.simple_prompt,
            seed=original_shot.seed,
            image_url=result["image_url"],
            aspect_ratio=original_shot.aspect_ratio,
            notes=f"Modified {request.parameter} from {shot_id}"
        )
        
        shots_db[new_shot_id] = modified_shot
        
        # Convert datetime for JSON
        modified_dict = modified_shot.dict(exclude={'structured_prompt'})
        modified_dict['created_at'] = modified_shot.created_at.isoformat()
        modified_dict['modified_at'] = modified_shot.modified_at.isoformat() if modified_shot.modified_at else None
        
        return JSONResponse(content={
            "success": True,
            "original_shot_id": shot_id,
            "modified_shot_id": new_shot_id,
            "parameter_changed": request.parameter,
            "new_value": request.value,
            "shot": modified_dict,
            "image_url": modified_shot.image_url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storyboards/create")
async def create_storyboard(request: CreateStoryboardRequest):
    """
    Create multi-shot storyboard from script
    """
    try:
        print(f"\n{'='*80}")
        print(f"📽️ NEW STORYBOARD REQUEST")
        print(f"{'='*80}")
        
        storyboard_id = f"storyboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Cinema Crew creates storyboard
        print(f"\n🤖 Cinema Crew creating {request.num_shots} shots...")
        crew_results = cinema_crew.create_storyboard(
            script=request.script,
            num_shots=request.num_shots
        )
        
        # Create Storyboard object
        storyboard = Storyboard(
            storyboard_id=storyboard_id,
            title=request.title,
            description=request.script[:200],
            original_script=request.script,
            style_preset=request.style_preset
        )
        
        # Generate each shot with Bria
        for i, crew_result in enumerate(crew_results, 1):
            print(f"\n🎨 Generating shot {i}/{len(crew_results)}...")
            
            fibo_result = bria_client.generate_image(
                structured_prompt=crew_result["structured_prompt"],
                aspect_ratio=request.aspect_ratio,
                sync=False
            )
            
            shot = Shot(
                shot_id=f"{storyboard_id}_shot{i}",
                shot_number=i,
                scene_description=crew_result["scene_description"],
                shot_type=crew_result["shot_type"],
                structured_prompt=crew_result["structured_prompt"],
                simple_prompt=crew_result["simple_prompt"],
                seed=fibo_result["seed"],
                image_url=fibo_result["image_url"],
                aspect_ratio=request.aspect_ratio,
                purpose=crew_result.get("purpose", "")
            )
            
            shots_db[shot.shot_id] = shot
            storyboard.add_shot(shot)
        
        # Save storyboard
        storyboards_db[storyboard_id] = storyboard
        
        storyboard_file = f"outputs/storyboards/{storyboard_id}.json"
        with open(storyboard_file, 'w') as f:
            json.dump(storyboard.dict(), f, indent=2, default=str)
        
        print(f"\n{'='*80}")
        print(f"✅ STORYBOARD CREATED: {storyboard_id}")
        print(f"{'='*80}\n")
        
        return JSONResponse(content={
            "success": True,
            "storyboard_id": storyboard_id,
            "storyboard": storyboard.dict(default=str),
            "message": f"Storyboard with {len(storyboard.shots)} shots created"
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/storyboards/{storyboard_id}")
async def get_storyboard(storyboard_id: str):
    """Get storyboard details"""
    if storyboard_id not in storyboards_db:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    storyboard = storyboards_db[storyboard_id]
    return JSONResponse(content=storyboard.dict(default=str))

@app.get("/api/storyboards")
async def list_storyboards():
    """List all storyboards"""
    storyboards = [
        {
            "storyboard_id": sb.storyboard_id,
            "title": sb.title,
            "num_shots": len(sb.shots),
            "created_at": sb.created_at.isoformat()
        }
        for sb in storyboards_db.values()
    ]
    
    return JSONResponse(content={"storyboards": storyboards, "total": len(storyboards)})

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated files"""
    # Search in outputs directories
    possible_paths = [
        f"outputs/shots/{filename}",
        f"outputs/hdr/{filename}",
        f"outputs/storyboards/{filename}"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path, filename=filename)
    
    raise HTTPException(status_code=404, detail="File not found")

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Server startup"""
    print("\n" + "="*80)
    print("🎬 FIBO CINEMATICS STUDIO API")
    print("="*80)
    print("✅ FastAPI server starting...")
    print("✅ Bria FIBO client connected")
    print("✅ Cinema Crew ready (4 agents)")
    print("✅ HDR pipeline initialized")
    print("="*80)
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("="*80 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )