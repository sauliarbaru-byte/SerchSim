import re

with open('Index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract script
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if script_match:
    js_content = script_match.group(1).strip()
    with open('main.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print('main.js created.')
else:
    print('Script not found!')

# Replace script in Index.html
new_content = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="style.css">', content, flags=re.DOTALL)
new_content = re.sub(r'<script>.*?</script>', '<script src="main.js"></script>', new_content, flags=re.DOTALL)

with open('Index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Index.html updated.')
