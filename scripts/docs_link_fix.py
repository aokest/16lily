#!/usr/bin/env python3
"""
文档内部链接修复脚本

功能：
1. 扫描指定目录下的所有Markdown文件
2. 检测文档中的内部链接（指向其他.md文件的相对链接）
3. 根据新的文档目录结构更新链接路径
4. 支持手动确认或自动修复模式

使用场景：
- 文档目录结构调整后，需要更新文档间的交叉引用
- 确保文档链接指向正确的新位置

作者：AI助理
创建日期：2025-12-31
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib

class DocumentLinkFixer:
    """文档链接修复器"""
    
    def __init__(self, docs_root: str):
        """
        初始化修复器
        
        参数：
            docs_root: 文档根目录路径
        """
        self.docs_root = Path(docs_root).resolve()
        if not self.docs_root.exists():
            raise ValueError(f"文档根目录不存在: {self.docs_root}")
        
        # 文件索引：文件名 -> 相对路径列表（可能有重复文件名）
        self.file_index: Dict[str, List[Path]] = {}
        
        # 链接模式：匹配Markdown链接 [text](path)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def build_file_index(self) -> None:
        """
        构建文件索引
        
        遍历docs目录，记录所有.md文件的相对路径
        """
        print(f"正在构建文件索引，根目录: {self.docs_root}")
        
        for file_path in self.docs_root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() == '.md':
                rel_path = file_path.relative_to(self.docs_root)
                filename = file_path.name
                
                if filename not in self.file_index:
                    self.file_index[filename] = []
                self.file_index[filename].append(rel_path)
        
        print(f"索引构建完成，找到 {len(self.file_index)} 个不同的.md文件")
    
    def find_file_by_name(self, filename: str) -> Optional[List[Path]]:
        """
        通过文件名查找文件
        
        参数：
            filename: 要查找的文件名（带扩展名）
        
        返回：
            相对路径列表，如果未找到则None返回
        """
        # 确保文件名有.md扩展名
        if not filename.lower().endswith('.md'):
            filename = f"{filename}.md"
        
        return self.file_index.get(filename)
    
    def is_valid_link(self, link_path: str, source_file: Path) -> bool:
        """
        检查链接是否有效
        
        参数：
            link_path: 链接路径（相对或绝对）
            source_file: 源文件的相对路径
        
        返回：
            如果链接指向存在的文件则返回True
        """
        if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
            return True  # 外部链接或锚点，跳过
        
        # 尝试解析相对路径
        try:
            # 相对于源文件所在目录
            source_dir = self.docs_root / source_file.parent
            target_path = (source_dir / link_path).resolve()
            
            # 检查目标是否在docs根目录内且文件存在
            if target_path.is_file() and self.docs_root in target_path.parents:
                return True
        except Exception:
            pass
        
        return False
    
    def suggest_new_path(self, filename: str) -> Optional[Path]:
        """
        根据文件名建议新路径
        
        参数：
            filename: 文件名
        
        返回：
            建议的相对路径，如果找不到则返回None
        """
        paths = self.find_file_by_name(filename)
        if not paths:
            return None
        
        # 如果有多个同名文件，选择最可能的（不在archive中）
        non_archive_paths = [p for p in paths if 'archive' not in str(p)]
        if non_archive_paths:
            return non_archive_paths[0]
        
        # 否则返回第一个
        return paths[0]
    
    def fix_links_in_file(self, file_path: Path, dry_run: bool = True) -> int:
        """
        修复单个文件中的链接
        
        参数：
            file_path: 文件路径
            dry_run: 是否为试运行（不实际修改）
        
        返回：
            修复的链接数量
        """
        fixes = 0
        file_content = file_path.read_text(encoding='utf-8', errors='ignore')
        new_content = file_content
        
        # 查找所有链接
        for match in self.link_pattern.finditer(file_content):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # 跳过非.md链接
            if not link_url.lower().endswith('.md'):
                continue
            
            # 链接检查是否有效
            if self.is_valid_link(link_url, file_path.relative_to(self.docs_root)):
                continue  # 链接有效，跳过
            
            # 提取文件名
            filename = os.path.basename(link_url)
            
            # 查找建议的新路径
            new_path = self.suggest_new_path(filename)
            if not new_path:
                print(f"  ⚠️  警告：找不到文件 {filename}，无法修复链接")
                continue
            
            # 构建新的相对路径
            source_dir = file_path.parent
            target_path = self.docs_root / new_path
            
            # 计算新的相对路径
            try:
                new_relative = os.path.relpath(target_path, source_dir)
            except ValueError:
                # 在不同驱动器上，使用基于根的路径
                new_relative = str(new_path)
            
            # 替换链接
            old_link = f"[{link_text}]({link_url})"
            new_link = f"[{link_text}]({new_relative})"
            
            if old_link != new_link:
                print(f"  🔧 修复链接: {old_link} -> {new_link}")
                new_content = new_content.replace(old_link, new_link)
                fixes += 1
        
        # 如果不是试运行，则写入文件
        if not dry_run and fixes > 0:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"  💾 已保存修改到 {file_path}")
        
        return fixes
    
    def fix_all_links(self, dry_run: bool = True) -> Dict[str, int]:
        """
        修复所有文件中的链接
        
        参数：
            dry_run: 是否为试运行
        
        返回：
            字典：文件名 -> 修复数量
        """
        print(f"{'试运行模式' if dry_run else '实际修复模式'}")
        
        results = {}
        total_fixes = 0
        
        # 获取所有.md文件
        md_files = list(self.docs_root.rglob("*.md"))
        print(f"扫描到 {len(md_files)} 个.md文件")
        
        for file_path in md_files:
            rel_path = file_path.relative_to(self.docs_root)
            print(f"\n处理文件: {rel_path}")
            
            fixes = self.fix_links_in_file(file_path, dry_run)
            if fixes > 0:
                results[str(rel_path)] = fixes
                total_fixes += fixes
        
        print(f"\n{'='*50}")
        print(f"总计修复: {total_fixes} 个链接")
        print(f"涉及文件: {len(results)} 个")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='修复文档内部链接')
    parser.add_argument('--docs-root', default='./docs',
                       help='文档根目录路径 (默认: ./docs)')
    parser.add_argument('--apply', action='store_true',
                       help='实际应用修复 (默认: 试运行)')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细信息')
    
    args = parser.parse_args()
    
    try:
        # 创建修复器
        fixer = DocumentLinkFixer(args.docs_root)
        
        # 构建文件索引
        fixer.build_file_index()
        
        # 修复链接
        results = fixer.fix_all_links(dry_run=not args.apply)
        
        # 显示摘要
        if results:
            print("\n修复摘要:")
            for file_path, count in sorted(results.items()):
                print(f"  {file_path}: {count} 个链接")
        
        if not args.apply:
            print("\n💡 提示: 使用 --apply 参数实际应用修复")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())