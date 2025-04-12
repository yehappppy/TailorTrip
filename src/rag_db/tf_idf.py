__author__ = "yh"
__date__ = "2025-04-11"
__description__ = "Initialize TF-IDF Searcher"

import os
import pickle
import logging
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tf_idf.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TFIDFSearch:
    def __init__(self, config: Dict, chunked_texts: List[str] = None, new_sources: Optional[set] = None):
        self.config = config
        self.vectorizer_path = os.path.join(self.config["tfidf_path"], "vectorizer.pkl")
        self.matrix_path = os.path.join(self.config["tfidf_path"], "tfidf_matrix.pkl")
        if self._model_exists() and self._load_model():
            pass
        elif not chunked_texts or len(chunked_texts) == 0:
            logger.info("Empty chunked texts provided!")
            raise ValueError("chunked_texts cannot be empty!")
        else:
            self.vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.vectorizer.fit_transform(chunked_texts)
            self._update_existing_sources(new_sources)
            self._save_model()

    def _model_exists(self) -> bool:
        """Check if the model exists"""
        return os.path.exists(self.vectorizer_path) and os.path.exists(self.matrix_path)

    def _load_model(self):
        """Loading Saved Models"""
        try:
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(self.matrix_path, 'rb') as f:
                self.tfidf_matrix = pickle.load(f)
            logger.info(f"Successfully loaded trained TF-IDF model from: \n{self.vectorizer_path} \n{self.matrix_path}")
            return True
        except Exception as e:
            logger.info(f"Failed to load model: {str(e)}")
            return False

    def _save_model(self):
        """Saving Trained Models"""
        try:
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            with open(self.matrix_path, 'wb') as f:
                pickle.dump(self.tfidf_matrix, f)
            logger.info(f"Successfully saved trained TF-IDF model to: \n{self.vectorizer_path} \n{self.matrix_path}")
        except Exception as e:
            logger.info(f"Failed to save model: {str(e)}")
            raise

    def _update_existing_sources(self, new_sources: Optional[set] = None):
        existing_sources_path = os.path.join(self.config['docs_path'], 'existing_sources_tfidf.json')
        try:
            with open(existing_sources_path, 'r', encoding='utf-8') as f:
                existing_sources = set(json.load(f))
        except:
            existing_sources = set()
        if new_sources and existing_sources_path:
            try:
                updated_sources = existing_sources.union(new_sources)
                with open(existing_sources_path, 'w', encoding='utf-8') as f:
                    json.dump(list(updated_sources), f, ensure_ascii=False, indent=2)
                logger.info(f"Updated processed sources file with {len(new_sources)} new entries")
            except Exception as e:
                logger.error(f"Failed to update processed sources: {str(e)}")

    def _update_vocab_tfidf(self):
        """Update the vocabulary and TF-IDF weights of the TF-IDF model"""
        ### TODO: This should be an asychronous method
        pass

    def search(self, query: str, k: int) -> List[Dict]:
        """Performs a TF-IDF search and returns Top-K documents."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get Top-K results
        top_indices = scores.argsort()[::-1][:k]
        results = [
            {
                "doc_id": idx,
                "score": scores[idx],
                "content": self.documents[idx]
            }
            for idx in top_indices if scores[idx] > 0
        ]
        return results
