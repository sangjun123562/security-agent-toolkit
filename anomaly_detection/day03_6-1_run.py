import json                                                                          # 저장한 파일을 다시 읽기 위해 json 을 불러온다
from login_detection import load_events, pick_login_failures, count_by_ip, pick_alert_ips, EVENTS_PATH, LOGIN_LIMIT  # 오전 3교시에 만든 함수를 불러온다
from traffic_detection import add_minute_column, count_web_per_minute, make_traffic_limit, pick_spike_minutes, TRAFFIC_PATH, SPIKE_MULTIPLE  # 5교시에 만든 함수를 불러온다
from alerts import make_login_alerts, make_traffic_alerts, save_alerts, ALERTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                                    # 이벤트 파일을 표로 읽는다
login_failures = pick_login_failures(events)                                         # 로그인 실패 이벤트만 골라낸다
login_counts = count_by_ip(login_failures)                                           # 주소별로 실패 횟수를 센다
alert_ips = pick_alert_ips(login_counts, LOGIN_LIMIT)                                # 알림 기준 이상인 주소만 고른다
login_alerts = make_login_alerts(alert_ips)                                          # 주소마다 알림 한 건을 만든다
login_alert_count = len(login_alerts)                                                # 로그인 실패 알림이 몇 건인지 센다
print("--- 단계 1: 로그인 실패 알림", login_alert_count, "건")                       # 단계 1 시작을 알리는 줄과 건수

events = add_minute_column(events)                                                   # 시각에서 초를 버린 minute 열을 붙인다
minute_counts = count_web_per_minute(events)                                         # 웹 서버 요청을 분마다 센다
limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)                             # 급증 기준을 정한다
spike_minutes = pick_spike_minutes(minute_counts, limit)                             # 요청이 급증한 분만 고른다
traffic_alerts = make_traffic_alerts(spike_minutes)                                  # 분마다 알림 한 건을 만든다
traffic_alert_count = len(traffic_alerts)                                            # 트래픽 급증 알림이 몇 건인지 센다
print("--- 단계 2: 트래픽 급증 알림", traffic_alert_count, "건")                     # 단계 2 시작을 알리는 줄과 건수

all_alerts = login_alerts + traffic_alerts                                           # 두 리스트를 이어 붙여 알림 하나의 리스트로 모은다
saved_count = save_alerts(all_alerts, ALERTS_PATH)                                   # 모은 알림을 파일에 저장하고 저장한 건수를 받는다
print("--- 단계 3:", ALERTS_PATH, "에 알림", saved_count, "건 저장")                 # 단계 3 시작을 알리는 줄과 건수

with open(ALERTS_PATH, encoding="utf-8") as file:                                    # 저장한 파일을 읽기 모드로 연다
    saved_alerts = json.load(file)                                                   # JSON 을 파이썬 리스트로 읽는다
print("--- 단계 4: 저장된 알림")                                                     # 단계 4 시작을 알리는 줄
for alert in saved_alerts:                                                           # 알림을 하나씩 꺼낸다
    print(alert)                                                                     # 알림 한 건을 출력한다
