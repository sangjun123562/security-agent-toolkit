import json                                                      # JSON 문자열을 만드는 모듈을 불러온다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from flask import Flask, request                                 # 서버를 만드는 Flask 와 요청 정보를 담은 request 를 불러온다
from conditional import load_rules, evaluate_conditional         # 5교시에 만든 조건 판정 함수를 불러온다

app = Flask(__name__)                                            # 서버 프로그램을 만든다
app.json.ensure_ascii = False                                    # 응답의 한글이 \uXXXX 로 깨지지 않게 한다
RULES = load_rules("config/conditions.json")                     # 조건 파일을 서버를 켤 때 한 번 읽는다
LOG_PATH = "server_log.jsonl"                                    # 요청 로그를 남길 파일 이름
TIME_FORMAT = "%Y-%m-%dT%H:%M"                                   # 주소로 받는 시각 문자열의 형식(예: 2026-10-30T10:00)


def parse_time(text):                                            # 시각 문자열을 받는 함수
    """2026-10-30T10:00 모양 문자열을 시각으로 바꿔 리턴한다. 문자열이 없거나 모양이 틀리면 None 을 리턴한다."""
    if text is None:                                             # 시각 문자열이 아예 없으면
        return None                                              # 없다고 알린다
    try:                                                         # 아래를 시도한다 (미리 채움)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. datetime.strptime(text, TIME_FORMAT) 의 결과(시각)를 리턴한다
        return datetime.strptime(text, TIME_FORMAT)
    except ValueError:                                          # 모양이 틀렸으면 (미리 채움)
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. None 을 리턴한다 (없다고 알린다)
        return None


def write_log(entry):                                            # 로그에 쓸 딕셔너리를 받는 함수
    """딕셔너리 한 건을 JSON 한 줄로 만들어 로그 파일 끝에 덧붙인다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. 파일을 여는 모드 "a"(덧붙이기: 기존 내용 뒤에 쓴다)를 mode 에 담는다
    mode = "a"
    with open(LOG_PATH, mode, encoding="utf-8") as f:            # 파일을 mode(덧붙이기 모드)로 연다
        text = json.dumps(entry, ensure_ascii=False)             # 딕셔너리를 JSON 문자열로 만든다(한글은 그대로)
        f.write(text + "\n")                                     # 한 줄로 파일 끝에 쓴다


@app.route("/check")                                             # 주소 /check 로 오는 요청을 아래 함수가 받는다
def check():                                                     # 요청 한 건을 처리하는 함수
    """주소의 user · resource · action · network · time 으로 판정하고, 허용이면 200, 거부이면 403, 값이 빠졌으면 400 으로 답한다."""
    user = request.args.get("user")                              # 요청 주소에서 user 값을 꺼낸다(주소에 없으면 None)
    resource = request.args.get("resource")                      # 요청 주소에서 resource 값을 꺼낸다
    action = request.args.get("action")                          # 요청 주소에서 action 값을 꺼낸다
    network = request.args.get("network")                        # 요청 주소에서 network 값을 꺼낸다
    time_text = request.args.get("time")                         # 요청 주소에서 time 값을 꺼낸다(없으면 None)
    now = parse_time(time_text)                                  # 시각으로 바꾼다(없거나 모양이 틀리면 None)
    if None in (user, resource, action, network, now):           # 빠졌거나 모양이 틀린 값이 하나라도 있으면 (미리 채움)
        return {"allowed": False, "reason": "입력이 잘못됨"}, 400   # 요청이 잘못됐다는 상태 코드 400 으로 답한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. evaluate_conditional(user, resource, action, network, now, RULES) 의 결과를 allowed, reason 으로 받는다
    allowed, reason = evaluate_conditional(user, resource, action, network, now, RULES)
    log_entry = {
        "time": request.args.get("time"),                        # 시각
        "user": user,                                            # 사용자
        "permission": f"{resource}:{action}",                    # 권한
        "network": network,                                      # 접속 위치
        "allowed": allowed,                                      # 허용 여부
        "reason": reason,                                        # 이유
    }
    write_log(log_entry)                                         # 요청 로그를 한 줄 덧붙인다 (미리 채움)
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. allowed 가 참이면
    if allowed:
    # 6.   {"allowed": True, "reason": reason} 과 상태 코드 200 을 함께 리턴한다
        return {"allowed": True, "reason": reason}, 200 
    # 7. {"allowed": False, "reason": reason} 과 상태 코드 403 을 함께 리턴한다 (if 밖, 함수 안쪽 줄에 맞춘다)
    return {"allowed": False, "reason": reason}, 403

if __name__ == "__main__":                                       # 이 파일을 직접 실행했을 때만
    app.run(port=5001)                                           # 5001번 포트로 서버를 켠다
