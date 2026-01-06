#!/usr/bin/env python3
"""
文档重复内容检测脚本

功能：
1. 扫描指定目录下的所有Markdown文件
2. 计算文件的哈希值（基于内容）
3. 识别重复的文件内容
4. 检测相似的内容（基于文本相似度）
5. 生成重复内容报告

使用场景：
- 文档重整后，检测是否有重复或高度相似的内容
- 帮助识别可以合并或删除的重复文档

作者：AI助理
创建日期：2025-12-31
"""

import os
import re
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import difflib

class DocumentDuplicateChecker:
    """文档重复内容检测器"""
    
    def __init__(self, docs_root: str):
        """
        初始化检测器
        
        参数：
            docs_root: 文档根目录路径
        """
        self.docs_root = Path(docs_root).resolve()
        if not self.docs_root.exists():
            raise ValueError(f"文档根目录不存在: {self.docs_root}")
        
        # 文件哈希索引：哈希值 -> 文件路径列表
        self.hash_index: Dict[str, List[Path]] = defaultdict(list)
        
        # 文件内容缓存：文件路径 -> 内容
        self.content_cache: Dict[Path, str] = {}
    
    def get_file_hash(self, file_path: Path) -> str:
        """
        计算文件的哈希值
        
        参数：
            file_path: 文件路径
        
        返回：
            MD5哈希值
        """
        # 读取文件内容
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        self.content_cache[file_path] = content
        
        # 计算哈希值
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def build_hash_index(self) -> None:
        """
        构建哈希索引
        
        扫描所有.md文件，计算哈希值并建立索引
        """
        print(f"正在构建哈希索引，根目录: {self.docs_root}")
        md_files = list(self.docs_root.rglob("*.md"))
        print(f"找到 {len(md_files)} 个.md文件")
        
        for i, file_path in enumerate(md_files, 1):
            rel_path = file_path.relative_to(self.docs_root)
            if i % 50 == 0:
                print(f"  处理进度: {i}/{len(md_files)}")
            
            try:
                file_hash = self.get_file_hash(file_path)
                self.hash_index[file_hash].append(rel_path)
            except Exception as e:
                print(f"  ⚠️  警告：处理文件 {rel_path} 时出错: {e}")
        
        print(f"哈希索引构建完成")
    
    def find_exact_duplicates(self) -> Dict[str, List[Path]]:
        """
        查找完全相同的重复文件
        
        返回：
字典            ：哈希值 -> 文件路径列表（至少2个文件）
        """
        duplicates = {}
        for file_hash, file_paths in self.hash_index.items():
            if len(file_paths) >= 2:
                duplicates[file_hash] = file_paths
        
        return duplicates
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        参数：
            text1: 第一个文本
            text2: 第二个文本
        
        返回：
            相似度分数 (0.0 ~ 1.0)
        """
        # 使用difflib的SequenceMatcher
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def find_similar_documents(self, threshold: float = 0.8) -> List[Tuple[Path, Path, float]]:
        """
        查找相似的文档
        
        参数：
            threshold: 相似度阈值 (默认: 0.8)
        
        返回：
            列表：(文件1路径, 文件2路径, 相似度)
        """
        similar_pairs = []
        file_paths = list(self.content_cache.keys())
        
        print(f"正在计算文档相似度，共 {len(file_paths)} 个文件")
        
        # 比较每对文件
        for i in range(len(file_paths)):
            path1 = file_paths[i]
            content1 = self.content_cache[path1]
            
            for j in range(i + 1, len(file_paths)):
                path2 = file_paths[j]
                content2 = self.content_cache[path2]
                
                # 计算相似度
                similarity = self.calculate_similarity(content1, content2)
                
                if similarity >= threshold:
                    rel_path1 = path1.relative_to(self.docs_root)
                    rel_path2 = path2.relative_to(self.docs_root)
                    similar_pairs.append((rel_path1, rel_path2, similarity))
        
        # 按相似度降序排序
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        生成重复内容报告
        
        参数：
            output_file: 输出文件路径 (可选)
        
        返回：
            报告内容
        """
        report_lines = []
        
        # 报告头部
        report_lines.append("=" * 60)
        report_lines.append("文档重复内容检测报告")
        report_lines.append(f"生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"文档根目录: {self.docs_root}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # 1. 完全相同的重复文件
        exact_duplicates = self.find_exact_duplicates()
        
        report_lines.append("1. 完全相同的重复文件")
        report_lines.append("-" * 40)
        
        if exact_duplicates:
            report_lines.append(f"找到 {len(exact_duplicates)} 组完全相同的重复文件:")
            report_lines.append("")
            
            for i, (file_hash, file_paths) in enumerate(exact_duplicates.items(), 1):
                report_lines.append(f"第 {i }组 (哈希: {file_hash[:8]}...):")
                for file_path in file_paths:
                    report_lines.append(f"  - {file_path}")
                report_lines.append("")
        else:
            report_lines.append("✅ 未发现完全相同的重复文件")
            report_lines.append("")
        
        # 2. 高度相似的文档
        similar_docs = self.find_similar_documents(threshold=0.7)
        
        report_lines.append("2. 高度相似的文档 (相似度 ≥ 70%)")
        report_lines.append("-" * 40)
        
        if similar_docs:
            # 按相似度分组
            high_similarity = [p for p in similar_docs if p[2] >= 0.9]
            medium_similarity = [p for p in similar_docs if 0.7 <= p[2] < 0.9]
            
            report_lines.append(f"高度相似 (≥90%): {len(high_similarity)} 对")
            report_lines.append(f"中度相似 (70%-90%): {len(medium_similarity)} 对")
            report_lines.append("")
            
            if high_similarity:
                report_lines.append("高度相似文档对:")
                for path1, path2, similarity in high_similarity[:10]:  # 显示前10对
                    report_lines.append(f"  - {path1} ↔ {path2} ({similarity:.1%})")
                if len(high_similarity) > 10:
                    report_lines.append(f"  ... 还有 {len(high_similarity) - 10} 对未显示")
                report_lines.append("")
            
            if medium_similarity:
                report_lines.append("中度相似文档对 (前10对):")
                for path1, path2, similarity in medium_similarity[:10]:
                    report_lines.append(f"  - {path1} ↔ {path2} ({similarity:.1%})")
                if len(medium_similarity) > 10:
                    report_lines.append(f"  ... 还有 {len(medium_similarity) - 10} 对未显示")
                report_lines.append("")
        else:
            report_lines.append("✅ 未发现高度相似的文档")
            report_lines.append("")
        
        # 3. 统计
        report_lines.append("3. 统计信息")
        report_lines.append("-" * 40)
        
        total_files = len(self.content_cache)
        total_duplicates = sum(len(paths) for paths in exact_duplicates.values())
        unique_files = total_files - total_duplicates + len(exact_duplicates)
        
        report_lines.append(f"📊 文件总数: {total_files}")
        report_lines.append(f"📊 唯一文件数: {unique_files}")
        report_lines.append(f"📊 重复文件数: {total_duplicates - len(exact_duplicates)}")
        report_lines.append(f"📊 重复文件组数: {len(exact_duplicates)}")
        
        # 重复文件大小统计
        if exact_duplicates:
            total_wasted_space = 0
            for file_hash, file_paths in exact_duplicates.items():
                if file_paths:
                    # 获取第一个文件的大小
                    file_path = self.docs_root / file_paths[0]
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        wasted_space = file_size * (len(file_paths) - 1)
                        total_wasted_space += wasted_space
            
            report_lines.append(f"📊 潜在浪费空间: {self._format(total_size_wasted_space)}")
        
        report_lines.append("")
        
        # 4. 建议操作
        report_lines.append("4. 建议操作")
        report_lines.append("-" * 40)
        
        if exact_duplicates or similar_docs:
            report_lines.append("建议按以下顺序处理重复文档:")
            report_lines.append("")
            report_lines.append("1. 完全相同的重复文件:")
            report_lines.append("   - 保留一份，删除其他副本")
            report_lines.append("   - 更新所有指向被删除文件的链接")
            report_lines.append("")
            report_lines.append("2. 高度相似的文档 (≥90%):")
            report_lines.append("   - 比较内容差异，决定是否合并")
            report_lines.append("   - 保留更完整的版本，删除冗余版本")
            report_lines.append("")
            report_lines.append("3. 中度相似的文档 (70%-90%):")
            report_lines.append("   - 评估是否需要同时保留")
            report_lines.append("   - 考虑重写或重构内容")
            report_lines.append("")
            report_lines.append("💡 提示: 使用 docs_link_fix.py 修复链接")
        else:
            report_lines.append("✅ 文档状态良好，无需特别处理")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        report_content = "\n".join(report_lines)
        
        # 写入输出文件
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(report_content, encoding='utf-8')
            print(f"报告已保存到: {output_path}")
        
        return report_content
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        参数：
            size_bytes: 字节数
        
        返回：
            格式化后的字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检测文档重复内容   ')
 parser.add_argument('--docs-root', default='./docs',
                       help='文档根目录路径 (默认: ./docs)')
    parser.add_argument('--output', '-o', 
                       help='输出报告文件路径 (可选)')
    parser.add_argument('--threshold', type=float, default=0.8,
                       help='相似度阈值 (默认: 0.8)')
    parser.add_argument('--quick', action='store_true',
                       help='快速模式 (仅检测完全相同的重复)')
    
    args = parser.parse_args()
    
   :
 try        # 创建检测器
        checker = DocumentDuplicateChecker(args.docs_root)
        
        # 构建哈希索引       
 checker.build_hash_index()
        
        # 生成报告
        report = checker.generate_report(args.output)
        
        # 打印报告摘要
        print("\n" + "="*50)
        print("检测完成!")
        print("="*50)
        
        # 显示摘要
        exact_duplicates = checker.find_exact_duplicates()
        if exact_duplicates:
            print(f"⚠️  发现 {len(exact_duplicates)} 组完全相同的重复文件")
            for file_hash, file_paths in list(exact_duplicates.items())[:3]:  # 显示前3组
                print(f"  组: {file_hash[:8]}... 包含 {len(file_paths)} 个文件")
                for path in file_paths[:3]:  # 显示前3个文件
                    print(f"    - {path}")
                if len(file_paths) > 3:
                    print(f"    ... 还有 {len(file_paths) - 3} 个文件")
                print()
        
        if not args.quick:
            similar_docs = checker.find_similar_documents(args.threshold)
            if similar_docs:
                print(f"⚠️  发现 {len(similar_docs)} 对相似文档 (阈值: {args.threshold})")
                for path1, path2, similarity in similar_docs[:5]:  # 显示前5对
                    print(f"  - {path1} ↔ {path2 ({}similarity:.1%})")
        
        if not exact_duplicates and (args.quick or not similar_docs):
            print("✅ 未发现重复或高度相似的文档")
        
        print(f"\n详细报告已{'保存到: ' + args.output if args.output else '在控制台显示'}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())