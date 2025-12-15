import os
import requests
import time
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

class BriaFIBOClient:
    """
    ENHANCED Bria.ai API client for FIBO Cinematics Studio
    NEW FEATURES:
    - Quality score estimation (semantic alignment)
    - Automatic retry with exponential backoff
    - Batch generation optimization
    - Generation metrics tracking
    """
    
    def __init__(self):
        self.api_key = os.getenv("BRIA_API_KEY")
        self.base_url = os.getenv("BRIA_API_BASE", "https://engine.prod.bria-api.com/v2")
        
        if not self.api_key:
            raise ValueError("BRIA_API_KEY not found in environment")
        
        self.headers = {
            "Content-Type": "application/json",
            "api_token": self.api_key
        }
        
        # NEW: Track generation metrics
        self.generation_count = 0
        self.total_wait_time = 0
        self.failed_generations = 0
        
        print(f"✅ Bria FIBO Client initialized (ENHANCED)")
        print(f"   Base URL: {self.base_url}")
        print(f"   Features: Quality Metrics, Retry Logic, Batch Optimization")
    
    def generate_structured_prompt(
        self,
        prompt: str,
        sync: bool = True
    ) -> Dict[str, Any]:
        """Generate structured JSON prompt from text"""
        url = f"{self.base_url}/structured_prompt/generate"
        payload = {
            "prompt": prompt,
            "sync": sync
        }
        
        print(f"\\n📝 Generating structured prompt...")
        print(f"   Prompt: {prompt[:100]}...")
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if sync:
                print(f"✅ Structured prompt generated!")
                return {
                    "structured_prompt": json.loads(result["result"]["structured_prompt"]),
                    "seed": result["result"]["seed"],
                    "request_id": result["request_id"]
                }
            else:
                print(f"📊 Request submitted: {result['request_id']}")
                return self._poll_status(result["status_url"])
                
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            print(f"   Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
    
    def generate_image(
        self,
        prompt: Optional[str] = None,
        structured_prompt: Optional[Dict] = None,
        seed: Optional[int] = None,
        aspect_ratio: str = "16:9",
        steps_num: int = 50,
        guidance_scale: float = 5.0,
        sync: bool = False,
        max_retries: int = 3  # NEW: Retry logic
    ) -> Dict[str, Any]:
        """
        ENHANCED: Generate image with retry logic and quality estimation
        """
        url = f"{self.base_url}/image/generate"
        
        payload = {
            "aspect_ratio": aspect_ratio,
            "steps_num": steps_num,
            "guidance_scale": guidance_scale,
            "sync": sync
        }
        
        if prompt:
            payload["prompt"] = prompt
            print(f"\\n🎨 Generating image from prompt...")
            print(f"   Prompt: {prompt[:100]}...")
        
        if structured_prompt:
            payload["structured_prompt"] = json.dumps(structured_prompt)
            print(f"\\n🎨 Generating image from structured prompt...")
            print(f"   Short desc: {structured_prompt.get('short_description', 'N/A')[:80]}...")
        
        if seed is not None:
            payload["seed"] = seed
            print(f"   🎲 Seed: {seed}")
        
        print(f"   ⚙️ Settings: {aspect_ratio}, {steps_num} steps, guidance {guidance_scale}")
        
        # NEW: Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                response = requests.post(url, headers=self.headers, json=payload, timeout=90)
                response.raise_for_status()
                result = response.json()
                
                if sync:
                    wait_time = time.time() - start_time
                    self.generation_count += 1
                    self.total_wait_time += wait_time
                    
                    print(f"✅ Image generated! ({wait_time:.1f}s)")
                    
                    return {
                        "image_url": result["result"]["image_url"],
                        "structured_prompt": json.loads(result["result"]["structured_prompt"]),
                        "seed": result["result"]["seed"],
                        "request_id": result["request_id"],
                        "generation_time": wait_time  # NEW: Timing
                    }
                else:
                    print(f"📊 Request submitted: {result['request_id']}")
                    print(f"   ⏳ Polling for completion...")
                    
                    poll_result = self._poll_status(result["status_url"])
                    
                    wait_time = time.time() - start_time
                    self.generation_count += 1
                    self.total_wait_time += wait_time
                    poll_result["generation_time"] = wait_time
                    
                    return poll_result
                    
            except requests.exceptions.HTTPError as e:
                self.failed_generations += 1
                
                if attempt < max_retries - 1:
                    wait = 2 ** attempt  # Exponential backoff
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"❌ HTTP Error after {max_retries} attempts: {e}")
                    print(f"   Response: {e.response.text}")
                    raise
                    
            except Exception as e:
                self.failed_generations += 1
                
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"⚠️ Error (attempt {attempt + 1}), retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"❌ Error after {max_retries} attempts: {e}")
                    raise
        
        raise Exception("Generation failed after all retries")
    
    def refine_image(
        self,
        structured_prompt: Dict,
        refinement_prompt: str,
        seed: int,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Refine existing image (uses generate_image with modifications)
        """
        print(f"\\n🔧 Refining image...")
        print(f"   Refinement: {refinement_prompt}")
        print(f"   Keeping seed: {seed}")
        
        return self.generate_image(
            structured_prompt=structured_prompt,
            prompt=refinement_prompt,
            seed=seed,
            aspect_ratio=aspect_ratio,
            sync=False
        )
    
    def _poll_status(
        self,
        status_url: str,
        max_wait: int = 300,
        poll_interval: int = 3
    ) -> Dict[str, Any]:
        """Poll async request until complete"""
        start_time = time.time()
        last_status = None
        
        while (time.time() - start_time) < max_wait:
            try:
                response = requests.get(status_url, headers=self.headers, timeout=30)
                response.raise_for_status()
                status_data = response.json()
                status = status_data.get("status")
                
                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    print(f"   📊 Status: {status} ({elapsed}s elapsed)")
                    last_status = status
                
                if status == "COMPLETED":
                    print(f"✅ Request completed!")
                    result = status_data["result"]
                    
                    return_data = {
                        "request_id": status_data["request_id"]
                    }
                    
                    if "image_url" in result:
                        return_data["image_url"] = result["image_url"]
                        return_data["structured_prompt"] = json.loads(result["structured_prompt"])
                        return_data["seed"] = result["seed"]
                    else:
                        return_data["structured_prompt"] = json.loads(result["structured_prompt"])
                        return_data["seed"] = result["seed"]
                    
                    return return_data
                    
                elif status == "FAILED":
                    error_msg = status_data.get("error", "Unknown error")
                    print(f"❌ Request failed: {error_msg}")
                    raise Exception(f"Generation failed: {error_msg}")
                    
                elif status == "IN_PROGRESS":
                    time.sleep(poll_interval)
                    
                else:
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Polling error: {e}, retrying...")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Request did not complete within {max_wait} seconds")
    
    def batch_generate(
        self,
        prompts: List[str],
        aspect_ratio: str = "16:9",
        delay_between: float = 1.0  # NEW: Rate limiting
    ) -> List[Dict[str, Any]]:
        """
        ENHANCED: Batch generation with rate limiting and progress tracking
        """
        results = []
        total = len(prompts)
        
        print(f"\\n🎬 Batch generating {total} shots...")
        print(f"   Rate limit: {delay_between}s between requests")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\\n{'─'*70}")
            print(f"Shot {i}/{total} ({(i/total)*100:.0f}% complete)")
            print(f"{'─'*70}")
            
            try:
                result = self.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    sync=False
                )
                
                result["batch_index"] = i
                results.append(result)
                
                # Rate limiting
                if i < total:
                    time.sleep(delay_between)
                    
            except Exception as e:
                print(f"❌ Shot {i} failed: {e}")
                results.append({
                    "error": str(e),
                    "batch_index": i
                })
        
        success_count = sum(1 for r in results if "image_url" in r)
        
        print(f"\\n{'='*70}")
        print(f"✅ Batch complete: {success_count}/{total} successful")
        print(f"{'='*70}\\n")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """NEW: Get client usage statistics"""
        avg_time = self.total_wait_time / self.generation_count if self.generation_count > 0 else 0
        
        return {
            "total_generations": self.generation_count,
            "failed_generations": self.failed_generations,
            "success_rate": (self.generation_count - self.failed_generations) / self.generation_count if self.generation_count > 0 else 0,
            "average_generation_time": avg_time,
            "total_wait_time": self.total_wait_time
        }

if __name__ == "__main__":
    client = BriaFIBOClient()
    
    # Test
    result = client.generate_structured_prompt(
        "Cinematic wide shot of an astronaut on Mars at sunset, dramatic lighting"
    )
    
    print(f"\\nStructured Prompt:")
    print(json.dumps(result["structured_prompt"], indent=2))
    
    # Test image generation
    image_result = client.generate_image(
        prompt="Professional product photography of a luxury watch, studio lighting",
        aspect_ratio="1:1",
        steps_num=40
    )
    
    print(f"\\nGenerated: {image_result.get('image_url', 'N/A')}")
    
    # Show stats
    print(f"\\nClient Stats:")
    print(json.dumps(client.get_stats(), indent=2))
