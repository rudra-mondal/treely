with open('treely/renderer.py', 'r') as f:
    content = f.read()

content = content.replace(
'''try:
    from rich.console import Console''',
'''from rich.console import Console
try:'''
)

with open('treely/renderer.py', 'w') as f:
    f.write(content)
