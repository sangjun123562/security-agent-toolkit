def lookup_account(entity, users_info):                              # 대상 이름과 계정 정보 딕셔너리를 받는 함수
    """계정 정보 파일에서 이 대상이 재직 중인지, VIP 계정인지 찾아 딕셔너리로 리턴한다.
    파일에 이름이 없는 대상(IP 등)은 처음 값(False)을 그대로 리턴한다.
    """
    account = {"employed": False, "vip": False}                      # 처음에는 모르는 상태로 시작한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. entity 가 users_info 안에 있으면 (if, in)
    if entity in users_info:
    # 2.   account 의 "employed" 에 users_info[entity]["employed"] 를 담는다
        account["employed"] = users_info[entity]["employed"]
    # 3.   account 의 "vip" 에 users_info[entity]["vip"] 를 담는다
        account["vip"] = users_info[entity]["vip"]
    return account                                                   # 계정 정보를 리턴한다


def lookup_source_ip(entity, source_ips, trusted_ips):               # 대상 이름 · 접속 IP 딕셔너리 · 신뢰 IP 리스트를 받는 함수
    """이 대상이 접속한 IP 와, 그 IP 가 신뢰 IP 목록에 있는지 찾아 딕셔너리로 리턴한다.
    접속 IP 를 모르는 대상은 처음 값(None 과 False)을 그대로 리턴한다.
    """
    ip_info = {"source_ip": None, "ip_trusted": False}               # 처음에는 모르는 상태로 시작한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. entity 가 source_ips 안에 있으면 (if, in)
    if entity in source_ips:
    # 5.   ip_info 의 "source_ip" 에 source_ips[entity] 를 담는다
        ip_info["source_ip"] = source_ips[entity]
    # 6.   ip_info 의 "ip_trusted" 에 source_ips[entity] 가 trusted_ips 안에 있는지(in)의 결과를 담는다
        ip_info["ip_trusted"] = source_ips[entity] in trusted_ips
    return ip_info                                                   # 접속 IP 정보를 리턴한다


def enrich_incident(incident, users_info, source_ips, trusted_ips):  # 인시던트 · 계정 정보 · 접속 IP 딕셔너리 · 신뢰 IP 리스트를 받는 함수
    """위 두 함수가 찾은 정보를 모아 알림에 context 라는 이름으로 붙이고, 붙인 알림을 리턴한다.
    붙이고 나면 알림만 봐도 퇴사 · VIP · 접속 IP 를 알 수 있어서, 조치하기 전에 확인할 때 쓴다.
    """
    entity = incident["entity"]                                      # 대응할 대상(사용자 이름 또는 IP)
    account = lookup_account(entity, users_info)                     # 계정 정보를 찾는다
    ip_info = lookup_source_ip(entity, source_ips, trusted_ips)      # 접속 IP 정보를 찾는다
    account_known = entity in users_info                             # 계정 정보에 있는 대상인지 구한다
    context = {"account_known": account_known, "employed": account["employed"], "vip": account["vip"], "source_ip": ip_info["source_ip"], "ip_trusted": ip_info["ip_trusted"]}  # 다섯 가지 맥락을 합친다
    incident["context"] = context                                    # 인시던트에 맥락을 붙인다
    return incident                                                  # 맥락이 붙은 인시던트를 리턴한다
