import urllib.request, re

res = urllib.request.urlopen('http://localhost:3000')
html = res.read().decode('utf-8')

css_links = re.findall(r'href="(/_next/static/css/[^"]+)"', html)
print('CSS count:', len(css_links))
for link in css_links:
    css_res = urllib.request.urlopen('http://localhost:3000' + link)
    print('CSS:', link, 'Status:', css_res.status, 'Size:', len(css_res.read()))

js_links = re.findall(r'src="(/_next/static/[^"]+)"', html)
print('JS count:', len(js_links))
for link in js_links[:5]:
    js_res = urllib.request.urlopen('http://localhost:3000' + link)
    print('JS:', link, 'Status:', js_res.status, 'Size:', len(js_res.read()))
