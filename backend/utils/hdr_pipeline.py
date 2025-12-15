# utils/hdr_pipeline.py
import numpy as np
import cv2
from PIL import Image
import os
from typing import Tuple, Optional, Dict
import requests
from io import BytesIO
from datetime import datetime

class CinematicHDR:
    """
    Professional 16-bit HDR pipeline for FIBO Cinematics Studio
    Converts 8-bit FIBO outputs to 16-bit with cinematic color grading
    """
    
    def __init__(self, output_dir: str = "outputs/hdr"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Color science constants
        self.bit_depth_16 = 65535  # 2^16 - 1
        self.bit_depth_8 = 255      # 2^8 - 1
        
        print(f"🎨 Cinematic HDR Pipeline initialized")
        print(f"   Output: {output_dir}")
    
    def download_image(self, url: str) -> np.ndarray:
        """Download image from URL"""
        print(f"📥 Downloading image...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        img_array = np.array(img)
        
        # Handle RGBA
        if len(img_array.shape) == 3 and img_array.shape[2] == 4:
            img_array = img_array[:, :, :3]
        
        print(f"✅ Downloaded: {img_array.shape}")
        return img_array
    
    def convert_to_16bit(self, img_8bit: np.ndarray) -> np.ndarray:
        """Convert 8-bit to 16-bit color space"""
        print(f"🔄 Converting to 16-bit...")
        
        # Scale to 16-bit range
        img_16bit = (img_8bit.astype(np.uint16) * 257)  # 257 = 65535/255
        
        print(f"✅ 16-bit conversion complete")
        return img_16bit
    
    def apply_cinematic_grade(
        self,
        img_16bit: np.ndarray,
        preset: str = "neutral",
        exposure: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        temperature: float = 0.0
    ) -> np.ndarray:
        """
        Apply professional color grading
        
        Presets:
        - neutral: Clean, balanced
        - warm: Golden hour feel
        - cool: Sci-fi/clinical
        - dramatic: High contrast
        - vintage: Desaturated, warm
        - noir: High contrast B&W tint
        """
        
        print(f"🎨 Applying '{preset}' grade...")
        
        # Apply preset adjustments
        if preset == "warm":
            exposure += 0.1
            temperature += 0.15
            saturation *= 0.95
        elif preset == "cool":
            temperature -= 0.15
            saturation *= 0.9
        elif preset == "dramatic":
            contrast *= 1.3
            saturation *= 0.85
            exposure -= 0.1
        elif preset == "vintage":
            saturation *= 0.7
            temperature += 0.1
            contrast *= 0.9
        elif preset == "noir":
            saturation *= 0.3
            contrast *= 1.4
        
        # Convert to float [0, 1]
        img_float = img_16bit.astype(np.float32) / self.bit_depth_16
        
        # 1. Exposure (in stops)
        if exposure != 0:
            img_float = img_float * (2 ** exposure)
        
        # 2. Contrast
        if contrast != 1.0:
            img_float = (img_float - 0.5) * contrast + 0.5
        
        # 3. Saturation
        if saturation != 1.0:
            gray = 0.299 * img_float[:,:,0] + 0.587 * img_float[:,:,1] + 0.114 * img_float[:,:,2]
            gray = gray[:,:,np.newaxis]
            img_float = gray + saturation * (img_float - gray)
        
        # 4. Color temperature
        if temperature != 0:
            img_float[:,:,0] = img_float[:,:,0] + (temperature * 0.1)  # Red
            img_float[:,:,2] = img_float[:,:,2] - (temperature * 0.1)  # Blue
        
        # Clip to valid range
        img_float = np.clip(img_float, 0.0, 1.0)
        
        # Convert back to 16-bit
        img_graded = (img_float * self.bit_depth_16).astype(np.uint16)
        
        print(f"✅ Grading complete")
        return img_graded
    
    def export_formats(
        self,
        img_16bit: np.ndarray,
        base_filename: str
    ) -> Dict[str, str]:
        """
        Export in multiple professional formats
        
        Returns:
            Dict with paths to each format
        """
        
        paths = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 16-bit TIFF (DaVinci Resolve, Nuke)
        tiff_path = os.path.join(self.output_dir, f"{base_filename}_{timestamp}_16bit.tiff")
        print(f"💾 Exporting TIFF...")
        
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img_16bit, cv2.COLOR_RGB2BGR)
        cv2.imwrite(tiff_path, img_bgr)
        paths['tiff_16bit'] = tiff_path
        
        file_size = os.path.getsize(tiff_path) / (1024 * 1024)
        print(f"✅ TIFF: {file_size:.2f} MB")
        
        # 2. 16-bit PNG (universal)
        png_path = os.path.join(self.output_dir, f"{base_filename}_{timestamp}_16bit.png")
        print(f"💾 Exporting PNG...")
        
        # PIL for 16-bit PNG
        img_pil = Image.fromarray(img_16bit, mode='RGB')
        img_pil.save(png_path, format='PNG', compress_level=6)
        paths['png_16bit'] = png_path
        
        file_size = os.path.getsize(png_path) / (1024 * 1024)
        print(f"✅ PNG: {file_size:.2f} MB")
        
        # 3. 8-bit web preview (tone mapped)
        preview_path = os.path.join(self.output_dir, f"{base_filename}_{timestamp}_preview.jpg")
        print(f"🌐 Creating web preview...")
        
        web_preview = self._create_web_preview(img_16bit)
        cv2.imwrite(preview_path, cv2.cvtColor(web_preview, cv2.COLOR_RGB2BGR), 
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        paths['web_preview'] = preview_path
        
        file_size = os.path.getsize(preview_path) / 1024
        print(f"✅ Preview: {file_size:.2f} KB")
        
        return paths
    
    def _create_web_preview(self, img_16bit: np.ndarray) -> np.ndarray:
        """Create 8-bit web preview with tone mapping"""
        
        # Convert to float
        img_float = img_16bit.astype(np.float32) / self.bit_depth_16
        
        # Apply Reinhard tone mapping
        img_bgr = cv2.cvtColor(img_float, cv2.COLOR_RGB2BGR)
        tonemap = cv2.createTonemapReinhard(gamma=2.2, intensity=0, light_adapt=0.8, color_adapt=0)
        ldr = tonemap.process(img_bgr)
        
        # Back to RGB
        ldr_rgb = cv2.cvtColor(ldr, cv2.COLOR_BGR2RGB)
        
        # Convert to 8-bit
        img_8bit = (np.clip(ldr_rgb, 0, 1) * 255).astype(np.uint8)
        
        return img_8bit
    
    def create_comparison(
        self,
        original_8bit: np.ndarray,
        graded_16bit: np.ndarray,
        output_path: str
    ):
        """Create side-by-side before/after comparison"""
        
        print(f"📊 Creating comparison...")
        
        # Convert graded to 8-bit for display
        graded_8bit = self._create_web_preview(graded_16bit)
        
        # Ensure same size
        h, w = original_8bit.shape[:2]
        graded_8bit_resized = cv2.resize(graded_8bit, (w, h))
        
        # Add 10px black separator
        separator = np.zeros((h, 10, 3), dtype=np.uint8)
        
        # Create side-by-side
        comparison = np.hstack([original_8bit, separator, graded_8bit_resized])
        
        # Add labels
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.5
        thickness = 3
        
        # Original label
        cv2.putText(comparison, "ORIGINAL (8-bit)", 
                    (30, 60), font, font_scale, (255, 255, 255), thickness)
        cv2.putText(comparison, "ORIGINAL (8-bit)", 
                    (30, 60), font, font_scale, (0, 0, 0), thickness - 1)
        
        # Graded label
        cv2.putText(comparison, "GRADED (16-bit)", 
                    (w + 40, 60), font, font_scale, (255, 255, 255), thickness)
        cv2.putText(comparison, "GRADED (16-bit)", 
                    (w + 40, 60), font, font_scale, (0, 0, 0), thickness - 1)
        
        # Save
        cv2.imwrite(output_path, cv2.cvtColor(comparison, cv2.COLOR_RGB2BGR), 
                    [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        print(f"✅ Comparison saved: {output_path}")
    
    def process_shot(
        self,
        image_url: str,
        shot_id: str,
        preset: str = "neutral",
        exposure: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        temperature: float = 0.0
    ) -> Dict[str, str]:
        """
        Complete HDR pipeline for a shot
        
        Returns:
            Dict with all output paths
        """
        
        print(f"\n{'='*70}")
        print(f"🎬 HDR PIPELINE: Processing shot {shot_id}")
        print(f"{'='*70}\n")
        
        # Download
        original_8bit = self.download_image(image_url)
        
        # Convert to 16-bit
        img_16bit = self.convert_to_16bit(original_8bit)
        
        # Apply grading
        graded_16bit = self.apply_cinematic_grade(
            img_16bit,
            preset=preset,
            exposure=exposure,
            contrast=contrast,
            saturation=saturation,
            temperature=temperature
        )
        
        # Export formats
        paths = self.export_formats(graded_16bit, shot_id)
        
        # Create comparison
        comparison_path = os.path.join(
            self.output_dir, 
            f"{shot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_comparison.jpg"
        )
        self.create_comparison(original_8bit, graded_16bit, comparison_path)
        paths['comparison'] = comparison_path
        
        print(f"\n{'='*70}")
        print(f"✅ HDR PIPELINE COMPLETE")
        print(f"{'='*70}\n")
        
        for format_name, path in paths.items():
            print(f"  {format_name}: {os.path.basename(path)}")
        
        return paths


if __name__ == "__main__":
    pipeline = CinematicHDR()
    
    # Test with sample URL (replace with real FIBO output)
    test_url = "https://picsum.photos/1920/1080"
    
    results = pipeline.process_shot(
        image_url=test_url,
        shot_id="test_shot",
        preset="dramatic",
        exposure=0.2,
        contrast=1.15
    )
    
    print("\n✅ Test complete!")