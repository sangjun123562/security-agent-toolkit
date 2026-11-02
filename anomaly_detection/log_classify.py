SUSPICIOUS_STATUS = (401, 403)                  # 의심으로 보는 상태 코드(로그인 실패 · 접근 거부)


def is_suspicious(entry):                       # 읽은 요청 딕셔너리를 받는 함수
    """상태 코드가 401 · 403 이거나 경로에 /admin 이 있으면 True, 아니면 False 를 리턴한다.
    먼저 살펴볼 만한 요청을 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. entry["status"] 가 SUSPICIOUS_STATUS 안에 있는지(in)의 결과를 bad_status 에 담는다
    bad_status = entry["status"] in SUSPICIOUS_STATUS
    # 2. entry["path"] 안에 "/admin" 이 들어 있는지(in)의 결과를 admin_path 에 담는다
    admin_path = "/admin" in entry["path"]
    # 3. bad_status 또는 admin_path 가 참인지(or)의 결과를 리턴한다
    return bad_status or admin_path


def is_error(entry):                            # 읽은 요청 딕셔너리를 받는 함수
    """상태 코드가 400 이상이면 True, 아니면 False 를 리턴한다.
    오류로 끝난 요청을 가려낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. entry["status"] 가 400 이상인지의 결과(True 또는 False)를 리턴한다
    return entry["status"] >= 400

def classify_line(entry):                       # 읽은 요청 딕셔너리를 받는 함수
    """요청을 「의심」 · 「오류」 · 「정상」 중 하나로 가른다.
    로그를 훑어 먼저 살펴볼 줄을 고를 때 쓰며, 의심을 먼저 확인한다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. is_suspicious(entry) 가 참이면 (if)
    if is_suspicious(entry):
    # 6.   "의심" 을 리턴한다
        return "의심"
    # 7. is_error(entry) 가 참이면 (if)
    if is_error(entry):
    # 8.   "오류" 를 리턴한다
        return "오류"
    return "정상"                               # 어느 조건에도 안 맞으면 정상이다


def label_entries(entries):                     # 읽은 요청 리스트를 받는 함수
    """요청마다 "group" 키(정상 · 오류 · 의심)를 적은 복사본 리스트를 리턴한다.
    읽은 로그에 분류 이름표를 붙일 때 쓴다.
    """
    labeled = []                                # 결과를 담을 빈 리스트
    for entry in entries:                       # 요청을 하나씩 꺼낸다
        item = entry.copy()                     # 원래 요청은 바꾸지 않고 복사한다
        item["group"] = classify_line(entry)    # 분류를 복사본에 적는다
        labeled.append(item)                    # 복사본을 결과 리스트에 추가한다
    return labeled                              # 분류를 적은 리스트를 리턴한다


def count_groups(labeled):                      # 분류를 적은 요청 리스트를 받는 함수
    """분류별 요청 수를 {분류: 횟수} 딕셔너리로 센다.
    정상 · 오류 · 의심이 각각 몇 개인지 볼 때 쓴다.
    """
    counts = {"정상": 0, "오류": 0, "의심": 0}  # 세 분류를 0 으로 시작한다
    for item in labeled:                        # 요청을 하나씩 꺼낸다
        group = item["group"]                   # 그 요청의 분류
        counts[group] = counts[group] + 1       # 그 분류의 횟수를 1 늘린다
    return counts                               # 분류별 횟수를 리턴한다
