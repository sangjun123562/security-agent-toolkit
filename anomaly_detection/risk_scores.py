import json                                        # 점수를 JSON 파일로 쓰기 위해 json 을 불러온다
import pandas as pd                                    # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users  # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures, find_scan_ips  # 4교시 함수를 불러온다

RISK_PATH = "day03_risk_scores.json"                   # 점수를 저장할 파일 이름
HIGH_LIMIT = 60                                        # 점수가 이 값 이상이면 high
MID_LIMIT = 35                                         # 점수가 이 값 이상이면 mid, 그보다 낮으면 low
WEIGHTS = {"퇴사한 계정": 60, "권한 없음": 20, "규칙은 허용인데 서버가 거절": 10,
           "업무 시간 밖 로그인": 15, "평소와 다른 IP": 20, "대량 다운로드": 25,
           "경로 스캔": 30, "여러 로그 연결": 30}      # 탐지된 규칙마다 점수
SERVER_RULES = {"퇴사한 계정": "퇴사한 계정", "권한 없음": "권한 없음", "허용": "규칙은 허용인데 서버가 거절"}  # 서버 판정 이유를 규칙 이름으로 바꾼다


def add_finding(findings, entity, rule):               # 리스트 · 대상 · 규칙 이름을 받는 함수
    """대상과 탐지된 규칙을 한 건 추가하되 같은 건은 한 번만 추가한다.
    같은 규칙이 여러 이벤트에 해당해도 점수가 중복되지 않게 할 때 쓴다.
    """
    finding = {"entity": entity, "rule": rule}         # 대상과 규칙을 딕셔너리로 만든다
    if finding not in findings:                        # 아직 없는 건이면
        findings.append(finding)                       # 리스트에 추가한다


def collect_findings(events, chains):                  # 이벤트 표와 연결된 사건을 받는 함수
    """오전 탐지 3개와 5교시 연결 결과를 (대상, 탐지된 규칙) 리스트로 모은다.
    점수를 매기기 전에 한 번에 쓴다.
    """
    findings = []                                      # 탐지된 규칙을 담을 빈 리스트

    server_failures = pick_server_failures(events)     # 판정 서버 실패 이벤트를 고른다
    suspicious = pick_suspicious(server_failures)      # 먼저 확인할 서버 이벤트를 고른다
    suspicious_list = suspicious.to_dict("records")    # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for event in suspicious_list:                      # 이벤트를 하나씩 꺼낸다
        reason, priority = judge_failure(event["user"], event["action"])  # 3과목 규칙으로 다시 판정한다
        rule = SERVER_RULES.get(reason, reason)        # 판정 이유를 규칙 이름으로 바꾼다
        add_finding(findings, event["user"], rule)     # 사용자와 규칙을 추가한다

    saas = pick_saas(events)                           # SaaS 이벤트를 고른다
    logins = pick_logins(saas)                         # 로그인 이벤트를 고른다
    off_hours_logins = find_off_hours_logins(logins)   # 업무 시간 밖 로그인을 찾는다
    off_hours_users = list(off_hours_logins["user"])   # 그 로그인의 사용자 이름만 리스트로 만든다
    new_ip_users = find_new_ip_users(logins)           # 평소와 다른 IP 로 로그인한 사용자를 찾는다
    bulk_users = find_bulk_download_users(saas)        # 대량 다운로드 사용자를 찾는다
    for user in off_hours_users:                       # 업무 시간 밖 로그인 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "업무 시간 밖 로그인")  # 사용자와 규칙을 추가한다
    for user in new_ip_users:                          # 평소와 다른 IP 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "평소와 다른 IP")  # 사용자와 규칙을 추가한다
    for user in bulk_users:                            # 대량 다운로드 사용자를 하나씩 꺼낸다
        add_finding(findings, user, "대량 다운로드")   # 사용자와 규칙을 추가한다

    web_failures = pick_web_failures(events)           # 웹 실패 이벤트를 고른다
    scan_ips, many_kinds = find_scan_ips(web_failures)  # 경로 스캔 IP 를 찾는다
    for ip in scan_ips:                                # 스캔 IP 를 하나씩 꺼낸다
        add_finding(findings, ip, "경로 스캔")         # IP 와 규칙을 추가한다

    for chain in chains:                               # 연결된 사건을 하나씩 꺼낸다
        add_finding(findings, chain["user"], "여러 로그 연결")  # 사용자와 규칙을 추가한다
    return findings                                    # 탐지된 규칙 리스트를 리턴한다


