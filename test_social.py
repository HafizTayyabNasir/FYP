import httpx
import re

url = 'https://www.sprucestreetnyc.org/'
r = httpx.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print('status:', r.status_code)

patterns = {
    "facebook": r'https?://(?:www\.)?(?:facebook\.com|fb\.com)/(?!(?:tr|plugins|share|login|dialog|sharer|photo|video|groups|events|pages/create)(?:/|$))([a-zA-Z0-9._%-]+)/?(?:\?[^"\'<>\s]*)?',
    "instagram": r'https?://(?:www\.)?instagram\.com/(?!(?:p|reel|explore|accounts|tv|stories)(?:/|$))([a-zA-Z0-9._]+)/?(?:\?[^"\'<>\s]*)?'
}

for name, p in patterns.items():
    print(name, 'search:', re.search(p, r.text, re.IGNORECASE))
    print(name, 'findall:', re.findall(p, r.text, re.IGNORECASE))
