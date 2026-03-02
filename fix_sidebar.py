import os
import re

folders = ['pages', '.']

for folder in folders:
    for fname in os.listdir(folder):
        if fname.endswith('.py') and fname != 'fix_sidebar.py' and fname != 'fix.py':
            fpath = os.path.join(folder, fname)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Remove all st.page_link lines
            new_content = re.sub(r'^\s*st\.page_link\(.*?\)\n', '', content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Fixed: {fpath}')

print('Done!')