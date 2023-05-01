import requests
from bs4 import BeautifulSoup

def get_session(username, password):
    s = requests.Session()
    mainpage = s.get('https://arena.petlja.org')
    soup = BeautifulSoup(mainpage.text, 'html.parser')
    verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    s.post(
        'https://arena.petlja.org/sr-Latn-RS/Account/Login?returnurl=/',
        data= {
            'LoginViewModel.UserNameOrEmail': username,
            'LoginViewModel.Password': password,
            '__RequestVerificationToken': verification_token,
            'LoginViewModel.RememberMe': 'false'
        }
    )
    s.headers.update({'Authorization': f'Bearer {s.cookies["PetljaCookie"]}'})
    return s