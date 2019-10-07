"""URL helpers library."""

from functools import partial
from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import PurePath
import re
import socket
from typing import Set, TypeVar
from urllib.parse import parse_qs, unquote_plus, urlparse, urlsplit, urlunsplit
from urllib.request import urlopen

import attr
from dns.resolver import Resolver
from multiping import MultiPing
import requests
from slugify import slugify
from tldextract import extract as tldextract
import validators
from w3lib.url import canonicalize_url
from werkzeug.urls import url_fix

from bripy.bllb.bllb_str import hash_utf8


AnyStr = TypeVar("AnyStr", str, bytes)


@attr.s(repr=False)
class URL:
    """URL holder object."""

    url = attr.ib()
    parse = None

    def __attrs_post_init__(self) -> None:
        """Initialize parsed url object."""
        self.parse = urlparse(self.url)

    def __repr__(self) -> str:
        """Return url as repr."""
        return self.url

    @property
    def ext(self) -> str:
        """Get file extension from url."""
        result = self.parse.path
        result = unquote_plus(result)
        result = PurePath(result).suffix
        # split on space
        result = re.split(r"\s", result)[0].split(".")[-1]
        return result

    @property
    def domain(self) -> str:
        """Return subdomain."""
        domain = getattr(self.parse, "netloc")
        if getattr(self.parse, "username"):
            domain = domain.split("@")[1]
        if getattr(self.parse, "port"):
            domain = domain.split(":")[0]
        return domain

    @property
    def is_valid_domain(self) -> bool:
        """Validate subdomain."""
        return validators.domain(self.domain)

    @property
    def tld(self) -> bool:
        """Extract TLD."""
        return tldextract(self.url).registered_domain

    @property
    def is_valid_tld(self) -> bool:
        """Validate TLD."""
        return validators.domain(self.tld)

    @property
    def get_qs(self) -> dict:
        """Parse query fields and values."""
        return parse_qs(getattr(self.parse, "query"), keep_blank_values=True)

    @property
    def fixed(self) -> object:
        """Werkzeug url_fix to fix URL."""
        return URL(url_fix(self.url))

    @property
    def prep(self) -> str:
        """Canonicalize, cleanup url, remove schema.

        Sorts params, removes frags.
        Build url with blank scheme.
        Split url into 5 tuple.
        """
        return canonicalize_url(
            urlunsplit([""] + list(urlsplit(self.url.lower())[1:])))

    @property
    def bhash(self) -> str:
        """Return hash value of URL after cleaning."""
        return hash_utf8(self.prep)

    @property
    def slug(self) -> str:
        """Return slug of URL after cleaning."""
        return slugify(self.prep)

    def clean(self, include_scheme=True, include_fragments=False):
        """Reassemble clean URL."""
        u = urlsplit(self.url)
        scheme = ""
        if include_scheme:
            scheme = u.scheme
        # username and password may be case sensitive
        # From RFC 5321, section-2.3.11
        # https://stackoverflow.com/questions/9807909/are-email-addresses-case-sensitive
        netloc = ""
        if u.username:
            netloc = u.username
            if u.password:
                netloc += ":" + u.password
            netloc += "@"
        # domain names are not case sensitive
        # RFC 1035, section 3.1
        netloc += u.hostname.lower()
        if u.port and u.port not in [80, 443]:  # remove standard http(s) ports
            netloc += ":" + str(u.port)
        path = u.path.strip("/")  # remove leading and trailing slashes
        query = u.query
        fragment = ""
        if include_fragments:
            fragment = u.fragment
        return canonicalize_url(  # rebuild url with blank scheme
            urlunsplit((scheme, netloc, path, query, fragment)))

    @property
    def check(self):
        """Various checks for URL."""
        url = self.url
        logger.debug('validating url: {}'.format(url))
        if not validators.url(url):
            logger.info('url did not validate')
            return False
        logger.debug('checking dns')
        if not DNS().validate_domain(self.domain):
            logger.info('unable to resolve dns')
            return False
        logger.debug('requesting http head')
        try:
            r = requests.head(url, allow_redirects=True)
            r.raise_for_status()
        except Exception:
            logger.info('http head request failed', exc_info=True)
            return False
        else:
            logger.info('no connection error')
            if r.ok:
                return True
            else:
                logger.info('response not ok: {}'.format(r))
                return False


