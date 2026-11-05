import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
USUAL_IPS = {"seoyeon": "198.51.100.9", "junho": "192.0.2.41", "jiwoo": "198.51.100.52"}  # 사용자별 평소 IP. gaeun 은 평소 기록이 없어 넣지 않았다
BUSINESS_START = 8                                    # 업무 시간이 시작하는 시
BUSINESS_END = 20                                     # 업무 시간이 끝나는 시(20시대, 20:59 까지가 업무 시간)
DOWNLOAD_LIMIT = 5                                    # 파일을 이 횟수 이상 내려받으면 대량 다운로드로 본다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_saas(events):                                # 이벤트 표를 받는 함수
    """SaaS 로그의 이벤트만 골라 새 표로 만든다.
    SaaS 이상 사용을 찾기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_saas = sources == "saas"                       # 각 행이 SaaS 이벤트인지 비교해 True 또는 False 를 만든다
    saas = events[is_saas]                            # True 인 행만 골라 새 표로 만든다
    return saas                                       # SaaS 이벤트 표를 리턴한다


def pick_logins(saas):                                # SaaS 이벤트 표를 받는 함수
    """로그인 이벤트만 골라 새 표로 만든다.
    로그인 시각과 IP 를 살펴보기 전에 쓴다.
    """
    actions = saas["action"]                          # action 열만 꺼낸다
    is_login = actions == "login"                     # 각 행이 로그인인지 비교해 True 또는 False 를 만든다
    logins = saas[is_login]                           # True 인 행만 골라 새 표로 만든다
    return logins                                     # 로그인 이벤트 표를 리턴한다


def find_off_hours_logins(logins):                    # 로그인 표를 받는 함수
    """업무 시간 밖에 시도한 로그인만 골라 새 표로 만든다.
    새벽 로그인처럼 평소에 없는 시각을 찾을 때 쓴다.
    """
    times = pd.to_datetime(logins["time"])            # 문자열 시각을 시각 값으로 바꾼다 — 미리 채운 줄
    hours = times.dt.hour                             # 시각 값에서 시(0~23)만 꺼낸다 — 미리 채운 줄

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. hours 가 BUSINESS_START 이상 BUSINESS_END 이하인지 between 으로 구해 is_business_hour 에 담는다
    is_business_hour = hours.between(BUSINESS_START, BUSINESS_END)
    # 2. is_business_hour 의 반대를 ~ 로 구해 is_off_hours 에 담는다
    is_off_hours = ~is_business_hour
    off_hours_logins = logins[is_off_hours]           # True 인 행만 골라 새 표로 만든다
    return off_hours_logins                           # 업무 시간 밖 로그인 표를 리턴한다


def find_new_ip_users(logins):                        # 로그인 표를 받는 함수
    """평소와 다른 IP 로 로그인한 사용자를 골라 리스트로 만든다.
    계정을 다른 사람이 쓰는지 의심할 때 쓴다.
    """
    new_ip_users = []                                 # 사용자를 담을 빈 리스트
    login_list = logins.to_dict("records")            # 표를 이벤트 딕셔너리 리스트로 바꾼다
    for login in login_list:                          # 로그인을 하나씩 꺼낸다
        user = login["user"]                          # 그 로그인의 사용자
        ip = login["ip"]                              # 그 로그인의 IP
        usual_ip = USUAL_IPS.get(user)                # 그 사용자의 평소 IP(기록이 없으면 None)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. usual_ip 가 None 이 아닌지 구해 has_usual_ip 에 담는다 (None 인지는 is None, 아닌지는 is not None)
        has_usual_ip = usual_ip is not None 
        # 4. ip 가 usual_ip 와 다른지 != 로 구해 is_new_ip 에 담는다 (같은지는 ==, 다른지는 !=)
        is_new_ip = ip != usual_ip
        if has_usual_ip and is_new_ip:                # 평소 IP 기록이 있고, 이번 IP 가 평소와 다르면
            # 5. new_ip_users 에 user 를 추가한다
            new_ip_users.append(user)
    return new_ip_users                               # 평소와 다른 IP 로 로그인한 사용자를 리턴한다


def find_bulk_download_users(saas):                   # SaaS 이벤트 표를 받는 함수
    """파일을 기준 횟수 이상 내려받은 사용자를 리스트로 만든다.
    자료를 한꺼번에 빼 가는 사용자를 찾을 때 쓴다.
    """
    actions = saas["action"]                          # action 열만 꺼낸다
    is_download = actions == "file.download"          # 각 행이 다운로드인지 비교해 True 또는 False 를 만든다
    downloads = saas[is_download]                     # True 인 행만 골라 새 표로 만든다
    counts = downloads.groupby("user").size()         # user 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size) — 사용자별 다운로드 횟수
    is_bulk = counts >= DOWNLOAD_LIMIT                # 사용자마다 횟수가 기준 이상인지 비교해 True 또는 False 를 만든다
    bulk_counts = counts[is_bulk]                     # 기준 이상인 사용자와 횟수만 남긴다
    bulk_users = list(bulk_counts.index)              # 사용자 이름만 리스트로 만든다
    return bulk_users                                 # 대량 다운로드 사용자를 리턴한다
