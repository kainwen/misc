from flask import Flask, url_for
from jinja2 import Template
import os

app = Flask(__name__, static_url_path="/", static_folder='./')

html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Solution</title>
</head>

<body>
  {% for pic,label in data %}
  <h2> {{ pic }}  </h2>
  <img src="{{ pic }}" width="300" height="400" class="image">
  {{ label }}
  <hr>
  {% endfor %}
  </ul>
</body>
</html>
"""

@app.route('/')
def index():
    pics = []
    for fn in os.listdir("."):
        if fn.endswith(".png"):
            pics.append(fn)
    pics.sort(key=lambda s: int(s.split(".")[0]))
    pics = [url_for('static', filename=pic) for pic in pics]
    with open("labels") as f:
        ls = f.readlines()
    ls.append("done")
    template = Template(html)
    return template.render(data=zip(pics, ls))
    

app.run(host='0.0.0.0', port=8080)
