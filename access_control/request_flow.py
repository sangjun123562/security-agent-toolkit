import json                                                      # JSON 파일을 쓰는 모듈을 불러온다


def save_requests(requests, path):                               # 요청서 목록과 저장할 파일 경로를 받는 함수
    """요청서 목록을 JSON 파일로 저장한다. 한글이 그대로 보이게 쓴다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. path 를 쓰기 모드("w")로, encoding="utf-8" 로 열어 f 로 받는다
    with open(path, "w", encoding="utf-8") as f:
    # 2.   json.dump 로 requests 를 f 에 쓴다. ensure_ascii=False 와 indent=2 를 함께 쓴다
        json.dump(requests, f, ensure_ascii=False, indent=2)
    # 3. 저장한 요청서 건수 len(requests) 를 리턴한다 (with 블록 밖, 함수 안쪽 줄에 맞춘다)
    return len(requests)


def count_by_status(requests):                                   # 요청서 목록을 받는 함수
    """상태(status)별 요청서 건수를 딕셔너리로 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 빈 딕셔너리 counts 를 만든다
    counts = {}
    # 2. requests 에서 request 를 하나씩 꺼낸다
    for request in requests:
    # 3.   request["status"] 를 status 에 담는다
        status = request["status"]
    # 4.   counts[status] 를 지금 값(없으면 0)에 1 을 더한 값으로 바꾼다
        counts[status] = counts.get(status, 0) + 1
    # 5. 반복이 끝나면 counts 를 리턴한다
    return counts
