import os
import re

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F1FF"
        u"\U00002700-\U000027BF"
        u"\U0001F900-\U0001F9FF"
        u"\U00002500-\U00002BEF"
        u"\U0001F000-\U0001FAFF"
        u"\U00000023-\U00000039]\u20e3"
        u"\U0001FA70-\U0001FAFF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

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