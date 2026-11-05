from access_detection import load_events, pick_server_failures, pick_suspicious, judge_failure, EVENTS_PATH  # 방금 만든 함수를 불러온다

LABELS = {"퇴사한 계정": "퇴사한 계정", "권한 없음": "권한 없음", "허용": "규칙은 허용인데 서버가 거절"}  # 판정 이유를 담당자가 읽는 말로 바꾼다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
server_failures = pick_server_failures(events)               # 판정 서버의 실패 이벤트만 골라낸다
failure_count = len(server_failures)                         # 서버 실패가 모두 몇 개인지 센다
print("--- 단계 1: 판정 서버의 실패 이벤트", failure_count, "개")  # 단계 1 시작을 알리는 줄과 개수

suspicious = pick_suspicious(server_failures)                # 먼저 확인할 실패 이벤트만 골라낸다
suspicious_count = len(suspicious)                           # 먼저 확인할 이벤트가 몇 개인지 센다
print("--- 단계 2: 먼저 확인할 실패 이벤트", suspicious_count, "개")  # 단계 2 시작을 알리는 줄과 개수

suspicious_list = suspicious.to_dict("records")              # 표를 이벤트 딕셔너리 리스트로 바꾼다
judged_list = []                                             # 판정 결과를 담을 빈 리스트
for event in suspicious_list:                                # 이벤트를 하나씩 꺼낸다
    reason, priority = judge_failure(event["user"], event["action"])  # 3과목 규칙으로 다시 판정한다
    judged = {"priority": priority, "reason": reason, "event": event}  # 순서 · 이유 · 이벤트를 딕셔너리로 만든다
    judged_list.append(judged)                               # 판정 결과를 리스트에 추가한다

print("--- 단계 3: 우선순위")                            # 단계 3 시작을 알리는 줄
for priority in [1, 2, 3]:                                   # 우선순위대로 꺼낸다
    for judged in judged_list:                               # 판정 결과를 하나씩 꺼낸다
        if judged["priority"] == priority:                   # 지금 순서의 결과이면
            event = judged["event"]                          # 그 이벤트를 꺼낸다
            label = LABELS.get(judged["reason"], judged["reason"])  # 담당자가 읽는 말로 바꾼다
            print(priority, label, event["user"], event["action"], event["time"])  # 순서 · 이유 · 사용자 · 행동 · 시각을 출력한다
