import pandas as pd                                                 # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                              # 읽을 정규화 이벤트 파일 이름
TYPE_ORDER = ["비정상 로그인", "비인가 접근", "기타 실패", "정상"]  # 결과를 보여 줄 유형 순서


def load_events(path):                                              # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                                     # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                                   # 이벤트 표를 리턴한다


def classify_event(action, result):                                 # 행동과 결과를 받는 함수
    """이벤트 하나의 유형 이름을 정한다.
    알림이 온 이벤트가 어떤 유형의 일인지 담당자가 바로 알 수 있게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. if 로 시작한다: result 가 "실패" 이고(and) action 이 "POST /login" 과 같으면
    if result == "실패" and action == "POST /login":
    # 2.   그 if 안쪽에서 "비정상 로그인" 을 리턴한다
        return "비정상 로그인"
    # 3. if 로 시작한다: result 가 "실패" 이고(and) "/admin" in action 이 True 이면
    if result == "실패" and "/admin" in action:
    # 4.   그 if 안쪽에서 "비인가 접근" 을 리턴한다
        return "비인가 접근"
    if result == "실패":                                            # 위 두 유형이 아닌 실패이면
        return "기타 실패"                                          # 기타 실패로 분류한다
    return "정상"                                                   # 실패가 아니면 정상이다


def count_types(events):                                            # 이벤트 표를 받는 함수
    """유형별 이벤트 수를 {유형: 개수} 딕셔너리로 센다.
    어떤 유형의 일이 얼마나 있는지 한눈에 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. events.to_dict("records") 로 표를 딕셔너리 리스트로 바꿔 event_list 에 담는다
    event_list = events.to_dict("records")
    counts = {}                                                     # 유형별 횟수를 담을 딕셔너리
    for event in event_list:                                        # 이벤트를 하나씩 꺼낸다
        action = event["action"]                                    # 그 이벤트의 행동
        result = event["result"]                                    # 그 이벤트의 결과
        type_name = classify_event(action, result)                  # 유형 이름을 정한다
        counts[type_name] = counts.get(type_name, 0) + 1            # counts 에 이 유형이 있으면 그 값을, 없으면 0 을 꺼내 1 을 더하고 다시 저장한다
    return counts                                                   # 유형별 횟수를 리턴한다
