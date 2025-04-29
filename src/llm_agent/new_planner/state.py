# State structure for new_planner workflow
from typing import Any, Dict, List, Optional

from typing import TypedDict, Optional, List, Dict, Any

class PlannerState(TypedDict, total=False):
    """规划器状态，使用TypedDict以兼容langgraph"""
    user_input: str
    keyword: Optional[str]
    references: Optional[List[str]]
    plan: Optional[Dict[str, Any]]
    
def create_initial_state(user_input: str) -> PlannerState:
    """创建初始状态"""
    return PlannerState(user_input=user_input)
