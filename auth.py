import requests
from bs4 import BeautifulSoup
from getpass import getpass
from urls import ARENA_URL


def get_credentials():
    username = input("Petlja username: ")
    password = getpass("Petlja password: ")
    return username, password


def get_csrf_token(page):
    soup = BeautifulSoup(page, "html.parser")
    csrf_token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value")
    return csrf_token


def get_session(username=None, password=None):
    if username is None or password is None:
        username, password = get_credentials()

    s = requests.Session()
    mainpage = s.get(ARENA_URL)
    csrf_token = get_csrf_token(mainpage.text)
    login = s.post(
        f"{ARENA_URL}/sr-Latn-RS/Account/Login",
        data={
            "LoginViewModel.UserNameOrEmail": username,
            "LoginViewModel.Password": password,
            "__RequestVerificationToken": csrf_token,
            "LoginViewModel.RememberMe": "false",
        },
        allow_redirects=False,
    )

    if login.status_code == 302:
        jwt = s.cookies["PetljaCookie"]
        s.headers.update({"Authorization": f"Bearer {jwt}"})
        return s
    elif login.status_code == 200:
        raise PermissionError("Wrong username or password")
    else:
        raise Exception
