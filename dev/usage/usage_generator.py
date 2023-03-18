import sys

import requests

if __name__ == "__main__":
    response = requests.post(
        url="https://carbonara-42.herokuapp.com/api/cook",
        json={
            "code": sys.stdin.read(),
            "language": "plaintext",
            "backgroundColor": "transparent",
        },
        timeout=5,
    )

    with open("assets/images/usage.png", "wb") as file:
        file.write(response.content)
