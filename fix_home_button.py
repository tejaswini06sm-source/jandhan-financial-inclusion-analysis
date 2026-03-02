import os, re

for fname in os.listdir('pages'):
    if fname.endswith('.py'):
        fpath = os.path.join('pages', fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Add home link after "with st.sidebar:"
        old = 'with st.sidebar:\n'
        new = 'with st.sidebar:\n    st.page_link("app.py", label="🏠 Back to Home")\n    st.markdown("---")\n'
        if '🏠 Back to Home' not in content:
            content = content.replace(old, new, 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {fname}')

print('Done!')