import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

EVENTS_PATH = "normalized_events.json"                # 읽을 정규화 이벤트 파일 이름
SCANNER_PATTERN = "/.env|/wp-login|/phpmyadmin"       # 스캐너가 자주 요청하는 경로. | 는 「또는」이라는 뜻이다


def load_events(path):                                # 파일 경로를 받는 함수
    """이벤트 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    events = pd.read_json(path)                       # 파일 속 이벤트를 표 한 개로 읽는다
    return events                                     # 이벤트 표를 리턴한다


def pick_web_failures(events):                        # 이벤트 표를 받는 함수
    """웹 서버 로그에서 실패한 이벤트만 골라 새 표로 만든다.
    경로 스캔 요청을 찾기 전에 쓴다.
    """
    sources = events["source"]                        # source 열만 꺼낸다
    is_web = sources == "web"                         # 각 행이 웹 서버 이벤트인지 비교해 True 또는 False 를 만든다
    results = events["result"]                        # result 열만 꺼낸다
    is_fail = results == "실패"                       # 각 행이 실패인지 비교해 True 또는 False 를 만든다
    both_true = is_web & is_fail                      # 두 조건이 모두 True 인 행만 True 로 만든다
    web_failures = events[both_true]                  # True 인 행만 골라 새 표로 만든다
    return web_failures                               # 웹 실패 이벤트 표를 리턴한다


def find_scan_ips(web_failures):                      # 웹 실패 표를 받는 함수
    """스캐너가 요청하는 경로를 요청한 IP 와 요청 횟수를 찾는다.
    한 번의 오타 요청이나 로그인 실패만 있는 IP 를 거르고 경로 스캔만 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web_failures 의 "action" 열을 꺼내 actions 에 담는다
    actions = web_failures["action"]
    # 2. actions 에 .str.contains(SCANNER_PATTERN) 을 붙여 스캐너 경로가 들어 있는지 구해 is_scanner 에 담는다
    is_scanner = actions.str.contains(SCANNER_PATTERN)
    # 3. web_failures 에서 is_scanner 가 True 인 행만 골라 scanner_rows 에 담는다
    scanner_rows = web_failures[is_scanner]
    # 4. scanner_rows 의 "ip" 열에 .value_counts() 를 붙여 IP 별로 몇 번 요청했는지 세어 scan_counts 에 담는다
    scan_counts = scanner_rows["ip"].value_counts()
    scan_ips = list(scan_counts.index)                # 스캔으로 보는 IP 이름만 리스트로 만든다
    return scan_ips, scan_counts                      # 스캔 IP 리스트와 IP 별 요청 횟수를 리턴한다


def explain_scan(ip, request_count):                  # IP 와 스캐너 경로 요청 횟수를 받는 함수
    """스캔으로 본 IP 하나를 담당자가 읽을 설명 딕셔너리로 만든다.
    왜 의심했는지 이유를 알림에 남길 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. "스캐너 경로를 " 와 str(request_count) 와 "번 요청" 을 + 로 연결해 reason 에 담는다 (문구는 복사해 붙여도 된다)
    reason = "스캐너 경로를" + str(request_count) + "번 요청"
    # 6. 키 "ip" 에 ip, 키 "reason" 에 reason 을 담은 딕셔너리를 scan_info 에 담는다
    scan_info = {"ip":ip, "reason":reason}
    return scan_info                                  # 설명 딕셔너리를 리턴한다
