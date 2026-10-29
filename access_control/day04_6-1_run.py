from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report                        # 오후 5교시에 만든 리포트 함수를 불러온다
from report_exclude import load_exclude_map, split_by_exclude   # 방금 만든 회수 제외 함수를 불러온다

NOW = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 글자의 형식

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다
unused = find_unused(access_list, load_last_used(), NOW, 90)     # 같은 현황에서 90일 넘게 안 쓴 권한을 찾는다(규칙에 걸린 권한도 빼지 않고 전부 넣는다)
report = generate_report(access_list, stale, unused, 90, NOW.strftime(TIME_FORMAT))   # 5교시와 같은 방법으로 리포트를 만든다

exclude_map = load_exclude_map("config/exclude_list.json")   # 회수 제외 목록을 읽는다
to_revoke, excluded = split_by_exclude(report["findings"], exclude_map)   # 후보를 회수 대상과 회수 제외로 나눈다

print("--- 단계 1: 분류 - 후보", report["finding_count"], "건 중 회수 대상", len(to_revoke), "건, 회수 제외", len(excluded), "건")   # 단계 1 시작을 알리는 줄
print("--- 단계 2: 제외 - 회수 제외한 후보와 제외 이유")              # 단계 2 시작을 알리는 줄
for item in excluded:                                            # 회수 제외한 후보를 하나씩 꺼낸다
    print(item["user"], item["permission"], "<-", item["source"], "|", item["exclude_reason"])   # 사용자 · 권한 <- 출처 | 제외 이유를 출력한다

print("--- 단계 3: 확인 - 제외 목록에 있지만 회수 대상으로 남은 후보")        # 단계 3 시작을 알리는 줄
for item in to_revoke:                                           # 회수 대상을 하나씩 꺼낸다
    if item["user"] + ":" + item["permission"] in exclude_map:   # 제외 목록에 있는 권한이면
        print(item["user"], item["permission"], "<-", item["source"], "|", ", ".join(item["reasons"]))   # 사용자 · 권한 <- 출처 | 이유들을 출력한다
