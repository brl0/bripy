"""Tests for URL, DNS, and Server classes in ubrl module."""
# pylint: disable=unused-wildcard-import

import pytest

try:
    from .context import DNS, Server, URL
except ImportError:
    from context import DNS, Server, URL


def test_import():
    """Test that classes were imported."""
    assert "URL" in globals()
    assert "DNS" in globals()
    assert "Server" in globals()


def test_URL_cls():
    """Test that repr matches input and parsing is right."""
    test_url = "scheme://username:password@www.fake.url:80/path/file.ext"
    url = URL(test_url)
    assert str(url) == test_url
    assert url.domain == "www.fake.url"
    assert url.ext == "ext"
    assert url.parse.username == "username"
    assert url.is_valid_domain
    assert len(url.bhash) == 32
    assert url.prep == "//username:password@www.fake.url:80/path/file.ext"


def test_URL_2():
    """Test tld and that qs are parsed correctly."""
    test_url = "https://www.google.com/search?q=python+urllib"
    url = URL(test_url)
    assert url.tld == "google.com"
    assert url.is_valid_tld
    assert "python urllib" in url.get_qs["q"]


def test_DNS_cls():
    """Test repr and any nameserver is responsive."""
    dns = DNS()
    assert str(dns) == str(DNS.DEFAULT_DNS)
    assert dns.nameservers
    assert dns.validate_domain("google.com")


test_ips = ["127.0.0.1"] + DNS.DEFAULT_DNS


@pytest.mark.parametrize("ip", test_ips)
def test_ip(ip):
    """Test known ip address."""
    server = Server(ip)
    assert str(server) == ip
    assert server.ping()


def test_bad_ip():
    """Test known bad ip address."""
    ip = "1.1.0.1"
    server = Server(ip)
    assert str(server) == ip
    assert not server.ping()


test_domains = {"IPv4": "ipv4.google.com", "IPv6": "ipv6.google.com"}


@pytest.mark.parametrize(
    "domain", test_domains.values(), ids=list(test_domains.keys())
)
def test_domain(domain):
    """Test known domain."""
    dns = DNS()
    ip = dns.query(domain)[0]
    server = Server(ip)
    assert str(server) == ip
    assert dns.validate_domain(domain)
    assert server.ping


def test_ipv6():
    """Test IPv6."""
    domain = "ipv6.google.com"
    dns = DNS()
    ip = dns.query(domain)[0]
    server = Server(ip)
    assert server.check_service_v6(80, 5)


@pytest.mark.parametrize("ip", DNS.PROVIDERS["GOOGLE_DNSv6"])
def test_ipv6_dns(ip):
    """Test known ip address."""
    server = Server(ip)
    assert str(server) == ip
    assert server.check_service_v6(53, 5)


test_servers = DNS.DEFAULT_DNS + [
    "127.0.0.1",
    "ipv4.google.com",
    "ipv6.google.com",
]


@pytest.mark.parametrize("target", test_servers)
def test_server_ip(target):
    """Test ping for know servers."""
    server = Server(target)
    assert server.ping()


@pytest.mark.parametrize(
    "ips", DNS.PROVIDERS.values(), ids=list(DNS.PROVIDERS.keys())
)
def test_dns_server_lists(ips):
    """Test known DNS servers."""
    for ip in ips:
        server = Server(ip)
        assert server.ping()
        assert server.check_service(53, 5)
