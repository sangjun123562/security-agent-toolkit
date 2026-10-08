import json                                                   # JSON 문자열 ↔ 딕셔너리를 바꾸는 도구
import requests                                               # 인터넷으로 요청을 보내는 도구 (9/30)


def count_failed_logins(args):                                # 도구 — 한 계정의 로그인 실패 횟수를 센다
    with open("normalized_logs.json", encoding="utf-8") as f:  # 9/29 에 정리한 로그 파일을 연다
        rows = json.load(f)                                   # 파일 내용을 리스트로 읽는다
    count = 0                                                 # 센 횟수. 0 에서 시작
    for row in rows:                                          # 로그를 한 건씩 꺼낸다
        # 계정이 같고 등급이 WARN(실패)이면
        if row["user"] == args["user"] and row["level"] == "WARN":
            count = count + 1                                 # 하나 센다
    return count                                              # 센 횟수를 돌려준다


def lookup_ip(args):                                          # 도구 — IP 의 나라와 통신사를 조회한다
    # 조회 API 에 IP 를 물어 딕셔너리로 받는다
    data = requests.get("https://ipwho.is/" + args["ip"], timeout=10).json()
    return data["country"] + " / " + data["connection"]["isp"]  # 나라와 통신사를 " / " 로 이어 돌려준다


tool_registry = {}                                            # 빈 레지스트리
# 1. tool_registry 의 "count_failed_logins" 키에 함수 count_failed_logins 를 담으세요
tool_registry["count_failed_logins"] = count_failed_logins
# 2. tool_registry 의 "lookup_ip" 키에 함수 lookup_ip 를 담으세요
tool_registry["lookup_ip"] = lookup_ip


def route_tool_call(choice):                                  # 라우터 — 이름으로 함수를 찾아 실행한다
    name = choice["tool"]                                     # 고른 도구의 이름
    # 3. func 라는 변수를 만들어 tool_registry 에서 name 으로 꺼낸 함수를 담으세요
    func = tool_registry.get(name)                            # 이름으로 함수를 꺼낸다. 없으면 None

    if func:                                                  # 함수를 찾았으면
        return func(choice["args"])                           # 그 함수에 인자를 넣어 실행한 결과를 돌려준다

    print("[오류] 등록되지 않은 도구:", name)
    return None
