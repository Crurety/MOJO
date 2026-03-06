#!/usr/bin/env python3
"""批量修复所有速率限制装饰器缺少request参数的问题"""

import re
import os
from pathlib import Path

def fix_file(file_path):
    """修复单个文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # 检查是否是@limiter.limit装饰器
        if '@limiter.limit' in line:
            # 查找下一个@router装饰器
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('@'):
                new_lines.append(lines[j])
                j += 1

            # 现在j应该指向def行
            if j < len(lines) and lines[j].strip().startswith('def '):
                def_line = lines[j]

                # 检查函数参数中是否已有request
                if 'request:' not in def_line and 'request =' not in def_line:
                    # 找到函数名和参数开始位置
                    match = re.match(r'(\s*def\s+\w+\s*\()(.*)$', def_line)
                    if match:
                        indent_and_def = match.group(1)
                        rest = match.group(2)

                        # 如果参数在同一行结束
                        if ')' in rest and rest.strip() != '):':
                            # 在第一个参数前添加request
                            new_def = indent_and_def + 'request: Request, ' + rest
                            new_lines.append(new_def)
                            modified = True
                            i = j + 1
                            continue
                        elif rest.strip() == '):':
                            # 没有参数
                            new_def = indent_and_def + 'request: Request):\n'
                            new_lines.append(new_def)
                            modified = True
                            i = j + 1
                            continue
                        else:
                            # 参数跨多行，在下一行添加request
                            new_lines.append(def_line)
                            # 找到第一个参数行
                            k = j + 1
                            if k < len(lines):
                                param_line = lines[k]
                                indent = len(param_line) - len(param_line.lstrip())
                                new_param = ' ' * indent + 'request: Request,\n'
                                new_lines.append(new_param)
                                modified = True
                            i = j + 1
                            continue

                new_lines.append(def_line)
                i = j + 1
                continue

            i = j
            continue

        i += 1

    if modified:
        # 确保导入了Request
        content = ''.join(new_lines)
        if 'from fastapi import' in content:
            # 检查是否已导入Request
            import_match = re.search(r'from fastapi import ([^\n]+)', content)
            if import_match:
                imports = import_match.group(1)
                if 'Request' not in imports:
                    # 添加Request到导入
                    new_imports = imports.rstrip() + ', Request'
                    content = content.replace(
                        f'from fastapi import {imports}',
                        f'from fastapi import {new_imports}',
                        1
                    )

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

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
            if fix_file(py_file):
                fixed_files.append(py_file.name)
                print(f"✓ 已修复: {py_file.name}")
            else:
                print(f"- 无需修复: {py_file.name}")
        except Exception as e:
            print(f"✗ 修复失败 {py_file.name}: {e}")

    if fixed_files:
        print(f"\n总共修复了 {len(fixed_files)} 个文件")
    else:
        print("\n没有文件需要修复")

if __name__ == '__main__':
    main()
