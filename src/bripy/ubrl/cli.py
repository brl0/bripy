"""Command line interface for ubrl."""

from typing import List

import click

from bripy.ubrl.ubrl import DNS, Server


@click.group()
def main():
    """Command line interface for ubrl."""
    pass  # noqa


@main.command(help="| Pings target and returns count, target, ip, and True or False.")
@click.argument("target")
@click.option("--count", default=1, help="Number of results to collect.")
@click.option("--timeout", default=1, help="Seconds to allow for response.")
@click.option("--tries", default=1, help="Number of tries for each result.")
def ping(target: str, count: int, timeout: int, tries: int) -> list[bool]:
    """Ping command."""
    server = Server(target)
    results = []
    for i in range(count):
        result = server.ping(tries=tries, timeout=timeout)
        results.append(result)
        print((i, server, server.ip, result))
    print(results)
    return results


@main.command(help="| Pings target tcp port.")
@click.argument("target", type=str)
@click.argument("port", type=int)
@click.option("--count", default=1, help="Number of results to collect.")
@click.option("--timeout", default=1, help="Seconds to allow for response.")
def pingport(target: str, port: int, count: int, timeout: int) -> list[bool]:
    """Pingport command."""
    server = Server(target)
    results = []
    for i in range(count):
        result = server.check_service(port=port, timeout=timeout)
        results.append(result)
        print((i, server, port, server.ip, result))
    print(results)
    return results


@main.command(help="| Query default name servers for IPv4 and IPv6 addresses.")
@click.argument("target", type=str)
def query(target: str) -> list[str]:
    """Query command."""
    dns = DNS()
    print(f"nameservers: {DNS.nameservers}")
    results = dns.query(target)
    print(f"results: {results}")
    return results


if __name__ == "__main__":
    main()
