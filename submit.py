import requests
from bs4 import BeautifulSoup
import time
from getpass import getpass

PETLJA_URL = 'https://arena.petlja.org'

def get_credentials():
    username = input('Petlja username: ')
    password = getpass('Petlja password: ')
    return username, password

def get_session(username=None, password=None):
    if username is None or password is None:
        username, password = get_credentials()

    s = requests.Session()
    mainpage = s.get(PETLJA_URL)
    soup = BeautifulSoup(mainpage.text, 'html.parser')
    verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    login = s.post(
        f'{PETLJA_URL}/sr-Latn-RS/Account/Login',
        data= {
            'LoginViewModel.UserNameOrEmail': username,
            'LoginViewModel.Password': password,
            '__RequestVerificationToken': verification_token,
            'LoginViewModel.RememberMe': 'false'
        },
        allow_redirects=False,
    )

    if login.status_code == 302:
        jwt = s.cookies['PetljaCookie']
        s.headers.update({'Authorization': f'Bearer {jwt}'})
        return s
    elif login.status_code == 200:
        raise PermissionError('Wrong username or password')
    else:
        raise Exception

def submit(competition_id, problem_id, source, language_id):
    session = None
    while session is None:
        try:
            session = get_session()
        except PermissionError as e:
            print(e)
    
    submit = session.post(
        f'{PETLJA_URL}/api/competition/submit-competition-problem',
        json= {
            "competitionId": competition_id,
            "problemId": problem_id,
            "source": source,
            "languageId": language_id
        }
    )
    submission_id = submit.json()['value']
    time.sleep(2) # FIXME wait until evaluation is finished
    submission_data = session.post(
        f'{PETLJA_URL}/api/competition/submissions',
        json= {
            "competitionId": competition_id,
            "idStamp": submission_id,
            "loadNew": 'true'
        }
    )
    score = submission_data.json()['value']['item1'][0]['score']
    return score