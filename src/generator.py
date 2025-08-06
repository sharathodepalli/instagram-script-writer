"""Script generation module using retrieval-augmented generation."""

from typing import Dict, List, Optional, Any
from pinecone import Pinecone
import tenacity
import openai
from openai import APIError, RateLimitError

# Updated imports to resolve deprecation warnings
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
    
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.prompts import PromptTemplate
from langchain.schema import Document

try:
    # Try relative import first (for when running as part of the app)
    from .config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        MODEL_FINE_TUNED,
        RETRIEVAL_TOP_K,
        TEMPERATURE,
        DEFAULT_HASHTAGS,
        logger
    )
except ImportError:
    # Fall back to absolute import (for when running directly)
    from src.config import (
        PINECONE_API_KEY,
        PINECONE_HOST,
        PINECONE_INDEX,
        PINECONE_REGION,
        EMBEDDING_MODEL,
        MODEL_FINE_TUNED,
        RETRIEVAL_TOP_K,
        TEMPERATURE,
        DEFAULT_HASHTAGS,
        logger
    )


class ScriptGenerator:
    """Generates Instagram scripts using retrieval-augmented generation."""
    
    def __init__(self):
        """Initialize the generator with necessary components."""
        self._initialize_pinecone()
        self.index_name = PINECONE_INDEX  # Add this line
        
        # Initialize embeddings with multiple fallbacks
        self.embeddings = self._initialize_embeddings()
        
        self.llm = ChatOpenAI(
            model=MODEL_FINE_TUNED,
            temperature=TEMPERATURE
        )
        self._setup_prompts()
        
    def _initialize_embeddings(self):
        """Initialize embeddings with fallback options."""
        models_to_try = [
            EMBEDDING_MODEL,
            "all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/all-distilroberta-v1"
        ]
        
        for model_name in models_to_try:
            try:
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},  # Force CPU to avoid device issues
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info(f"Successfully initialized embeddings with model: {model_name}")
                return embeddings
            except Exception as e:
                logger.warning(f"Failed to initialize embeddings with {model_name}: {e}")
                continue
        
        # If all else fails, raise an error
        raise RuntimeError("Failed to initialize any embedding model")
        
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone connection."""
        try:
            self.pc = Pinecone(api_key=PINECONE_API_KEY)
            logger.info(f"Connected to Pinecone with API key: {PINECONE_API_KEY[:5]}...")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
            
    def _setup_prompts(self) -> None:
        """Setup prompt templates for generation."""
        self.system_prompt = """You are a skilled Instagram content creator who writes engaging, conversational scripts.

Your writing style is:
- Witty, warm, and conversational
- Uses short paragraphs and sentences
- Includes rhetorical questions to engage viewers
- Incorporates sensory details and vivid descriptions
- Ends with a friendly call-to-action
- Authentic and relatable tone

Structure your scripts with:
1. HOOK: Attention-grabbing opening (first 3 seconds)
2. BODY: Main content with value/entertainment
3. CTA: Clear call-to-action
4. CAPTION: Instagram caption (<=125 characters)
5. VISUAL DIRECTIONS: Brief notes for video creation
6. HASHTAGS: 5-7 relevant hashtags"""

        self.prompt_template = PromptTemplate(
            input_variables=["context", "topic"],
            template="""SYSTEM: {system_prompt}

Here are examples of previous Instagram scripts in the target style:

{context}

Now write a new Instagram Reel script on the topic: "{topic}"

Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS.

Script:"""
        )
        
    def get_retriever(self):
        """Get Pinecone retriever for examples using direct client approach."""
        try:
            if not self.pc:
                logger.error("Pinecone client not initialized")
                return None
            
            # Get index directly
            index = self.pc.Index(self.index_name)
            
            # Create a custom retriever function
            def retrieve_documents(query: str, k: int = RETRIEVAL_TOP_K):
                try:
                    # Generate embedding for the query
                    query_embedding = self.embeddings.embed_query(query)
                    
                    # Query Pinecone directly
                    response = index.query(
                        vector=query_embedding,
                        top_k=k,
                        include_metadata=True
                    )
                    
                    # Convert to Document objects
                    docs = []
                    for match in response.matches:
                        doc = Document(
                            page_content=match.metadata.get("text", ""),
                            metadata={
                                "source": match.metadata.get("source", "unknown"),
                                "score": match.score
                            }
                        )
                        docs.append(doc)
                    
                    return docs
                except Exception as e:
                    logger.error(f"Query failed: {e}")
                    return []
            
            # Create a simple retriever-like object
            class SimpleRetriever:
                def get_relevant_documents(self, query: str):
                    return retrieve_documents(query)
            
            logger.info(f"Created direct retriever for index: {self.index_name}")
            return SimpleRetriever()
            
        except Exception as e:
            logger.error(f"Failed to create retriever: {e}")
            return None
            
    @tenacity.retry(
        wait=tenacity.wait_exponential(min=1, max=10),
        stop=tenacity.stop_after_attempt(5),
        retry=tenacity.retry_if_exception_type((RateLimitError, APIError))
    )
    def _call_llm(self, prompt: str) -> str:
        """Make a rate-limited call to the LLM."""
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=MODEL_FINE_TUNED,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
            
    def generate_script(self, topic: str, use_retrieval: bool = True) -> Dict[str, Any]:
        """
        Generate an Instagram script for the given topic.
        
        Args:
            topic: The topic/theme for the script
            use_retrieval: Whether to use retrieval for examples
            
        Returns:
            Dictionary containing the generated script and metadata
        """
        logger.info(f"Generating script for topic: {topic}")
        
        try:
            if use_retrieval:
                # Try to use retrieval-augmented generation
                retriever = self.get_retriever()
                
                if retriever is not None:
                    try:
                        # Get relevant examples using our direct retriever
                        relevant_docs = retriever.get_relevant_documents(topic)
                        
                        if relevant_docs:
                            # Create context from retrieved documents
                            context = "\n\n".join([doc.page_content for doc in relevant_docs])
                            
                            # Generate script with context
                            prompt = f"""Here are some example Instagram scripts for reference:

