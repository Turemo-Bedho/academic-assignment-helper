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
    
    def generate_and_store_embeddings_for_existing_sources(self, db: Session):
        """Generate and store embeddings for all academic sources that don't have them"""
        try:
            # Get all sources without embeddings
            sources_without_embeddings = db.query(models.AcademicSource).filter(
                models.AcademicSource.embedding == None
            ).all()
            
            print(f"Found {len(sources_without_embeddings)} sources without embeddings")
            
            for source in sources_without_embeddings:
                # Create embedding text from title and abstract
                embedding_text = f"{source.title}. {source.abstract}"
                embedding = self.get_embedding(embedding_text)
                
                if embedding:
                    # Convert to the format PostgreSQL expects
                    embedding_array = "[" + ",".join(map(str, embedding)) + "]"
                    
                    # Update the source with the embedding
                    update_sql = text("""
                        UPDATE academic_sources 
                        SET embedding = :embedding::vector 
                        WHERE id = :source_id
                    """)
                    
                    db.execute(update_sql, {
                        "embedding": embedding_array,
                        "source_id": source.id
                    })
                    
                    print(f"✅ Added embedding for source: {source.title}")
                else:
                    print(f"❌ Failed to generate embedding for source: {source.title}")
            
            db.commit()
            print("✅ All embeddings generated and stored successfully")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error generating embeddings: {e}")


    def search_similar_sources(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar academic sources using vector similarity"""
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            print("Embedding generation failed")
            return []
        
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        print(f"Query: {query}, Embedding length: {len(query_embedding)}")
        
        query_sql = text("""
            SELECT id, title, authors, publication_year, abstract, source_type,
                embedding <=> :embedding as similarity
            FROM academic_sources
            ORDER BY similarity
            LIMIT :top_k
        """)
        
        results = db.execute(query_sql, {"embedding": embedding_str, "top_k": top_k})
        
        sources = []
        for i, row in enumerate(results):
            print(f"Row {i}: similarity = {row[6]}, type = {type(row[6])}")
            
            # Safe conversion
            similarity = row[6]
            if similarity is None:
                print(f"Warning: NULL similarity for record {row[0]}")
                similarity = 1.0
                
            sources.append({
                "id": row[0],
                "title": row[1],
                "authors": row[2],
                "publication_year": row[3],
                "abstract": row[4],
                "source_type": row[5],
                "similarity_score": float(similarity)
            })
        
        print(f"Found {len(sources)} sources")
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