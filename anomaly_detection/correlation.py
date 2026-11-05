import pandas as pd                                    # 판다스를 pd 라는 짧은 이름으로 불러온다
from access_detection import load_events, pick_server_failures, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins      # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures      # 4교시 함수를 불러온다

MIN_SOURCES = 2                                        # 서로 다른 로그(source)가 이 개수 이상이면 연결된 것으로 본다
WINDOW_MINUTES = 60                                    # 한 사용자의 이벤트가 이 분 안에 모여 있어야 연결된 것으로 본다


def make_ip_user_map(logins):                          # SaaS 로그인 표를 받는 함수
    """성공한 SaaS 로그인에서 IP 마다 사용자를 찾아 딕셔너리로 만든다.
    웹 서버 로그에는 사용자가 없어서 IP 로 사용자를 찾을 때 쓴다.
    """
    ip_user = {}                                       # IP → 사용자 딕셔너리
    login_list = logins.to_dict("records")             # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                           # 로그인을 하나씩 꺼낸다
        if login["result"] == "성공":                  # 성공한 로그인이면
            ip_user[login["ip"]] = login["user"]       # 그 IP 의 사용자를 딕셔너리에 담는다
    return ip_user                                     # IP → 사용자 딕셔너리를 리턴한다


def attach_user_to_web(web_failures, ip_user):         # 웹 실패 표와 IP → 사용자 딕셔너리를 받는 함수
    """IP 로 사용자를 알 수 있는 웹 실패 이벤트에 user 열을 붙인다.
    웹 로그를 서버 · SaaS 로그와 같은 사용자 기준으로 연결해 분석할 때 쓴다.
    """
    ips = web_failures["ip"]                           # ip 열만 꺼낸다
    known_ips = list(ip_user)                          # 딕셔너리의 키(IP)만 리스트로 만든다
    is_known = ips.isin(known_ips)                     # 행마다 사용자를 아는 IP 인지 구해 True 또는 False 를 만든다
    known_web = web_failures[is_known]                 # True 인 행만 골라 새 표를 만든다
    web_part = known_web.copy()                        # 원본을 바꾸지 않도록 복사한다 — 미리 채운 줄

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web_part 의 "ip" 열을 꺼내 .map(ip_user) 를 붙여 IP 마다 사용자를 구해 users 에 담는다
    users = web_part["ip"].map(ip_user)
    web_part["user"] = users                           # 표에 user 열을 붙인다 — 미리 채운 줄
    return web_part                                    # user 열이 붙은 웹 이벤트 표를 리턴한다


def build_timeline(server_part, saas_part, web_part):  # 세 로그의 표를 받는 함수
    """세 로그의 표를 하나로 합쳐 사용자 · 시각 순으로 정렬하고, 하루 중 몇 분인지 열을 붙인다.
    사용자마다 서로 다른 로그의 이벤트를 시간순으로 놓고 볼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. pd.concat 에 [server_part, saas_part, web_part] 리스트를 전달해 timeline 에 담는다
    timeline = pd.concat([server_part, saas_part, web_part])
    # 3. timeline 에 .sort_values 를 붙이고 ["user", "time"] 리스트를 전달해 사용자 순, 같은 사용자는 시각 순으로 정렬한 결과를 timeline 에 담는다
    timeline = timeline.sort_values(["user", "time"])
    times = pd.to_datetime(timeline["time"])           # 문자열 시각을 시각 값으로 바꾼다
    hours = times.dt.hour                              # 시각 값에서 시(0~23)만 꺼낸다
    minutes = times.dt.minute                          # 시각 값에서 분(0~59)만 꺼낸다
    timeline["minute_of_day"] = hours * 60 + minutes   # 자정부터 몇 분이 지났는지 열을 붙인다 — 미리 채운 줄
    return timeline                                    # 정렬된 이벤트 표를 리턴한다


def find_chains(timeline):                             # 정렬된 이벤트 표를 받는 함수
    """서로 다른 로그가 짧은 시간 안에 한 사용자에게 모여 있는 사건을 찾는다.
    이벤트 하나씩이 아니라 한 사용자의 사건으로 연결해 분석할 때 쓴다.
    """
    grouped = timeline.groupby("user")                 # user 가 같은 행끼리 그룹으로 만든다
    source_counts = grouped["source"].nunique()        # 그룹마다 서로 다른 로그(source)가 몇 종류인지 센다
    latest = grouped["minute_of_day"].max()            # 그룹마다 가장 늦은 시각(분)을 구한다
    earliest = grouped["minute_of_day"].min()          # 그룹마다 가장 이른 시각(분)을 구한다
    spans = latest - earliest                          # 그룹마다 처음부터 마지막까지 몇 분인지 구한다

    chains = []                                        # 연결된 사건을 담을 빈 리스트
    not_chained = []                                   # 로그 종류는 여럿이지만 시간 차가 60분을 초과해 연결되지 않은 사용자 정보
    for user in source_counts.index:                   # 사용자를 하나씩 꺼낸다
        source_count = source_counts[user]             # 그 사용자의 로그 종류 수
        span = spans[user]                             # 그 사용자의 처음부터 마지막까지 분
        has_many_sources = source_count >= MIN_SOURCES  # 로그 종류가 기준 이상인지 구한다
        is_close = span <= WINDOW_MINUTES              # 시간 간격이 기준 이내인지 구한다
        if has_many_sources and is_close:              # 로그 종류도 충분하고 60분 이내이면 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 4. "서로 다른 로그 " 와 str(source_count) 와 "종류 · " 와 str(span) 과 "분 안" 을 + 로 연결해 reason 에 담는다
            reason = "서로 다른 로그 " + str(source_count) + "종류 · " + str(span) + "분 안"
            # 5. chains 에 키 "user" 에 user, 키 "reason" 에 reason 을 담은 딕셔너리를 추가한다
            chains.append({"user": user, "reason": reason})
        if has_many_sources and not is_close:          # 로그 종류는 여럿인데 시간 차가 60분을 초과하면 — 미리 채운 줄
            not_chained.append({"user": user, "source_count": int(source_count), "span_minutes": int(span)})  # 연결되지 않은 사용자와 두 숫자를 추가한다
    return chains, not_chained                         # 연결된 사건과 연결되지 않은 사용자를 리턴한다


def find_chains_in_events(events):                     # 이벤트 표를 받는 함수
    """이벤트 표 하나로 위 함수를 차례로 불러 연결된 사건 리스트를 만든다.
    6교시에서 점수를 매기기 전에 한 번에 쓴다.
    """
    server_failures = pick_server_failures(events)     # 판정 서버 실패 이벤트를 고른다
    server_part = server_failures                      # 서버 실패 이벤트 전체를 쓴다
    saas_part = pick_saas(events)                      # SaaS 이벤트를 고른다
    logins = pick_logins(saas_part)                    # 로그인 이벤트를 고른다
    ip_user = make_ip_user_map(logins)                 # IP → 사용자 딕셔너리를 만든다
    web_failures = pick_web_failures(events)           # 웹 실패 이벤트를 고른다
    web_part = attach_user_to_web(web_failures, ip_user)  # 사용자를 아는 웹 이벤트에 user 열을 붙인다
    timeline = build_timeline(server_part, saas_part, web_part)  # 세 로그를 합쳐 정렬한다
    chains, not_chained = find_chains(timeline)        # 연결된 사건을 찾는다
    return chains                                      # 연결된 사건 리스트를 리턴한다
