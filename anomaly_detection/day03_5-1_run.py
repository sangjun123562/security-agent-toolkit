from traffic_detection import load_events, add_minute_column, count_web_per_minute, make_traffic_limit, pick_spike_minutes, EVENTS_PATH, TRAFFIC_PATH, SPIKE_MULTIPLE  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                                    # 이벤트 파일을 표로 읽는다
events = add_minute_column(events)                                                   # 시각에서 초를 버린 minute 열을 붙인다
times = events["time"]                                                               # time 열만 꺼낸다
minutes = events["minute"]                                                           # minute 열만 꺼낸다
first_times = times.head(3)                                                          # 시각의 처음 3개만 꺼낸다
first_minutes = minutes.head(3)                                                      # 분의 처음 3개만 꺼낸다
print("--- 단계 1: time 열과 minute 열의 처음 3개 비교")                             # 단계 1 시작을 알리는 줄
print(first_times)                                                                   # 처음 3개의 시각을 출력한다
print(first_minutes)                                                                 # 처음 3개의 분을 출력한다

counts = count_web_per_minute(events)                                                # 웹 서버 요청을 분마다 센다
print("--- 단계 2: 웹 서버의 분당 요청 수")                                          # 단계 2 시작을 알리는 줄
print(counts)                                                                        # 분마다 요청 수를 출력한다

limit = make_traffic_limit(TRAFFIC_PATH, SPIKE_MULTIPLE)                             # 지난 7일 평균으로 급증 기준을 정한다
print("--- 단계 3: 급증 기준(평소 평균의", SPIKE_MULTIPLE, "배)", limit, "번 이상")  # 단계 3 시작을 알리는 줄과 급증 기준

spike_minutes = pick_spike_minutes(counts, limit)                                    # 기준 이상인 분만 고른다
print("--- 단계 4: 요청이 급증한 분")                                                # 단계 4 시작을 알리는 줄
print(spike_minutes)                                                                 # 요청이 급증한 분과 요청 수를 출력한다
