from normalize_web import normalize_web         # 방금 만든 웹 서버 로그 정규화 함수를 불러온다

events = []                                     # 정규화한 이벤트를 모을 리스트
fail_count = 0                                  # 읽기 실패한 줄 수를 0 으로 시작한다
with open("access_sample.log", encoding="utf-8") as log_file:  # 샘플 로그 파일을 연다
    for line in log_file:                       # 파일에서 한 줄씩 꺼낸다
        event = normalize_web(line)             # 한 줄을 공통 이벤트로 바꾼다
        if event is None:                       # 깨진 줄이라 읽지 못했으면
            fail_count = fail_count + 1         # 읽기 실패한 줄 수를 1 늘린다
        else:                                   # 바꿨으면
            events.append(event)                # 이벤트 리스트에 추가한다

event_count = len(events)                       # 정규화한 이벤트 수를 센다
print("--- 단계 1: 정규화한 이벤트", event_count, "개 · 읽기 실패", fail_count, "줄")  # 단계 1 시작을 알리는 줄
first_event = events[0]                         # 첫 이벤트를 꺼낸다
print(first_event)                              # 첫 이벤트를 출력한다

first_failed = None                             # 처음 나오는 실패 이벤트를 담을 변수(아직 없음)
for event in events:                            # 이벤트를 하나씩 꺼낸다
    if event["result"] == "실패" and first_failed is None:  # 실패 이벤트이고 아직 담은 것이 없으면
        first_failed = event                    # 이 이벤트를 담는다
print("--- 단계 2: 처음 나오는 실패 이벤트")    # 단계 2 시작을 알리는 줄
print(first_failed)                             # 처음 나오는 실패 이벤트를 출력한다

counts = {}                                     # 결과별 횟수를 담을 딕셔너리
for event in events:                            # 이벤트를 하나씩 꺼낸다
    result = event["result"]                    # 그 이벤트의 결과
    counts[result] = counts.get(result, 0) + 1  # 그 결과의 횟수를 1 늘린다
print("--- 단계 3: 성공 · 실패별 개수")         # 단계 3 시작을 알리는 줄
print(counts)                                   # 성공 · 실패별 개수를 출력한다
