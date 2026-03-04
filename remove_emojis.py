import os
import re

def remove_emojis(text):
    # Remove all non-ASCII characters that are emoji/symbol ranges
    cleaned = re.sub(r'[^\x00-\x7F\u0900-\u097F\u20B9]+', '', text)
    return cleaned

folders = ['.', 'pages', 'utils']

for folder in folders:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if fname.endswith('.py'):
            fpath = os.path.join(folder, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            cleaned = remove_emojis(content)
            if cleaned != content:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                print(f"Cleaned: {fpath}")

print("Done.")