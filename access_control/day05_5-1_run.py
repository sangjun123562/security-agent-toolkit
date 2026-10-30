from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from conditional import load_rules, evaluate_conditional         # 방금 만든 조건 판정 함수를 불러온다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 문자열의 형식
RULES = load_rules("config/conditions.json")                     # 조건 파일을 읽는다

CASES = [                                                        # 시험할 요청 여덟 건. (사용자, 자원, 행위, 접속 위치, 시각)
    ("seoyeon", "SALES", "QUERY", "office", "2026-10-30 10:00"),     # 1. 조건이 없는 조회 권한
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 09:00"),    # 2. 시작 시각 정각, 사내망
    ("seoyeon", "SALES", "CHANGE", "office", "2026-10-30 18:00"),    # 3. 끝 시각 정각
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 10:00"),  # 4. 업무 시간 안, 외부 접속
    ("seoyeon", "SALES", "CHANGE", "external", "2026-10-30 22:00"),  # 5. 시간도 위치도 어긋남
    ("junho", "SETTLE", "QUERY", "vpn", "2026-10-30 19:30"),         # 6. 정산 조회는 20시까지
    ("gaeun", "ACCOUNT", "CHANGE", "vpn", "2026-10-30 10:00"),       # 7. 계정 변경은 사내망만
    ("dami", "SALES", "QUERY", "office", "2026-10-30 10:00"),        # 8. 퇴사한 사용자
]

print("--- 단계 1: 판정 - 요청", len(CASES), "건")                  # 단계 1 시작을 알리는 줄
number = 0                                                       # 요청 번호를 0 으로 시작한다
for user, resource, action, network, time_text in CASES:         # 요청을 하나씩 꺼낸다
    number += 1                                                  # 요청 번호를 1 늘린다
    now = datetime.strptime(time_text, TIME_FORMAT)              # 시각 문자열을 시각으로 바꾼다
    ok, reason = evaluate_conditional(user, resource, action, network, now, RULES)   # 조건까지 판정한다
    if ok:                                                       # 허용이면
        result = "허용"                                           # 허용이라고 적는다
    else:                                                        # 거부이면
        result = "거부"                                           # 거부라고 적는다
    permission = f"{resource}:{action}"                          # 권한 문자열을 만든다
    time_text = now.strftime("%H:%M")                            # 시각을 「시:분」 문자열로 바꾼다
    verdict = f"{result}({reason})"                              # 결과와 이유를 합친다
    print(number, user, permission, network, time_text, "->", verdict)  # 번호 · 요청과 결과를 출력한다

print("--- 단계 2: 확인 - 조건 파일에 적힌 조건")                      # 단계 2 시작을 알리는 줄
for rule in RULES:                                               # 조건을 하나씩 꺼낸다
    hours = rule["hours"]                                        # 허용 시간대 [시작 시, 끝 시]
    hours_text = f"{hours[0]}시부터 {hours[1]}시 전까지"                # 시간대를 문자열로 만든다
    networks_text = ", ".join(rule["networks"])                  # 허용 접속 위치를 쉼표로 이어 붙인다
    print(rule["permission"], "|", hours_text, "|", networks_text)  # 권한 | 시간대 | 허용 접속 위치를 출력한다
