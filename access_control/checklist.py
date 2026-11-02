import json                                                      # JSON 파일을 읽는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 만료 시각 문자열의 형식 (예: 2026-11-03 18:00)


def load_state(path):                                            # 파일 경로를 받는 함수
    """점검할 데이터(사용자 · 역할의 부서 · 예외)를 읽어 딕셔너리로 리턴한다.
    정기 점검을 시작할 때 쓴다.
    """
    with open(path, encoding="utf-8") as json_file:                      # 파일을 연다
        return json.load(json_file)                                      # 읽은 내용을 바로 리턴한다


def check_employed(users):                                       # 사용자 딕셔너리를 받는 함수
    """퇴사했는데 계정이 남아 있는 사용자 이름 리스트를 리턴한다.
    정기 점검에서 퇴사자 계정을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. info["employed"] 가 거짓이면 (if not …)
        if not info["employed"]:
        # 2.   name 을 problems 에 추가한다
            problems.append(name)
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def check_expired(exceptions, now):                              # 예외 리스트와 지금 시각(datetime)을 받는 함수
    """만료 시각이 지났는데 남아 있는 예외의 번호 리스트를 리턴한다.
    정기 점검에서 기간이 끝난 예외를 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 예외 번호를 모을 리스트
    for exception in exceptions:                                       # 예외를 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. exception["expires"] 를 TIME_FORMAT 으로 읽어 시각 expires_at 에 담는다 (datetime.strptime)
        expires_at = datetime.strptime(exception["expires"], TIME_FORMAT)
        # 4. expires_at 이 now 보다 이르거나 같으면 (<=)
        if expires_at <= now:
        # 5.   exception["id"] 를 problems 에 추가한다
            problems.append(exception["id"])
    return problems                                              # 문제가 있는 예외 번호를 리턴한다


def check_dept(users, role_dept):                                # 사용자 딕셔너리와 역할별 부서 딕셔너리를 받는 함수
    """부서가 역할의 부서와 다른 사용자 이름 리스트를 리턴한다.
    정기 점검에서 엉뚱한 부서에 역할이 남은 사람을 찾을 때 쓴다.
    """
    problems = []                                                # 문제가 있는 사용자 이름을 모을 리스트
    for name, info in users.items():                             # 사용자 이름과 사용자 항목을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 6. role_dept 에서 info["role"] 의 부서를 찾아 expected_dept 에 담는다
        expected_dept = role_dept[info["role"]]
        # 7. expected_dept 가 info["dept"] 와 다르면 (!=)
        if expected_dept != info["dept"]:
        # 8.   name 을 problems 에 추가한다
            problems.append(name)
    return problems                                              # 문제가 있는 사용자 이름을 리턴한다


def run_checklist(state, now):                                   # 읽은 데이터와 지금 시각을 받는 함수
    """점검 세 가지를 실행한다.
    점검 이름과 문제 리스트를 담은 딕셔너리의 리스트를 리턴한다.
    매주 어긋난 곳을 한 번에 찾을 때 쓴다.
    """
    users = state["users"]                                       # 사용자 딕셔너리를 꺼낸다
    exceptions = state["exceptions"]                             # 예외 리스트를 꺼낸다
    role_dept = state["role_dept"]                               # 역할별 부서 딕셔너리를 꺼낸다
    results = []                                                 # 점검 결과를 모을 리스트
    results.append({"name": "퇴사자 계정 점검", "problems": check_employed(users)})            # 첫째 점검 결과를 추가한다
    results.append({"name": "만료 예외 점검", "problems": check_expired(exceptions, now)})     # 둘째 점검 결과를 추가한다
    results.append({"name": "부서와 역할 점검", "problems": check_dept(users, role_dept)})     # 셋째 점검 결과를 추가한다
    return results                                               # 점검 결과 리스트를 리턴한다
