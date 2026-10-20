SESSION_LIMITS = {"settlement": 30, "admin": 5}              # 자원별 세션 유지 시간(분). 위험한 자원일수록 짧다

SESSIONS = [                                                                                   # 지금 열려 있는 세션 7개
    {"id": 1, "user": "junho",   "resource": "settlement", "age": 10},                          # 접속한 지 10분 지난 정산 조회 세션
    {"id": 2, "user": "junho",   "resource": "settlement", "age": 26},                          # 26분 지난 정산 조회 세션
    {"id": 3, "user": "junho",   "resource": "settlement", "age": 41},                          # 41분 지난 정산 조회 세션
    {"id": 4, "user": "gaeun",   "resource": "admin",      "age": 3},                           # 3분 지난 권한 변경 세션
    {"id": 5, "user": "gaeun",   "resource": "admin",      "age": 4},                           # 4분 지난 권한 변경 세션
    {"id": 6, "user": "gaeun",   "resource": "admin",      "age": 12},                          # 12분 지난 권한 변경 세션
    {"id": 7, "user": "seoyeon", "resource": "settlement", "age": 30},                          # 30분 지난 정산 조회 세션
]

def session_state(session):                                  # 세션 하나의 상태를 판정하는 함수
    """세션이 '유지' '재인증' '종료' 중 어느 상태인지 리턴한다"""
    limit = SESSION_LIMITS[session["resource"]]              # 이 세션의 자원에 정해진 유지 시간(분)
    # 1. session["age"] 가 limit 보다 크면 "종료" 를 리턴한다   # ←
    if session["age"]>limit:
        return "종료"
    # 2. session["age"] 가 limit * 0.8 이상이면 "재인증" 을 리턴한다   # ←
    if session["age"]>=limit*0.8:
        return "재인증"
    
    return "유지"                                             # 위 둘이 아니면 유지한다

for session in SESSIONS:                                     # 세션을 하나씩 꺼낸다
    print(session["id"], session["user"], session["resource"], session["age"], "->", session_state(session))   # 번호 · 계정 · 자원 · 경과 분 -> 상태 를 출력한다
