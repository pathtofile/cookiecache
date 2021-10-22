import os
import sys
import json
import datetime
import argparse
import http.cookiejar
from typing import Optional, Tuple
import browser_cookie3


def get_fresh_cookies(
    domain_name: Optional[str] = None,
    cookie_name: Optional[dict] = None,
    browser: Optional[str] = None,
) -> Tuple[dict, http.cookiejar.CookieJar]:
    """
    Use browser_cookie3 to get a fresh set of cookies
    """
    output_cookies = dict()
    if domain_name is None:
        domain_name = ""
    if browser is None:
        cj = browser_cookie3.load(domain_name=domain_name)
    elif browser == "chrome":
        cj = browser_cookie3.chrome(domain_name=domain_name)
    elif browser == "chromium":
        cj = browser_cookie3.chromium(domain_name=domain_name)
    elif browser == "opera":
        cj = browser_cookie3.opera(domain_name=domain_name)
    elif browser == "brave":
        cj = browser_cookie3.brave(domain_name=domain_name)
    elif browser == "edge":
        cj = browser_cookie3.edge(domain_name=domain_name)
    elif browser == "firefox":
        cj = browser_cookie3.firefox(domain_name=domain_name)
    else:
        # Default to all
        cj = browser_cookie3.load(domain_name=domain_name)
    cj_cookies = cj._cookies
    for cj_domain in cj_cookies:
        for cj_path in cj_cookies[cj_domain]:
            for cj_name in cj_cookies[cj_domain][cj_path]:
                if cookie_name is not None and cj_name != cookie_name:
                    continue

                # Get cookie and prep for output
                cj_cookie = cj_cookies[cj_domain][cj_path][cj_name]
                if cj_cookie.expires is None:
                    cj_cookie.expires = 0
                if cj_domain not in output_cookies:
                    output_cookies[cj_domain] = list()

                output_cookies[cj_domain].append(
                    {
                        "name": cj_name,
                        "path": cj_path,
                        "value": cj_cookie.value,
                        "expires": cj_cookie.expires,
                    }
                )
    return output_cookies, cj


def save_cookies_mozilla(cj: http.cookiejar.CookieJar, filename: str):
    cj_moz = http.cookiejar.MozillaCookieJar()
    cookies = cj._cookies
    for domain in cookies:
        for path in cookies[domain]:
            for name in cookies[domain][path]:
                # Get cookie and prep for output
                cookie = cookies[domain][path][name]
                cj_moz.set_cookie(cookie)
    cj_moz.save(filename)


def save_cookies_json(cookies: dict, filename: str, pretty: bool = True):
    """
    Save cookies to file
    """
    indent = 2
    if not pretty:
        indent = None
    with open(filename, "w") as f:
        f.write(json.dumps(cookies, indent=indent))


def check_if_exired(cookies: dict) -> bool:
    """
    Check if any of the cookies have expired
    ignores cookies with no expiry
    """
    now = datetime.datetime.now()
    for domain in cookies:
        for cookie in cookies[domain]:
            expires = datetime.datetime.fromtimestamp(cookie["expires"])
            if cookie["expires"] != 0 and expires < now:
                return True
    return False


def flatten_cookies(cookies: dict) -> dict:
    """
    Flatten cookies into dict like { "cookie_name": "cookie_value" }
    Used to pass into requests
    """
    cookies_flat = dict()
    for domain in cookies:
        for cookie in cookies[domain]:
            cookies_flat[cookie["name"]] = cookie["value"]
    return cookies_flat


def load_cookies(
    filename: Optional[str] = None,
    domain_name: Optional[str] = None,
    cookie_name: Optional[dict] = None,
    browser: Optional[str] = None,
    check_expiry: bool = True,
    force_refresh: bool = False,
    curl_format: bool = False,
) -> dict:
    """
    Load cookies. If filename is not None, load and save
    cookies to disk.
    """
    need_to_save = False

    if filename is None:
        cookies, cj = get_fresh_cookies(
            domain_name, cookie_name=cookie_name, browser=browser
        )
    # curl_format always gets fresh to make it easier for me
    elif force_refresh or curl_format or not os.path.exists(filename):
        # Need to get cookies
        need_to_save = True
        cookies, cj = get_fresh_cookies(
            domain_name, cookie_name=cookie_name, browser=browser
        )
    else:
        with open(filename, "r") as f:
            cookies = json.loads(f.read())
        if check_expiry and check_if_exired(cookies):
            need_to_save = True
            cookies, cj = get_fresh_cookies(
                domain_name, cookie_name=cookie_name, browser=browser
            )

    if need_to_save:
        if curl_format:
            save_cookies_mozilla(cj, filename)
        else:
            save_cookies_json(cookies, filename)
    return cookies


def main():
    browsers = ["chrome", "chromium", "opera", "brave", "edge", "firefox"]
    parser = argparse.ArgumentParser(
        "CookieCache - Simplify getting and storing cookies from the browser to use in Python"
    )
    parser.add_argument(
        "--filename", "-f", help="Optional, filename to save cookies to"
    )
    parser.add_argument(
        "--domain", "-d", help="Optional, only get cookies from domains containing this"
    )
    parser.add_argument(
        "--cookie", "-c", help="Optional, only get cookies that match this"
    )
    parser.add_argument(
        "--browser",
        "-b",
        choices=browsers,
        help="Optional, only get cookies from this browser",
    )
    parser.add_argument(
        "--check-expiry",
        action="store_true",
        dest="check",
        help="If set, check cookie expiry and refresh if needed",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        dest="force",
        help="If set, always get fresh cookies from browser",
    )
    parser.add_argument(
        "--curl",
        action="store_true",
        help="Save cookies in Netscae/Mozilla format for cURL, etc. Must also use --filename",
    )

    args = parser.parse_args()
    if args.curl and args.filename is None:
        print("--curl must be used with --filename")
        sys.exit(1)
    cookies = load_cookies(
        filename=args.filename,
        domain_name=args.domain,
        cookie_name=args.cookie,
        browser=args.browser,
        check_expiry=args.check,
        force_refresh=args.force,
        curl_format=args.curl,
    )

    if args.filename is not None:
        print(f"Written cookies to {args.filename}")
    else:
        print(json.dumps(cookies, indent=2))


if __name__ == "__main__":
    main()
