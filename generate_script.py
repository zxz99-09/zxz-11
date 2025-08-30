import json
from jinja2 import Environment, FileSystemLoader

# 读取 JSON 配置
with open('configs/config.json', 'r') as f:
    config = json.load(f)

# 加载模板
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('script_template1.py.j2')

# 渲染模板
rendered = template.render(config)

# 写入生成的脚本
with open('script1.py', 'w') as f:
    f.write(rendered)

print("✅ script.py 已生成")

template = env.get_template('script_template2.py.j2')

# 渲染模板
rendered = template.render(config)

# 写入生成的脚本
with open('script2.py', 'w') as f:
    f.write(rendered)
