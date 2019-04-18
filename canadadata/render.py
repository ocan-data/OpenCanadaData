from IPython.display import HTML, display

def _render_list_html(l):
    o = []
    for e in l:
        o.append('<li>%s</li>' % _render_as_html(e))
    return '<ol>%s</ol>' % ''.join(o)

def _render_dict_html(d):
    o = []
    for k, v in d.items():
        o.append('<tr><td>%s</td><td>%s</td></tr>' % (str(k), _render_as_html(v)))
    return '<table>%s</table>' % ''.join(o)

def _render_as_html(e):
    o = []
    if isinstance(e, list):
        o.append(_render_list_html(e))
    elif isinstance(e, dict):
        o.append(_render_dict_html(e))
    else:
        o.append(str(e))
    return '<html><body>%s</body></html>' % ''.join(o)

def render_as_html(e):
    display(HTML(_render_as_html(e)))