import re
html = open('skool_page.html', encoding='utf-8').read()
urls = re.findall(r'https?://[^\s"\'<>]+(?:wistia|vimeo|m3u8|mp4)[^\s"\'<>]*', html, re.IGNORECASE)
print('\n'.join(set(urls)))
