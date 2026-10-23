from rbac import check_permission                                # 10/21(수)에 만든 역할 판정 함수를 불러온다
from exception_policy import EXCEPTIONS                          # 10/22(목)에 만든 예외 목록을 불러온다


def grant_request(request):                                      # 요청서를 받는 함수
    """승인된 요청서를 정책으로 한 번 더 확인하고, 통과하면 예외 권한을 부여한다. (성공 여부, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. request["status"] 가 "approved" 가 아니면 False, "승인되지 않음" 을 리턴한다
    if request["status"] != "approved":
        return False, "승인되지 않음"

    # 2. check_permission 에 request 의 "user" · "resource" · "action" 을 넣어 ok, judge_reason 으로 나눠 받는다
    ok, judge_reason = check_permission(request["user"],request["action"],request["action"])
    # 3. ok 이거나 judge_reason 이 "권한 없음" 이 아니면 False, f"부여하지 않음({judge_reason})" 을 리턴한다
    if ok or judge_reason != "권한 없음":
        return False, f"부여하지 않음({judeg_erason})"
    # 4. 예외 딕셔너리 exception 을 만든다. 칸 다섯 개의 값은 이렇게 정한다:
    #    "id" 는 EXCEPTIONS 의 개수 + 1, "user" · "permission" · "reason" 은 request 의 같은 이름 칸,
    #    "expires" 는 request["until"] (이름이 다른 것에 주의)
    exception = {
        "id": len(EXCEPTIONS) + 1,
        "user": request["user"],
        "permission": request["permission"],
        "expires": request["until"],
        "reason": request["reason"]
    }
    # 5. EXCEPTIONS 에 exception 을 더한다
    EXCEPTIONS.append(exception)
    # 6. request["exception_id"] 를 exception["id"] 로 정한다 (어느 예외를 부여했는지 요청서에 적어 둔다)
    request["exception_id"] = Exception["id"]
    # 7. request["status"] 를 "granted" 로 바꾼다
    request["status"] = "granted"
    # 8. True, "부여" 를 리턴한다
    return True, "부여"