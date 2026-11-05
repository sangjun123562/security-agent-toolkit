import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다
from rbac import check_permission                     # 3과목(접근통제)에서 만든 권한 판정 함수를 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
REPEAT_LIMIT = 3                                      # 한 사용자의 실패가 이 횟수 이상이면 먼저 확인한다
PRIORITY = {"퇴사한 계정": 1, "권한 없음": 2, "허용": 3}  # 판정 이유별로 우선순위(작을수록 먼저)


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_server_failures(events):                     # 이벤트 표를 받는 함수
    """판정 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    서버가 거절한 요청을 조사하기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_server = sources == "server"                   # 각 행이 판정 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                        # result 열만 꺼낸다
    is_fail = results == "실패"                       # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_server & is_fail                   # 두 조건이 모두 True 인 행만 True 로 만든다
    server_failures = events[both_true]               # True 인 행만 골라 새 표로 만든다
    return server_failures                            # 서버 실패 이벤트 표를 리턴한다


def pick_suspicious(server_failures):                 # 서버 실패 표를 받는 함수
    """실패가 반복된 사용자의 이벤트만 골라 새 표로 만든다.
    같은 사용자가 여러 번 거절당했는지 볼 때 쓴다.
    """
    users = server_failures["user"]                   # user 열만 꺼낸다
    user_counts = users.value_counts()                # 사용자마다 실패가 몇 번인지 센다
    is_many = user_counts >= REPEAT_LIMIT             # 사용자마다 실패 횟수가 REPEAT_LIMIT 이상인지 비교해 True 또는 False 를 만든다
    repeated_users = user_counts[is_many]             # 반복된 사용자와 횟수만 남긴다

    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. repeated_users 의 .index 를 repeated_names 에 담는다
    repeated_names = repeated_users.index
    # 2. users 가 repeated_names 안에 있는지 isin 으로 구해 is_repeated_user 에 담는다
    is_repeated_user = users.isin(repeated_names)
    # 3. server_failures 에서 is_repeated_user 가 True 인 행만 골라 suspicious 에 담는다
    suspicious = server_failures[is_repeated_user]
    return suspicious                                 # 먼저 확인할 실패 이벤트 표를 리턴한다


def judge_failure(user, action):                      # 사용자와 행동을 받는 함수
    """서버가 거절한 요청을 3과목(접근통제) 권한 규칙으로 다시 판정해 이유와 우선순위를 리턴한다.
    거절이 규칙대로인지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. action 을 ":" 기준으로 나눠 parts 에 담는다 (예: "SALES:QUERY" → ["SALES", "QUERY"]. 앞 조각이 자원, 뒤 조각이 행위)
    parts = action.split(":")
    resource = parts[0]                               # 첫 번째 조각이 자원이다
    permission_action = parts[1]                      # 두 번째 조각이 행위이다

    # 5. check_permission 에 user, resource, permission_action 을 전달하고, 결과를 is_allowed 와 reason 에 나눠 담는다 (모양: is_allowed, reason = check_permission(...). is_allowed 는 이 문제에서 쓰지 않는다)
    is_allowed, reason = check_permission(user, resource, permission_action)
    # 6. PRIORITY 에서 reason 의 순서를 꺼내 priority 에 담는다 (딕셔너리에 없는 이유이면 4 — .get(reason, 4))
    priority = PRIORITY.get(reason, 4)
    return reason, priority                           # 판정 이유와 우선순위를 리턴한다
