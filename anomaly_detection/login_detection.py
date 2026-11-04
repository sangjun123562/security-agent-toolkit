import pandas as pd                               # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"            # 읽을 정규화 이벤트 파일 이름
LOGIN_LIMIT = 5                                   # 알림 기준: 평소 하루 최대가 4번이라 5번 이상이면 알린다


def load_events(path):                            # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                   # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                 # 이벤트 표를 리턴한다


def pick_login_failures(events):                  # 이벤트 표를 받는 함수
    """로그인 요청이 실패한 이벤트만 골라 새 표로 만든다.
    로그인 실패가 많은 주소를 조사하기 전에 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다) 
    # 1. events 의 "action" 열을 꺼내 actions 에 담는다
    actions = events["action"]
    # 2. actions 가 "POST /login" 과 같은지 비교한 결과(==)를 is_login 에 담는다
    is_login = actions == "POST /login"
    # 3. events 의 "result" 열을 꺼내 results 에 담는다
    results = events["result"]
    # 4. results 가 "실패" 와 같은지 비교한 결과(==)를 is_fail 에 담는다
    is_fail = results == "실패"
    # 5. is_login & is_fail 로 두 조건을 합쳐 both_true 에 담는다 (둘 다 True 인 행만 True)
    both_true = is_login & is_fail
    # 6. events 에서 both_true 가 True 인 행만 골라 login_failures 에 담는다 (events[both_true])
    login_failures = events[both_true]
    return login_failures                         # 로그인 실패 이벤트만 담은 표를 리턴한다


def count_by_ip(login_failures):                  # 로그인 실패 표를 받는 함수
    """로그인 실패를 접속 주소별로 센다.
    같은 주소가 반복해서 실패했는지 볼 때 쓴다.
    """
    counts = login_failures.groupby("ip").size()  # ip 가 같은 행끼리 그룹으로 만들고(groupby) 바로 그룹마다 행이 몇 개인지 센다(size)
    return counts                                 # 주소별 실패 횟수를 리턴한다


def pick_alert_ips(counts, limit):                # 주소별 횟수와 알림 기준을 받는 함수
    """실패 횟수가 알림 기준 이상인 주소만 골라 리턴한다.
    알림을 보낼 주소를 가릴 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. counts 가 limit 이상인지 비교한 결과(>=)를 is_many 에 담는다
    is_many = counts >= limit
    # 8. counts 에서 is_many 가 True 인 것만 골라 alert_ips 에 담는다 (counts[is_many])
    alert_ips = counts[is_many]
    return alert_ips                              # 알림 기준 이상인 주소와 횟수를 리턴한다
