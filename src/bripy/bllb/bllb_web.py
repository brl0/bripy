"""bllb web helpers."""


def new_webdriver(chromiumbrowser_path):
    """Create new Selenium webdriver."""
    from selenium import webdriver

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chromiumbrowser_path

    # original options
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--test-type")

    # recommended options
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    chrome_options.add_argument("--disable-gpu")

    # suggested "optimal settings"
    # https://bugs.chromium.org/p/chromium/issues/detail?id=737678
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-breakpad")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-features=site-per-process")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--enable-automation")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--metrics-recording-only")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--password-store=basic")
    chrome_options.add_argument("--safebrowsing-disable-auto-update")
    chrome_options.add_argument("--use-mock-keychain")

    # currently unused options
    # chrome_options.add_argument("--user-data-dir=.\temp")
    # chrome_options.add_argument("--remote-debugging-address=0.0.0.0")
    # chrome_options.add_argument("--remote-debugging-port=9222")

    return webdriver.Chrome(
        executable_path=chromiumbrowser_path,
        chrome_options=chrome_options)
