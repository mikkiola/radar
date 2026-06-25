#!/usr/bin/env python3
import os

for folder, title in [('02_Patterns', 'Паттерны'), ('01_Assessments', 'Оценки')]:
    files = sorted([f for f in os.listdir(f'docs/{folder}') if f.endswith('.md') and f != 'index.md'])
    lines = [f'# {title}', '']
    for f in files:
        name = f.replace('_', ' ').replace('.md', '')
        lines.append(f'- [{name}]({f})')
    with open(f'docs/{folder}/index.md', 'w') as fh:
        fh.write('\n'.join(lines))
    print(f"{folder}/index.md: {len(files)} файлов")
