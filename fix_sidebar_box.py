import os

pages = ['app.py'] + [f'pages/{f}' for f in os.listdir('pages') if f.endswith('.py')]

for f in pages:
    with open(f, encoding='utf-8') as file:
        content = file.read()
    if 'District data' in content or 'Gender data' in content or 'data-sources' in content:
        print(f"FOUND IN: {f}")
        # Find the lines
        for i, line in enumerate(content.split('\n'), 1):
            if any(x in line for x in ['District data', 'Gender data', 'source', 'kpi-card', 'info-box']):
                print(f"  Line {i}: {line.strip()}")