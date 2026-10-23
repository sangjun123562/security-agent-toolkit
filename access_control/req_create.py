from rbac import USERS                                           # 10/21(수)에 만든 사용자 딕셔너리를 불러온다

REQUESTS = []                                                    # 접수한 요청서를 모아 두는 목록(프로그램이 끝나면 사라진다)


def create_request(user, resource, action, until, reason, received_at):  # 요청자 · 자원 · 행위 · 희망 만료 시각 · 이유 · 접수 시각을 받는 함수
    """요청서를 만들어 REQUESTS 에 넣고 (True, 요청서)를 리턴한다. 접수할 수 없으면 (False, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. user 가 USERS 에 없으면 False, "등록되지 않은 사용자" 를 리턴한다
    if user not in USERS:
        return False, " 등록되지 않은 사용자"
    # 2. reason 이 빈 글자("")이면 False, "이유가 없음" 을 리턴한다
    if reason == "":
        return False, "이유가 없음"
    # 3. until 이 received_at 과 같거나 앞서면(until <= received_at) False, "만료 시각이 이미 지났음" 을 리턴한다
    if until <= received_at:
        return False, "만료 시각이 이미 지났음"
    # 4. 딕셔너리 request 를 만든다. 칸 아홉 개의 이름은 2.1 의 표와 같고, 값은 이렇게 정한다:
    request = {
        "id": len(REQUESTS) + 1,
        "user": user,
        "resource": resource,
        "action": action,
        "permission": f"{resource}:{action}",
        "until": until,
        "reason": reason,
        "requested_at": received_at,
        "status": "reviewing"
    }
    #    "id" 는 REQUESTS 의 개수 + 1, "permission" 은 f"{resource}:{action}", "requested_at" 은 received_at,
    #    "status" 는 "reviewing", 나머지 다섯 칸(user · resource · action · until · reason)은 같은 이름의 값을 그대로 넣는다
    # 5. REQUESTS 목록 끝에 request 를 더한다
    REQUESTS.append(request)
    # 6. True, request 를 리턴한다
    return True, request
