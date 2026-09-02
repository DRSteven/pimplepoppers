"""Build page.html (artifact body, images inlined) and index.html (standalone, images as files)."""
import base64, io

# One place to change when Zoho finishes applying the custom domain:
DESK = "https://pimplepoppers.zohodesk.eu/portal/nl/home"
# -> "https://support.pimplepoppers.be/portal/nl/home"

def datauri(path):
    return "data:image/png;base64," + base64.b64encode(open(path, 'rb').read()).decode('ascii')

tpl = io.open('template.html', encoding='utf-8').read()

def fill(logo_top, logo_bottom, splat):
    return (tpl.replace('__LOGO_TOP__', logo_top)
               .replace('__LOGO_BOTTOM__', logo_bottom)
               .replace('__SPLAT__', splat)
               .replace('__DESK__', DESK))

# artifact body: everything inlined (external images are blocked by the artifact CSP)
page = fill(datauri('logo-top-embed.png'), datauri('logo-bottom-embed.png'), datauri('splat-invert.png'))
io.open('page.html', 'w', encoding='utf-8').write(page)

# hosted: real files, full document
body = fill('logo-top.png', 'logo-bottom.png', 'splat-invert.png')
cut = body.index('<div class="band-white">')
head, markup = body[:cut].rstrip(), body[cut:]
head = head.replace('<title>Pimple Poppers</title>',
                    '<title>Pimple Poppers</title>\n'
                    '<link rel="icon" href="favicon.ico" sizes="any">\n'
                    '<link rel="icon" href="favicon-512.png" type="image/png">')
doc = ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<meta name="description" content="Pimple Poppers - de IT- en supportpartner voor '
       'animatieproductiehuizen in Belgie.">\n'
       f'{head}\n</head>\n<body>\n{markup}\n</body>\n</html>\n')
io.open('index.html', 'w', encoding='utf-8').write(doc)

print(f"page.html  {len(page):>9,} chars (images inlined)")
print(f"index.html {len(doc):>9,} chars (images as files)")

from html.parser import HTMLParser
VOID = {'meta','link','br','img','hr','input','source'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.st=[]; s.bad=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.st.append(t)
    def handle_endtag(s,t):
        if s.st and s.st[-1]==t: s.st.pop()
        elif t in s.st:
            while s.st and s.st.pop()!=t: pass
            s.bad.append('mismatch:'+t)
        else: s.bad.append('stray:'+t)
p=P(); p.feed(doc)
print("unclosed:", p.st or "none", "| issues:", p.bad or "none")
assert '__' not in page and '__' not in doc, "unreplaced placeholder!"
print("placeholders: all replaced")
