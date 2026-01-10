#!/usr/bin/env python3
"""
数据处理模块 - Day 2
负责数据清洗、分块、格式化
"""

import re
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """文本块数据类"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    chunk_index: int

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化处理器
        
        Args:
            chunk_size: 文本块大小（字符数）
            chunk_overlap: 块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊控制字符（保留常见标点）
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        return text.strip()
    
    def clean_code(self, code: str, language: str = "python") -> str:
        """
        清理代码
        
        Args:
            code: 原始代码
            language: 编程语言
            
        Returns:
            清理后的代码
        """
        if not code:
            return ""
        
        lines = code.split('\n')
        
        # 移除行尾空白
        lines = [line.rstrip() for line in lines]
        
        # 移除空行
        lines = [line for line in lines if line.strip()]
        
        # 重新组合
        return '\n'.join(lines)
    
    def split_text(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """
        分割文本为块
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            文本块列表
        """
        if not text:
            return []
        
        # 按句子分割（简单实现）
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                # 保存当前块
                if current_chunk:
                    chunk_content = ' '.join(current_chunk)
                    chunk = TextChunk(
                        content=chunk_content,
                        metadata=metadata.copy(),
                        chunk_id=f"{metadata.get('source', 'unk')}_{len(chunks)}",
                        chunk_index=len(chunks)
                    )
                    chunks.append(chunk)
                
                # 开始新块，包含重叠
                overlap_sentences = current_chunk[-self._get_overlap_sentence_count():] if current_chunk else []
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
        
        # 添加最后一个块
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = TextChunk(
                content=chunk_content,
                metadata=metadata.copy(),
                chunk_id=f"{metadata.get('source', 'unk')}_{len(chunks)}",
                chunk_index=len(chunks)
            )
            chunks.append(chunk)
        
        logger.info(f"分割文本完成: {len(chunks)}个块")
        return chunks
    
    def split_code_by_functions(self, code: str, language: str = "python") -> List[TextChunk]:
        """
        按函数分割代码
        
        Args:
            code: 代码文本
            language: 编程语言
            
        Returns:
            代码块列表
        """
        chunks = []
        
        if language.lower() == "python":
            # Python函数分割
            function_pattern = r'def\s+\w+\s*\([^)]*\)\s*:'
            lines = code.split('\n')
            
            current_function = []
            in_function = False
            indent_level = 0
            
            for line in lines:
                # 检查是否是新函数
                if re.match(function_pattern, line.strip()):
                    if current_function:
                        # 保存上一个函数
                        chunk_content = '\n'.join(current_function)
                        metadata = {
                            "type": "code",
                            "language": language,
                            "unit": "function"
                        }
                        chunk = TextChunk(
                            content=chunk_content,
                            metadata=metadata,
                            chunk_id=f"func_{len(chunks)}",
                            chunk_index=len(chunks)
                        )
                        chunks.append(chunk)
                    
                    # 开始新函数
                    current_function = [line]
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                
                elif in_function:
                    if line.strip() and (len(line) - len(line.lstrip())) > indent_level:
                        current_function.append(line)
                    else:
                        # 函数结束
                        if current_function:
                            chunk_content = '\n'.join(current_function)
                            metadata = {
                                "type": "code",
                                "language": language,
                                "unit": "function"
                            }
                            chunk = TextChunk(
                                content=chunk_content,
                                metadata=metadata,
                                chunk_id=f"func_{len(chunks)}",
                                chunk_index=len(chunks)
                            )
                            chunks.append(chunk)
                        
                        current_function = []
                        in_function = False
        
        else:
            # 其他语言使用通用分割
            metadata = {
                "type": "code",
                "language": language,
                "unit": "file"
            }
            chunk = TextChunk(
                content=code,
                metadata=metadata,
                chunk_id="code_0",
                chunk_index=0
            )
            chunks.append(chunk)
        
        logger.info(f"分割代码完成: {len(chunks)}个函数/块")
        return chunks
    
    def create_metadata(self, 
                       source_type: str, 
                       repo_name: str, 
                       file_path: str,
                       **extra_metadata) -> Dict[str, Any]:
        """
        创建标准化的元数据
        
        Args:
            source_type: 来源类型 ('code', 'doc', 'issue')
            repo_name: 仓库名称
            file_path: 文件路径
            **extra_metadata: 额外元数据
            
        Returns:
            元数据字典
        """
        import time
        
        metadata = {
            "source_type": source_type,
            "repository": repo_name,
            "file_path": file_path,
            "timestamp": time.time()
        }
        
        metadata.update(extra_metadata)
        return metadata
    
    def _get_overlap_sentence_count(self) -> int:
        """计算重叠句子数量"""
        # 简单实现：返回固定的重叠字符数对应的句子数
        return max(1, self.chunk_overlap // 50)  # 假设平均句子长度50字符

def test_processor():
    """测试处理器"""
    print("=" * 60)
    print("数据处理器测试")
    print("=" * 60)
    
    processor = DataProcessor(chunk_size=300, chunk_overlap=50)
    
    # 测试文本清理
    print("\n1. 测试文本清理...")
    dirty_text = "  这是一个  测试文本。  \n\n有多余的空白 和换行。  "
    clean_text = processor.clean_text(dirty_text)
    print(f"   原始: {repr(dirty_text)}")
    print(f"   清理后: {repr(clean_text)}")
    
    # 测试文本分割
    print("\n2. 测试文本分割...")
    test_text = """
    这是一个测试文本。我们将测试文本分割功能。
    这个功能很重要，因为它可以将长文本分割成小块。
    每个小块都可以被单独处理和分析。
    这样可以提高处理效率，并且更容易管理。
    """
    
    metadata = {"source": "test", "type": "text"}
    chunks = processor.split_text(test_text, metadata)
    
    print(f"   原始文本长度: {len(test_text)} 字符")
    print(f"   分割为: {len(chunks)} 个块")
    
    for i, chunk in enumerate(chunks[:3]):  # 显示前3个
        print(f"   块{i+1}: {len(chunk.content)}字符")
        print(f"     内容: {chunk.content[:50]}...")
    
    # 测试代码清理
    print("\n3. 测试代码清理...")
    dirty_code = """
def hello():
    print("Hello")  
    
    # 多余空白
    return True
    
    
"""
    clean_code = processor.clean_code(dirty_code, "python")
    print(f"   原始代码行数: {len(dirty_code.split(chr(10)))}")
    print(f"   清理后行数: {len(clean_code.split(chr(10)))}")
    
    # 测试代码分割
    print("\n4. 测试代码分割...")
    python_code = '''
    def function1():
    """第一个函数"""
        print("Hello from function1")
    def function2(param1, param2):
    """第二个函数"""
        result = param1 + param2
        return result
    '''
    code_chunks = processor.split_code_by_functions(python_code, "python")
    print(f"   分割为: {len(code_chunks)} 个函数")
    
    for i,chunk in enumerate(code_chunks):
        lines = chunk.content.split(chr(10))
        first_line = lines[0] if lines else ""
        print(f"   函数{i+1}: {len(lines)}行")
        print(f"     内容: {first_line}")


    
    print("\n" + "=" * 60)
    print("  数据处理器测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_processor()