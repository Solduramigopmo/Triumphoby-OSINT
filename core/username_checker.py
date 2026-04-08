import json
import time
from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


class UsernameChecker:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.request_timeout = 5
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

    @staticmethod
    def _safe_text(value: Any, max_len: int = 280) -> str:
        if value is None:
            return ""
        text = str(value).replace("\n", " ").replace("\r", " ").strip()
        text = " ".join(text.split())
        return text[:max_len]

    @staticmethod
    def _extract_meta(soup: BeautifulSoup, names: list[str], max_len: int = 280) -> str:
        for name in names:
            tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
            if tag and tag.get("content"):
                return UsernameChecker._safe_text(tag.get("content"), max_len)
        return ""

    def _find_first_person_object(self, data: Any) -> Optional[Dict[str, Any]]:
        if isinstance(data, dict):
            data_type = data.get("@type")
            if data_type == "Person" or (isinstance(data_type, list) and "Person" in data_type):
                return data
            for value in data.values():
                person_obj = self._find_first_person_object(value)
                if person_obj:
                    return person_obj
        elif isinstance(data, list):
            for item in data:
                person_obj = self._find_first_person_object(item)
                if person_obj:
                    return person_obj
        return None

    def _extract_json_ld_person(self, soup: BeautifulSoup) -> Dict[str, Any]:
        person_data: Dict[str, Any] = {}
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        for script in scripts:
            payload = script.string or script.get_text() or ""
            payload = payload.strip()
            if not payload:
                continue
            try:
                json_data = json.loads(payload)
            except Exception:
                continue
            person_obj = self._find_first_person_object(json_data)
            if not person_obj:
                continue
            name = self._safe_text(person_obj.get("name"), 140)
            description = self._safe_text(person_obj.get("description"), 280)
            location = ""
            location_obj = person_obj.get("homeLocation") or person_obj.get("location")
            if isinstance(location_obj, dict):
                location = self._safe_text(location_obj.get("name"), 120)
            elif isinstance(location_obj, str):
                location = self._safe_text(location_obj, 120)
            same_as = person_obj.get("sameAs")
            if isinstance(same_as, list):
                person_data["same_as_count"] = len(same_as)
            if name:
                person_data["name"] = name
            if description:
                person_data["description"] = description
            if location:
                person_data["location"] = location
            if person_data:
                return person_data
        return person_data

    def _extract_profile_metadata(self, html: str, profile_url: str, service_name: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        title = self._safe_text(soup.title.string if soup.title and soup.title.string else "", 140)
        canonical = ""
        canonical_tag = soup.find("link", rel=lambda x: isinstance(x, str) and "canonical" in x.lower())
        if canonical_tag and canonical_tag.get("href"):
            canonical = self._safe_text(canonical_tag.get("href"), 220)

        display_name = self._extract_meta(
            soup,
            ["profile:username", "og:title", "twitter:title"],
            140,
        )
        bio = self._extract_meta(
            soup,
            ["description", "og:description", "twitter:description"],
            320,
        )
        image = self._extract_meta(soup, ["og:image", "twitter:image"], 220)
        location_hint = self._extract_meta(
            soup,
            ["profile:location", "place:location:locality", "geo.position"],
            120,
        )
        json_ld_person = self._extract_json_ld_person(soup)
        if not display_name and json_ld_person.get("name"):
            display_name = self._safe_text(json_ld_person["name"], 140)
        if not bio and json_ld_person.get("description"):
            bio = self._safe_text(json_ld_person["description"], 320)
        if not location_hint and json_ld_person.get("location"):
            location_hint = self._safe_text(json_ld_person["location"], 120)

        profile_data: Dict[str, Any] = {
            "service": service_name,
            "profile_url": profile_url,
            "display_name": display_name,
            "bio": bio,
            "title": title,
            "location_hint": location_hint,
            "image": image,
            "canonical": canonical,
        }
        if "same_as_count" in json_ld_person:
            profile_data["same_as_count"] = json_ld_person["same_as_count"]
        return {k: v for k, v in profile_data.items() if v not in ("", None)}

    def _is_not_found_page(self, html: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        title_text = self._safe_text(soup.title.string if soup.title and soup.title.string else "", 220).lower()
        body_text = self._safe_text(soup.get_text(" ", strip=True), 6000).lower()

        title_indicators = [
            "404 not found",
            "page not found",
            "profile not found",
            "user not found",
            "this page isn't available",
            "account suspended",
        ]
        body_indicators = [
            "this account doesn't exist",
            "the page you requested does not exist",
            "the page you were looking for doesn't exist",
            "profile not found",
            "user not found",
            "sorry, this page isn't available",
            "no such user",
            "account not found",
        ]

        if any(indicator in title_text for indicator in title_indicators):
            return True
        if any(indicator in body_text for indicator in body_indicators):
            return True
        return False

    def check_username(self, username, service, collect_profile=False):
        url = service["url_template"].format(username=username)
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.request_timeout,
                allow_redirects=True,
            )
            result = {"found": False, "url": url, "status": response.status_code}
            if response.status_code == 200:
                found = not self._is_not_found_page(response.text)
                result["found"] = found
                if found and collect_profile:
                    profile = self._extract_profile_metadata(response.text, url, service["name"])
                    if profile:
                        result["profile"] = profile
            return result
        except RequestException as e:
            return {"found": False, "url": url, "error": str(e)}

    def check_all(self, username, callback=None, stop_flag=None, collect_profile=False):
        results = []
        for i, service in enumerate(self.services):
            if stop_flag and stop_flag():
                break
            result = self.check_username(username, service, collect_profile=collect_profile)
            result["name"] = service["name"]
            results.append(result)
            if callback:
                callback(i, len(self.services), result)
            time.sleep(0.2)
        return results
