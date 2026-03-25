import re, glob
for f in glob.glob('frontend/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        t = file.read()
    
    def replacer(m):
        style_content = m.group(1)
        # Add semicolon before closing brace if missing
        fixed = re.sub(r'([^;\{\s])(\s*\})', r'\1;\2', style_content)
        return '<style>' + fixed + '</style>'
    
    new_t = re.sub(r'<style>(.*?)</style>', replacer, t, flags=re.DOTALL)
    
    if new_t != t:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_t)
        print(f"Fixed semicolons in {f}")
