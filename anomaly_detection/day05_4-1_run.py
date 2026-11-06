from final_check import load_table, apply_exception, merge_alerts, evaluate, make_summary, ALERTS_PATH, LOGIN_ALERTS_PATH, PROBLEMS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
login_alerts = load_table(LOGIN_ALERTS_PATH)          # 로그인 규칙 알림 파일을 표로 읽는다
problems = load_table(PROBLEMS_PATH)                  # 진짜 문제 파일을 표로 읽는다

removed_alerts, kept_alerts = apply_exception(alerts)  # 믿는 IP 예외 규칙을 적용한다
removed_count = len(removed_alerts)                   # 빠진 알림이 몇 개인지 센다
kept_count = len(kept_alerts)                         # 남은 알림이 몇 개인지 센다
print("--- 단계 1: 믿는 IP 예외 규칙 적용 ---")       # 단계 1 제목
print("빠진 알림 수:", removed_count)                 # 빠진 알림 수를 출력한다
print("남은 알림 수:", kept_count)                    # 남은 알림 수를 출력한다

all_alerts = merge_alerts(kept_alerts, login_alerts)  # 로그인 규칙의 알림을 합친다
all_count = len(all_alerts)                           # 합친 알림이 몇 개인지 센다
print("--- 단계 2: 로그인 규칙의 알림 합치기 ---")    # 단계 2 제목
print("합친 뒤 알림 수:", all_count)                  # 합친 알림 수를 출력한다

false_alarm_count, missed_problems = evaluate(all_alerts, problems)  # 오탐 수와 놓친 문제를 구한다
print("--- 단계 3: 합친 알림의 오탐 ---")             # 단계 3 제목
print("오탐 수:", false_alarm_count)                  # 오탐 수를 출력한다

missed_count = len(missed_problems)                   # 놓친 문제가 몇 개인지 센다
print("--- 단계 4: 아직 놓친 진짜 문제 ---")          # 단계 4 제목
print("미탐 수:", missed_count)                       # 미탐 수를 출력한다
missed_list = missed_problems.to_dict("records")      # 표를 문제 딕셔너리 리스트로 바꾼다
for problem in missed_list:                           # 놓친 문제를 하나씩 꺼낸다
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])  # 문제 번호 · 대상 · 내용을 출력한다

summary = make_summary(all_count, false_alarm_count, missed_count)  # 결과를 한 문장으로 만든다
print("--- 단계 5: 한 문장 요약 ---")                 # 단계 5 제목
print(summary)                                        # 요약 문장을 출력한다
