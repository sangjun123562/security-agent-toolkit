import pandas as pd                     # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"  # 읽을 정규화 이벤트 파일 이름
FAILED_PATH = "failed_events.csv"       # 실패한 이벤트를 저장할 파일 이름


def load_events(path):                  # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)         # 파일을 읽어 표로 만든다
    return events                       # 표를 리턴한다


def pick_failed(events):                # 표를 받는 함수
    """실패한 이벤트만 골라 새 표로 만든다.
    무엇이 잘못됐는지 조사할 때 성공한 이벤트는 빼고 보는 데 쓴다.
    """
    results = events["result"]          # result 열 하나를 꺼낸다
    is_fail = results == "실패"         # 행마다 실패면 True, 아니면 False
    failed = events[is_fail]            # True 인 행만 남긴다
    return failed                       # 실패한 행만 담은 표를 리턴한다


def count_by_user(failed):              # 실패한 이벤트 표를 받는 함수
    """실패 횟수를 사용자별로 세어 많은 순서로 리턴한다.
    누구에게 실패가 많이 났는지 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. failed 를 "user" 열 기준으로 묶어(groupby) grouped 에 담는다
    grouped = failed.groupby("user")
    # 2. grouped.size() 의 결과를 counts 에 담는다
    counts = grouped.size()
    # 3. counts 를 큰 값부터 정렬해(sort_values, ascending=False) sorted_counts 에 담는다
    sorted_counts = counts.sort_values(ascending=False)
    return sorted_counts                # 많은 순서로 정렬한 개수를 리턴한다


def add_hour(events):                   # 표를 받는 함수
    """time 열을 시각으로 바꾸고 「시」만 담은 hour 열을 더한다.
    시간대별로 세기 전에 쓴다.
    """
    times = pd.to_datetime(events["time"])  # 문자열 시각을 시각 값으로 바꾼다
    hours = times.dt.hour               # 시각에서 「시」(0~23)만 꺼낸다
    events["hour"] = hours              # hour 라는 새 열로 표에 더한다
    return events                       # hour 열이 더해진 표를 리턴한다


def count_by_hour(failed):              # 실패한 이벤트 표를 받는 함수
    """실패 횟수를 시간대별로 센다.
    실패가 몇 시에 많이 났는지 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. failed 를 "hour" 열 기준으로 묶어 grouped 에 담는다
    grouped = failed.groupby("hour")
    # 5. grouped.size() 의 결과를 counts 에 담는다
    counts = grouped.size()
    return counts                       # 시간대별 개수를 리턴한다


def save_failed(failed, path):          # 표와 저장할 파일 이름을 받는 함수
    """실패한 이벤트 표를 CSV 파일로 저장한다.
    담당자가 엑셀로 근거를 확인하게 할 때 쓴다.
    """
    failed.to_csv(path, index=False)    # 표를 CSV 파일로 저장한다 — 미리 채운 줄
