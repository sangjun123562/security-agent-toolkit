from normalize_json_csv import load_server, load_saas  # 방금 만든 파일 읽기 함수를 불러온다

server_events = load_server("server_log.jsonl")     # 판정 서버 로그를 공통 이벤트로 바꾼다
saas_events = load_saas("saas_events.csv")          # SaaS 로그를 공통 이벤트로 바꾼다

server_count = len(server_events)                   # 판정 서버 이벤트 수를 센다
server_counts = {}                                  # 결과별 횟수를 담을 딕셔너리
for event in server_events:                         # 이벤트를 하나씩 꺼낸다
    result = event["result"]                        # 그 이벤트의 결과
    server_counts[result] = server_counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 1: 판정 서버 이벤트", server_count, "개")  # 단계 1 시작을 알리는 줄
print(server_counts)                                # 성공 · 실패별 개수를 출력한다

saas_count = len(saas_events)                       # SaaS 이벤트 수를 센다
saas_counts = {}                                    # 결과별 횟수를 담을 딕셔너리
for event in saas_events:                           # 이벤트를 하나씩 꺼낸다
    result = event["result"]                        # 그 이벤트의 결과
    saas_counts[result] = saas_counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 2: SaaS 이벤트", saas_count, "개")  # 단계 2 시작을 알리는 줄
print(saas_counts)                                  # 성공 · 실패별 개수를 출력한다

first_server = server_events[0]                     # 판정 서버 첫 이벤트를 꺼낸다
first_saas = saas_events[0]                         # SaaS 첫 이벤트를 꺼낸다
print("--- 단계 3: 각 로그의 첫 이벤트")            # 단계 3 시작을 알리는 줄
print(first_server)                                 # 판정 서버 첫 이벤트를 출력한다
print(first_saas)                                   # SaaS 첫 이벤트를 출력한다
