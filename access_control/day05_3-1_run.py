from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 2교시에 만든 회수 계획 함수를 불러온다
from revoke_approve import load_sensitive, mark_approvals        # 방금 만든 승인 함수를 불러온다

DECISIONS = {"dami:SALES:QUERY": "승인", "dami:SALES:CHANGE": "승인"}  # 보안 책임자의 결정. 여기 없는 계획은 아직 결정하지 않은 것이다

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 2교시와 같은 방법으로 회수 계획을 세운다
sensitive = load_sensitive("config/sensitive.json")              # 민감한 권한 리스트를 읽는다
results = mark_approvals(plans, sensitive, DECISIONS)            # 계획마다 승인 상태를 적는다

print("--- 단계 1: 승인 상태 - 계획 8건")                        # 단계 1 시작을 알리는 줄
for item in results:                                             # 결과를 하나씩 꺼낸다
    print(item["user"], item["permission"], "<-", item["source"], "|", item["method"], "| 영향", item["impact"], "건 |", item["approval"])  # 사용자 · 권한 <- 출처 | 방법 | 영향 | 승인 상태를 출력한다

print("--- 단계 2: 집계 - 승인 상태별 건수")                     # 단계 2 시작을 알리는 줄
counts = {}                                                      # 승인 상태 → 건수를 담을 빈 딕셔너리
for item in results:                                             # 결과를 하나씩 꺼낸다
    count_key = item["approval"]                                 # 세는 기준이 되는 키
    old_count = counts.get(count_key, 0)                         # 그 키의 지금까지 센 수(처음이면 0)
    counts[count_key] = old_count + 1                            # 1 늘려서 다시 적는다
print(counts)                                                    # 승인 상태별 건수를 출력한다
