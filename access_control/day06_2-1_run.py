from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from checklist import TIME_FORMAT, load_state, run_checklist     # 방금 만든 점검 함수를 불러온다

NOW = datetime.strptime("2026-11-02 10:00", TIME_FORMAT)         # 점검하는 시각을 2026-11-02 10:00 으로 고정한다
state = load_state("config/week_state.json")                     # 점검할 데이터 파일을 읽는다
users = state["users"]                                           # 사용자 딕셔너리를 꺼낸다
exceptions = state["exceptions"]                                 # 예외 리스트를 꺼낸다

user_count = len(users)                                          # 사용자가 몇 명인지 센다
exception_count = len(exceptions)                                # 예외가 몇 개인지 센다
print("--- 단계 1: 점검 대상 - 사용자", user_count, "명 · 예외", exception_count, "개")  # 단계 1 시작을 알리는 줄
results = run_checklist(state, NOW)                              # 점검 세 가지를 실행한다
print("--- 단계 2: 점검 결과")                                      # 단계 2 시작을 알리는 줄
for result in results:                                           # 점검 결과를 하나씩 꺼낸다
    name = result["name"]                                        # 점검 이름을 꺼낸다
    problems = result["problems"]                                # 문제가 있는 사용자 · 예외 리스트를 꺼낸다
    if len(problems) == 0:                                       # 문제가 하나도 없으면
        status = "통과"                                           # 통과라고 적는다
    else:                                                        # 문제가 있으면
        status = "실패"                                           # 실패라고 적는다
    print(name, "|", status, "|", problems)                      # 점검 이름 | 결과 | 문제 리스트를 출력한다
