import re, glob
for file in glob.glob('frontend/*.html'):
    with open(file, encoding='utf-8') as f: text = f.read()
    print(file)
    print("  missing semicolons:", len(re.findall(r'[^;\{\}]\s*\}', text)))
