import requests

LOGIN_URL = "https://automation.vnrvjiet.ac.in/EduPrime3/VNRVJIET/Login/CheckLogin"


def get_session(username, password):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://automation.vnrvjiet.ac.in/EduPrime3/VNRVJIET",
    }

    payload = {"username": username, "xpassword": password, "Domain": "VNRVJIET"}

    res = session.post(LOGIN_URL, data=payload, headers=headers, allow_redirects=True)

    # Check if login succeeded
    if "Logout" not in res.text and "Dashboard" not in res.text:
        print("Login failed response preview:")
        print(res.text[:300])
        raise Exception("Login failed")

    print("Login successful.")
    return session
