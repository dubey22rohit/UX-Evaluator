import os
import google.generativeai as genai
from typing import Dict, Any, List
from loguru import logger
from dotenv import load_dotenv
import json
import asyncio

# Load environment variables
load_dotenv()

class ChatAnalyzer:
    """
    A class for providing an interactive chat interface to query UX analysis results
    using Google's Gemini API.
    """
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize the ChatAnalyzer with analysis results.
        
        Args:
            analysis_results: Results from the UX analysis
        """
        self.analysis_results = analysis_results
        self.gemini_client = None
        self.chat_history = []
        self._init_ai_client()
    
    def _init_ai_client(self):
        """Initialize Gemini AI client"""
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
        else:
            logger.warning("Google API key not found. Chat analysis will be unavailable.")
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """
        Process a user question about the UX analysis results.
        
        Args:
            question: User's question about the analysis
            
        Returns:
            Dict containing the response and any relevant context
        """
        try:
            if not self.gemini_client:
                return {
                    "error": "Gemini API client not initialized",
                    "response": "Unable to process questions without API access"
                }
            
            # Construct context-aware prompt
            prompt = f"""
            You are a UX expert assistant analyzing these UX evaluation results:
            {json.dumps(self.analysis_results)}
            
            Previous conversation context:
            {self._format_chat_history()}
            
            Please answer this question about the analysis:
            {question}
            
            Provide a clear, concise response focusing on relevant findings from the analysis.
            If the question cannot be answered from the available analysis data, say so.
            """
            
            # Get Gemini's response
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                [
                    {"text": prompt},
                    {"text": json.dumps(self.analysis_results)}
                ]
            )
            
            # Update chat history
            self.chat_history.append({
                "question": question,
                "response": response.text
            })
            
            return {
                "response": response.text,
                "context": self._extract_relevant_context(question)
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return {
                "error": str(e),
                "response": "Sorry, I encountered an error processing your question."
            }
    
    def _format_chat_history(self) -> str:
        """
        Format chat history for context.
        
        Returns:
            Formatted string of chat history
        """
        if not self.chat_history:
            return "No previous conversation"
            
        history = []
        for entry in self.chat_history[-3:]:  # Include last 3 exchanges for context
            history.append(f"Q: {entry['question']}")
            history.append(f"A: {entry['response']}")
        
        return "\n".join(history)
    
    def _extract_relevant_context(self, question: str) -> Dict[str, Any]:
        """
        Extract analysis context relevant to the question.
        
        Args:
            question: User's question
            
        Returns:
            Dict containing relevant analysis data
        """
        # This is a simple implementation that could be enhanced with more
        # sophisticated relevance matching
        relevant_context = {
            "total_issues": self.analysis_results.get("total_issues", 0),
            "relevant_issues": []
        }
        
        # Extract issues that might be relevant to the question
        question_lower = question.lower()
        for issue in self.analysis_results.get("issues", []):
            if any(keyword in question_lower for keyword in [
                issue.get("type", "").lower(),
                issue.get("heuristic", "").lower(),
                issue.get("severity", "").lower()
            ]):
                relevant_context["relevant_issues"].append(issue)
        
        return relevant_context
    
    def clear_chat_history(self) -> None:
        """Clear the chat history"""
        self.chat_history = []