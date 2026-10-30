from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다


def load_sensitive(path):                                        # 민감한 권한 파일 경로를 받는 함수
    """민감한 권한 파일을 읽어 「자원:행위」 문자열의 리스트를 리턴한다. 파일이 없거나 깨졌으면 빈 리스트를 리턴한다."""
    return load_json(path, [])                                   # 안전하게 읽어 그대로 리턴한다


def plan_key(plan):                                              # 계획 한 건을 받는 함수
    """「사용자:권한」 문자열(예: "dami:SALES:CHANGE")을 리턴한다. 승인 결정을 찾는 키로 쓴다."""
    user = plan["user"]                                          # 계획의 사용자
    permission = plan["permission"]                              # 계획의 권한
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. f"{user}:{permission}" 을 리턴한다 (사용자와 권한을 : 로 이어 붙인 문자열)
    return f"{user}:{permission}"

def needs_approval(plan, sensitive):                             # 계획 한 건과 민감한 권한 리스트를 받는 함수
    """민감한 권한이거나 영향이 2건 이상이면 True, 아니면 False 를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. plan["permission"] 이 sensitive 안에 있는지(in)를 is_sensitive 에 담는다
    is_sensitive = plan["permission"] in sensitive
    # 3. plan["impact"] 가 2 이상인지(>=)를 is_big_impact 에 담는다
    is_big_impact = plan["impact"] >= 2
    # 4. is_sensitive 이거나 is_big_impact 이면 True 가 되도록 리턴한다 (or)
    return is_sensitive or is_big_impact
        


def mark_approvals(plans, sensitive, decisions):                 # 계획 리스트 · 민감한 권한 리스트 · 승인 결정 딕셔너리를 받는 함수
    """계획마다 "approval" 키(승인 상태)를 적은 복사본 리스트를 리턴한다. 승인 상태는 「승인 불필요」 · 「승인됨」 · 「승인 대기」 중 하나다."""
    results = []                                                 # 결과를 담을 빈 리스트
    for plan in plans:                                           # 계획을 하나씩 꺼낸다
        item = plan.copy()                                       # 원래 계획은 바꾸지 않고 복사한다
        key = plan_key(plan)                                     # 승인 결정을 찾는 「사용자:권한」 문자열을 만든다
        decision = decisions.get(key)                            # 보안 책임자의 결정을 꺼낸다(결정이 없으면 None)
        needs = needs_approval(plan, sensitive)                  # 승인이 필요한 계획인지 알아본다(True 또는 False)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 5. needs 가 거짓이면 (not)
        if not needs:
        # 6.   item["approval"] 을 "승인 불필요" 로 정한다
            item["approval"] = "승인 불필요"
        # 7. 그렇지 않고 decision 이 "승인" 이면 (elif)
        elif decision == "승인":
        # 8.   item["approval"] 을 "승인됨" 으로 정한다
            item["approval"] = "승인됨"
        # 9. 그렇지 않으면 (else)
        else:
        # 10.  item["approval"] 을 "승인 대기" 로 정한다
            item["approval"] = "승인 대기"
        results.append(item)                                     # 승인 상태를 적은 복사본을 결과 리스트에 추가한다
    return results                                               # 결과 리스트를 리턴한다

