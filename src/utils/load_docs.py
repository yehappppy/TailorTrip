import os
import re
import json
import uuid
import logging
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def extract_blogs(text_data):
    """
    Extract blog information from the text data.
    
    Parameters:
        text_data: Text containing multiple blogs.
        
    Returns:
        A list of dictionaries, each representing a blog with the following structure:
        {
            "title": Title,
            "content": Content,
            "comment": Comment,
            "ocr": OCR text
        }
    """
    # Define regex pattern to match each blog block
    blog_pattern = re.compile(
        r'<blog \d+>.*?'
        r'<title>(.*?)</title>.*?'
        r'<content>(.*?)</content>.*?'
        r'<comment>(.*?)</comment>.*?'
        r'<ocr>(.*?)</ocr>.*?'
        r'</blog \d+>',
        re.DOTALL  # Make '.' match all characters including newlines
    )
    
    # Find all matching blog entries
    blogs = blog_pattern.findall(text_data)
    
    # Convert matches into a list of dictionaries
    blog_list = []
    for blog in blogs:
        blog_dict = {
            "title": blog[0].strip(),
            "content": blog[1].strip(),
            "comment": blog[2].strip(),
            "ocr": blog[3].strip()
        }
        blog_list.append(blog_dict)
    
    return blog_list

def load_docs(docs_path: str, chunk_size: int, chunk_overlap: int):
    chunked_docs = []
    new_sources = set()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # Create directory if not exists
    existing_sources_dir = os.path.join(docs_path, "history")
    if not os.path.exists(existing_sources_dir):
        os.mkdir(existing_sources_dir)
    existing_sources_path = os.path.join(existing_sources_dir, 'existing_sources.json')
    
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
                    blogs = extract_blogs(content)
                    for blog in blogs:
                        title = blog.get("title", "")
                        content = blog.get("content", "")
                        comment = blog.get("comment", "")
                        chunked_docs.append(
                            Document(
                                id=str(uuid.uuid4()),
                                page_content=" ".join([title, content]),
                                metadata={
                                    "source": file_path,
                                    "title": title,
                                    "content": content,
                                    "comment": comment
                                }
                            )
                        )
                    new_sources.add(file_path)
                    logger.info(f"Loaded new document: {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {str(e)}")
                continue

    if not new_sources:
        logger.warning("No new documents to load after deduplication")
        return None, None
    
    return chunked_docs, new_sources