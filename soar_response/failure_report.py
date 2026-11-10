def collect_failures(action_log):  # 감사 기록 리스트를 받는 함수
    """감사 기록에서 결과가 「실패」로 시작하는 기록만 골라 리스트로 리턴한다.
    담당자가 아침에 가장 먼저 볼 「확인이 필요한 건」 목록을 만들 때 쓴다.
    """
    failures = []                  # 실패한 기록을 담을 빈 리스트
    for entry in action_log:       # 기록을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. entry["result"] 가 "실패" 로 시작하면 (if, startswith)
        if entry["result"].strip().startswith("실패"):
        # 7.   failures 에 entry 를 추가한다 (append)
            failures.append(entry)
    return failures                # 실패한 기록 리스트를 리턴한다
