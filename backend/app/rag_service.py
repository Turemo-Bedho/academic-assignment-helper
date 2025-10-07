import openai
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from typing import List, Dict, Any
from . import models, config

class RAGService:
    def __init__(self):
        openai.api_key = config.settings.OPENAI_API_KEY
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def search_similar_sources(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar academic sources using vector similarity"""
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return []
        
        # Convert embedding to string format for PostgreSQL
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # Perform vector similarity search
        query_sql = text("""
            SELECT id, title, authors, publication_year, abstract, source_type,
                   embedding <=> :embedding as similarity
            FROM academic_sources
            ORDER BY similarity
            LIMIT :top_k
        """)
        
        results = db.execute(query_sql, {"embedding": embedding_str, "top_k": top_k})
        
        sources = []
        for row in results:
            sources.append({
                "id": row[0],
                "title": row[1],
                "authors": row[2],
                "publication_year": row[3],
                "abstract": row[4],
                "source_type": row[5],
                "similarity_score": float(row[6])
            })
        
        return sources
    
    def analyze_assignment_content(self, text: str, similar_sources: List[Dict]) -> Dict[str, Any]:
        """Analyze assignment content using AI"""
        try:
            sources_context = "\n".join([
                f"Source {i+1}: {source['title']} by {source['authors']} ({source['publication_year']}) - {source['abstract'][:200]}..."
                for i, source in enumerate(similar_sources[:3])
            ])
            
            prompt = f"""
            Analyze the following academic assignment and provide structured analysis:
            
            ASSIGNMENT TEXT:
            {text[:2000]}...
            
            RELEVANT SOURCES:
            {sources_context}
            
            Please provide analysis in JSON format with these fields:
            - topic: main topic of the assignment
            - key_themes: list of key themes identified
            - research_questions: list of research questions found or suggested
            - academic_level: estimated academic level (e.g., undergraduate, graduate)
            - research_suggestions: suggestions for further research
            - citation_recommendations: recommended citation styles and sources to cite
            - plagiarism_risk: assessment of plagiarism risk level (low/medium/high)
            """
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an academic research assistant. Provide structured JSON analysis of academic assignments."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return {
                "topic": "Unknown",
                "key_themes": [],
                "research_questions": [],
                "academic_level": "Unknown",
                "research_suggestions": "Analysis unavailable",
                "citation_recommendations": "Use appropriate academic citation style",
                "plagiarism_risk": "unknown"
            }