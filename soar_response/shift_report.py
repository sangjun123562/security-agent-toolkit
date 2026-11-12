def is_failure(record):                                     # 기록 한 건을 받는 함수
    """기록의 조치 후 상태에 「확인 실패」가 들어 있으면 True, 아니면 False 를 리턴한다.
    조치했다고 했지만 실제로 바뀌지 않은 건을 찾아낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. "확인 실패" 가 record 의 "after" 안에 있는지(in)의 결과를 리턴한다
    return "확인 실패" in record["after"]

def is_unchanged(record):                                   # 기록 한 건을 받는 함수
    """조치 전과 후 상태가 같으면 True, 다르면 False 를 리턴한다.
    실제로 바뀐 것이 없는 기록을 찾아낼 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. record 의 "before" 와 "after" 가 같은지(==)의 결과를 리턴한다
    return record["before"] == record["after"]

def classify_record(record):                                # 기록 한 건을 받는 함수
    """기록을 「확인 실패」 · 「변경 없음」 · 「변경됨」 중 하나로 나눠 리턴한다.
    근무 보고에서 조치 결과를 종류별로 셀 때 쓴다.
    """
    if is_failure(record):                                  # 확인에 실패한 기록이면 — 미리 채운 줄
        return "확인 실패"                                  # 확인 실패로 나눈다 — 미리 채운 줄
    if is_unchanged(record):                                # 바뀐 것이 없으면 — 미리 채운 줄
        return "변경 없음"                                  # 변경 없음으로 나눈다 — 미리 채운 줄
    return "변경됨"                                         # 그 밖에는 실제로 바뀐 기록이다 — 미리 채운 줄


def summarize(log):                                         # 기록 리스트를 받는 함수
    """기록을 종류별로 몇 건인지 세어 딕셔너리로 리턴한다.
    근무를 넘길 때 오늘 조치가 어떻게 끝났는지 한눈에 보여 줄 때 쓴다.
    """
    counts = {"변경됨": 0, "변경 없음": 0, "확인 실패": 0}  # 종류별 건수를 셀 딕셔너리
    for record in log:                                      # 기록을 하나씩 꺼낸다
        kind = classify_record(record)                      # 기록의 종류를 구한다 — 미리 채운 줄
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 8. counts[kind] 에 counts[kind] + 1 을 담는다 (그 종류의 건수를 1 늘린다)
        counts[kind] = counts[kind] + 1
    return counts                                           # 종류별 건수를 리턴한다
