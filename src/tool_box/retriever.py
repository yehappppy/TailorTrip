__author__ = "yh"
__date__ = "2025-04-11"
__description__ = "Hybrid retriever combining TF-IDF and FAISS"

import os
import re
import yaml
import json
import nltk
import torch
import logging
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from symspellpy import SymSpell, Verbosity
from typing import List, Tuple, Optional
from langchain.vectorstores import FAISS
from src.rag_db.tf_idf import TFIDFSearch
from src.rag_db.auto_embed import AutoEmbedding
from src.rag_db.vector_store import KnowledgeBase

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("retriever.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)['database_configuration']

def load_data(docs_path: str, chunk_size: int, chunk_overlap: int, existing_sources_path: Optional[str] = None):
    docs = []
    metadata = []
    new_sources = set()

    # Load existing sources
    existing_sources = set()
    if existing_sources_path and os.path.exists(existing_sources_path):
        try:
            with open(existing_sources_path, 'r', encoding='utf-8') as f:
                existing_sources = set(json.load(f))
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load existing sources: {str(e)}")

    for filename in os.listdir(docs_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(docs_path, filename)
            if file_path in existing_sources:
                logger.info(f"Skipped existing document: {file_path}")
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    docs.append(content)
                    metadata.append({"source": file_path})
                    new_sources.add(file_path)
                    logger.info(f"Loaded new document: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {str(e)}")
                continue

    if not docs:
        logger.warning("No new documents to load after deduplication")
        return []

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_texts = [text for doc in docs for text in splitter.split_text(doc)]
    chunked_docs = splitter.create_documents(docs, metadata)

    return chunked_texts, chunked_docs, new_sources

class TextProcessor:
    def __init__(self):
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def __call__(self, text: str) -> List[str]:
        # Tokenize, convert to lowercase, and filter non-alphabetic characters
        words = word_tokenize(text.lower()) # Convert to lowercase
        words = [re.sub(r'[^a-z]', '', word) for word in words] # Remove non-alphabetic characters
        words = [word for word in words if word] # Remove empty strings

        # filter stop words and lemmatize
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in stop_words]
        
        return words

class SpellingCorrector:
    def __init__(self, corpus: Optional[List[str]] = None):
        self.config = load_config()
        self.text_processor = TextProcessor()
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        if corpus:
            vocab_path = os.path.join(self.config["data_path"], "vocab.json")
            self._build_dictionary_from_files(corpus, vocab_path)

    def _build_dictionary_from_files(self, corpus: List[str], vocab_path: str) -> None:
        """Build dictionary by processing text content and counting word frequencies."""
        try:
            with open(vocab_path, 'w', encoding='utf-8') as f:
                vocab = json.load(f)
        except:
            vocab = {}
        
        # update vocabulary
        for text in corpus:
            words = self.text_processor(text)
            for word in words:
                vocab[word] = vocab.get(word, 0) + 1
        
        # update SpellingCorrector
        for word, count in vocab.items():
            self.sym_spell.words[word] = count
        
        # save updated vocabulary
        with open(vocab_path, 'w', encoding='utf-8') as f:
            json.dump(vocab, f, ensure_ascii=False, indent=4)
        logger.info(f"Built dictionary with {len(word_counts)} words")

    def __call__(self, query: str) -> str:
        """Spelling Correction with SymSpell"""
        corrected_words = []
        for word in query.split():
            # Find the best correction candidate (limit maximum edit distance = 2)
            suggestions = self.sym_spell.lookup(
                word, 
                Verbosity.CLOSEST, 
                max_edit_distance=2,
                include_unknown=True  # If no correction can be found, keep the original word
            )
            best_candidate = suggestions[0].term if suggestions else word
            corrected_words.append(best_candidate)
        return " ".join(corrected_words)

config = load_config()
chunked_texts, chunked_docs, new_sources = load_data(
    config['docs_path'], 
    config['chunk_size'], 
    config['chunk_overlap'], 
    config['existing_sources_path']
)
spelling_corrector = SpellingCorrector()

class FuzzyRetriever:
    def __init__(self):
        self.tfidf_search = TFIDFSearch(config, chunked_texts, new_sources)
    
    def search(self, query: str) -> List[Tuple[str, float]]:
        """TF-IDF Fuzzy Search"""
        return self.tfidf_search.search(spelling_corrector(query), config["semantic_k"])

class SemanticRetriever:
    def __init__(self):
        self.rag_db = KnowledgeBase(config, chunked_docs, new_sources)

    def search(self, query: str) -> List[Tuple[str, float]]:
        """FAISS Semantic Search"""
        return self.rag_db.search(spelling_corrector(query), config["semantic_k"])

class HybridRetriever:
    def __init__(self):
        self.tfidf_search = TFIDFSearch(config, chunked_texts, new_sources)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embeddings = AutoEmbedding(
            config['embedding_model'],
            config['embedding_type'],
            model_kwargs={"device": device}
        )

    def search(self, query: str) -> List[Tuple[str, float]]:
        """Mixed search: TF-IDF coarse screening + FAISS fine screening"""
        # 1. TF-IDF Initial Screening Candidate Documents
        query = spelling_corrector(query)
        candidate_docs = self.tfidf_search.search(query, config["fuzzy_k"])

        # 2. FAISS semantic search for candidate documents
        if not candidate_docs:
            return []
        
        # Temporary construction of FAISS sub-indexes (candidate documents only)
        candidate_embeddings = self.embeddings.embed_documents(candidate_docs)
        temp_faiss = FAISS.from_embeddings(
            list(zip(candidate_docs, candidate_embeddings)),
            self.embeddings
        )
        
        # 3. Returns the final sorted result
        return temp_faiss.similarity_search_with_score(query, config['semantic_k'])
