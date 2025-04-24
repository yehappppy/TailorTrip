from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class SearchNode:
    """搜索树的节点类"""
    keyword: str
    content: str = ""
    is_specific: bool = False
    children: List["SearchNode"] = field(default_factory=list)
    parent: Optional["SearchNode"] = field(default=None, repr=False)
    
    def __post_init__(self):
        """在节点创建后设置子节点的parent引用"""
        for child in self.children:
            child.parent = self
    
    def add_child(self, child: "SearchNode") -> None:
        """添加子节点，并自动设置其parent引用
        
        Args:
            child: 要添加的子节点
        """
        child.parent = self
        self.children.append(child)
    
    def get_ancestors(self) -> List["SearchNode"]:
        """获取节点的所有祖先节点，从父节点到根节点
        
        Returns:
            List[SearchNode]: 祖先节点列表，从近到远排序
        """
        ancestors = []
        current = self.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    def get_root(self) -> "SearchNode":
        """获取根节点
        
        Returns:
            SearchNode: 根节点
        """
        current = self
        while current.parent is not None:
            current = current.parent
        return current
    
    def get_siblings(self) -> List["SearchNode"]:
        """获取节点的所有兄弟节点（不包括自身）
        
        Returns:
            List[SearchNode]: 兄弟节点列表
        """
        if self.parent is None:
            return []
        return [child for child in self.parent.children if child is not self]
    
    def get_subtree_nodes(self) -> List["SearchNode"]:
        """获取以当前节点为根的子树中的所有节点（包括自身）
        
        Returns:
            List[SearchNode]: 子树中的所有节点
        """
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_subtree_nodes())
        return nodes
    
    def find_nodes_by_keyword(self, keyword: str) -> List["SearchNode"]:
        """在子树中查找包含指定关键词的节点
        
        Args:
            keyword: 要查找的关键词
            
        Returns:
            List[SearchNode]: 匹配的节点列表
        """
        nodes = []
        if keyword.lower() in self.keyword.lower():
            nodes.append(self)
        for child in self.children:
            nodes.extend(child.find_nodes_by_keyword(keyword))
        return nodes
    
    def get_path_to_root(self) -> List[str]:
        """获取从当前节点到根节点的关键词路径
        
        Returns:
            List[str]: 关键词路径，从当前节点到根节点
        """
        path = [self.keyword]
        current = self.parent
        while current is not None:
            path.append(current.keyword)
            current = current.parent
        return path
    
    def to_dict(self) -> Dict[str, Any]:
        """将节点转换为字典格式"""
        return {
            "keyword": self.keyword,
            "content": self.content,
            "is_specific": self.is_specific,
            "children": [child.to_dict() for child in self.children]
        }


@dataclass
class SearchTree:
    """搜索树类"""
    root: Optional[SearchNode] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """将整个树转换为字典格式"""
        if self.root is None:
            return {}
        return self.root.to_dict()
    
    def to_json(self) -> str:
        """将树转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
