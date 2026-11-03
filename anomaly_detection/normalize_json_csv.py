import csv                                           # CSV 파일을 읽는 도구를 불러온다
import json                                          # JSON 문자열을 딕셔너리로 바꾸는 도구를 불러온다
from datetime import datetime                        # 날짜와 시각을 다루는 도구를 불러온다

SERVER_TIME_FORMAT = "%Y-%m-%dT%H:%M"                # 판정 서버 시각의 모양(예: 2026-11-02T09:40)
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"             # 공통 시각의 모양(예: 2026-11-02 09:40:00)
ALLOWED_MAP = {True: "성공", False: "실패"}          # 판정 서버의 allowed 값을 공통 결과로 바꾸는 표
RESULT_MAP = {"success": "성공", "failure": "실패"}  # SaaS 의 outcome 값을 공통 결과로 바꾸는 표


def convert_server_time(time_text):                  # 판정 서버 시각 문자열을 받는 함수
    """판정 서버 시각을 공통 모양의 문자열로 바꾼다.
    예: 2026-11-02T09:40 → 2026-11-02 09:40:00.
    판정 서버 로그를 공통 이벤트로 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. datetime.strptime(time_text, SERVER_TIME_FORMAT) 의 결과를 parsed 에 담는다
    parsed = datetime.strptime(time_text, SERVER_TIME_FORMAT)
    # 2. parsed.strftime(COMMON_TIME_FORMAT) 의 결과를 time_out 에 담는다
    time_out = parsed.strftime(COMMON_TIME_FORMAT)
    return time_out                                  # 공통 모양의 시각 문자열을 리턴한다


def normalize_server(line):                          # 판정 서버 로그 한 줄(JSON 문자열)을 받는 함수
    """판정 서버 로그 한 줄을 공통 이벤트 딕셔너리로 바꾼다.
    판정 서버 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    item = json.loads(line)                          # JSON 문자열을 딕셔너리로 바꾼다
    time_out = convert_server_time(item["time"])     # 공통 모양의 시각으로 바꾼다
    allowed = item["allowed"]                        # 허용이었는지(True 또는 False)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. ALLOWED_MAP 에서 allowed 에 해당하는 값을 꺼내 result 에 담는다 (ALLOWED_MAP[allowed])
    result = ALLOWED_MAP[allowed]
    raw_text = line.strip()                          # 원래 줄(양끝 공백과 줄바꿈 뺀 것)을 보관한다
    event = {                                        # 공통 이벤트의 키로 묶는다
        "time": time_out,                            # 일어난 시각
        "source": "server",                          # 어느 로그에서 왔는지
        "user": item["user"],                        # 요청한 사용자
        "ip": None,                                  # 판정 서버 로그에는 접속 주소가 없다
        "action": item["permission"],                # 요청한 권한
        "result": result,                            # 성공인지 실패인지
        "raw": raw_text,                             # 원래 로그 줄
    }
    return event                                     # 공통 이벤트를 리턴한다


def normalize_saas(row):                             # SaaS CSV 한 행(딕셔너리)을 받는 함수
    """SaaS 로그 한 행을 공통 이벤트 딕셔너리로 바꾼다.
    SaaS 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. row["account"] 를 "@" 기준으로 나눠 account_parts 에 담는다 (account 예: seoyeon@a-corp.example)
    account_parts = row["account"].split("@")
    # 5. account_parts 의 첫 값을 user 에 담는다
    user = account_parts[0]
    outcome = row["outcome"]                         # success 또는 failure
    # 6. RESULT_MAP 에서 outcome 에 해당하는 값을 꺼내 result 에 담는다
    result = RESULT_MAP[outcome]
    event = {                                        # 공통 이벤트의 키로 묶는다
        "time": row["time"],                         # SaaS 시각은 이미 공통 모양이라 그대로 쓴다
        "source": "saas",                            # 어느 로그에서 왔는지
        "user": user,                                # 메일 주소에서 꺼낸 사용자 이름
        "ip": row["ip_address"],                     # 접속 주소
        "action": row["event"],                      # 무엇을 했는지
        "result": result,                            # 성공인지 실패인지
        "raw": row,                                  # 원래 CSV 행(딕셔너리)을 보관한다
    }
    return event                                     # 공통 이벤트를 리턴한다


def load_server(path):                               # 판정 서버 로그 파일 경로를 받는 함수
    """판정 서버 로그 파일의 모든 줄을 공통 이벤트 리스트로 바꾼다.
    판정 서버 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                      # 결과를 담을 리스트
    with open(path, encoding="utf-8") as server_file:  # 파일을 연다
        for line in server_file:                     # 한 줄씩 꺼낸다
            event = normalize_server(line)           # 공통 이벤트로 바꾼다
            events.append(event)                     # 리스트에 추가한다
    return events                                    # 이벤트 리스트를 리턴한다


def load_saas(path):                                 # SaaS CSV 파일 경로를 받는 함수
    """SaaS CSV 파일의 모든 행을 공통 이벤트 리스트로 바꾼다.
    SaaS 로그를 정규화 결과에 합칠 준비를 할 때 쓴다.
    """
    events = []                                      # 결과를 담을 리스트
    with open(path, encoding="utf-8", newline="") as saas_file:  # 파일을 연다(CSV 는 newline="" 을 붙인다)
        reader = csv.DictReader(saas_file)           # 첫 줄을 열 이름으로 삼아 행마다 딕셔너리로 읽는다
        for row in reader:                           # 행을 하나씩 꺼낸다
            event = normalize_saas(row)              # 공통 이벤트로 바꾼다
            events.append(event)                     # 리스트에 추가한다
    return events                                    # 이벤트 리스트를 리턴한다
