import os
import yaml
import sys
import json
import re
from loguru import logger

def load_config():
    # 加载配置文件
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logger(name=None):
    """配置日志系统
    参数:
        name: 日志文件名前缀，为空时使用'app'
    返回:
        配置好的日志记录器
    """
    config = load_config()
    log_print = config.get('application_settings', {}).get('log_print', False)
    log_level = config.get('application_settings', {}).get('log_level', 'INFO')
    log_dir = config.get('application_settings', {}).get('log_dir', './output/logs')
    
    # 如果没有指定名称，使用默认名称
    if name is None:
        name = 'app'
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 移除默认的处理器
    logger.remove()
    
    # 如果配置了控制台输出，则添加控制台处理器
    if log_print:
        logger.add(sys.stderr, level=log_level)
    
    # 添加文件处理器
    log_file = os.path.join(log_dir, f"{name}_{{time}}.log")
    logger.add(
        log_file,
        rotation="10 MB",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    return logger

def get_logger(name=None):
    """获取日志记录器
    参数:
        name: 日志文件名前缀，为空时使用当前配置
    返回:
        日志记录器实例
    """
    # 如果指定了名称，则重新配置logger
    if name is not None:
        return setup_logger(name)
    return logger

def structure_output(input:str):
    """将输入字符串转换为JSON结构
    参数:
        input: 输入字符串，可能包含JSON数据
    返回:
        解析后的JSON对象，如果解析失败则返回None
    """
    try:
        # 尝试直接解析JSON
        return json.loads(input)
    except Exception:
        # 从标记语言代码块中提取JSON（如果存在）
        code_block_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', input)
        if code_block_match:
            input = code_block_match.group(1)
            
        # 尝试提取大括号内的内容
        match = re.search(r'\{[\s\S]*\}', input)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                # 修复常见的JSON问题
                # 将单引号替换为双引号，但保留转义的单引号
                json_str = re.sub(r"(?<!\\)'([^']+)(?<!\\)'", r'"\\1"', match.group())
                # 删除尾随逗号
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                # 为未引用的键添加引号
                json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
                
                try:
                    return json.loads(json_str)
                except Exception:
                    pass
        
        return None

# 初始化默认logger
setup_logger()