from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def exclude_key(entry):                                          # 사용자와 권한이 든 딕셔너리(후보 또는 제외 목록의 한 건)를 받는 함수
    """「사용자:권한」 글자를 리턴한다. 제외 목록과 후보를 비교하는 키로 쓴다."""
    return f"{entry['user']}:{entry['permission']}"              # 사용자와 권한을 : 로 이어 붙인다


def make_excluded(finding, reason):                              # 후보 한 건과 제외 이유 글자를 받는 함수
    """후보를 복사해 "exclude_reason" 키(제외 이유)를 적어 리턴한다. 원래 후보는 바꾸지 않는다."""
    item = finding.copy()                                        # 원래 후보는 바꾸지 않고 복사한다
    item["exclude_reason"] = reason                              # 복사본에 제외 이유를 적는다
    return item                                                  # 복사본을 리턴한다


def load_exclude_map(path):                                      # 회수 제외 목록 파일 경로를 받는 함수
    """회수 제외 목록 파일을 읽어 「사용자:권한」 글자를 키로, 제외 이유를 값으로 하는 딕셔너리를 리턴한다."""
    exclude_map = {}                                             # 빈 딕셔너리로 시작한다
    for item in load_json(path, []):                             # 제외 목록의 권한을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        exclude_map[exclude_key(item)] = item["reason"]          # 그 권한의 「사용자:권한」 글자를 키로, 제외 이유를 값으로 담는다
    return exclude_map                                           # 딕셔너리를 리턴한다


def split_by_exclude(findings, exclude_map):                     # 후보 목록과 제외 이유 딕셔너리를 받는 함수
    """후보를 (회수 대상 후보 목록, 회수 제외 후보 목록) 두 목록으로 나눠 리턴한다. 제외 목록에 있어도 후보의 이유(reasons)에 「퇴사한 계정」이 있으면 제외하지 않는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 빈 목록 to_revoke 와 빈 목록 excluded 를 만든다
    to_revoke = [] 
    excluded = []
    # 2. findings 에서 finding 을 하나씩 꺼낸다
    for finding in findings:
    # 3.   exclude_key(finding) 을 key 에 담는다
        key = exclude_key(finding)
    # 4.   key 가 exclude_map 에 있고(in), "퇴사한 계정" 이 finding["reasons"] 에 없으면 (not in) — 두 조건을 and 로 이어 한 줄에 쓴다
        if key in exclude_map and "퇴사한 계정" not in finding["reasons"]:
    # 5.     make_excluded(finding, exclude_map[key]) 를 excluded 에 추가한다
            excluded.append(make_excluded(finding,exclude_map[key]))
    # 6.   그렇지 않으면 (else)
        else:
    # 7.     to_revoke 에 finding 을 추가한다
            to_revoke.append(finding)
    # 8. 두 목록 to_revoke, excluded 를 리턴한다
    return to_revoke, excluded
