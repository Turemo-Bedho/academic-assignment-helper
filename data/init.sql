-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    student_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    filename TEXT NOT NULL,
    original_text TEXT,
    topic TEXT,
    academic_level TEXT,
    word_count INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id),
    suggested_sources JSONB,
    plagiarism_score FLOAT,
    flagged_sections JSONB,
    research_suggestions TEXT,
    citation_recommendations TEXT,
    confidence_score FLOAT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS academic_sources (
    id SERIAL PRIMARY KEY,
    title TEXT,
    authors TEXT,
    publication_year INTEGER,
    abstract TEXT,
    full_text TEXT,
    source_type TEXT,
    embedding VECTOR(1536)
);

-- Insert sample academic sources (these will be used for RAG)
INSERT INTO academic_sources (title, authors, publication_year, abstract, full_text, source_type) VALUES
(
    'Machine Learning in Education: A Comprehensive Review',
    'Smith, J., Johnson, A., Williams, R.',
    2023,
    'This paper reviews the applications of machine learning in educational settings, focusing on personalized learning and assessment systems.',
    'Machine learning has revolutionized educational technology by enabling personalized learning paths and automated assessment systems. This comprehensive review covers recent advancements in educational AI, including natural language processing for essay grading, computer vision for student engagement analysis, and recommendation systems for learning materials. The study also addresses ethical considerations and future directions for AI in education.',
    'paper'
),
(
    'Natural Language Processing for Academic Writing Analysis',
    'Chen, L., Kumar, S., Garcia, M.',
    2022,
    'Exploring NLP techniques for analyzing academic writing quality and detecting plagiarism in student assignments.',
    'This research investigates transformer-based models for academic writing analysis. We propose a multi-modal approach combining syntactic analysis, semantic similarity, and citation pattern recognition to detect plagiarism and assess writing quality. Our method achieves 94% accuracy in identifying paraphrased content and provides detailed feedback on writing structure and argument coherence.',
    'paper'
),
(
    'Vector Databases for Educational Content Retrieval',
    'Brown, T., Davis, K., Wilson, P.',
    2023,
    'A study on using vector databases and semantic search for efficient educational content retrieval and recommendation.',
    'Vector databases enable semantic search capabilities that traditional keyword-based systems cannot match. This study demonstrates how educational platforms can use vector embeddings to recommend relevant research papers, course materials, and learning resources based on semantic similarity rather than exact keyword matches. Our evaluation shows a 67% improvement in recommendation relevance compared to traditional methods.',
    'paper'
),
(
    'Ethical Considerations in AI-Powered Education Systems',
    'Anderson, R., Lee, H., Martinez, J.',
    2022,
    'Discussion of ethical implications and considerations when implementing AI systems in educational environments.',
    'As AI systems become more prevalent in education, addressing ethical concerns becomes paramount. This paper examines issues of data privacy, algorithmic bias, transparency, and accountability in educational AI. We propose a framework for ethical AI implementation that prioritizes student privacy, ensures algorithmic fairness, and maintains human oversight in critical educational decisions.',
    'paper'
),
(
    'Automated Plagiarism Detection: Current State and Future Directions',
    'Wilson, P., Zhang, W., Rodriguez, M.',
    2021,
    'Analysis of modern plagiarism detection systems and emerging challenges in academic integrity.',
    'This survey examines the evolution of plagiarism detection technologies from simple string matching to sophisticated semantic analysis. We discuss the limitations of current systems in detecting AI-generated content and paraphrased plagiarism. The paper concludes with recommendations for developing more robust detection systems that can adapt to emerging writing technologies.',
    'paper'
);

