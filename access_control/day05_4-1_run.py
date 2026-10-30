from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from rbac import USERS, ROLES                                    # 10/21(수)에 만든 사용자 · 역할 딕셔너리를 불러온다
from exception_policy import EXCEPTIONS, TIME_FORMAT             # 10/22(목)에 만든 예외 리스트와 시각 형식을 불러온다
from policy import evaluate_access                               # 10/22(목)에 만든 최종 판정 함수를 불러온다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from revoke_input import load_to_revoke                          # 어제 점검 결과(회수 대상)를 만드는 함수를 불러온다
from revoke_plan import plan_revocation                          # 2교시에 만든 회수 계획 함수를 불러온다
from revoke_approve import load_sensitive, mark_approvals        # 3교시에 만든 승인 함수를 불러온다
from revoke import execute_revocation, save_log                  # 방금 만든 회수 실행 함수와 이력 저장 함수를 불러온다

NOW_TEXT = "2026-10-30 10:00"                                    # 오늘 오전 실습의 지금 시각 문자열(고정)
NOW = datetime.strptime(NOW_TEXT, TIME_FORMAT)                   # 같은 시각을 시각으로 바꾼다. 판정 함수가 쓴다
DECISIONS = {"dami:SALES:QUERY": "승인", "dami:SALES:CHANGE": "승인"}  # 보안 책임자의 결정(3교시와 같다)

to_revoke = load_to_revoke()                                     # 어제 점검한 회수 대상을 만든다
plans = plan_revocation(to_revoke, USERS, ROLES)                 # 회수 계획을 세운다
sensitive = load_sensitive("config/sensitive.json")              # 민감한 권한 리스트를 읽는다
plans = mark_approvals(plans, sensitive, DECISIONS)              # 계획마다 승인 상태를 적는다

def judge(plan):                                                 # 계획 한 건을 받는 함수
    """계획의 사용자 · 권한을 지금 판정해 「허용(이유)」 또는 「거부(이유)」 문자열을 리턴한다."""
    resource, action = plan["permission"].split(":")             # "SALES:QUERY" 를 자원과 행위로 나눈다
    ok, reason = evaluate_access(plan["user"], resource, action, NOW)  # 최종 판정을 한다
    if ok:                                                       # 허용이면
        return "허용(" + reason + ")"                            # 허용과 이유를 하나의 문자열로 합친다
    return "거부(" + reason + ")"                                # 거부와 이유를 하나의 문자열로 합친다


def judge_all(plans):                                            # 계획 리스트를 받는 함수
    """계획마다 judge 로 판정한 문자열을 같은 순서의 리스트로 리턴한다."""
    results = []                                                 # 판정을 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        verdict = judge(plan)                                    # 계획 한 건을 판정한다
        results.append(verdict)                                  # 판정해서 추가한다
    return results                                               # 판정 리스트를 리턴한다


before = judge_all(plans)                                        # 회수하기 전의 판정을 모두 구해 둔다
log = execute_revocation(plans, USERS, ROLES, EXCEPTIONS, NOW_TEXT)  # 회수를 실행한다
after = judge_all(plans)                                         # 회수한 뒤의 판정을 모두 구한다

print("--- 단계 1: 실행 - 회수 결과")                            # 단계 1 시작을 알리는 줄
done = 0                                                         # 실행한 건수를 0 으로 시작한다
for entry in log:                                                # 이력을 하나씩 꺼낸다
    print(entry["user"], entry["permission"], "|", entry["method"], "|", entry["result"])  # 사용자 · 권한 | 방법 | 결과를 출력한다
    if entry["result"] == "실행":                                # 실행한 건이면
        done = done + 1                                          # 건수를 1 늘린다
print("실행", done, "건, 대기", len(log) - done, "건")           # 실행과 대기 건수를 출력한다

print("--- 단계 2: 확인 - 회수 전후의 판정")                     # 단계 2 시작을 알리는 줄
plan_count = len(plans)                                          # 개수를 먼저 구한다
for i in range(plan_count):                                      # 번호 i 로 회수 전 리스트와 회수 후 리스트를 짝지어 꺼낸다
    mark = "그대로"                                              # 표시를 그대로로 시작한다
    if before[i] != after[i]:                                    # 회수 전후의 판정이 다르면
        mark = "바뀜"                                            # 바뀜으로 고친다
    print(plans[i]["user"], plans[i]["permission"], "|", before[i], "->", after[i], "|", mark)  # 전후 판정과 표시를 출력한다

print("--- 단계 3: 저장 - 회수 이력")                            # 단계 3 시작을 알리는 줄
count = save_log(log, "revocation_log.json")                     # 이력을 파일로 저장한다
saved = load_json("revocation_log.json", [])                     # 저장한 파일을 다시 읽어
print("저장", count, "건, 다시 읽은 건수", len(saved), "건, 첫 이력:", saved[0]["user"], saved[0]["permission"], saved[0]["result"])  # 건수와 첫 이력을 출력한다
