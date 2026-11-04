from classify import load_events, count_types, EVENTS_PATH, TYPE_ORDER  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                                       # 이벤트 파일을 표로 읽는다
counts = count_types(events)                                            # 유형별로 센다
print("--- 단계 1: 유형별 이벤트 수")                                   # 단계 1 시작을 알리는 줄
for type_name in TYPE_ORDER:                                            # 정해 둔 유형 순서대로 꺼낸다
    count = counts.get(type_name, 0)                                    # 그 유형의 개수(없으면 0)
    print(type_name, count)                                             # 유형과 개수를 출력한다

values = counts.values()                                                # 유형별 개수만 꺼낸다
total = sum(values)                                                     # 모든 유형의 개수를 더한다
print("--- 단계 2: 전체 이벤트", total, "개")                           # 단계 2 시작을 알리는 줄과 전체 개수
