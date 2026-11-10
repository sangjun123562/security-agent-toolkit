from safe_runner import safe_run_action                                            # 오전 4교시에 만든 안전한 액션 실행 함수를 불러온다

MAX_TRIES = 3                                                                      # 한 액션을 시도하는 최대 횟수


def flaky_run_action(action, incident, state, fail_plan):                          # 액션 · 인시던트 · 모의 시스템 · 실패 계획을 받는 함수
    """실패 계획에 이 액션이 앞으로 실패할 횟수가 남아 있으면 연결 오류를 일으키고, 없으면 오전의 safe_run_action 으로 실행한다.
    외부 서비스가 잠깐 응답하지 않는 상황을 흉내 낼 때 쓴다.
    """
    key = incident["id"] + "|" + action                                            # 실패 계획에서 찾을 이름 (인시던트 번호 | 액션)
    remaining = fail_plan.get(key, 0)                                              # 이 액션이 앞으로 실패해야 하는 횟수 (없으면 0)
    if remaining > 0:                                                              # 아직 실패해야 하면
        fail_plan[key] = remaining - 1                                             # 남은 실패 횟수를 1 줄이고
        raise ConnectionError("연결 실패: " + action + " 서비스가 응답하지 않음")  # 연결 오류를 일으킨다
    return safe_run_action(action, incident, state)                                # 실패 계획에 없으면 정상으로 실행한다


def run_with_retry(action, incident, state, fail_plan, max_tries):                 # 액션 · 인시던트 · 모의 시스템 · 실패 계획 · 최대 시도 횟수를 받는 함수
    """액션을 실행해 보고, 연결 오류가 나면 최대 횟수까지 다시 시도한다. 성공하면 결과를, 모두 실패하면 실패 문장을 리턴한다.
    외부 서비스가 잠깐 멈춰도 자동 대응이 끝까지 가게 할 때 쓴다.
    """
    last_error = ""                                                                # 마지막 오류 문장 : 처음에는 비어 있다
    for attempt in range(1, max_tries + 1):                                        # 1 번부터 최대 횟수까지 시도 번호를 하나씩 꺼낸다
        try:                                                                       # 오류가 날 수 있는 부분을 시작한다 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 1. flaky_run_action(action, incident, state, fail_plan) 의 결과를 result 에 담는다
            result = flaky_run_action(action, incident, state, fail_plan)
            # 2. result + " (시도 " + str(attempt) + "회)" 를 리턴한다 (성공하면 여기서 끝난다)
            return result + "(시도 " + str(attempt) + "회)"
        except ConnectionError as error:                                           # 연결 오류가 나면 — 미리 채운 줄
            # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
            # 3. str(error) 를 last_error 에 담는다 (오류 문장을 기억해 두고 다음 시도로 간다)
            last_error = str(error)
    return "실패: " + last_error + " (" + str(max_tries) + "회 모두 실패)"         # 모든 시도가 실패했으면 실패 문장을 리턴한다 — 미리 채운 줄
