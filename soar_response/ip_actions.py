from containment_store import make_record                                              # 기록 한 건을 만드는 함수를 불러온다

SHARED_IP_LIMIT = 2                                                                    # 한 IP 를 쓰는 계정이 이 수 이상이면 공유 IP 로 본다
DEFAULT_TTL = 120                                                                      # 차단을 유지하는 시간(분)


def is_in_allowlist(ip, allowlist_ips):                                                # IP 와 허용 목록을 받는 함수
    """IP 가 허용 목록에 있으면 True, 없으면 False 를 리턴한다.
    협력사 사무실처럼 차단하면 안 되는 IP 를 찾아낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. ip 가 allowlist_ips 안에 있는지(in)의 결과를 리턴한다
    return ip in allowlist_ips


def count_users_on_ip(ip, ip_users):                                                   # IP 와 IP 별 사용 계정 딕셔너리를 받는 함수
    """그 IP 를 쓰는 계정이 몇 개인지 리턴한다. ip_users.json 에 없는 IP 는 0 을 리턴한다.
    차단하면 정상 사용자가 몇 명 영향을 받는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. ip_users.get(ip, []) 의 개수(len)를 리턴한다 (목록에 없으면 빈 리스트로 본다)
    return len(ip_users.get(ip, []))

def check_ip_policy(ip, allowlist_ips, ip_users):                                      # IP · 허용 목록 · 사용 계정 딕셔너리를 받는 함수
    """자동으로 차단하면 안 되는 IP 이면 그 이유 문장을, 아니면 빈 글자("")를 리턴한다.
    허용 목록 IP 이거나 여러 계정이 함께 쓰는 IP 를 차단하기 전에 가려낼 때 쓴다.
    """
    if is_in_allowlist(ip, allowlist_ips):                                             # 허용 목록 IP 이면 — 미리 채운 줄
        return "허용 목록 IP 라서 차단하지 않음"                                       # 이유를 리턴한다 — 미리 채운 줄
    if count_users_on_ip(ip, ip_users) >= SHARED_IP_LIMIT:                             # 여러 계정이 함께 쓰는 IP 이면 — 미리 채운 줄
        return "여러 계정이 함께 쓰는 IP 라서 담당자 승인 필요"                        # 이유를 리턴한다 — 미리 채운 줄
    return ""                                                                          # 막을 이유가 없으면 빈 글자를 리턴한다 — 미리 채운 줄


def block_ip(ip, state, incident_id, reason, ttl):                                     # IP · 상태 · 인시던트 번호 · 이유 · 유지 시간을 받는 함수
    """IP 를 차단하고 끝나는 시각을 적은 뒤, 실제로 차단됐는지 확인해 기록 한 건을 리턴한다.
    영구 차단 대신, 시간이 지나면 자동으로 풀리는 임시 차단을 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. state["blocked_ips"] 에 ip 를 추가한다 (append)
    state["blocked_ips"].append(ip)
    # 4. state["block_expiry"][ip] 에 state["clock"] + ttl 을 저장한다 (끝나는 시각)
    state["block_expiry"][ip] = state["clock"] + ttl
    after = "차단됨"                                                                   # 조치 뒤 상태 : 일단 차단됐다고 적고 — 미리 채운 줄
    if ip not in state["blocked_ips"]:                                                 # 실제로 확인해 차단되지 않았으면 — 미리 채운 줄
        after = "차단되지 않음 (확인 실패)"                                            # 확인 실패라고 고쳐 적는다 — 미리 채운 줄
    return make_record("IP 차단", ip, incident_id, "차단되지 않음", after, reason + " (" + str(ttl) + "분 뒤 자동 해제)")  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def unblock_ip(ip, state, incident_id, reason):                                        # IP · 상태 · 인시던트 번호 · 이유를 받는 함수
    """차단한 IP 를 풀고 끝나는 시각 기록도 지운 뒤 기록 한 건을 리턴한다.
    시간이 끝나서 풀거나 오탐으로 풀 때 쓴다.
    """
    state["blocked_ips"].remove(ip)                                                    # 차단 리스트에서 제거한다 — 미리 채운 줄
    state["block_expiry"].pop(ip)                                                      # 끝나는 시각 기록도 지운다 — 미리 채운 줄
    return make_record("IP 해제", ip, incident_id, "차단됨", "차단되지 않음", reason)  # 조치 전 · 후 상태와 함께 기록한다 — 미리 채운 줄


def expire_blocks(state, incident_id):                                                 # 상태와 인시던트 번호를 받는 함수
    """끝나는 시각이 지난 차단을 모두 풀고 해제 기록 리스트를 리턴한다.
    임시 차단이 사람 손 없이 풀리게 할 때 쓴다.
    """
    records = []                                                                       # 해제 기록을 저장할 빈 리스트
    for ip in list(state["blocked_ips"]):                                              # 차단 리스트의 복사본에서 IP 를 하나씩 꺼낸다 (원본을 바꾸며 돌면 안 되기 때문이다)
        end_time = state["block_expiry"][ip]                                           # 그 IP 의 차단이 끝나는 시각 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. end_time 이 state["clock"] 이하이면 (if, <=)
        if end_time <= state["clock"]: 
        # 6.   unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제") 의 결과를 records 에 추가한다 (append)
            records.append(
                unblock_ip(ip, state, incident_id, "차단 시간이 끝나 자동 해제")
                )
    return records                                                                     # 해제 기록 리스트를 리턴한다
