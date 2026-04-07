import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlencode
from config import SEARCH_ENGINES
import json
import time
class SearchEngine:
    def __init__(self, settings=None):
        self.engines = SEARCH_ENGINES
        self.settings = settings or {}
        self.session = requests.Session()
        user_agent = self.settings.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        if self.settings.get('proxy_enabled', False):
            proxy_url = self.settings.get('proxy_http', '') or self.settings.get('proxy_https', '')
            if proxy_url:
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                self.session.proxies.update(proxies)
                print(f"[PROXY] Enabled: {proxy_url}")
    def search(self, query, engine="DuckDuckGo"):
        print(f"[DORKING] Query: {query}")
        print(f"[DORKING] Engine: {engine}")
        timeout = self.settings.get('timeout', 15)
        try:
            if engine == "Google":
                return self._google_dorking(query, timeout)
            elif engine == "DuckDuckGo":
                return self._duckduckgo_dorking(query, timeout)
            elif engine == "Bing":
                return self._bing_dorking(query, timeout)
            else:
                return self._generic_search(query, engine, timeout)
        except Exception as e:
            print(f"[DORKING] Error: {str(e)}")
            raise Exception(f"Dorking failed: {str(e)}")
    def _google_dorking(self, query, timeout=15):
        results = []
        max_results = self.settings.get('max_results', 20)
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}"
            print(f"[GOOGLE] URL: {url}")
            response = self.session.get(url, timeout=timeout)
            print(f"[GOOGLE] Status: {response.status_code}")
            with open('google_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("[GOOGLE] Saved response to google_response.html")
            if response.status_code != 200:
                print(f"[GOOGLE] Bad status: {response.status_code}")
                return []
            soup = BeautifulSoup(response.text, 'html.parser')
            if "detected unusual traffic" in response.text.lower() or "captcha" in response.text.lower():
                print("[GOOGLE] Detected CAPTCHA or block page")
                return []
            print(f"[GOOGLE] Parsing results...")
            for item in soup.find_all('div', class_='g'):
                try:
                    h3 = item.find('h3')
                    if not h3:
                        continue
                    title = h3.get_text(strip=True)
                    link = item.find('a', href=True)
                    if not link:
                        continue
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        continue
                    if 'google.com' in href or 'youtube.com/redirect' in href:
                        continue
                    snippet = ""
                    snippet_div = item.find('div', class_=['VwiC3b', 'IsZvec', 'yXK7lf'])
                    if snippet_div:
                        snippet = snippet_div.get_text(strip=True)
                    if title and href:
                        results.append({
                            'title': title,
                            'url': href,
                            'snippet': snippet
                        })
                        print(f"[GOOGLE] Found: {title[:50]}")
                except Exception as e:
                    print(f"[GOOGLE] Parse error: {e}")
                    continue
            print(f"[GOOGLE] Total results: {len(results)}")
        except Exception as e:
            print(f"[GOOGLE] Error: {e}")
            import traceback
            traceback.print_exc()
        return results[:max_results]
    def _duckduckgo_dorking(self, query, timeout=15):
        results = []
        max_results = self.settings.get('max_results', 20)
        try:
            from urllib.parse import urlparse, parse_qs, unquote
            url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
            print(f"[DDG] URL: {url}")
            headers = {
                'User-Agent': self.settings.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=timeout, proxies=self.session.proxies if self.session.proxies else None)
            print(f"[DDG] Status: {response.status_code}")
            with open('ddg_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("[DDG] Saved response to ddg_response.html")
            if response.status_code != 200:
                print(f"[DDG] Bad status, trying Bing...")
                return self._bing_dorking(query, timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            result_links = soup.find_all('a', class_='result-link')
            print(f"[DDG] Found {len(result_links)} result links")
            for link in result_links:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    if 'duckduckgo.com/l/' in href:
                        parsed = urlparse('https:' + href if href.startswith('//') else href)
                        params = parse_qs(parsed.query)
                        if 'uddg' in params:
                            real_url = unquote(params['uddg'][0])
                        else:
                            continue
                    else:
                        real_url = href
                    if not real_url or not real_url.startswith('http'):
                        continue
                    snippet = ""
                    parent_tr = link.find_parent('tr')
                    if parent_tr:
                        next_tr = parent_tr.find_next_sibling('tr')
                        if next_tr:
                            snippet_td = next_tr.find('td', class_='result-snippet')
                            if snippet_td:
                                snippet = snippet_td.get_text(strip=True)
                    results.append({
                        'title': title,
                        'url': real_url,
                        'snippet': snippet
                    })
                    print(f"[DDG] Found: {title[:50]}")
                except Exception as e:
                    print(f"[DDG] Parse error: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            print(f"[DDG] Total results: {len(results)}")
            if not results:
                print("[DDG] No results, trying Bing...")
                return self._bing_dorking(query, timeout)
        except Exception as e:
            print(f"[DDG] Error: {e}")
            import traceback
            traceback.print_exc()
            return self._bing_dorking(query, timeout)
        return results[:max_results]
    def _bing_dorking(self, query, timeout=15):
        results = []
        max_results = self.settings.get('max_results', 20)
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
            print(f"[BING] URL: {url}")
            response = self.session.get(url, timeout=timeout)
            print(f"[BING] Status: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('li', class_='b_algo'):
                try:
                    h2 = item.find('h2')
                    if not h2:
                        continue
                    link = h2.find('a')
                    if not link:
                        continue
                    title = h2.get_text(strip=True)
                    url = link.get('href', '')
                    snippet_elem = item.find('p')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    if url and title:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                        print(f"[BING] Found: {title[:50]}")
                except:
                    continue
        except Exception as e:
            print(f"[BING] Error: {e}")
        return results[:max_results]
    def _generic_search(self, query, engine):
        results = []
        try:
            url = self.engines[engine] + quote_plus(query)
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                try:
                    href = link['href']
                    text = link.get_text(strip=True)
                    if text and 'http' in href and len(text) > 15:
                        skip = ['google.com', 'bing.com', 'yandex', 'baidu', 'duckduckgo']
                        if not any(s in href.lower() for s in skip):
                            results.append({
                                'title': text[:100],
                                'url': href,
                                'snippet': ''
                            })
                            if len(results) >= 20:
                                break
                except:
                    continue
        except Exception as e:
            print(f"[GENERIC] Error: {e}")
        return results[:20]