def score_findings(findings):                          # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙의 점수를 더해 점수가 높은 순으로 정렬한다.
    어느 대상부터 볼지 순서를 정할 때 쓴다.
    """
    findings_table = pd.DataFrame(findings)            # 딕셔너리 리스트를 표로 만든다 — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. findings_table 의 "rule" 열을 꺼내 .map(WEIGHTS) 를 붙여 규칙마다 점수를 구해 points 에 담는다
    points = findings_table["rule"].map(WEIGHTS)
    findings_table["points"] = points                  # 표에 points 열을 붙인다 — 미리 채운 줄
    grouped = findings_table.groupby("entity")         # entity 가 같은 행끼리 그룹으로 만든다
    # 2. grouped 에서 "points" 열을 골라 .sum() 을 붙여 그룹마다 점수 합계를 구해 totals 에 담는다
    totals = grouped["points"].sum()
    totals = totals.sort_values(ascending=False)       # 점수가 높은 순으로 정렬한다 — 미리 채운 줄
    return totals                                      # 대상별 점수를 리턴한다


def make_grade(score):                                 # 점수를 받는 함수
    """점수로 high · mid · low 등급을 정한다.
    점수가 높은 대상부터 먼저 보게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. if 로 시작한다: score 가 HIGH_LIMIT 이상이면
    if score >= HIGH_LIMIT:
    # 4.   그 if 안쪽에서 "high" 를 리턴한다
        return "high"
    if score >= MID_LIMIT:                             # 점수가 mid 기준 이상이면 — 미리 채운 줄 (위 high 와 같은 모양)
        return "mid"                                   # mid 이다 — 미리 채운 줄
    return "low"                                       # 둘 다 아니면 low 이다


def collect_reasons(findings):                         # 탐지된 규칙 리스트를 받는 함수
    """대상마다 탐지된 규칙 이름을 모아 딕셔너리로 만든다.
    왜 그 등급인지 이유를 함께 저장할 때 쓴다.
    """
    reasons = {}                                       # 대상 → 규칙 이름 리스트 딕셔너리
    for finding in findings:                           # 탐지된 규칙을 하나씩 꺼낸다
        entity = finding["entity"]                     # 그 건의 대상
        if entity not in reasons:                      # 처음 나온 대상이면
            reasons[entity] = []                       # 빈 리스트를 만든다
        reasons[entity].append(finding["rule"])        # 그 대상의 규칙 이름을 추가한다
    return reasons                                     # 대상별 규칙 이름을 리턴한다


def make_records(totals, reasons):                     # 대상별 점수와 이유를 받는 함수
    """대상마다 점수 · 등급 · 이유를 담은 딕셔너리 리스트를 만든다.
    담당자가 읽을 파일의 내용을 만들 때 쓴다.
    """
    records = []                                       # 기록을 담을 빈 리스트
    for entity, score in totals.items():               # 대상과 점수를 한 쌍씩 꺼낸다
        grade = make_grade(score)                      # 점수로 등급을 정한다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. 키 "entity" 에 entity, "score" 에 int(score), "grade" 에 grade, "reasons" 에 reasons[entity] 를 담은 딕셔너리를 record 에 담는다 (int 는 JSON 저장용)
        record = {
            "entity":entity,
            "score":int(score),
            "grade":grade,
            "reasons":reasons[entity]
        }
        records.append(record)                         # 기록을 리스트에 추가한다
    return records                                     # 기록 리스트를 리턴한다


def save_records(records, path):                       # 기록 리스트와 파일 경로를 받는 함수
    """기록 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다.
    담당자와 다른 프로그램이 같은 파일을 읽게 할 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:    # path 파일을 쓰기 모드로 연다
        json.dump(records, file, ensure_ascii=False, indent=2)  # 한글은 그대로, 줄을 나눠 저장한다
    saved_count = len(records)                         # 저장한 기록이 몇 건인지 센다
    return saved_count                                 # 저장한 건수를 리턴한다
