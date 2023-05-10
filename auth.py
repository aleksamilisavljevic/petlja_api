from getpass import getpass

import requests
from bs4 import BeautifulSoup

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

    session = requests.Session()
    mainpage = session.get(ARENA_URL)
    csrf_token = get_csrf_token(mainpage.text)
    login = session.post(
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
        jwt = session.cookies["PetljaCookie"]
        session.headers.update({"Authorization": f"Bearer {jwt}"})
        return session
    elif login.status_code == 200:
        raise PermissionError("Wrong username or password")
    else:
        raise RuntimeError(
            f"Unknown error: login failed with status code {login.status_code}"
        )
