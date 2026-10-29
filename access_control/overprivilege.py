def entry_key(entry):                                            # 현황의 권한 한 건의 식별 키를 만드는 함수
    """현황의 권한 한 건(또는 그 복사본)의 식별 키(user:permission:source 를 이어 붙인 글자)를 리턴한다."""
    return entry["user"] + ":" + entry["permission"] + ":" + entry["source"]   # 세 값을 : 로 이어 붙인다


def make_stale_reason(stale):                                    # 규칙에 걸린 권한 목록을 받는 함수
    """규칙에 걸린 권한의 식별 키를 키로, 걸린 이유를 값으로 하는 딕셔너리를 리턴한다."""
    stale_reason = {}                                            # 식별 키 → 걸린 이유를 담을 빈 딕셔너리
    for item in stale:                                           # 규칙에 걸린 권한을 하나씩 꺼낸다
        stale_reason[entry_key(item)] = item["reason"]           # 식별 키로 걸린 이유를 찾을 수 있게 담는다
    return stale_reason                                          # 딕셔너리를 리턴한다


def make_unused_keys(unused):                                    # 안 쓴 권한 목록을 받는 함수
    """안 쓴 권한의 식별 키를 담은 목록을 리턴한다."""
    unused_keys = []                                             # 안 쓴 권한의 식별 키를 담을 빈 목록
    for item in unused:                                          # 안 쓴 권한을 하나씩 꺼낸다
        unused_keys.append(entry_key(item))                      # 식별 키를 목록에 추가한다
    return unused_keys                                           # 목록을 리턴한다


def generate_report(access_list, stale, unused, days, generated_at):   # 현황 · 규칙 결과 · 안 쓴 결과 · 기준 일 수 · 만든 시각 글자를 받는 함수
    """과다권한 후보 리포트(딕셔너리)를 리턴한다. 후보마다 "reasons" 키에 이유 목록을 적는다."""
    stale_reason = make_stale_reason(stale)                      # 규칙에 걸린 권한의 식별 키 → 걸린 이유 딕셔너리를 만든다(미리 채움)
    unused_keys = make_unused_keys(unused)                       # 안 쓴 권한의 식별 키 목록을 만든다(미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 후보를 담을 빈 목록 findings 를 만든다
    findings = []
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    for entry in access_list:
    # 3.   entry_key(entry) 가 리턴하는 식별 키를 key 에 담는다
        key = entry_key(entry)
    # 4.   빈 목록 reasons 를 만든다
        reasons = []

    # 5.   key 가 stale_reason 에 있으면 (in)
        if key in stale_reason:
    # 6.     reasons 에 stale_reason[key] 를 추가한다
            reasons.append(stale_reason[key])
    # 7.   key 가 unused_keys 에 있으면 (in)
        if key in unused_keys:    
    # 8.     reasons 에 f"{days}일 넘게 안 씀(이력 없음 포함)" 을 추가한다
            reasons.append(f"{days}일 넘게 안 씀(이력 없음 포함)")
    # 9.   reasons 의 개수가 0 보다 크면 (len(reasons) > 0)
        if len(reasons) > 0:
    # 10.    entry.copy() 를 finding 에 담는다
            finding = entry.copy()
    # 11.    finding["reasons"] 를 reasons 로 정한다
            finding["reasons"] = reasons
    # 12.    findings 에 finding 을 추가한다
            findings.append(finding)
    # 13. 딕셔너리를 리턴한다: "generated_at" 은 generated_at, "total" 은 len(access_list), "finding_count" 는 len(findings), "findings" 는 findings
    return {
        "generated_at": generated_at,
        "total": len(access_list),
        "finding_count": len(findings),
        "findings": findings
    }
