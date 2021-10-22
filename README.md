# CookieCache
Simplify getting and using cookies from the browser to use in Python.

**NOTE**: All the logic to interface with the browsers is done by the
[Browser Cookie 3](https://github.com/borisbabic/browser_cookie3) library.

This code wraps that BrowserCookie3 in a CLI and library that caches
the selected cookies as JSON to disk, so they can be transferred to
other machines, or be used again without having to interactivly
re-enter MacOS user credentials.

# Install
```bash
pip install cookiecache
```

# Usage
The idea is you run cookiecache once (either as a cli tool or as a library), and
then cache the cookies to JSON on disk. Then the next time you run the same thing, cookiecache
will look in the JSON file first, and only get fresh cookies from the browser if they have expired.

## CLI
Examples:
```bash
# Get github session cookies and save to disk
cookiecache --domain "github.com" --cookie "_gh_sess" --filename "cookies.json"

# Get all github cookies in Netscape/Mozilla format to use with curl, et.c:
cookiecache --domain "github.com" --filename "cookies.txt" --curl

# All options:
cookiecache --help
```

## Library
To use cookiecache as a library call `load()` with arguments similar to
the cli:
```python
import cookiecache

# Get github session cookies and save to disk
# After the first run this will load the cookies
# from disk first, and only get them from the brower
# if they have expired
cookies = cookiecache.load(
    domain="github.com",
    cookie="_gh_sess",
    filename="cookies.json",
)

# Load all cookies from JSON file from another machine, ie.
# Don't attempt to refresh or get cookies from this machine
cookies = cookiecache.load(
    filename="cookies.json",
    check_expiry=False
)

# Get cookies only from Chrome, and don't read or save to disk
cookies = cookiecache.load(
    domain="github.com",
    browser="chrome",
)

# Convert cookies from cookiecache to a flat key-value
# pair to use with Requests
cookies = cookiecache.load(domain="github.com")
cookies_flat = cookiecache.flatten_cookies(cookies)
reqeusts.get("http://github.com", cookies=cookies_flat)
```
