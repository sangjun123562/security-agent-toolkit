def split_request(line):                       # 로그 한 줄(문자열)을 받는 함수
    """로그 한 줄을 큰따옴표 기준으로 앞 · 요청 · 뒤 세 조각으로 나눈다.
    한 덩어리 문자열인 로그에서 값을 꺼내기 시작할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. line 을 큰따옴표(")로 두 번만 나눠 prefix, request_text, suffix 세 이름에 담는다 (line.split('"', 2))
    prefix, request_text, suffix = line.split('"', 2)
    return prefix, request_text, suffix        # 세 조각을 리턴한다


def read_request(request_text):                # 요청 조각(예: GET /login HTTP/1.1)을 받는 함수
    """요청 조각에서 방법(method)과 경로(path)를 꺼낸다.
    무엇을 요청했는지 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. request_text 를 공백 기준으로 나눠 method, path, protocol 세 이름에 담는다 (request_text.split())
    method, path, protocol = request_text.split()
    return method, path                        # 방법과 경로를 리턴한다


def read_status(suffix):                       # 요청 뒤 조각(예:  401 312 "-" "Mozilla/5.0")을 받는 함수
    """요청 뒤 조각에서 상태 코드를 꺼내 정수로 리턴한다.
    요청이 성공했는지 실패했는지 가를 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. suffix 를 공백 기준으로 나눠 parts 에 담는다 (suffix.split())
    parts = suffix.split()
    # 4. parts 의 첫 값을 status_text 에 담는다 (parts[0])
    status_text = parts[0]
    # 5. status_text 를 int 로 바꿔 status 에 담는다
    status = int(status_text)
    return status                              # 상태 코드(정수)를 리턴한다


def read_client(prefix):                       # 요청 앞 조각(예: 203.0.113.50 - - [02/Nov/2026:09:12:03 +0900] )을 받는 함수
    """요청 앞 조각에서 접속자 주소를 꺼낸다.
    어느 주소가 요청했는지 알고 싶을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. prefix 를 공백 기준으로 나눠 parts 에 담는다 (prefix.split())
    parts = prefix.split()
    # 7. parts 의 첫 값을 client_ip 에 담는다 (parts[0])
    client_ip = parts[0]
    return client_ip                           # 접속자 주소를 리턴한다


def parse_line(line):                          # 로그 한 줄을 받는 함수
    """로그 한 줄을 ip · method · path · status 딕셔너리로 바꾼다.
    깨진 줄이면 None 을 리턴한다.
    접속 로그를 분석하기 전에 한 줄을 값으로 나눌 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. 큰따옴표가 두 개보다 적으면 (if line.count('"') < 2:)
    if line.count('"') < 2:
        return None                            # 읽을 수 없으니 None 을 리턴한다
    prefix, request_text, suffix = split_request(line)  # 세 조각으로 나눈다
    method, path = read_request(request_text)  # 요청 조각에서 방법과 경로를 꺼낸다
    status = read_status(suffix)               # 뒤 조각에서 상태 코드를 꺼낸다
    client_ip = read_client(prefix)            # 앞 조각에서 접속자 주소를 꺼낸다
    entry = {                                  # 꺼낸 값을 딕셔너리로 묶는다
        "ip": client_ip,                       # 접속자 주소
        "method": method,                      # 요청 방법
        "path": path,                          # 요청 경로
        "status": status,                      # 상태 코드(정수)
    }
    return entry                               # 딕셔너리를 리턴한다
