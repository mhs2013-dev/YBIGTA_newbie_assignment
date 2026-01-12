from __future__ import annotations

import socket
from typing import Optional


def resolve(host: str) -> tuple[list[str], Optional[str]]:
    """
    도메인 이름을 IP 주소 리스트로 변환합니다.
    """
    try:
        infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        
        ###########################################################
        # TODO: sockaddr에서 IP 주소만 추출하여 리스트(ips)로 만드세요.
        # HINT: 리스트 컴프리헨션을 사용하여 sockaddr[0] 값을 가져오세요.

        #ips = [] # TODO: [이곳에 IP 리스트 생성 코드를 작성하세요]
        ips: list[str] = []
        seen: set[str] = set()

        for info in infos:
            sockaddr = info[4]        # (ip, port) 또는 (ip, port, flowinfo, scopeid)
            ip = str(sockaddr[0])
            if ip not in seen:
                seen.add(ip)
                ips.append(ip)

        ###########################################################

        return ips, None
    except Exception as e:
        return [], str(e)


def pick_ip(ips: list[str], prefer: str = "any") -> Optional[str]:
    """
    주어진 IP 리스트 중 prefer 정책에 맞는 최적의 IP 하나를 선택하여 반환합니다. 
    
    요구사항:
    1. prefer가 "ipv4"인 경우: 리스트에서 가장 먼저 발견되는 IPv4 주소(:가 없는 주소)를 반환합니다. 
    2. prefer가 "ipv6"인 경우: 리스트에서 가장 먼저 발견되는 IPv6 주소(:가 있는 주소)를 반환합니다. 
    3. 정책에 맞는 주소가 없거나 prefer가 "any"인 경우: 리스트의 첫 번째 주소를 반환합니다. 
    """
    if not ips:
        return None

    ###########################################################
    # TODO: prefer 정책에 따른 IP 선택 로직을 직접 구현하세요.
    # HINT: 리스트를 순회하며 조건문(if)으로 주소 형식을 검사해야 합니다.
    ###########################################################
    if prefer == "ipv4":
        for ip in ips:
            if ":" not in ip:
                return ip
    elif prefer == "ipv6":
        for ip in ips:
            if ":" in ip:
                return ip

    return ips[0]