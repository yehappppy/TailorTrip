from difflib import SequenceMatcher
import json
from typing import List, Dict

class SearchEngine:
    def __init__(self):
        # 模拟数据库或搜索索引
        self.data = [
            {
                "title": "Python Programming Tutorial",
                "url": "https://example.com/python-tutorial",
                "description": "Learn Python programming from basics to advanced concepts."
            },
            {
                "title": "JavaScript Fundamentals",
                "url": "https://example.com/javascript",
                "description": "Complete guide to JavaScript programming language."
            },
            {
                "title": "Web Development Guide",
                "url": "https://example.com/web-dev",
                "description": "Learn web development using HTML, CSS and JavaScript."
            },
            {
                "title": "Data Science with Python",
                "url": "https://example.com/data-science",
                "description": "Introduction to data science using Python and its libraries."
            },
            {
                "title": "Machine Learning Basics",
                "url": "https://example.com/ml",
                "description": "Getting started with machine learning algorithms."
            }
        ]
        
        # 创建搜索索引
        self.search_index = self._create_search_index()

    def _create_search_index(self) -> Dict[str, List[str]]:
        """创建搜索索引，将单词映射到文档"""
        index = {}
        for i, item in enumerate(self.data):
            # 将标题和描述分词
            words = (item['title'] + ' ' + item['description']).lower().split()
            for word in words:
                if word not in index:
                    index[word] = []
                if i not in index[word]:
                    index[word].append(i)
        return index

    def _calculate_similarity(self, query: str, text: str) -> float:
        """计算查询词与文本的相似度"""
        return SequenceMatcher(None, query.lower(), text.lower()).ratio()

    def _highlight_text(self, text: str, query: str) -> str:
        """高亮匹配的文本"""
        if not query:
            return text
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        if query_lower in text_lower:
            start = text_lower.find(query_lower)
            end = start + len(query)
            return f"{text[:start]}[{text[start:end]}]{text[end:]}"
        return text

    def search(self, query: str, threshold: float = 0.3) -> List[Dict]:
        """搜索功能"""
        if not query:
            return []

        # 存储搜索结果和相似度分数
        results = []
        seen_docs = set()

        # 对查询词进行分词
        query_words = query.lower().split()

        # 对每个查询词进行模糊匹配
        for word in query_words:
            # 在索引中查找相似的词
            for index_word, doc_ids in self.search_index.items():
                similarity = self._calculate_similarity(word, index_word)
                
                if similarity >= threshold:
                    for doc_id in doc_ids:
                        if doc_id not in seen_docs:
                            doc = self.data[doc_id].copy()
                            
                            # 计算文档相关度分数
                            title_similarity = self._calculate_similarity(query, doc['title'])
                            desc_similarity = self._calculate_similarity(query, doc['description'])
                            doc['score'] = (title_similarity * 2 + desc_similarity) / 3
                            
                            # 高亮匹配文本
                            doc['title'] = self._highlight_text(doc['title'], query)
                            doc['description'] = self._highlight_text(doc['description'], query)
                            
                            results.append(doc)
                            seen_docs.add(doc_id)

        # 按相关度排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def get_suggestions(self, prefix: str, max_suggestions: int = 5) -> List[str]:
        """获取搜索建议"""
        if not prefix:
            return []

        suggestions = []
        prefix = prefix.lower()

        # 从索引中找到匹配的词
        for word in self.search_index.keys():
            if word.startswith(prefix):
                suggestions.append(word)
            elif self._calculate_similarity(prefix, word[:len(prefix)]) > 0.8:
                suggestions.append(word)

        # 排序并限制建议数量
        suggestions.sort(key=lambda x: (-len(set(prefix) & set(x)), len(x)))
        return suggestions[:max_suggestions]

def print_results(results: List[Dict]):
    """格式化打印搜索结果"""
    if not results:
        print("\n没有找到相关结果")
        return
    
    print("\n搜索结果:")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   描述: {result['description']}")
        print(f"   相关度: {result['score']:.2f}")
        print("-" * 50)

def main():
    """主函数：模拟搜索引擎交互"""
    search_engine = SearchEngine()
    
    while True:
        query = input("\n请输入搜索内容 (输入 'q' 退出): ").strip()
        
        if query.lower() == 'q':
            break
        
        # 获取并显示搜索建议
        if len(query) >= 2:
            suggestions = search_engine.get_suggestions(query)
            if suggestions:
                print("\n搜索建议:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
        
        # 执行搜索并显示结果
        results = search_engine.search(query)
        print_results(results)

if __name__ == "__main__":
    main()