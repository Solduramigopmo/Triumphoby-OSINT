import re
import asyncio
import aiohttp
from typing import Dict, Optional, List
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
NUMVERIFY_API_KEY = None
TELEGRAM_API_ID = None
TELEGRAM_API_HASH = None
TELEGRAM_PHONE = None
SMSC_LOGIN = None
SMSC_PASSWORD = None
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TRUECALLER_API_KEY = None
VIBER_TOKEN = None
WHATSAPP_TOKEN = None
SERPAPI_KEY = None
def get_country_flag(country_code: str) -> str:
    if not country_code or len(country_code) != 2:
        return "🌍"
    code_points = [ord(c) + 127397 for c in country_code.upper()]
    return chr(code_points[0]) + chr(code_points[1])
class PhoneChecker:
    def __init__(self, settings=None):
        self.session: Optional[aiohttp.ClientSession] = None
        self.settings = settings or {}
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    def parse_number(self, phone: str, region: str = None) -> Optional[phonenumbers.PhoneNumber]:
        try:
            phone = re.sub(r'[^\d+]', '', phone)
            if region:
                return phonenumbers.parse(phone, region)
            if phone.startswith('+'):
                return phonenumbers.parse(phone, None)
            for reg in ['US', 'RU', 'GB', 'DE', 'UA']:
                try:
                    parsed = phonenumbers.parse(phone, reg)
                    if phonenumbers.is_valid_number(parsed):
                        return parsed
                except:
                    continue
            return None
        except:
            return None
    def get_basic_info(self, phone_number: phonenumbers.PhoneNumber) -> Dict:
        try:
            region_code = phonenumbers.region_code_for_number(phone_number)
            is_possible = phonenumbers.is_possible_number(phone_number)
            is_valid = phonenumbers.is_valid_number(phone_number)
            validity_status = is_valid or is_possible
            return {
                'valid': validity_status,
                'possible': is_possible,
                'strictly_valid': is_valid,
                'international': phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'national': phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                'e164': phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164),
                'country_code': phone_number.country_code,
                'national_number': phone_number.national_number,
                'region_code': region_code,
                'country_flag': get_country_flag(region_code),
                'location': geocoder.description_for_number(phone_number, 'en'),
                'carrier': carrier.name_for_number(phone_number, 'en') or 'Unknown',
                'timezones': timezone.time_zones_for_number(phone_number),
                'number_type': self._get_number_type(phone_number)
            }
        except Exception as e:
            return {'error': str(e)}
    def _get_number_type(self, phone_number: phonenumbers.PhoneNumber) -> str:
        num_type = phonenumbers.number_type(phone_number)
        types = {
            0: 'Fixed Line',
            1: 'Mobile',
            2: 'Fixed Line or Mobile',
            3: 'Toll Free',
            4: 'Premium Rate',
            5: 'Shared Cost',
            6: 'VoIP',
            7: 'Personal Number',
            8: 'Pager',
            9: 'UAN',
            10: 'Voicemail',
            99: 'Unknown'
        }
        return types.get(num_type, 'Unknown')
    async def hlr_lookup(self, phone: str) -> Dict:
        try:
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            print(f"[HLR] Checking phone: {clean_phone}")
            smsc_login = self.settings.get('smsc_login') or SMSC_LOGIN
            smsc_password = self.settings.get('smsc_password') or SMSC_PASSWORD
            if smsc_login and smsc_password:
                try:
                    url = 'https://smsc.ru/sys/info.php'
                    params = {
                        'login': smsc_login,
                        'psw': smsc_password,
                        'phone': clean_phone,
                        'fmt': '3'
                    }
                    print(f"[HLR] Trying SMSC.ru with API key")
                    async with self.session.get(url, params=params, ssl=False, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            print(f"[HLR] SMSC API response: {text[:200]}")
                            result = {}
                            lines = text.strip().split('\n')
                            for line in lines:
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip().lower().replace(' ', '_')
                                    value = value.strip()
                                    result[key] = value
                            if result:
                                return {
                                    'country': result.get('страна', result.get('country', 'Unknown')),
                                    'operator': result.get('оператор', result.get('operator', 'Unknown')),
                                    'region': result.get('регион', result.get('region', 'Unknown')),
                                    'timezone': result.get('часовой_пояс', result.get('timezone', 'Unknown')),
                                    'status': result.get('статус', result.get('status', 'Unknown')),
                                    'mcc': result.get('mcc', ''),
                                    'mnc': result.get('mnc', ''),
                                }
                except Exception as e:
                    print(f"[HLR] SMSC.ru API failed: {e}")
            numverify_key = self.settings.get('numverify_api_key') or NUMVERIFY_API_KEY
            if numverify_key:
                try:
                    url = f'http://apilayer.net/api/validate'
                    params = {
                        'access_key': numverify_key,
                        'number': clean_phone,
                        'format': '1'
                    }
                    print(f"[HLR] Trying Numverify API")
                    async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get('valid'):
                                return {
                                    'country': data.get('country_name', 'Unknown'),
                                    'operator': data.get('carrier', 'Unknown'),
                                    'location': data.get('location', 'Unknown'),
                                    'line_type': data.get('line_type', 'Unknown'),
                                    'status': 'Available' if data.get('valid') else 'Invalid'
                                }
                except Exception as e:
                    print(f"[HLR] Numverify failed: {e}")
            return {
                'error': 'No API keys configured',
                'note': 'Add SMSC.ru or Numverify API keys in Settings'
            }
        except Exception as e:
            print(f"[HLR] Error: {e}")
            return {'error': f'HLR lookup error: {str(e)}'}
    async def search_truecaller(self, phone: str) -> Dict:
        try:
            return {
                'service': 'Truecaller',
                'status': 'unavailable',
                'note': 'Requires Truecaller API access or web scraping'
            }
        except Exception as e:
            return {'error': str(e)}
    async def search_getcontact(self, phone: str) -> Dict:
        try:
            return {
                'service': 'GetContact',
                'status': 'unavailable',
                'note': 'Requires GetContact API access'
            }
        except Exception as e:
            return {'error': str(e)}
    async def search_eyecon(self, phone: str) -> Dict:
        try:
            return {
                'service': 'Eyecon',
                'status': 'unavailable',
                'note': 'Requires Eyecon API access'
            }
        except Exception as e:
            return {'error': str(e)}
    async def search_social_media(self, phone: str) -> Dict:
        results = {}
        results['facebook'] = {
            'url': f'https://www.facebook.com/search/top/?q={phone}',
            'note': 'Manual check required (login needed)'
        }
        results['instagram'] = {
            'url': f'https://www.instagram.com/explore/tags/{phone.replace("+", "")}/',
            'note': 'Manual check required'
        }
        results['vk'] = {
            'url': f'https://vk.com/search?c[section]=people&c[q]={phone}',
            'note': 'Manual check required'
        }
        results['linkedin'] = {
            'url': f'https://www.linkedin.com/search/results/all/?keywords={phone}',
            'note': 'Manual check required (login needed)'
        }
        return results
    async def search_google(self, phone: str) -> Dict:
        try:
            queries = {
                'general': f'https://www.google.com/search?q="{phone}"',
                'social': f'https://www.google.com/search?q="{phone}"+site:facebook.com+OR+site:instagram.com+OR+site:vk.com',
                'business': f'https://www.google.com/search?q="{phone}"+contact+OR+phone',
            }
            return {
                'service': 'Google Search',
                'queries': queries,
                'note': 'Open these URLs in browser for manual search'
            }
        except Exception as e:
            return {'error': str(e)}
    async def check_online_status(self, phone: str) -> Dict:
        results = {}
        results['telegram'] = await self._check_telegram(phone)
        results['whatsapp'] = await self._check_whatsapp(phone)
        results['viber'] = await self._check_viber(phone)
        return results
    async def _check_telegram(self, phone: str) -> Dict:
        try:
            return {
                'registered': 'unknown',
                'note': 'Requires Telegram API credentials (api_id, api_hash)'
            }
        except Exception as e:
            return {'error': str(e)}
    async def _check_whatsapp(self, phone: str) -> Dict:
        try:
            return {
                'registered': 'unknown',
                'note': 'Requires WhatsApp Web session or API access'
            }
        except Exception as e:
            return {'error': str(e)}
    async def _check_viber(self, phone: str) -> Dict:
        try:
            return {
                'registered': 'unknown',
                'note': 'Requires Viber API credentials'
            }
        except Exception as e:
            return {'error': str(e)}
    async def osint_search(self, phone: str) -> Dict:
        results = {
            'google_results': [],
            'social_media': {},
            'data_breaches': []
        }
        try:
            search_queries = [
                f'"{phone}"',
                f'"{phone}" site:facebook.com',
                f'"{phone}" site:linkedin.com',
                f'"{phone}" site:twitter.com'
            ]
            results['note'] = 'OSINT search requires API keys (SerpAPI, Hunter.io, etc.)'
        except Exception as e:
            results['error'] = str(e)
        return results
    async def full_check(self, phone: str, region: str = None) -> Dict:
        parsed = self.parse_number(phone, region)
        if not parsed:
            return {'error': 'Invalid phone number format'}
        basic_info = self.get_basic_info(parsed)
        e164_format = basic_info.get('e164', phone)
        tasks = {
            'hlr': self.hlr_lookup(e164_format),
            'online_status': self.check_online_status(e164_format),
            'truecaller': self.search_truecaller(e164_format),
            'getcontact': self.search_getcontact(e164_format),
            'eyecon': self.search_eyecon(e164_format),
            'social_media': self.search_social_media(e164_format),
            'google': self.search_google(e164_format),
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        response = {
            'basic': basic_info,
            'sources': {}
        }
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                response['sources'][key] = {'error': str(result)}
            else:
                response['sources'][key] = result
        return response