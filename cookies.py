from selenium import webdriver

from private_const import EMAIL, PASS, LOGIN_URL
from const import XSRF_COOKIE, LARAVEL_COOKIE, redis_client, CACHE_XSRF_EXPIRE, CACHE_LARAVEL_EXPIRE


def get_authentication_cookies(force_refresh=False):
    token = redis_client.get(XSRF_COOKIE)
    laravel = redis_client.get(LARAVEL_COOKIE)

    if not force_refresh and token and laravel:
        return token, laravel

    browser = webdriver.PhantomJS()
    browser.get(LOGIN_URL)
    email = browser.find_element_by_id("email")
    password = browser.find_element_by_id("password")
    form = browser.find_element_by_id("loginForm")
    email.send_keys(EMAIL)
    password.send_keys(PASS)
    form.submit()
    cookies = browser.get_cookies()

    for cookie in cookies:
        name, value = cookie['name'], cookie['value']
        if name == XSRF_COOKIE:
            token = value
            redis_client.set(XSRF_COOKIE, value, CACHE_XSRF_EXPIRE)
        elif name == LARAVEL_COOKIE:
            laravel = value
            redis_client.set(LARAVEL_COOKIE, value, CACHE_LARAVEL_EXPIRE)

    browser.quit()
    return token, laravel


def populate_cookies_dict(cookies, force_refresh=False):
    xsrf, laravel = get_authentication_cookies(force_refresh)
    cookies[XSRF_COOKIE] = xsrf
    cookies[LARAVEL_COOKIE] = laravel
