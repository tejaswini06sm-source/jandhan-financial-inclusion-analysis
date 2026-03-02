import os

folders = ['pages', '.']
fixed = 0

for folder in folders:
    for fname in os.listdir(folder):
        if fname.endswith('.py'):
            fpath = os.path.join(folder, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                original = content
                content = content.replace(
                    'open(css_file, encoding="utf-8")',
                    'open(css_file, encoding="utf-8")'
                )
                content = content.replace(
                    'open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8")',
                    'open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css"), encoding="utf-8")'
                )
                content = content.replace(
                    'open(os.path.join(os.path.dirname(__file__), "assets", "style.css"), encoding="utf-8")',
                    'open(os.path.join(os.path.dirname(__file__), "assets", "style.css"), encoding="utf-8")'
                )
                if content != original:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f'Fixed: {fpath}')
                    fixed += 1
            except Exception as e:
                print(f'Error on {fpath}: {e}')

print(f'Done. Fixed {fixed} files.')