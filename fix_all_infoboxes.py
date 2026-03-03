import os

pages = ['app.py'] + [f'pages/{f}' for f in os.listdir('pages') if f.endswith('.py')]

inline_style = "style='background:#FFFFFF;border-left:4px solid #2563B0;border-radius:6px;padding:10px 14px;font-size:13px;color:#1E293B;line-height:1.6;'"

fixed = 0
for f in pages:
    with open(f, encoding='utf-8') as file:
        content = file.read()
    
    if "class='info-box'" in content:
        new_content = content.replace("class='info-box'", inline_style)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Fixed: {f}")
        fixed += 1

print(f"\nDone. Fixed {fixed} files.")