{context}

Now write a new Instagram Reel script on the topic: "{topic}"

Follow the same style and structure as the examples above.
Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS."""
                            
                            script = self._call_llm(prompt)
                            source_docs = relevant_docs
                            
                            logger.info(f"Generated script using {len(relevant_docs)} retrieved examples")
                        else:
                            logger.warning("No relevant documents found, using direct generation")
                            # Fall back to direct generation
                            prompt = f"""Write an Instagram Reel script on the topic: "{topic}"

Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS."""
                            
                            script = self._call_llm(prompt)
                            source_docs = []
                        
                    except Exception as e:
                        logger.warning(f"Retrieval failed, falling back to direct generation: {e}")
                        # Fall back to direct generation
                        prompt = f"""Write an Instagram Reel script on the topic: "{topic}"

Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS."""
                        
                        script = self._call_llm(prompt)
                        source_docs = []
                else:
                    logger.warning("Retriever not available, using direct generation")
                    # Fall back to direct generation
                    prompt = f"""Write an Instagram Reel script on the topic: "{topic}"

Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS."""
                    
                    script = self._call_llm(prompt)
                    source_docs = []
                
            else:
                # Direct generation without retrieval
                prompt = f"""Write an Instagram Reel script on the topic: "{topic}"

Include all required sections: HOOK, BODY, CTA, CAPTION, VISUAL DIRECTIONS, and HASHTAGS."""
                
                script = self._call_llm(prompt)
                source_docs = []
            
            # Parse the script into sections
            parsed_script = self._parse_script(script)
            
            result = {
                "success": True,
                "topic": topic,
                "script": script,
                "parsed_script": parsed_script,
                "source_documents": [doc.metadata.get("source", "unknown") for doc in source_docs],
                "model_used": MODEL_FINE_TUNED,
                "retrieval_used": use_retrieval and len(source_docs) > 0
            }
            
            logger.info(f"Successfully generated script for topic: {topic}")
            return result
            
        except Exception as e:
            logger.error(f"Script generation failed for topic '{topic}': {e}")
            return {
                "success": False,
                "topic": topic,
                "error": str(e),
                "script": None
            }
            
    def _parse_script(self, script: str) -> Dict[str, str]:
        """
        Parse the generated script into structured sections.
        
        Args:
            script: Raw script text
            
        Returns:
            Dictionary with parsed sections
        """
        sections = {
            "hook": "",
            "body": "", 
            "cta": "",
            "caption": "",
            "visual_directions": "",
            "hashtags": ""
        }
        
        lines = script.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ['hook:', 'hook']):
                current_section = "hook"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
            elif any(keyword in lower_line for keyword in ['body:', 'body']):
                current_section = "body"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
            elif any(keyword in lower_line for keyword in ['cta:', 'call-to-action:', 'call to action:']):
                current_section = "cta"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
            elif any(keyword in lower_line for keyword in ['caption:', 'caption']):
                current_section = "caption"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
            elif any(keyword in lower_line for keyword in ['visual:', 'visual directions:', 'visuals:']):
                current_section = "visual_directions"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
            elif any(keyword in lower_line for keyword in ['hashtags:', 'hashtag:', '#']):
                current_section = "hashtags"
                line = line.split(':', 1)[-1].strip() if ':' in line else line
                
            # Add content to current section
            if current_section and line:
                if sections[current_section]:
                    sections[current_section] += f" {line}"
                else:
                    sections[current_section] = line
                    
        return sections
        
    def generate_multiple_variants(self, topic: str, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple script variants for A/B testing.
        
        Args:
            topic: The topic for scripts
            count: Number of variants to generate
            
        Returns:
            List of generated script variants
        """
        variants = []
        
        for i in range(count):
            logger.info(f"Generating variant {i+1}/{count} for topic: {topic}")
            
            # Vary temperature slightly for different variants
            original_temp = self.llm.temperature
            self.llm.temperature = original_temp + (i * 0.1)
            
            variant = self.generate_script(f"{topic} (variant {i+1})")
            if variant["success"]:
                variant["variant_number"] = i + 1
                variants.append(variant)
                
            # Reset temperature
            self.llm.temperature = original_temp
            
        logger.info(f"Generated {len(variants)} variants for topic: {topic}")
        return variants


def main():
    """CLI entry point for script generation."""
    topic = input("Enter the topic for your Instagram script: ").strip()
    
    if not topic:
        print("❌ Please provide a topic")
        return
        
    generator = ScriptGenerator()
    result = generator.generate_script(topic)
    
    if result["success"]:
        print("\n✅ Script generated successfully!\n")
        print("=" * 50)
        print(result["script"])
        print("=" * 50)
        
        if result["source_documents"]:
            print(f"\n📚 Based on examples from: {', '.join(result['source_documents'])}")
    else:
        print(f"❌ Generation failed: {result['error']}")


if __name__ == "__main__":
    main()
