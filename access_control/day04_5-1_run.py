from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report, entry_key             # 방금 만든 리포트 함수와 식별 키 함수를 불러온다

NOW = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")    # 오늘 오후 실습의 지금 시각(고정)
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 글자의 형식

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다
unused = find_unused(access_list, load_last_used(), NOW, 90)     # 같은 현황에서 90일 넘게 안 쓴 권한을 찾는다(규칙에 걸린 권한도 빼지 않고 전부 넣는다)

report = generate_report(access_list, stale, unused, 90, NOW.strftime(TIME_FORMAT))   # 과다권한 후보 리포트를 만든다

print("--- 단계 1: 요약 - 점검", report["total"], "건 중 후보", report["finding_count"], "건 (", report["generated_at"], ")")   # 단계 1 시작을 알리는 줄
for finding in report["findings"]:                               # 후보를 한 건씩 꺼낸다
    print(finding["user"], finding["permission"], "<-", finding["source"], "|", ", ".join(finding["reasons"]))   # 사용자 · 권한 <- 출처 | 이유들을 출력한다

print("--- 단계 2: 확인 - 후보가 아닌 권한")                       # 단계 2 시작을 알리는 줄
finding_keys = []                                                # 후보의 식별 키를 담을 빈 목록
for finding in report["findings"]:                               # 후보를 하나씩 꺼내
    finding_keys.append(entry_key(finding))                      # 그 식별 키를 목록에 추가한다
names = []                                                       # 후보가 아닌 권한(「사용자 권한」 글자)을 담을 빈 목록
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    if entry_key(entry) not in finding_keys:                     # 식별 키가 후보 목록에 없으면
        names.append(entry["user"] + " " + entry["permission"])  # 사용자와 권한을 목록에 추가한다
print(names)                                                     # 후보가 아닌 권한을 출력한다
