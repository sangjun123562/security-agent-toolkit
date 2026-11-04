import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
TRAFFIC_PATH = "baseline_traffic.csv"                 # 지난 7일 같은 시간대의 분당 요청 수 파일 이름
SPIKE_MULTIPLE = 3                                    # 평소 평균의 3배 이상이면 급증으로 본다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def add_minute_column(events):                        # 이벤트 표를 받는 함수
    """이벤트마다 시각에서 초를 버린 minute 열을 붙인다.
    분당 요청 수를 세기 전에 같은 분으로 그룹화할 기준을 만들 때 쓴다.
    """
    times = pd.to_datetime(events["time"])            # 문자열 시각을 시각 값으로 바꾼다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. times 에 .dt.floor("min") 을 붙여 초를 버린 시각을 minutes 에 담는다
    minutes = times.dt.floor("min")
    events["minute"] = minutes                        # 표에 minute 열을 붙인다 — 미리 채운 줄
    return events                                     # minute 열이 붙은 표를 리턴한다


def count_web_per_minute(events):                     # minute 열이 있는 이벤트 표를 받는 함수
    """웹 서버 이벤트만 골라 분마다 요청이 몇 개인지 센다.
    분당 요청 수를 평소와 비교하기 전에 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. events["source"] == "web" 으로 행마다 True 또는 False 를 구해 is_web 에 담는다 (웹 서버 이벤트이면 True)
    is_web = events["source"] == "web"
    # 3. events 에서 is_web 이 True 인 행만 골라 web_events 에 담는다 (events[is_web])
    web_events = events[is_web]
    counts = web_events.groupby("minute").size()      # minute 값이 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지(그 분의 요청 수) 센다(size)
    return counts                                     # 분마다 요청 수를 리턴한다


def make_traffic_limit(path, multiple):               # 파일 경로와 몇 배인지를 받는 함수
    """지난 7일 분당 요청 평균의 multiple 배를 급증 기준으로 정한다.
    평소보다 요청이 크게 늘어난 분을 가려낼 급증 기준을 정할 때 쓴다.
    """
    baseline = pd.read_csv(path)                      # 지난 7일 파일을 표로 읽는다
    average = baseline["requests_per_minute"].mean()  # 분당 요청 수 열을 꺼내(["requests_per_minute"]) 바로 7개의 평균을 구한다(mean)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. average 에 multiple 을 곱해 limit 에 담는다
    limit = average * multiple
    return limit                                      # 급증 기준을 리턴한다


def pick_spike_minutes(counts, limit):                # 분마다 요청 수와 급증 기준을 받는 함수
    """요청 수가 급증 기준 이상인 분만 골라 리턴한다.
    알림을 보낼 분을 가릴 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. counts 가 limit 이상인지 비교한 결과(>=)를 is_spike 에 담는다
    is_spike = counts >= limit
    # 6. counts 에서 is_spike 가 True 인 것만 골라 spike_minutes 에 담는다 (counts[is_spike])
    spike_minutes = counts[is_spike]
    return spike_minutes                              # 요청이 급증한 분과 요청 수를 리턴한다
