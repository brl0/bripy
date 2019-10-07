"""Tests for ubrl command line interface."""

import pytest
from scripttest import TestFileEnvironment as FileEnvironment

try:
    from .context import DNS
except ImportError:
    from context import DNS

env = FileEnvironment(ignore_hidden=False)


def test_cmd_ping_localhost():
    """Test ping command from cli."""
    res = env.run("ubrl", "ping", "127.0.0.1", expect_stderr=True)
    assert res.returncode == 0
    assert "127.0.0.1" in res.stdout
    assert "True" in res.stdout


test_domains = {"IPv4": "ipv4.google.com", "IPv6": "ipv6.google.com"}


@pytest.mark.parametrize("domain",
                         test_domains.values(),
                         ids=list(test_domains.keys()))
def test_cmd_ping(domain):
    """Test ping command from cli on multiple domains."""
    res = env.run("ubrl", "ping", domain, expect_stderr=True)
    assert res.returncode == 0
    assert domain in res.stdout
    assert "True" in res.stdout


@pytest.mark.parametrize("domain",
                         test_domains.values(),
                         ids=list(test_domains.keys()))
def test_cmd_pingport(domain):
    """Test pingport command from cli."""
    res = env.run("ubrl", "pingport", domain, "80", expect_stderr=True)
    assert res.returncode == 0
    assert domain in res.stdout
    assert "True" in res.stdout


def test_cmd_pingport_2():
    """Additional tests for pingport command."""
    res = env.run("ubrl", "pingport", "8.8.8.8", "53", expect_stderr=True)
    assert res.returncode == 0
    assert "8.8.8.8" in res.stdout
    assert "True" in res.stdout


def test_cmd_pingport_IPv6():
    """Test pingport command over IPv6."""
    res = env.run("ubrl",
                  "pingport",
                  "ipv6.google.com",
                  "80",
                  expect_stderr=True)
    assert res.returncode == 0
    assert "ipv6.google.com" in res.stdout
    assert "True" in res.stdout


def test_cmd_ping_IPv6():
    """Test ping command over IPv6."""
    res = env.run("ubrl", "ping", "ipv6.google.com", expect_stderr=True)
    assert res.returncode == 0
    assert "ipv6.google.com" in res.stdout
    assert "True" in res.stdout


def test_cmd_query():
    """Test query with known domains."""
    res = env.run("ubrl", "query", "dns.google.com", expect_stderr=True)
    assert res.returncode == 0
    for _ in DNS.PROVIDERS["GOOGLE_DNSv6"] + DNS.PROVIDERS["GOOGLE_DNS"]:
        assert _ in res.stdout
