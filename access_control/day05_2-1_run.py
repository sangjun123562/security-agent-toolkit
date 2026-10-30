from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 방금 만든 회수 계획 함수를 불러온다

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 회수 계획을 세운다(실제로는 지우지 않는다)

print("--- 단계 1: 계획 - 회수 대상", len(to_revoke), "건의 회수 방법")   # 단계 1 시작을 알리는 줄
for plan in plans:                                               # 계획을 하나씩 꺼낸다
    print(plan["user"], plan["permission"], "<-", plan["source"], "|", plan["method"], "| 영향", plan["impact"], "건")   # 사용자 · 권한 <- 출처 | 방법 | 영향을 출력한다

print("--- 단계 2: 집계 - 방법별 건수")                           # 단계 2 시작을 알리는 줄
counts = {}                                                      # 방법 → 건수를 담을 빈 딕셔너리
for plan in plans:                                               # 계획을 하나씩 꺼낸다
    count_key = plan["method"]                                   # 세는 기준이 되는 키
    old_count = counts.get(count_key, 0)                         # 그 키의 지금까지 센 수(처음이면 0)
    counts[count_key] = old_count + 1                            # 1 늘려서 다시 적는다
print(counts)                                                    # 방법별 건수를 출력한다

print("--- 단계 3: 확인 - 역할별 사용자 수와 이름")                    # 단계 3 시작을 알리는 줄
names_by_role = {"finance": [], "sales": []}                     # 역할 → 그 역할을 가진 사용자 이름 리스트
for name, info in USERS.items():                                 # 사용자를 하나씩 꺼낸다
    if info["role"] in names_by_role:                            # finance 나 sales 역할이면
        names_by_role[info["role"]].append(name)                 # 그 역할의 이름 리스트에 이름을 추가한다
for role in names_by_role:                                       # 두 역할을 하나씩 꺼낸다
    names = names_by_role[role]                                  # 그 역할의 이름 리스트
    print(role, len(names), "명", names)                         # 역할 · 사용자 수 · 이름을 출력한다
