"""Build page.html (artifact body, images inlined) and index.html (standalone, images as files)."""
import base64, io

# One place to change when Zoho finishes applying the custom domain:
DESK = "https://pimplepoppers.zohodesk.eu/portal/nl/home"
# -> "https://support.pimplepoppers.be/portal/nl/home"

SITE = "https://pimplepoppers.be/"
BLURB = ("Wij verzorgen de volledige technische ondersteuning van animatieproductiehuizen: "
         "renderfarms, kleurcontinuïteit, hardware, en het volledige beheer van katten in productie.")

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
DESCRIPTION = "Pimple Poppers - de IT- en supportpartner voor animatieproductiehuizen in Belgie."

# Link-preview card (WhatsApp / Slack / iMessage / Facebook) + one canonical address, so
# www / http / tracking-suffixed variants all resolve to the same page.
social = (f'<link rel="canonical" href="{SITE}">\n'
          '<meta property="og:type" content="website">\n'
          '<meta property="og:site_name" content="Pimple Poppers">\n'
          f'<meta property="og:url" content="{SITE}">\n'
          '<meta property="og:title" content="Pimple Poppers">\n'
          f'<meta property="og:description" content="{BLURB}">\n'
          f'<meta property="og:image" content="{SITE}og-card.png">\n'
          '<meta property="og:image:width" content="1200">\n'
          '<meta property="og:image:height" content="630">\n'
          '<meta property="og:image:alt" content="Het Pimple Poppers-logo: de splat op wit, '
          'het woordmerk op zwart.">\n'
          '<meta property="og:locale" content="nl_BE">\n'
          '<meta name="twitter:card" content="summary_large_image">\n'
          '<meta name="twitter:title" content="Pimple Poppers">\n'
          f'<meta name="twitter:description" content="{BLURB}">\n'
          f'<meta name="twitter:image" content="{SITE}og-card.png">')

doc = ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       f'<meta name="description" content="{DESCRIPTION}">\n'
       f'{social}\n'
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
