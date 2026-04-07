import requests
from requests.exceptions import RequestException
import time
class UsernameChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.services = [
            {"name": "GitHub", "url_template": "https://github.com/{username}"},
            {"name": "Twitter", "url_template": "https://twitter.com/{username}"},
            {"name": "Instagram", "url_template": "https://instagram.com/{username}"},
            {"name": "Reddit", "url_template": "https://reddit.com/user/{username}"},
            {"name": "YouTube", "url_template": "https://youtube.com/@{username}"},
            {"name": "TikTok", "url_template": "https://tiktok.com/@{username}"},
            {"name": "LinkedIn", "url_template": "https://linkedin.com/in/{username}"},
            {"name": "Pinterest", "url_template": "https://pinterest.com/{username}"},
            {"name": "Tumblr", "url_template": "https://{username}.tumblr.com"},
            {"name": "Twitch", "url_template": "https://twitch.tv/{username}"},
            {"name": "Steam", "url_template": "https://steamcommunity.com/id/{username}"},
            {"name": "Spotify", "url_template": "https://open.spotify.com/user/{username}"},
            {"name": "SoundCloud", "url_template": "https://soundcloud.com/{username}"},
            {"name": "Medium", "url_template": "https://medium.com/@{username}"},
            {"name": "DeviantArt", "url_template": "https://www.deviantart.com/{username}"},
            {"name": "Behance", "url_template": "https://www.behance.net/{username}"},
            {"name": "Dribbble", "url_template": "https://dribbble.com/{username}"},
            {"name": "Patreon", "url_template": "https://www.patreon.com/{username}"},
            {"name": "Telegram", "url_template": "https://t.me/{username}"},
            {"name": "VK", "url_template": "https://vk.com/{username}"},
            {"name": "Habr", "url_template": "https://habr.com/ru/users/{username}"},
            {"name": "GitLab", "url_template": "https://gitlab.com/{username}"},
            {"name": "Bitbucket", "url_template": "https://bitbucket.org/{username}"},
            {"name": "Quora", "url_template": "https://www.quora.com/profile/{username}"},
            {"name": "Flickr", "url_template": "https://www.flickr.com/people/{username}"},
            {"name": "Vimeo", "url_template": "https://vimeo.com/{username}"},
            {"name": "Keybase", "url_template": "https://keybase.io/{username}"},
            {"name": "HackerOne", "url_template": "https://hackerone.com/{username}"},
            {"name": "Kaggle", "url_template": "https://www.kaggle.com/{username}"},
            {"name": "HackerRank", "url_template": "https://www.hackerrank.com/{username}"},
            {"name": "LeetCode", "url_template": "https://leetcode.com/{username}"},
            {"name": "Codewars", "url_template": "https://www.codewars.com/users/{username}"},
            {"name": "Replit", "url_template": "https://replit.com/@{username}"},
            {"name": "CodePen", "url_template": "https://codepen.io/{username}"},
            {"name": "Trello", "url_template": "https://trello.com/{username}"},
            {"name": "WordPress", "url_template": "https://{username}.wordpress.com"},
            {"name": "Blogger", "url_template": "https://{username}.blogspot.com"},
            {"name": "Goodreads", "url_template": "https://www.goodreads.com/{username}"},
            {"name": "Last.fm", "url_template": "https://www.last.fm/user/{username}"},
            {"name": "Bandcamp", "url_template": "https://{username}.bandcamp.com"},
            {"name": "Mixcloud", "url_template": "https://www.mixcloud.com/{username}"},
            {"name": "Discogs", "url_template": "https://www.discogs.com/user/{username}"},
            {"name": "Genius", "url_template": "https://genius.com/{username}"},
            {"name": "MyAnimeList", "url_template": "https://myanimelist.net/profile/{username}"},
            {"name": "Letterboxd", "url_template": "https://letterboxd.com/{username}"},
            {"name": "Chess.com", "url_template": "https://www.chess.com/member/{username}"},
            {"name": "Lichess", "url_template": "https://lichess.org/@/{username}"},
            {"name": "Duolingo", "url_template": "https://www.duolingo.com/profile/{username}"},
            {"name": "About.me", "url_template": "https://about.me/{username}"},
            {"name": "Gravatar", "url_template": "https://gravatar.com/{username}"},
            {"name": "Disqus", "url_template": "https://disqus.com/by/{username}"},
            {"name": "Product Hunt", "url_template": "https://www.producthunt.com/@{username}"},
            {"name": "Hacker News", "url_template": "https://news.ycombinator.com/user?id={username}"},
        ]
    def check_username(self, username, service):
        url = service['url_template'].format(username=username)
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=5,
                allow_redirects=True
            )
            if response.status_code == 200:
                content_lower = response.text.lower()
                not_found_indicators = [
                    'page not found', 'user not found', 'profile not found',
                    '404', 'does not exist', 'doesn\'t exist',
                    'no such user', 'account not found', 'not available'
                ]
                found = not any(indicator in content_lower for indicator in not_found_indicators)
                return {"found": found, "url": url, "status": response.status_code}
            else:
                return {"found": False, "url": url, "status": response.status_code}
        except RequestException as e:
            return {"found": False, "url": url, "error": str(e)}
    def check_all(self, username, callback=None, stop_flag=None):
        results = []
        for i, service in enumerate(self.services):
            if stop_flag and stop_flag():
                break
            result = self.check_username(username, service)
            result['name'] = service['name']
            results.append(result)
            if callback:
                callback(i, len(self.services), result)
            time.sleep(0.2)
        return results