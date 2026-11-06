from tuning import load_table, count_false_alarms, apply_exception, count_real_removed, find_removed_users, ALERTS_PATH  # 방금 만든 함수를 불러온다

alerts = load_table(ALERTS_PATH)                      # 알림 파일을 표로 읽는다
alert_count = len(alerts)                             # 알림이 모두 몇 개인지 센다
false_alarm_count_before = count_false_alarms(alerts)  # 예외 규칙을 적용하기 전의 오탐 수를 센다
print("--- 단계 1: 예외 규칙을 적용하기 전 ---")      # 단계 1 제목
print("알림 수:", alert_count)                        # 적용 전 알림 수를 출력한다
print("오탐 수:", false_alarm_count_before)           # 적용 전 오탐 수를 출력한다

removed_alerts, kept_alerts = apply_exception(alerts)  # 믿는 IP 에서 온 IP 규칙 알림을 빼낸다
removed_count = len(removed_alerts)                   # 빠진 알림이 몇 개인지 센다
print("--- 단계 2: 예외 규칙으로 빠진 알림 ---")      # 단계 2 제목
print("빠진 알림 수:", removed_count)                 # 빠진 알림 수를 출력한다
removed_list = removed_alerts.to_dict("records")      # 표를 알림 딕셔너리 리스트로 바꾼다
for alert in removed_list:                            # 빠진 알림을 하나씩 꺼낸다
    print("빠진 알림:", alert["id"], alert["rule"], alert["user"], alert["ip"])  # 번호 · 규칙 · 사용자 · IP 를 출력한다
removed_users = find_removed_users(removed_alerts)    # 빠진 알림에 나온 사용자를 중복 없이 모은다
print("빠진 알림의 사용자:", removed_users)           # 사용자 이름을 출력한다

kept_count = len(kept_alerts)                         # 남은 알림이 몇 개인지 센다
false_alarm_count_after = count_false_alarms(kept_alerts)  # 적용 후의 오탐 수를 센다
print("--- 단계 3: 예외 규칙을 적용한 뒤 ---")        # 단계 3 제목
print("알림 수:", kept_count)                         # 적용 후 알림 수를 출력한다
print("오탐 수:", false_alarm_count_after)            # 적용 후 오탐 수를 출력한다

real_removed_count = count_real_removed(removed_alerts)  # 빠진 알림 중 진짜 문제였던 것을 센다
print("--- 단계 4: 빠진 알림 중 진짜 문제였던 것 ---")  # 단계 4 제목
print("진짜 문제였던 알림 수:", real_removed_count)   # 0 이면 진짜 문제는 지워지지 않은 것이다
