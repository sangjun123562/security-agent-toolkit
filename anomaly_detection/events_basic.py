import pandas as pd                     # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"  # 읽을 정규화 이벤트 파일 이름


def load_events(path):                  # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. pd.read_json 으로 path 의 파일을 읽어 events 에 담는다
    events = pd.read_json(path)
    return events                       # 표를 리턴한다


def describe_events(events):            # 표를 받는 함수
    """표의 크기와 앞 시각 3개를 구한다.
    새 파일을 받았을 때 내용이 제대로 들어 있는지 확인하는 데 쓴다.
    """
    shape = events.shape                # 표의 크기 (행 수, 열 수) — 미리 채운 줄
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. events 의 "time" 열을 꺼내 times 에 담는다 (events["time"])
    times = events["time"]
    first_times = times.head(3)         # 그 열의 앞 3개만 남긴다 — 미리 채운 줄
    return shape, first_times           # 크기와 처음 3개를 리턴한다


def pick_failed(events):                # 표를 받는 함수
    """실패한 이벤트만 골라 새 표로 만든다.
    무엇이 잘못됐는지 조사할 때 성공한 이벤트는 빼고 보는 데 쓴다.
    """
    results = events["result"]          # result 열 하나를 꺼낸다
    is_fail = results == "실패"         # 행마다 실패면 True, 아니면 False
    failed = events[is_fail]            # True 인 행만 남긴다
    return failed                       # 실패한 행만 담은 표를 리턴한다


def count_values(table, column):        # 표와 열 이름을 받는 함수
    """한 열의 값별 개수를 센다.
    소스별 · 결과별 · 사용자별로 몇 개인지 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. table 의 column 열을 꺼내 values 에 담는다
    values = table[column]
    # 4. values 에서 값별 개수를 value_counts() 로 세어 counts 에 담는다
    counts = values.value_counts()
    return counts                       # 값별 개수를 리턴한다
