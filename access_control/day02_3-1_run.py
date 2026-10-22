import json                                                      # 사용자 파일을 읽는 데 쓴다
from datetime import datetime                                    # 지금 시각을 만드는 데 쓴다
from exception_policy import find_exception, EXCEPTIONS, TIME_FORMAT   # 판정 함수 · 예외 목록 · 시각 형식을 불러온다

NOW = datetime.strptime("2026-10-22 14:00", TIME_FORMAT)         # 오늘 실습의 지금 시각(고정)

CHECKS = [                                                       # 단계 1 에서 판정할 (사용자, "자원:행위") 목록
    ("seoyeon", "SETTLE:QUERY"),                                 # 오늘 18시까지 예외
    ("junho", "SALES:CHANGE"),                                   # 10/20 에 끝난 예외
    ("dami", "SALES:QUERY"),                                     # 퇴사자에게 남은 예외
    ("batch-night", "SALES:QUERY"),                              # 내일 아침까지 예외
    ("gaeun", "SETTLE:QUERY"),                                   # 오늘 12시에 끝난 예외
    ("seoyeon", "ACCOUNT:CHANGE"),                               # 예외가 없는 권한
]

print("--- 단계 1: 판정 - 지금 유효한 예외가 있나")                 # 단계 1 시작을 알리는 줄
for user, permission in CHECKS:                                  # 하나씩 꺼낸다
    print(user, permission, "->", find_exception(user, permission, NOW))   # 사용자 권한 -> (결과, 번호) 를 출력한다

with open("config/users.json", encoding="utf-8") as f:           # 어제 만든 사용자 파일을 연다
    USERS = json.load(f)                                         # 사용자 → 정보 딕셔너리로 읽는다

print("--- 단계 2: 점검 - 예외 목록에서 회수할 것")                 # 단계 2 시작을 알리는 줄
for exc in EXCEPTIONS:                                           # 예외를 하나씩 꺼낸다
    expires = datetime.strptime(exc["expires"], TIME_FORMAT)     # 만료 시각을 시각으로 바꾼다
    if NOW >= expires:                                           # 이미 만료됐으면
        print("[회수] 만료됨", exc["id"], exc["user"], exc["permission"], exc["expires"])   # 만료된 예외를 출력한다
    elif not USERS[exc["user"]]["employed"]:                     # 만료 전인데 재직 중이 아니면(`not` 은 참 · 거짓을 뒤집음)
        print("[회수] 퇴사자", exc["id"], exc["user"], exc["permission"], exc["expires"])   # 퇴사자의 예외를 출력한다
    else:                                                        # 둘 다 아니면
        print("[유지]", exc["id"], exc["user"], exc["permission"], exc["expires"])   # 유지할 예외를 출력한다
