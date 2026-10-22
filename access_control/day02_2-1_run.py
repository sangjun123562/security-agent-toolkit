from rbac import USERS, check_permission                         # 어제의 사용자 딕셔너리와 판정 함수를 불러온다
from role_admin import assign_role, revoke_access                # 방금 만든 부여 · 회수 함수를 불러온다

CHECKS = [                                                       # 인사 변경 전후에 같은 요청을 판정해 볼 목록. (사용자, 자원, 행위)
    ("minsu", "SALES", "QUERY"),                                 # 오늘 입사하는 신입
    ("seoyeon", "SALES", "CHANGE"),                              # 재무로 옮기는 사람의 영업 실적 변경
    ("seoyeon", "SETTLE", "QUERY"),                              # 재무로 옮기는 사람의 정산 조회
    ("junho", "SETTLE", "QUERY"),                                # 오늘 퇴사하는 사람의 정산 조회
]


def run_checks(title):                                           # 제목을 받아 CHECKS 를 판정해 출력하는 함수
    print("---", title)                                          # 제목 줄을 출력한다
    for user, resource, action in CHECKS:                        # 요청을 하나씩 꺼낸다
        ok, reason = check_permission(user, resource, action)    # 어제의 판정 함수로 판정한다
        print(user, resource, action, "->", ok, reason)          # 사용자 · 자원 · 행위 -> 결과 이유 를 출력한다


run_checks("인사 변경 전")                                        # 변경 전 판정을 출력한다

print("--- 인사팀 통보 처리")                                      # 통보 처리 구간 시작을 알리는 줄
print("입사 minsu", assign_role(USERS, "minsu", "sales"))        # 신입 minsu 에게 영업 역할을 부여한다
print("입사 hana", assign_role(USERS, "hana", "salse"))          # 역할 이름 오타(salse)로 부여를 시도한다
print("hana 가 사용자에 들어갔나", "hana" in USERS)                # 오타라면 hana 가 들어가지 않아야 한다
print("이동 seoyeon", assign_role(USERS, "seoyeon", "finance"))  # seoyeon 의 역할을 재무로 바꾼다
print("퇴사 junho", revoke_access(USERS, "junho"))               # junho 의 접근을 회수한다
print("퇴사 ghost", revoke_access(USERS, "ghost"))               # 사용자 파일에 없는 이름의 회수를 시도한다

run_checks("인사 변경 후")                                        # 변경 후 판정을 출력한다
