import os
import json
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def load_docs(docs_path: str, chunk_size: int, chunk_overlap: int, existing_sources_path: Optional[str] = None):
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
        return None, None, None

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_texts = [text for doc in docs for text in splitter.split_text(doc)]
    chunked_docs = splitter.create_documents(docs, metadata)

    return chunked_texts, chunked_docs, new_sources