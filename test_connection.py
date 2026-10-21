"""Check that your PC can see and control the iPhone. Doesn't use Claude.

    python test_connection.py          # status + screenshot
    python test_connection.py --home   # also presses Home, to prove it can act
"""

import argparse
import os

from phone_agent.wda import WDA, WDAError


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--home", action="store_true")
    p.add_argument("--wda-url", default=os.getenv("WDA_URL", "http://localhost:8100"))
    args = p.parse_args()

    phone = WDA(args.wda_url)
    try:
        status = phone.status()
        print("1/3 ✅ WebDriverAgent is answering:", status.get("state", "ok"))
        print("2/3 ✅ Screen size (points):", phone.window_size())
        with open("screenshot.png", "wb") as f:
            f.write(phone.screenshot_png())
        print("3/3 ✅ Saved screenshot.png — open it to check it matches your phone.")
        if args.home:
            phone.home()
            print("✅ Pressed Home. Your phone should be on the home screen now.")
    except WDAError as e:
        print("❌", e)


if __name__ == "__main__":
    main()
