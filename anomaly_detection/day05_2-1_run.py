from evaluation import load_table, pick_real_alerts, find_false_alarms, find_missed, count_real_alerts, ALERTS_PATH, PROBLEMS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
problems = load_table(PROBLEMS_PATH)                  # 진짜 문제 파일을 표로 읽는다
alert_count = len(alerts)                             # 알림이 모두 몇 개인지 센다
print("--- 단계 1: 알림 전체 ---")                    # 단계 1 제목
print("알림 수:", alert_count)                        # 알림 수를 출력한다

real_alerts = pick_real_alerts(alerts)                # 진짜 문제였던 알림만 골라낸다
real_alert_count = count_real_alerts(alerts)          # 진짜 문제였던 알림이 몇 개인지 센다
print("--- 단계 2: 진짜 문제였던 알림 (맞게 찾은 알림) ---")  # 단계 2 제목
print("진짜 문제였던 알림 수:", real_alert_count)     # 맞게 찾은 알림 수를 출력한다

false_alarms, false_alarm_rule_counts = find_false_alarms(alerts)  # 오탐과 규칙별 오탐 개수를 구한다
false_alarm_count = len(false_alarms)                 # 오탐이 몇 개인지 센다
print("--- 단계 3: 오탐 (문제가 아닌데 난 알림) ---")  # 단계 3 제목
print("오탐 수:", false_alarm_count)                  # 오탐 수를 출력한다
print("오탐이 난 규칙과 오탐 수:")                    # 아래 표가 무엇인지 알리는 줄
print(false_alarm_rule_counts)                        # 규칙마다 오탐이 몇 개인지 출력한다

missed_problems = find_missed(problems, real_alerts)  # 알림이 나지 않은 진짜 문제를 찾는다
missed_count = len(missed_problems)                   # 놓친 문제가 몇 개인지 센다
print("--- 단계 4: 미탐 (알림이 나지 않은 진짜 문제) ---")  # 단계 4 제목
print("미탐 수:", missed_count)                       # 미탐 수를 출력한다
missed_list = missed_problems.to_dict("records")      # 표를 문제 딕셔너리 리스트로 바꾼다
for problem in missed_list:                           # 놓친 문제를 하나씩 꺼낸다
    print("놓친 문제:", problem["id"], problem["who"], problem["what"])  # 문제 번호 · 대상 · 내용을 출력한다
