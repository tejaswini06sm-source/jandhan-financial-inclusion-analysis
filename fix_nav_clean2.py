import os, re

for fname in os.listdir('pages'):
    if fname.endswith('.py'):
        fpath = os.path.join('pages', fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove only the dropdown block
        content = re.sub(
            r'\n    pages = \{[^}]+\}\n    selected_page = st\.selectbox\([^)]+\)\n    if selected_page:\n        st\.switch_page\(pages\[selected_page\]\)\n    st\.markdown\("---"\)',
            '',
            content,
            flags=re.DOTALL
        )

        # Also remove old Go button version
        content = re.sub(
            r'\n    page = st\.selectbox.*?st\.button\("Go ➜"\):\n        st\.switch_page\(page_map\[page\]\)\n    st\.markdown\("---"\)',
            '',
            content,
            flags=re.DOTALL
        )

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {fname}')

print('Done!')