@attr.s(repr=False)
class Server:
    """Server object."""

    target = attr.ib()
    ip_address = None

    def __repr__(self) -> str:
        """Return target as repr."""
        return self.target

    def __attrs_post_init__(self) -> None:
        """Attempt to resolve dns is target is not an IP."""
        try:
            self.ip_address = ip_address(self.target)
        except ValueError:
            dns = DNS()
            res = dns.query(self.target)
            self.ip_address = ip_address(res[0])

    @property
    def ip(self) -> str:
        """Convert and return ip_address object as string."""
        return str(self.ip_address)

    def check_service(self, port: int, timeout: int) -> bool:
        """Check that TCP server responds on port within timeout."""
        if isinstance(self.ip_address, IPv4Address):  # noqa
            return self.check_service_v4(port, timeout)
        elif isinstance(self.ip_address, IPv6Address):  # noqa
            return self.check_service_v6(port, timeout)
        else:  # noqa
            return False

    def check_service_v4(self, port: int, timeout: int) -> bool:
        """Check that IPv4 TCP server responds on port within timeout."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((self.ip, port))
        if result:  # noqa
            return False
        else:  # noqa
            return True

    def check_service_v6(self, port: int, timeout: int) -> bool:
        """Check that IPv6 TCP server responds on port within timeout."""
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((self.ip, port, 0, 0))
        if result:  # noqa
            return False
        else:  # noqa
            return True

    def ping(self, tries=1, timeout=1) -> bool:
        """Return true if server is reachable via ping."""
        try:
            mp = MultiPing([self.ip])
            mp.send()
            for _ in range(tries):
                responses, _ = mp.receive(timeout)
                if responses:
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def check_server(server, port: int, timeout: int) -> bool:
        """Functional interface to check_service."""
        return Server(server).check_service(port, timeout)


@attr.s(frozen=True, repr=False)
class DNS:
    """DNS resolver object."""

    DNS_PORT = 53
    PROVIDERS = {
        "CLOUDFLARE_DNS": ["1.1.1.1", "1.0.0.1"],
        "CLOUDFLARE_DNSv6": ["2606:4700:4700::1111", "2606:4700:4700::1001"],
        "GOOGLE_DNS": ["8.8.8.8", "8.8.4.4"],
        "GOOGLE_DNSv6": ["2001:4860:4860::8888", "2001:4860:4860::8844"],
        "OPENDNS": ["208.67.222.222", "208.67.220.220"],
        "NORTON_CONNECTSAFE": ["199.85.126.10", "199.85.127.10"],
        "COMODO_DNS": ["8.26.56.26", "8.20.247.20"],
        "QUAD9_DNS": ["9.9.9.9", "149.112.112.112"],
        "VERISIGN_DNS": ["64.6.64.6", "64.6.65.6"],
    }
    DEFAULT_DNS = PROVIDERS["GOOGLE_DNSv6"] + PROVIDERS["GOOGLE_DNS"]

    ns = attr.ib(default=DEFAULT_DNS)
    timeout = attr.ib(default=5)

    resolver = Resolver()

    def __repr__(self) -> str:
        """Return list of nameservers as repr."""
        return str(self.nameservers)

    def __attrs_post_init__(self) -> None:
        """Filter nonresponsive nameservers out."""
        check_ns = partial(Server.check_server,
                           port=self.DNS_PORT,
                           timeout=self.timeout)
        if self.ns is not None:
            ns = list(filter(check_ns, self.ns))
            if ns:
                self.resolver.nameservers = ns

    @property
    def nameservers(self) -> list:
        """Return nameservers set on resolver."""
        return self.resolver.nameservers

    def query(self, domain) -> list:
        """Perform DNS query, return list of string answers."""
        return self.query_v4(domain) + self.query_v6(domain)

    def query_v4(self, domain) -> list:
        """Perform IPv4 DNS query, return list of string answers."""
        try:
            return [a.to_text() for a in self.resolver.query(domain, "A")]
        except Exception:
            return []

    def query_v6(self, domain) -> list:
        """Perform IPv6 DNS query, return list of string answers."""
        try:
            return [a.to_text() for a in self.resolver.query(domain, "AAAA")]
        except Exception:
            return []

    def validate_domain(self, domain) -> bool:
        """Ensure domain can be resolved to a valid address.

        Does not ensure that all returned addresses are valid.
        """
        try:
            results = self.query(domain)
        except Exception:
            return False
        if list(filter(validators.ip_address.ipv4, results)):
            return True
        if list(filter(validators.ip_address.ipv6, results)):
            return True
        return False

    @staticmethod
    def get_psl() -> Set[str]:
        """Get public suffix list."""
        with urlopen('https://publicsuffix.org/list/public_suffix_list.dat'
                     ) as file:
            psl = set({
                line
                for line in file.read().decode('utf-8').splitlines()
                if line and line[:2] != '//'
            })
        return psl
