from access_detection import load_events, pick_server_failures, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins      # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures      # 4교시 함수를 불러온다
from correlation import make_ip_user_map, attach_user_to_web, build_timeline, find_chains, WINDOW_MINUTES  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                      # 이벤트 파일을 표로 읽는다
server_failures = pick_server_failures(events)         # 판정 서버 실패 이벤트를 고른다
server_part = server_failures                           # 서버 실패 이벤트 전체를 쓴다
saas_part = pick_saas(events)                          # SaaS 이벤트를 고른다
logins = pick_logins(saas_part)                        # 로그인 이벤트를 고른다
ip_user = make_ip_user_map(logins)                     # 성공한 로그인에서 IP → 사용자 딕셔너리를 만든다

web_failures = pick_web_failures(events)               # 웹 실패 이벤트를 고른다
web_part = attach_user_to_web(web_failures, ip_user)   # 사용자를 아는 웹 이벤트에 user 열을 붙인다
web_count = len(web_part)                              # 그 이벤트가 몇 개인지 센다
print("--- 단계 1: IP 로 사용자를 알 수 있는 웹 실패 이벤트", web_count, "개")  # 단계 1 시작을 알리는 줄과 개수

timeline = build_timeline(server_part, saas_part, web_part)  # 세 로그를 합쳐 사용자 · 시각 순으로 정렬한다
timeline_count = len(timeline)                         # 합친 이벤트가 몇 개인지 센다
print("--- 단계 2: 사용자별로 시간순으로 놓은 이벤트", timeline_count, "개")  # 단계 2 시작을 알리는 줄과 개수
print("gaeun 의 이벤트 (시각 · 로그 · 행동 · 결과)")  # 아래 줄들이 gaeun 의 이벤트라는 것을 알리는 줄

users = timeline["user"]                               # user 열만 꺼낸다
is_gaeun = users == "gaeun"                            # 행마다 gaeun 인지 비교해 True 또는 False 를 만든다
gaeun_rows = timeline[is_gaeun]                        # True 인 행만 골라 gaeun 의 이벤트 표를 만든다
gaeun_list = gaeun_rows.to_dict("records")             # 표를 이벤트 딕셔너리 리스트로 바꾼다
for event in gaeun_list:                               # gaeun 의 이벤트를 시간순으로 하나씩 꺼낸다
    print(event["time"], event["source"], event["action"], event["result"])  # 시각 · 로그 · 행동 · 결과를 출력한다

chains, not_chained = find_chains(timeline)            # 연결된 사건과 연결되지 않은 사용자를 찾는다
print("--- 단계 3:", WINDOW_MINUTES, "분 안에 서로 다른 로그로 연결된 사건")  # 단계 3 시작을 알리는 줄
for chain in chains:                                   # 연결된 사건을 하나씩 꺼낸다
    print(chain)                                       # 사건을 출력한다

print("--- 단계 4: 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자")  # 단계 4 시작을 알리는 줄
for item in not_chained:                               # 연결되지 않은 사용자를 하나씩 꺼낸다
    print(item)                                        # 사용자 · 로그 종류 수 · 첫 이벤트부터 마지막 이벤트까지의 분을 출력한다
