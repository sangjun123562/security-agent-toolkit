from events_basic import load_events, describe_events, pick_failed, count_values, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                   # 이벤트 파일을 표로 읽는다
shape, first_times = describe_events(events)        # 표 크기와 time 열의 처음 3개를 구한다
print("--- 단계 1: 표 크기(행 수, 열 수)와 처음 3개 시각")  # 단계 1 시작을 알리는 줄
print(shape)                                        # (행 수, 열 수)를 출력한다
for time_text in first_times:                       # 처음 3개 시각을 하나씩 꺼낸다
    print(time_text)                                # 시각 하나를 한 줄에 출력한다(모두 3줄)

result_counts = count_values(events, "result")      # result 열의 값별 개수를 센다
print("--- 단계 2: 성공 · 실패별 개수")             # 단계 2 시작을 알리는 줄
print(result_counts)                                # 성공 · 실패 개수를 출력한다

failed = pick_failed(events)                        # 실패한 이벤트만 골라낸다
failed_count = len(failed)                          # 실패한 이벤트가 몇 개인지 센다
source_counts = count_values(failed, "source")      # 실패한 이벤트의 소스별 개수를 센다
print("--- 단계 3: 실패한 이벤트", failed_count, "개의 소스별 개수")  # 단계 3 시작을 알리는 줄
print(source_counts)                                # 소스별 개수를 출력한다

all_source_counts = count_values(events, "source")  # 전체 이벤트의 소스별 개수를 센다
print("--- 단계 4: 전체 이벤트의 소스별 개수")      # 단계 4 시작을 알리는 줄
print(all_source_counts)                            # 소스별 전체 개수를 출력한다
