from login_detection import load_events, pick_login_failures, count_by_ip, pick_alert_ips, EVENTS_PATH, LOGIN_LIMIT  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                              # 이벤트 파일을 표로 읽는다
login_failures = pick_login_failures(events)                   # 로그인 실패 이벤트만 골라낸다
failure_count = len(login_failures)                            # 로그인 실패가 모두 몇 개인지 센다
print("--- 단계 1: 로그인 실패 이벤트", failure_count, "개")   # 단계 1 시작을 알리는 줄과 개수

counts = count_by_ip(login_failures)                           # 주소별로 실패 횟수를 센다
print("--- 단계 2: 주소별 로그인 실패 횟수")                   # 단계 2 시작을 알리는 줄
print(counts)                                                  # 주소별 횟수를 출력한다

alert_ips = pick_alert_ips(counts, LOGIN_LIMIT)                # 알림 기준 이상인 주소만 고른다
print("--- 단계 3: 알림 기준", LOGIN_LIMIT, "번 이상인 주소")  # 단계 3 시작을 알리는 줄과 알림 기준
print(alert_ips)                                               # 알림을 보낼 주소를 출력한다
