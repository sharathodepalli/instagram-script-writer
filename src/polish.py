"""Script polishing module for refining generated content."""

from typing import Dict, Any, Optional
import openai
from openai import APIError, RateLimitError
import tenacity

try:
    # Try relative import first (for when running as part of the app)
    from .config import (
        OPENAI_API_KEY,
        MODEL_FINE_TUNED,
        POLISH_TEMPERATURE,
        logger
    )
except ImportError:
    # Fall back to absolute import (for when running directly)
    from src.config import (
        OPENAI_API_KEY,
        MODEL_FINE_TUNED,
        POLISH_TEMPERATURE,
        logger
    )


class ScriptPolisher:
    """Handles polishing and refinement of generated Instagram scripts."""
    
    def __init__(self, model: str = None):
        """
        Initialize the polisher.
        
        Args:
            model: OpenAI model to use for polishing (default: uses MODEL_FINE_TUNED from config)
        """
        openai.api_key = OPENAI_API_KEY
        self.model = model or MODEL_FINE_TUNED
        self.temperature = POLISH_TEMPERATURE
        
    def _get_polish_prompt(self, script: str, focus_area: Optional[str] = None) -> str:
        """
        Create a polishing prompt based on the script and focus area.
        
        Args:
            script: The script to polish
            focus_area: Specific area to focus on (e.g., "engagement", "clarity", "voice")
            
        Returns:
            Formatted prompt for polishing
        """
        base_prompt = """You are an expert copyeditor and Instagram content strategist. Your task is to polish this Instagram script to make it more engaging, clear, and authentic while maintaining the original voice and style.

Focus on:
- Improving clarity and flow
- Enhancing engagement and hooks
- Maintaining authentic, conversational tone
- Optimizing for Instagram's format and audience
- Ensuring strong call-to-action
- Checking caption length (≤125 characters)
- Improving visual direction clarity"""

        if focus_area:
            base_prompt += f"\n- Special focus on: {focus_area}"
            
        base_prompt += f"""

Original script to polish:
{script}

Provide the polished version with the same structure (HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, HASHTAGS):"""

        return base_prompt
        
    @tenacity.retry(
        wait=tenacity.wait_exponential(min=1, max=10),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type((RateLimitError, APIError))
    )
    def _call_openai(self, prompt: str) -> str:
        """Make a rate-limited call to OpenAI API."""
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": "You are an expert copyeditor and Instagram content strategist."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
            
    def polish_script(self, script: str, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Polish a generated Instagram script.
        
        Args:
            script: The script to polish
            focus_area: Optional focus area for polishing
            
        Returns:
            Dictionary containing polished script and metadata
        """
        logger.info("Starting script polishing process")
        
        try:
            # Create polishing prompt
            prompt = self._get_polish_prompt(script, focus_area)
            
            # Get polished version
            polished_script = self._call_openai(prompt)
            
            # Calculate improvements
            improvements = self._analyze_improvements(script, polished_script)
            
            result = {
                "success": True,
                "original_script": script,
                "polished_script": polished_script,
                "model_used": self.model,
                "focus_area": focus_area,
                "improvements": improvements
            }
            
            logger.info("Script polishing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Script polishing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_script": script
            }
            
    def polish_multiple_passes(self, script: str, passes: int = 2) -> Dict[str, Any]:
        """
        Apply multiple polishing passes for higher quality.
        
        Args:
            script: The script to polish
            passes: Number of polishing passes
            
        Returns:
            Dictionary containing final polished script
        """
        logger.info(f"Starting {passes}-pass polishing process")
        
        current_script = script
        pass_results = []
        
        focus_areas = [
            "engagement and hooks",
            "clarity and flow", 
            "voice and authenticity"
        ]
        
        for i in range(passes):
            focus = focus_areas[i % len(focus_areas)] if i < len(focus_areas) else None
            
            logger.info(f"Polishing pass {i+1}/{passes}" + (f" (focus: {focus})" if focus else ""))
            
            result = self.polish_script(current_script, focus)
            
            if result["success"]:
                current_script = result["polished_script"]
                pass_results.append({
                    "pass_number": i + 1,
                    "focus_area": focus,
                    "improvements": result["improvements"]
                })
            else:
                logger.warning(f"Pass {i+1} failed: {result['error']}")
                break
                
        return {
            "success": len(pass_results) > 0,
            "original_script": script,
            "final_script": current_script,
            "passes_completed": len(pass_results),
            "pass_results": pass_results,
            "model_used": self.model
        }
        
    def _analyze_improvements(self, original: str, polished: str) -> Dict[str, Any]:
        """
        Analyze improvements made during polishing.
        
        Args:
            original: Original script text
            polished: Polished script text
            
        Returns:
            Dictionary with improvement metrics
        """
        original_length = len(original.split())
        polished_length = len(polished.split())
        
        # Extract captions for length comparison
        original_caption = self._extract_caption(original)
        polished_caption = self._extract_caption(polished)
        
        improvements = {
            "word_count_change": polished_length - original_length,
            "original_word_count": original_length,
            "polished_word_count": polished_length,
            "caption_length_original": len(original_caption) if original_caption else 0,
            "caption_length_polished": len(polished_caption) if polished_caption else 0,
            "caption_within_limit": len(polished_caption) <= 125 if polished_caption else False
        }
        
        return improvements
        
    def _extract_caption(self, script: str) -> Optional[str]:
        """Extract caption from script text."""
        lines = script.split('\n')
        
        for line in lines:
            if 'caption:' in line.lower():
                return line.split(':', 1)[-1].strip()
                
        return None
        
    def compare_versions(self, original: str, polished: str) -> Dict[str, Any]:
        """
        Compare original and polished versions side by side.
        
        Args:
            original: Original script
            polished: Polished script
            
        Returns:
            Comparison analysis
        """
        improvements = self._analyze_improvements(original, polished)
        
        return {
            "original": original,
            "polished": polished,
            "improvements": improvements,
            "side_by_side": {
                "original_lines": original.split('\n'),
                "polished_lines": polished.split('\n')
            }
        }


def main():
    """CLI entry point for script polishing."""
    print("Instagram Script Polisher")
    print("=" * 30)
    
    # Get script input
    script = input("\nPaste your script to polish:\n").strip()
    
    if not script:
        print("❌ Please provide a script to polish")
        return
        
    # Get focus area (optional)
    focus = input("\nFocus area (optional - press Enter to skip): ").strip()
    focus = focus if focus else None
    
    # Initialize polisher
    polisher = ScriptPolisher()
    
    # Polish script
    result = polisher.polish_script(script, focus)
    
    if result["success"]:
        print("\n✅ Script polished successfully!\n")
        print("ORIGINAL:")
        print("-" * 40)
        print(result["original_script"])
        print("\nPOLISHED:")
        print("-" * 40)
        print(result["polished_script"])
        
        improvements = result["improvements"]
        print(f"\n📊 Improvements:")
        print(f"   Word count: {improvements['original_word_count']} → {improvements['polished_word_count']}")
        if improvements["caption_length_polished"] > 0:
            print(f"   Caption length: {improvements['caption_length_polished']} chars (limit: 125)")
            
    else:
        print(f"❌ Polishing failed: {result['error']}")


if __name__ == "__main__":
    main()
