import os

folders = ['pages', '.']

for folder in folders:
    for fname in os.listdir(folder):
        if fname.endswith('.py') and not fname.startswith('fix'):
            fpath = os.path.join(folder, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            original = content
            content = content.replace('', '-')
            if content != original:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Fixed: {fpath}')

print('Done!')