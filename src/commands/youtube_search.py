import urllib.request
import urllib.parse
import re


def youtube_search(query):
    query_string = urllib.parse.urlencode({"search_query": query})
    html_content = urllib.request.urlopen("https://www.youtube.com.hk/results?" + query_string)
    search_results = re.findall(r'url\"\:\"\/watch\?v\=(.*?(?=\"))', html_content.read().decode())
    if search_results:
        return f"http://www.youtube.com/watch?v={search_results[0][:11]}"
