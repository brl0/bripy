"""Tests for URL, DNS, and Server classes in ubrl module."""
# pylint: disable=unused-wildcard-import

import pytest
from multiping import MultiPingError

from bripy.ubrl.ubrl import DNS, URL, Server, get_ip_version

xfail_ip6 = pytest.mark.xfail(reason="IPv6 not supported on WSL")


TEST_IPS = ("127.0.0.1",) + DNS.DEFAULT_DNS
TEST_DOMAINS = {"IPv4": "ipv4.google.com", "IPv6": "ipv6.google.com"}
TEST_SERVERS = DNS.DEFAULT_DNS + (
    "127.0.0.1",
    "ipv4.google.com",
    "ipv6.google.com",
)


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
    """Test any nameserver is responsive."""
    dns = DNS()
    assert dns.nameservers
    assert dns.validate_domain("google.com")


def try_ping(server, default=True):
    try:
        return server.ping()
    except MultiPingError:
        return default


@pytest.mark.parametrize("ip", TEST_IPS)
def test_ip(ip):
    """Test known ip address."""
    server = Server(ip)
    assert str(server) == ip
    assert try_ping(server)


def test_bad_ip():
    """Test known bad ip address."""
    ip = "1.1.0.1"
    server = Server(ip)
    assert str(server) == ip
    assert not try_ping(server, False)


@pytest.mark.parametrize("domain", TEST_DOMAINS.values(), ids=list(TEST_DOMAINS.keys()))
def test_domain(domain):
    """Test known domain."""
    dns = DNS()
    ip = dns.query(domain)[0]
    server = Server(ip)
    assert str(server) == ip
    assert dns.validate_domain(domain)
    assert try_ping(server)


@xfail_ip6
def test_ipv6():
    """Test IPv6."""
    domain = "ipv6.google.com"
    dns = DNS()
    ip = dns.query(domain)[0]
    server = Server(ip)
    assert server.check_service_v6(80, 5)


@xfail_ip6
@pytest.mark.parametrize("ip", DNS.PROVIDERS["GOOGLE_DNSv6"])
def test_ipv6_dns(ip):
    """Test known ipv6 address."""
    server = Server(ip)
    assert str(server) == ip
    assert server.check_service_v6(53, 5)


@pytest.mark.parametrize("target", TEST_SERVERS)
def test_server_ip(target):
    """Test ping for known servers."""
    server = Server(target)
    assert try_ping(server)


@pytest.mark.parametrize("ips", DNS.PROVIDERS.values(), ids=list(DNS.PROVIDERS.keys()))
def test_dns_server_lists_v4(ips):
    """Test known DNS servers."""
    for ip in ips:
        server = Server(ip)
        if get_ip_version(ip) == 4:
            assert try_ping(server)
            assert server.check_service(53, 5)


@xfail_ip6
@pytest.mark.parametrize("ips", DNS.PROVIDERS.values(), ids=list(DNS.PROVIDERS.keys()))
def test_dns_server_lists_v6(ips):
    """Test known DNS servers."""
    for ip in ips:
        server = Server(ip)
        if get_ip_version(ip) == 6:
            assert try_ping(server)
            assert server.check_service_v6(53, 5)
