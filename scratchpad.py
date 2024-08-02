from jinja2 import Template

context = {'product': ['hoodie', 'jacket', 'vest'], 'price': ["50", "40", "30"]}

html_template = """
<html>
<head></head>
<body>
<ul>
{% for index, item in enumerate(context['items']) %}
    {% set price = context['price'][index] %}
    <li>{{ item }} is on sale for ${{ price }}</li>
{% endfor %}
</ul>
</body>
</html>
"""

def build_html_body(context_dict):
    template = Template(html_template)
    html_content = template.render(context = context_dict)
    return html_content

result = build_html_body(context)
print(result)