from django import template


from words.cw import iter_api_phoneme
from .flask_server import app

# register = template.Library()


@app.template_filter('phon_length')
def phon_length(value):
    c = 0
    for x in iter_api_phoneme(value):
        c += 1
    return c
