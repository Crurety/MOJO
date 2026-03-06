#!/usr/bin/env python3
"""自动修复速率限制装饰器缺少request参数的问题"""

import re
import os
from pathlib import Path

def fix_rate_limit_in_file(file_path):
    """修复单个文件中的速率限制问题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 查找所有使用@limiter.limit的函数
    # 匹配模式: @limiter.limit(...) 后跟 @router.xxx(...) 后跟 def function_name(...)
    pattern = r'(@limiter\.limit\([^\)]+\)\s*\n@router\.\w+\([^\)]+\)\s*\ndef\s+\w+\s*\()([^)]*?)(\):)'

    def add_request_param(match):
        decorator = match.group(1)
        params = match.group(2)
        closing = match.group(3)

        # 检查是否已经有request参数
        if 'request:' in params or 'request =' in params:
            return match.group(0)

        # 检查是否需要添加Request导入
        needs_request_import = True

        # 添加request参数
        if params.strip():
            # 如果已有参数，在第一个参数后添加
            if ',' in params:
                # 在第一个参数后添加
                parts = params.split(',', 1)
                new_params = parts[0] + ', request: Request,' + parts[1]
            else:
                # 只有一个参数，在前面添加
                new_params = 'request: Request, ' + params
        else:
            # 没有参数，直接添加
            new_params = 'request: Request'

        return decorator + new_params + closing

    # 执行替换
    new_content = re.sub(pattern, add_request_param, content, flags=re.MULTILINE)

    # 确保导入了Request
    if new_content != original_content:
        if 'from fastapi import' in new_content and 'Request' not in new_content.split('from fastapi import')[1].split('\n')[0]:
            # 在fastapi导入中添加Request
            new_content = re.sub(
                r'(from fastapi import [^;\n]+)',
                lambda m: m.group(1) + ', Request' if 'Request' not in m.group(1) else m.group(1),
                new_content,
                count=1
            )

    # 如果内容有变化，写回文件
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    """主函数"""
    api_dir = Path('app/api/v1')
    fixed_files = []

    for py_file in api_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue

        try:
            if fix_rate_limit_in_file(py_file):
                fixed_files.append(py_file.name)
                print(f"✓ 已修复: {py_file.name}")
        except Exception as e:
            print(f"✗ 修复失败 {py_file.name}: {e}")

    if fixed_files:
        print(f"\n总共修复了 {len(fixed_files)} 个文件")
    else:
        print("\n没有需要修复的文件")

if __name__ == '__main__':
    main()
