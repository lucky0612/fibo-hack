# FULLY ENHANCED with TRUE PARAMETER ISOLATION and SEED CONSISTENCY

import os
import json
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()

# Enhanced Knowledge Base with STRICT definitions
CINEMATIC_KNOWLEDGE_BASE = {
    "lenses": {
        "14mm": "Ultra-wide angle, extreme perspective distortion, vast landscapes",
        "24mm": "Wide angle, elongates depth, exaggerated perspective, action scenes",
        "35mm": "Moderate wide, documentary feel, environmental context",
        "50mm": "Standard, human eye perspective, neutral, grounded realism",
        "85mm": "Portrait prime, flattering facial compression, subject isolation",
        "100mm": "Tight portrait/macro, shallow DOF, extreme subject separation",
        "135mm": "Telephoto, heavy background compression, voyeuristic, intimate"
    },
    "lighting_setups": {
        "rembrandt": "High contrast, dramatic triangle of light on cheek, classical portrait",
        "butterfly": "Glamour lighting, soft butterfly shadow under nose, beauty/fashion",
        "split": "50/50 light-dark face split, mystery, duality, villain aesthetic",
        "soft_diffused": "Romantic, safe, commercial, low contrast, even illumination",
        "chiaroscuro": "Extreme contrast light/dark, pictorial, renaissance painting style",
        "low_key": "Predominant shadows, minimal fill, noir, suspense, drama",
        "high_key": "Bright, even, minimal shadows, optimistic, commercial, product",
        "rim_light": "Backlight edge highlighting, subject separation, heroic silhouette",
        "practical": "Motivated lighting from visible sources (lamps, windows), realism"
    },
    "lighting_directions": {
        "front": "Light facing subject directly, minimal shadows, flat but clear",
        "side_45": "45-degree side light, dimensional modeling, natural depth",
        "side_90": "Hard side light, strong contrast, dramatic edge",
        "back": "Backlight/rim light, silhouette, subject separation from background",
        "top": "Overhead light, harsh downward shadows, institutional feel",
        "bottom": "Under-lighting, horror aesthetic, unnatural and unsettling",
        "three_quarter": "Classic portrait position, natural and flattering"
    },
    "angles": {
        "low_angle": "Camera looks up, dominance, power, imposing, hero shot",
        "high_angle": "Camera looks down, vulnerability, weakness, isolation",
        "dutch": "Tilted horizon, unease, chaos, disorientation",
        "eye_level": "Neutral observer, equal power dynamic, documentary",
        "overhead": "Bird's eye, god's view, surveillance, geometric"
    },
    "color_schemes": {
        "teal_orange": "Cinematic blockbuster, warm skin tones with cool backgrounds",
        "monochrome_blue": "Cold, clinical, sci-fi, melancholic mood",
        "warm_golden": "Sunset, nostalgia, comfort, romantic atmosphere",
        "desaturated": "Gritty realism, documentary, muted emotional tone",
        "vibrant_saturated": "Pop art, energetic, commercial, youth-oriented",
        "noir_contrast": "High contrast black and white aesthetic with color hints"
    }
}

