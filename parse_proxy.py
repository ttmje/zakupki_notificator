import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_html(url):
    r = requests.get(url)
    return r.text


def get_ip(html):
    soup = BeautifulSoup(html, 'html.parser')
    ip = soup.find('span', class_='ip').text.strip()
    ua = UserAgent(use_cache_server=False)
    ua.random
    print(ip)
    print(ua)


def main():
    url = 'http://sitespy.ru/my-ip'
    useragents = open('useragents.txt').read().split('\n')
    print(useragents[-1])

    html = get_html(url)
    get_ip(html)


if __name__ == '__main__':
    main()
