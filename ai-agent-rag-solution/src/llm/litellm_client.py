"""LiteLLM client wrapper for flexible LLM provider support."""
from typing import List, Dict, Optional
import litellm
from litellm import completion

class LiteLLMClient:
    """Wrapper for LiteLLM to interact with various LLM providers."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize LiteLLM client.
        
        Args:
            model: Model identifier (e.g., 'gpt-3.5-turbo', 'claude-3-haiku-20240307')
            temperature: Sampling temperature for responses
        """
        self.model = model
        self.temperature = temperature
        
        # Enable verbose logging for debugging (optional)
        litellm.set_verbose = False
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                return full_response
            else:
                # Non-streaming response
                return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(f"Error generating LLM response: {str(e)}")
    
    def generate_with_context(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response with RAG context.
        
        Args:
            query: User query
            context: Retrieved context from RAG
            chat_history: Previous chat messages
            system_prompt: Custom system prompt
            
        Returns:
            Generated response
        """
        messages = []
        
        # Add system prompt
        if not system_prompt:
            system_prompt = """You are a helpful AI assistant with access to document knowledge.
Answer questions based on the provided context. If the context doesn't contain 
relevant information, say so clearly. Be concise and accurate."""
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add chat history if available
        if chat_history:
            # Limit to last few messages to avoid context overflow
            recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
            messages.extend(recent_history)
        
        # Add current query with context
        user_message = f"""Context from documents:
{context}

Question: {query}

Please answer the question based on the context provided above."""
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self.generate_response(messages)
    
    def set_model(self, model: str):
        """Change the LLM model."""
        self.model = model
    
    def set_temperature(self, temperature: float):
        """Change the temperature setting."""
        self.temperature = temperature
