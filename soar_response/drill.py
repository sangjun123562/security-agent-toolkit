from enrichment import enrich_incident                                                      # 화요일 2교시 : 맥락 붙이기
from routing import decide_route                                                            # 화요일 3교시 : 경로 정하기
from containment_store import make_record                                                   # 기록 한 건을 만드는 함수를 불러온다
from containment import contain_account                                                     # 오전 4교시 : 잠금 → 세션 종료
from ip_actions import check_ip_policy, block_ip, DEFAULT_TTL                               # 오전 3교시 : IP 차단

CONTAINMENT_BY_RULE = {"퇴사한 계정": "계정 조치", "경로 스캔": "IP 차단"}                  # 탐지된 규칙에 따라 할 조치 : 이 표에 없는 규칙은 조치하지 않는다
FIREWALL_DOWN_FOR = ["INC-005"]                                                             # 방화벽 연결이 끊긴 상황을 흉내 낼 인시던트 번호 : 이 인시던트의 IP 차단은 실패한다


def choose_containment(incident):                                                           # 인시던트 하나를 받는 함수
    """탐지된 규칙을 하나씩 보고, 조치 표(CONTAINMENT_BY_RULE)에 있는 규칙이면 그 조치 이름을, 하나도 없으면 「없음」을 리턴한다.
    규칙마다 어떤 자동 조치를 할지 연결해 둘 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. incident["reasons"] 의 규칙을 하나씩 꺼낸다 (for, rule)
    for rule in incident["reasons"]:
    # 2.   rule 이 CONTAINMENT_BY_RULE 안에 있으면 (if, in)
        if rule in CONTAINMENT_BY_RULE:
    # 3.     CONTAINMENT_BY_RULE[rule] 을 리턴한다
            return CONTAINMENT_BY_RULE[rule]
    return "없음"                                                                           # 조치 표에 있는 규칙이 없으면 「없음」을 리턴한다 — 미리 채운 줄


def handle_incident(incident, state, refs):                                                 # 인시던트 · 연습용 시스템 상태 · 참고 데이터 딕셔너리를 받는 함수
    """알림 한 건에 맥락을 붙이고 경로를 정한 뒤, 오탐은 종료하고 VIP 는 승인 대기로 두고, 나머지는 규칙에 맞는 조치를 실행한다.
    알림 한 건을 처음부터 끝까지 처리할 때 쓰고, 처리 결과 문장과 조치 기록 리스트를 함께 리턴한다.
    """
    enrich_incident(incident, refs["users_info"], refs["source_ips"], refs["trusted_ips"])  # 화요일 : 맥락을 붙인다 — 미리 채운 줄
    route, reason = decide_route(incident)                                                  # 화요일 : 처리 경로와 이유를 정한다 — 미리 채운 줄
    if route == "오탐 종료":                                                                # 오탐으로 닫을 알림이면 — 미리 채운 줄
        return "오탐 종료", []                                                              # 조치하지 않고 끝낸다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. route 가 "승인 필요" 이면 (if, ==)
    if route == "승인 필요":
    # 5.   "승인 대기" 와 빈 리스트 [] 를 쉼표로 이어 함께 리턴한다 (담당자가 허락하기 전에는 조치하지 않는다)
        return "승인 대기", []
    kind = choose_containment(incident)                                                     # 할 조치 종류를 구한다 — 미리 채운 줄
    entity = incident["entity"]                                                             # 대응할 대상 — 미리 채운 줄
    if kind == "계정 조치":                                                                 # 계정 조치이면 — 미리 채운 줄
        records = contain_account(entity, state, refs["vip_accounts"], incident["id"], incident["reasons"][0])  # 잠금 → 세션 종료 — 미리 채운 줄
        return "조치함", records                                                            # 조치 결과를 리턴한다 — 미리 채운 줄
    if kind == "IP 차단":                                                                   # IP 차단이면 — 미리 채운 줄
        if incident["id"] in FIREWALL_DOWN_FOR:                                             # 방화벽 연결이 끊긴 상황이면 — 미리 채운 줄
            return "조치 실패", [make_record("IP 차단", entity, incident["id"], "차단되지 않음", "차단되지 않음 (확인 실패)", "방화벽 연결 실패")]  # 차단되지 않았다고 기록한다 — 미리 채운 줄
        refusal = check_ip_policy(entity, refs["allowlist_ips"], refs["ip_users"])          # 차단을 막을 이유를 구하고 — 미리 채운 줄
        if refusal != "":                                                                   # 막을 이유가 있으면 — 미리 채운 줄
            status = "조치하지 않음"                                                        # 기본은 조치하지 않음이고 — 미리 채운 줄
            if "승인 필요" in refusal:                                                      # 담당자 승인이 필요한 이유이면 — 미리 채운 줄
                status = "승인 대기"                                                        # 승인 대기로 바꾼다 — 미리 채운 줄
            return status, [make_record("IP 차단", entity, incident["id"], "변경 없음", "변경 없음", refusal)]  # 이유만 기록한다 — 미리 채운 줄
        return "조치함", [block_ip(entity, state, incident["id"], incident["reasons"][0], DEFAULT_TTL)]  # 차단하고 기록한다 — 미리 채운 줄
    return "조치하지 않음", []                                                              # 자동 조치 대상이 아니면 조치하지 않는다 — 미리 채운 줄
