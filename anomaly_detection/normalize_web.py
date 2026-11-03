from datetime import datetime                  # 날짜와 시각을 다루는 도구를 불러온다
from log_parse import split_request, read_request, read_status, read_client  # 어제 만든 로그 읽기 함수를 불러온다

NGINX_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"     # nginx 시각의 모양(예: 02/Nov/2026:09:12:03 +0900)
COMMON_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"       # 공통 시각의 모양(예: 2026-11-02 09:12:03)


def read_time_text(prefix):                    # 요청 앞 조각을 받는 함수
    """요청 앞 조각에서 대괄호 안의 시각 문자열을 꺼낸다.
    웹 서버 로그의 시각을 공통 모양으로 바꾸기 전에 쓴다.
    """
    parts = prefix.split()                     # 공백 기준으로 나눈다
    bracket_text = parts[3] + " " + parts[4]   # '[02/Nov/2026:09:12:03' 과 '+0900]' 를 이어 붙인다
    time_text = bracket_text.strip("[]")       # 양쪽 끝의 대괄호를 지운다
    return time_text                           # 대괄호 없는 시각 문자열을 리턴한다


def convert_time(time_text):                   # nginx 시각 문자열을 받는 함수
    """nginx 시각을 공통 모양의 문자열로 바꾼다.
    예: 02/Nov/2026:09:12:03 +0900 → 2026-11-02 09:12:03.
    웹 서버 로그를 공통 이벤트로 만들 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. datetime.strptime(time_text, NGINX_TIME_FORMAT) 의 결과를 parsed 에 담는다
    parsed = datetime.strptime(time_text,NGINX_TIME_FORMAT)
    # 2. parsed.replace(tzinfo=None) 의 결과를 local_time 에 담는다 (+0900 정보를 떼고 한국 시각만 남긴다)
    local_time = parsed.replace(tzinfo=None)
    # 3. local_time.strftime(COMMON_TIME_FORMAT) 의 결과를 time_out 에 담는다
    time_out = local_time.strftime(COMMON_TIME_FORMAT)
    return time_out                            # 공통 모양의 시각 문자열을 리턴한다


def convert_result(status):                    # 상태 코드(정수)를 받는 함수
    """상태 코드가 400 이상이면 「실패」, 아니면 「성공」을 리턴한다.
    웹 서버 로그의 결과를 공통 이벤트의 result 로 바꿀 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. status 가 400 이상이면 (if)
    if status >= 400:
    # 5.   "실패" 를 리턴한다
        return "실패"
    # 6. 그 밖에는 "성공" 을 리턴한다
    return "성공" 


def normalize_web(line):                       # 로그 한 줄을 받는 함수
    """웹 서버 로그 한 줄을 공통 이벤트 딕셔너리로 바꾸고, 깨진 줄이면 None 을 리턴한다.
    웹 서버 로그를 다른 로그와 같은 모양으로 맞출 때 쓴다.
    """
    if line.count('"') < 2:                    # 큰따옴표가 두 개보다 적은 깨진 줄이면
        return None                            # 읽지 않고 None 을 리턴한다
    prefix, request_text, suffix = split_request(line)  # 세 조각으로 나눈다
    method, path = read_request(request_text)  # 요청 조각에서 방법과 경로를 꺼낸다
    status = read_status(suffix)               # 뒤 조각에서 상태 코드를 꺼낸다
    client_ip = read_client(prefix)            # 앞 조각에서 접속자 주소를 꺼낸다
    time_text = read_time_text(prefix)         # 앞 조각에서 시각 문자열을 꺼낸다
    time_out = convert_time(time_text)         # 공통 모양의 시각으로 바꾼다
    result = convert_result(status)            # 상태 코드를 성공 · 실패로 바꾼다
    action = method + " " + path               # 방법과 경로를 하나의 행동으로 합친다
    raw_text = line.strip()                    # 원래 줄(양끝 공백과 줄바꿈 뺀 것)을 보관한다
    event = {                                  # 공통 이벤트의 키로 묶는다
        "time": time_out,                      # 일어난 시각
        "source": "web",                       # 어느 로그에서 왔는지
        "user": None,                          # 웹 서버 로그에는 사용자가 없다
        "ip": client_ip,                       # 접속자 주소
        "action": action,                      # 무엇을 했는지
        "result": result,                      # 성공인지 실패인지
        "raw": raw_text,                       # 원래 로그 줄
    }
    return event                               # 공통 이벤트를 리턴한다
