import json                                         # 파일에 JSON 으로 저장하는 도구를 불러온다
from normalize_web import normalize_web             # 웹 서버 로그 정규화 함수를 불러온다
from normalize_json_csv import load_server, load_saas  # 판정 서버 · SaaS 로그 읽기 함수를 불러온다

EVENTS_PATH = "normalized_events.json"              # 정규화한 이벤트를 저장할 파일 이름


def load_web(path):                                 # 웹 서버 로그 파일 경로를 받는 함수
    """웹 서버 로그 파일의 모든 줄을 공통 이벤트 리스트로 바꾸고 깨진 줄은 건너뛴다.
    웹 서버 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                     # 결과를 담을 리스트
    with open(path, encoding="utf-8") as web_file:  # 파일을 연다
        for line in web_file:                       # 한 줄씩 꺼낸다
            event = normalize_web(line)             # 공통 이벤트로 바꾼다
            if event is not None:                   # 읽을 수 있는 줄이면
                events.append(event)                # 리스트에 추가한다
    return events                                   # 이벤트 리스트를 리턴한다


def get_time(event):                                # 이벤트 하나를 받는 함수
    """정렬 기준으로 쓸 시각 문자열을 리턴한다.
    이벤트를 시간순으로 정렬할 때 쓴다.
    """
    return event["time"]                            # 이벤트의 time 값을 리턴한다


def merge_events(web, server, saas):                # 세 이벤트 리스트를 받는 함수
    """이벤트 리스트 세 개를 하나로 이어 붙이고 시간순으로 정렬한다.
    여러 로그에서 같은 계정이 한 일을 시간순으로 함께 보고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. web, server, saas 를 + 로 이어 붙여 events 에 담는다
    events = web + server + saas
    # 2. events.sort(key=get_time) 로 time 이 이른 것부터(오름차순) 정렬한다 (sort 는 events 자체를 바꾸고 아무것도 리턴하지 않는다)
    events.sort(key=get_time)
    return events                                   # 시간순으로 정렬한 이벤트 리스트를 리턴한다


def count_by_source(events):                        # 이벤트 리스트를 받는 함수
    """소스별 이벤트 수를 {소스: 개수} 딕셔너리로 센다.
    합친 이벤트가 로그 종류마다 몇 개씩 들어왔는지 확인할 때 쓴다.
    """
    counts = {}                                     # 결과를 담을 딕셔너리
    for event in events:                            # 이벤트를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. event 의 "source" 값을 source 에 담는다
        source = event["source"]
        # 4. counts 에서 source 의 현재 횟수(없으면 0)에 1 을 더해 counts[source] 에 담는다 (counts.get)
        counts[source] = counts.get(source, 0) + 1
    return counts                                   # 소스별 개수를 리턴한다


def count_missing(events, key):                     # 이벤트 리스트와 키 이름을 받는 함수
    """key 키의 값이 비어 있는(None) 이벤트 수를 리턴한다.
    분석에서 빠질 이벤트가 얼마나 되는지 미리 알아볼 때 쓴다.
    """
    missing = 0                                     # 비어 있는 개수를 0 으로 시작한다
    for event in events:                            # 이벤트를 하나씩 꺼낸다
        if event[key] is None:                      # 그 키의 값이 비어 있으면
            missing = missing + 1                   # 비어 있는 개수를 1 늘린다
    return missing                                  # 비어 있는 개수를 리턴한다


def save_events(events, path):                      # 이벤트 리스트와 저장할 파일 이름을 받는 함수
    """이벤트 리스트를 JSON 파일로 저장한다.
    정규화 결과를 다음 분석의 입력으로 남길 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as events_file:  # 파일을 쓰기 모드("w")로 연다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. json.dump(events, events_file, ensure_ascii=False, indent=2) 로 events 를 events_file 에 저장한다
        json.dump(events, events_file, ensure_ascii=False, indent=2)
