from review_list import build_access_list                        # 방금 만든 현황 함수를 불러온다

access_list = build_access_list()                                # 지금 부여돼 있는 권한 현황을 만든다

print("--- 단계 1: 현황 - 부여돼 있는 권한", len(access_list), "건")   # 단계 1 시작을 알리는 줄
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    print(entry["user"], entry["permission"], "<-", entry["source"], "| 재직", entry["employed"])   # 사용자 · 권한 <- 출처 | 재직 여부를 출력한다

print("--- 단계 2: 점검 - 사용자별 권한 개수")                     # 단계 2 시작을 알리는 줄
counts = {}                                                      # 사용자 → 권한 개수를 담을 빈 딕셔너리
for entry in access_list:                                        # 현황의 권한을 한 건씩 꺼낸다
    counts[entry["user"]] = counts.get(entry["user"], 0) + 1     # 그 사용자의 개수를 1 늘린다
print(counts)                                                    # 사용자별 개수를 출력한다
