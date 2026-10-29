from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from review_list import build_access_list                        # 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 방금 만든 규칙 점검 함수를 불러온다

NOW = datetime.strptime("2026-10-29 10:00", "%Y-%m-%d %H:%M")    # 오늘 실습의 지금 시각(고정)

access_list = build_access_list()                                # 현황을 만든다
stale = find_stale(access_list, NOW)                             # 규칙에 걸린 권한을 찾는다

print("--- 단계 1: 판정 - 규칙에 걸린 권한", len(stale), "건 (전체", len(access_list), "건 중)")   # 단계 1 시작을 알리는 줄
for entry in stale:                                              # 걸린 권한을 한 건씩 꺼낸다
    print(entry["user"], entry["permission"], "<-", entry["source"], "|", entry["reason"])   # 사용자 · 권한 <- 출처 | 이유를 출력한다

print("--- 단계 2: 점검 - 이유별 건수")                           # 단계 2 시작을 알리는 줄
counts = {}                                                      # 이유 → 건수를 담을 빈 딕셔너리
for entry in stale:                                              # 걸린 권한을 한 건씩 꺼낸다
    counts[entry["reason"]] = counts.get(entry["reason"], 0) + 1   # 그 이유의 건수를 1 늘린다
print(counts)                                                    # 이유별 건수를 출력한다
