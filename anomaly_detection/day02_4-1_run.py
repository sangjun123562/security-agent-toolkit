from normalize import load_web, merge_events, count_by_source, count_missing, save_events, EVENTS_PATH  # 방금 만든 함수를 불러온다
from normalize_json_csv import load_server, load_saas  # 판정 서버 · SaaS 로그 읽기 함수를 불러온다
import json                                           # 저장한 파일을 다시 읽을 수 있게 불러온다


def show_user(events, name):                          # 이벤트 리스트와 사용자 이름을 받는 함수
    """한 사용자의 이벤트를 시각 · 소스 · 행동 · 결과로 한 줄씩 출력한다.
    같은 사용자가 여러 로그에서 한 일을 시간순으로 볼 때 쓴다.
    """
    for event in events:                              # 이벤트를 하나씩 꺼낸다
        if event["user"] == name:                     # 그 사용자의 이벤트이면
            time_text = event["time"]                 # 시각
            source = event["source"]                  # 소스
            action = event["action"]                  # 행동
            result = event["result"]                  # 결과
            print(time_text, source, action, result)  # 한 줄로 출력한다


web = load_web("access_sample.log")                   # 웹 서버 로그를 공통 이벤트로 바꾼다
server = load_server("server_log.jsonl")              # 판정 서버 로그를 공통 이벤트로 바꾼다
saas = load_saas("saas_events.csv")                   # SaaS 로그를 공통 이벤트로 바꾼다
events = merge_events(web, server, saas)              # 하나로 합쳐 시간순으로 정렬한다

source_counts = count_by_source(events)               # 소스별 개수를 센다
print("--- 단계 1: 소스별 이벤트 수")                  # 단계 1 시작을 알리는 줄
print(source_counts)                                   # 소스별 개수를 출력한다

user_missing = count_missing(events, "user")           # user 가 비어 있는 이벤트 수를 센다
ip_missing = count_missing(events, "ip")               # ip 가 비어 있는 이벤트 수를 센다
print("--- 단계 2: 값이 None 인 이벤트 수")            # 단계 2 시작을 알리는 줄
print("user 가 비어 있는 이벤트", user_missing, "개")  # user 가 비어 있는 개수를 출력한다
print("ip 가 비어 있는 이벤트", ip_missing, "개")      # ip 가 비어 있는 개수를 출력한다

print("--- 단계 3: gaeun 의 이벤트를 시간순으로")     # 단계 3 시작을 알리는 줄
show_user(events, "gaeun")                            # gaeun 의 이벤트를 출력한다

save_events(events, EVENTS_PATH)                      # 이벤트를 JSON 파일로 저장한다
with open(EVENTS_PATH, encoding="utf-8") as events_file:  # 저장한 파일을 다시 연다
    saved_events = json.load(events_file)             # JSON 을 리스트로 읽는다
saved_count = len(saved_events)                       # 저장된 이벤트 수를 센다
print("--- 단계 4: 저장한 파일", EVENTS_PATH)         # 단계 4 시작을 알리는 줄
print("저장된 이벤트", saved_count, "개")             # 저장된 이벤트 수를 출력한다