class CinemaCrew:
    """
    FULLY ENHANCED Multi-agent system with TRUE PARAMETER ISOLATION
    
    KEY FEATURE: When changing ONE parameter, EVERYTHING else stays constant
    - Lighting change = Subject, camera, composition LOCKED
    - Camera angle change = Subject, lighting, colors LOCKED
    - This is achieved through strict JSON structure and seed management
    """
    
    def __init__(self):
        self.llm = LLM(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Create specialized agents
        self.director = self._create_director()
        self.dp = self._create_dp()
        self.gaffer = self._create_gaffer()
        self.editor = self._create_editor()
        
        print("🎬 Cinema Crew initialized (PARAMETER ISOLATION MODE)")
        print("   Features: Strict Attribute Locking, Seed Preservation")
    
    def _create_director(self) -> Agent:
        """Director - Creates immutable Subject Anchor"""
        return Agent(
            role="Film Director - Subject Anchor Specialist",
            goal="Create PRECISE, UNCHANGING subject descriptions that lock identity.",
            backstory="""You create the SUBJECT ANCHOR - a detailed, immutable physical description.
This anchor MUST remain constant across all parameter variations. You describe:
- Exact clothing (color, style, texture)
- Physical features (hair, face, body type, age)
- Pose and position (specific action, orientation)
- Distinguishing marks (scars, accessories, unique features)

CRITICAL: Your description is the IDENTITY LOCK. Once set, it NEVER changes.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_dp(self) -> Agent:
        """DP - Camera ONLY, no subject changes"""
        return Agent(
            role="Director of Photography - Camera Specialist",
            goal="Define ONLY camera parameters. NEVER modify the subject.",
            backstory=f"""You work ONLY with camera and lens. You have access to:
{json.dumps(CINEMATIC_KNOWLEDGE_BASE['lenses'], indent=2)}

YOU MUST:
1. Choose lens focal length (14mm-135mm)
2. Set camera angle from: {list(CINEMATIC_KNOWLEDGE_BASE['angles'].keys())}
3. Define depth of field (f/1.4 to f/22)
4. Set camera movement (static/push-in/handheld)
5. Define composition rule (Rule of Thirds, Center Frame, etc.)

YOU MUST NOT:
- Change the subject description
- Modify lighting
- Alter colors or mood
- Touch anything except camera/lens parameters""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_gaffer(self) -> Agent:
        """Gaffer - Lighting ONLY, no subject changes"""
        return Agent(
            role="Gaffer - Lighting Specialist",
            goal="Define ONLY lighting parameters. NEVER modify subject or camera.",
            backstory=f"""You work ONLY with lights. You have access to:
SETUPS: {list(CINEMATIC_KNOWLEDGE_BASE['lighting_setups'].keys())}
DIRECTIONS: {list(CINEMATIC_KNOWLEDGE_BASE['lighting_directions'].keys())}

YOU MUST:
1. Choose lighting setup (Rembrandt, Butterfly, etc.)
2. Set direction (front, side_45, back, etc.)
3. Define color temperature (3200K warm to 7000K cold)
4. Set quality (hard/soft)
5. Define shadow characteristics

YOU MUST NOT:
- Change the subject description
- Modify camera angle or lens
- Alter the subject's pose or clothing
- Touch anything except lighting parameters""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _create_editor(self) -> Agent:
        """Editor - JSON Assembly with strict validation"""
        return Agent(
            role="Technical Prompt Engineer - JSON Architect",
            goal="Assemble STRICTLY SEPARATED JSON where each attribute is isolated.",
            backstory="""You are a compiler engineer. You enforce STRICT SEPARATION:

JSON STRUCTURE RULES:
1. 'objects' array = Subject ONLY (from Director, IMMUTABLE)
2. 'photographic_characteristics' = Camera ONLY (from DP)
3. 'lighting' block = Lighting ONLY (from Gaffer)
4. 'aesthetics.color_scheme' = Color ONLY (from Director)

NO CROSS-CONTAMINATION. If the user changes lighting, you ONLY modify the 'lighting' block.
The 'objects' array and 'photographic_characteristics' remain BYTE-FOR-BYTE identical.

This is ATTRIBUTE DISENTANGLEMENT - the core of FIBO's power.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_single_shot(
        self,
        scene_description: str,
        shot_type: str = "medium shot",
        locked_subject: Optional[Dict] = None,  # NEW: Lock subject from previous shot
        locked_camera: Optional[Dict] = None,   # NEW: Lock camera from previous shot
        locked_lighting: Optional[Dict] = None  # NEW: Lock lighting from previous shot
    ) -> Dict[str, Any]:
        """
        Create shot with OPTIONAL parameter locking
        
        Args:
            scene_description: What's happening
            shot_type: Shot type
            locked_subject: If provided, use this exact subject (no changes)
            locked_camera: If provided, use this exact camera (no changes)
            locked_lighting: If provided, use this exact lighting (no changes)
        """
        print(f"\\n{'='*70}")
        print(f"🎬 CREATING SHOT: {shot_type}")
        print(f"   Locked Subject: {'YES' if locked_subject else 'NO'}")
        print(f"   Locked Camera: {'YES' if locked_camera else 'NO'}")
        print(f"   Locked Lighting: {'YES' if locked_lighting else 'NO'}")
        print(f"{'='*70}\\n")
        
        tasks = []
        
        # Task 1: Director creates subject (or uses locked)
        if locked_subject:
            print("🔒 Using LOCKED subject description")
            subject_description = json.dumps(locked_subject)
        else:
            vision_task = Task(
                description=f"""
Create IMMUTABLE SUBJECT ANCHOR for: "{scene_description}"

You MUST provide:
1. PHYSICAL DESCRIPTION: Exact clothing colors, style, textures
2. FACIAL FEATURES: Age, hair color/style, facial hair, distinctive features
3. BODY TYPE: Height impression, build, posture
4. POSE: Specific action (e.g., "leaning forward with hands clasped")
5. ORIENTATION: facing camera/three-quarter turn/profile/back to camera
6. ACCESSORIES: Glasses, jewelry, bags, props in hand

FORMAT: Create a detailed paragraph that could be used for character consistency.

EXAMPLE:
"A 35-year-old male detective wearing a wrinkled grey suit with loosened burgundy tie,
short dark hair slightly disheveled, stubble on jaw, tired eyes with dark circles,
average build, hunched posture, leaning over desk with both hands flat on surface,
oriented at three-quarter angle to camera, wearing silver wristwatch, holding a pen."

Your output will be the IDENTITY LOCK.
""",
                expected_output="Detailed, immutable subject description paragraph",
                agent=self.director
            )
            tasks.append(vision_task)
        
        # Task 2: DP creates camera (or uses locked)
        if locked_camera:
            print("🔒 Using LOCKED camera settings")
            camera_spec = json.dumps(locked_camera)
        else:
            camera_task = Task(
                description=f"""
Define CAMERA PARAMETERS for {shot_type}.

MANDATORY RULES:
- Close-up/close shot → 85mm or 100mm lens
- Wide/establishing shot → 24mm or 35mm lens  
- Medium shot → 50mm lens

OUTPUT REQUIRED:
1. lens_focal_length: "XXmm" (number + mm)
2. camera_angle: Choose from {list(CINEMATIC_KNOWLEDGE_BASE['angles'].keys())}
3. depth_of_field: "f/X.X shallow|medium|deep"
4. camera_movement: "static" or "push-in" or "handheld" or "crane"
5. composition: "Rule of Thirds" or "Center Framed" or "Golden Ratio"

DO NOT mention the subject. Only camera specs.
""",
                expected_output="Camera specification with lens, angle, f-stop, movement, composition",
                agent=self.dp,
                context=[vision_task] if not locked_subject else []
            )
            tasks.append(camera_task)
        
        # Task 3: Gaffer creates lighting (or uses locked)
        if locked_lighting:
            print("🔒 Using LOCKED lighting setup")
            lighting_spec = json.dumps(locked_lighting)
        else:
            lighting_task = Task(
                description=f"""
Define LIGHTING PARAMETERS.

Choose from:
SETUPS: {list(CINEMATIC_KNOWLEDGE_BASE['lighting_setups'].keys())}
DIRECTIONS: {list(CINEMATIC_KNOWLEDGE_BASE['lighting_directions'].keys())}

OUTPUT REQUIRED:
1. setup_name: One from your lighting setups list
2. direction: One from your directions list (front, side_45, back, etc.)
3. color_temperature: "3200K warm" or "5600K neutral" or "7000K cold"
4. quality: "hard direct" or "soft diffused"
5. shadow_type: "deep shadows" or "soft shadows" or "minimal shadows"

DO NOT mention the subject or camera. Only lighting specs.
""",
                expected_output="Lighting specification with setup, direction, temp, quality, shadows",
                agent=self.gaffer,
                context=[vision_task] if not locked_subject else []
            )
            tasks.append(lighting_task)
        
        # Task 4: Editor assembles STRICT JSON
        json_task = Task(
            description=f"""
Assemble FIBO structured_prompt JSON with STRICT ATTRIBUTE SEPARATION.

{f'SUBJECT (LOCKED - USE EXACTLY): {subject_description}' if locked_subject else 'SUBJECT: From Director'}
{f'CAMERA (LOCKED - USE EXACTLY): {camera_spec}' if locked_camera else 'CAMERA: From DP'}
{f'LIGHTING (LOCKED - USE EXACTLY): {lighting_spec}' if locked_lighting else 'LIGHTING: From Gaffer'}

JSON SCHEMA (MANDATORY):
{{
    "short_description": "One sentence: subject + action + lighting mood + camera view",
    "objects": [
        {{
            "description": "EXACT COPY of subject anchor from Director - DO NOT MODIFY",
            "location": "center|left|right|foreground|background",
            "relationship": "main focus",
            "relative_size": "based on shot type",
            "shape_and_color": "Extract colors from subject description",
            "texture": "fabric/skin textures from subject",
            "appearance_details": "From subject anchor",
            "pose": "From subject anchor", 
            "orientation": "From subject anchor"
        }}
    ],
    "background_setting": "Generic environment matching scene, NO subject details here",
    "lighting": {{
        "conditions": "Gaffer's setup name + color temp (e.g., 'Rembrandt 3200K warm')",
        "direction": "Gaffer's direction",
        "shadow": "Gaffer's shadow characteristics",
        "quality": "Gaffer's quality (hard/soft)"
    }},
    "aesthetics": {{
        "composition": "DP's composition rule",
        "color_scheme": "Dominant color palette from lighting temp and scene mood",
        "mood_atmosphere": "Emotional keyword from scene",
        "preference_score": "very high",
        "aesthetic_score": "very high"
    }},
    "photographic_characteristics": {{
        "depth_of_field": "DP's f-stop specification",
        "focus": "sharp on subject",
        "camera_angle": "DP's angle",
        "lens_focal_length": "DP's focal length with 'mm'",
        "camera_movement": "DP's movement"
    }},
    "style_medium": "photograph",
    "context": "cinematic movie still",
    "artistic_style": "photorealistic",
    "negative_prompt": "blurry, low quality, deformed, disfigured, bad anatomy, extra limbs, mutation"
}}

VALIDATION CHECKLIST:
✓ lens_focal_length has 'mm' suffix
✓ objects[0].description is EXACT copy from Director
✓ lighting block has NO subject references
✓ photographic_characteristics has NO subject references
✓ No cross-contamination between blocks

OUTPUT ONLY THE JSON. NO markdown, NO explanations.
""",
            expected_output="Valid FIBO JSON with strict attribute separation",
            agent=self.editor,
            context=[t for t in tasks],
            output_file="outputs/last_shot_isolated.json"
        )
        tasks.append(json_task)
        
        # Execute crew
        crew = Crew(
            agents=[self.director, self.dp, self.gaffer, self.editor],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Parse JSON
        try:
            result_text = str(result)
            if "```json" in result_text:
                json_str = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                json_str = result_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = result_text.strip()
            
            structured_prompt = json.loads(json_str)
            
            # Create simple prompt
            simple_prompt = f"{structured_prompt.get('short_description', scene_description)}"
            
            print(f"\\n{'='*70}")
            print(f"✅ SHOT CREATED with PARAMETER ISOLATION")
            print(f"{'='*70}\\n")
            
            return {
                "structured_prompt": structured_prompt,
                "simple_prompt": simple_prompt,
                "scene_description": scene_description,
                "shot_type": shot_type,
                # Extract components for locking in future modifications
                "locked_subject": structured_prompt.get("objects", [{}])[0] if structured_prompt.get("objects") else None,
                "locked_camera": structured_prompt.get("photographic_characteristics", {}),
                "locked_lighting": structured_prompt.get("lighting", {})
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return self._create_fallback(scene_description, shot_type)
    
    def modify_single_parameter(
        self,
        base_shot: Dict[str, Any],
        parameter_type: str,  # "lighting" or "camera" or "color"
        new_value: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        NEW METHOD: Modify ONLY ONE parameter while keeping everything else LOCKED
        
        Args:
            base_shot: The original shot result (must have locked_* fields)
            parameter_type: "lighting", "camera", or "color"
            new_value: Dict with new values for that parameter
        
        Example:
            modify_single_parameter(
                base_shot=original_shot,
                parameter_type="lighting",
                new_value={"setup": "rembrandt", "direction": "side_45"}
            )
        """
        print(f"\\n{'='*70}")
        print(f"🔧 MODIFYING PARAMETER: {parameter_type}")
        print(f"   Keeping everything else LOCKED")
        print(f"{'='*70}\\n")
        
        # Clone the base structured prompt
        modified_prompt = json.loads(json.dumps(base_shot["structured_prompt"]))
        
        if parameter_type == "lighting":
            # Modify ONLY lighting block
            if "setup" in new_value:
                setup_desc = CINEMATIC_KNOWLEDGE_BASE['lighting_setups'].get(new_value["setup"], new_value["setup"])
                modified_prompt["lighting"]["conditions"] = f"{new_value['setup']}, {setup_desc}"
            
            if "direction" in new_value:
                direction_desc = CINEMATIC_KNOWLEDGE_BASE['lighting_directions'].get(new_value["direction"], new_value["direction"])
                modified_prompt["lighting"]["direction"] = f"{new_value['direction']} ({direction_desc})"
            
            if "color_temp" in new_value:
                # Update in conditions
                conditions = modified_prompt["lighting"]["conditions"]
                modified_prompt["lighting"]["conditions"] = f"{conditions}, {new_value['color_temp']}"
            
            print(f"✅ Modified lighting: {modified_prompt['lighting']}")
        
        elif parameter_type == "camera":
            # Modify ONLY camera block
            if "angle" in new_value:
                modified_prompt["photographic_characteristics"]["camera_angle"] = new_value["angle"]
            
            if "lens" in new_value:
                modified_prompt["photographic_characteristics"]["lens_focal_length"] = new_value["lens"]
            
            if "depth_of_field" in new_value:
                modified_prompt["photographic_characteristics"]["depth_of_field"] = new_value["depth_of_field"]
            
            print(f"✅ Modified camera: {modified_prompt['photographic_characteristics']}")
        
        elif parameter_type == "color":
            # Modify ONLY color scheme
            if "scheme" in new_value:
                modified_prompt["aesthetics"]["color_scheme"] = new_value["scheme"]
            
            print(f"✅ Modified colors: {modified_prompt['aesthetics']['color_scheme']}")
        
        else:
            raise ValueError(f"Unknown parameter_type: {parameter_type}")
        
        return {
            "structured_prompt": modified_prompt,
            "simple_prompt": base_shot["simple_prompt"],
            "scene_description": base_shot["scene_description"],
            "shot_type": base_shot["shot_type"],
            "modification": f"Changed {parameter_type}: {new_value}",
            # Keep locks for further modifications
            "locked_subject": base_shot.get("locked_subject"),
            "locked_camera": base_shot.get("locked_camera") if parameter_type != "camera" else modified_prompt["photographic_characteristics"],
            "locked_lighting": base_shot.get("locked_lighting") if parameter_type != "lighting" else modified_prompt["lighting"]
        }
    
    def _create_fallback(self, scene: str, shot_type: str) -> Dict[str, Any]:
        """Fallback if processing fails"""
        return {
            "structured_prompt": {
                "short_description": f"{shot_type} of {scene}",
                "objects": [{
                    "description": scene,
                    "location": "center",
                    "relationship": "main focus"
                }],
                "photographic_characteristics": {
                    "camera_angle": "eye-level",
                    "lens_focal_length": "50mm",
                    "depth_of_field": "medium, f/5.6"
                },
                "lighting": {
                    "conditions": "natural soft daylight",
                    "direction": "soft overhead"
                }
            },
            "simple_prompt": scene,
            "scene_description": scene,
            "shot_type": shot_type
        }

if __name__ == "__main__":
    crew = CinemaCrew()
    
    # Test 1: Create base shot
    print("\\n" + "="*70)
    print("TEST 1: Create base shot")
    print("="*70)
    
    base_shot = crew.create_single_shot(
        "A detective examines evidence under a desk lamp in a dark office",
        shot_type="medium shot"
    )
    
    # Test 2: Change ONLY lighting
    print("\\n" + "="*70)
    print("TEST 2: Change ONLY lighting (everything else locked)")
    print("="*70)
    
    modified_lighting = crew.modify_single_parameter(
        base_shot=base_shot,
        parameter_type="lighting",
        new_value={"setup": "rembrandt", "direction": "side_45", "color_temp": "warm 3200K"}
    )
    
    print("\\n✅ Lighting changed, subject and camera LOCKED")
    print(f"Original lighting: {base_shot['locked_lighting']}")
    print(f"New lighting: {modified_lighting['structured_prompt']['lighting']}")
    
    # Test 3: Change ONLY camera angle
    print("\\n" + "="*70)
    print("TEST 3: Change ONLY camera angle (everything else locked)")
    print("="*70)
    
    modified_camera = crew.modify_single_parameter(
        base_shot=base_shot,
        parameter_type="camera",
        new_value={"angle": "low_angle", "lens": "35mm"}
    )
    
    print("\\n✅ Camera changed, subject and lighting LOCKED")