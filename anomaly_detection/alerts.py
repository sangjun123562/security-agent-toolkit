import json                                                                             # 알림을 JSON 파일로 쓰기 위해 json 을 불러온다

ALERTS_PATH = "alerts.json"                                                             # 알림을 모아 저장할 파일 이름


def make_alert(alert_type, target, count, note):                                        # 종류 · 대상 · 횟수 · 메모를 받는 함수
    """알림 한 건을 딕셔너리로 만든다.
    알림마다 같은 모양으로 담아 한 파일에 모을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 딕셔너리를 alert 에 담는다: 키 "type" 에는 alert_type, "target" 에는 target, "count" 에는 count, "note" 에는 note, "status" 에는 "확인 필요" 를 넣는다 (여러 줄로 나눠 써도 된다)
    alert = {
        "type":alert_type,
        "target":target,
        "count":count,
        "note":note,
        "status":"확인필요"
    }
    return alert                                                                        # 알림 한 건을 리턴한다


def make_login_alerts(alert_ips):                                                       # 알림 대상 주소와 횟수를 받는 함수
    """로그인 실패 알림 대상 주소마다 「비정상 로그인」 알림을 하나씩 만든다.
    3교시에서 추출한 주소를 알림 형식으로 바꿀 때 쓴다.
    """
    alerts = []                                                                         # 알림을 담을 빈 리스트
    for ip_address, count in alert_ips.items():                                         # 주소와 횟수를 한 쌍씩 꺼낸다
        note = "로그인 실패가 기준 이상 — 공격 확정이 아니라 먼저 살펴볼 곳"            # 담당자에게 보일 메모
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 2. make_alert 에 "비정상 로그인" · ip_address · count · note 를 전달해 alert 에 담는다
        alert = make_alert("비정상 로그인",ip_address,count,note)
        alerts.append(alert)                                                            # 알림을 리스트에 추가한다
    return alerts                                                                       # 로그인 실패 알림 리스트를 리턴한다


def make_traffic_alerts(spike_minutes):                                                 # 요청이 급증한 분과 요청 수를 받는 함수
    """요청이 급증한 분마다 「트래픽 급증」 알림을 하나씩 만든다.
    5교시에서 추출한 분을 알림 형식으로 바꿀 때 쓴다.
    """
    alerts = []                                                                         # 알림을 담을 빈 리스트
    for minute, count in spike_minutes.items():                                         # 분과 요청 수를 한 쌍씩 꺼낸다
        note = "요청이 평소의 3배 이상으로 늘어남 — 공격 확정이 아니라 먼저 살펴볼 곳"  # 담당자에게 보일 메모
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 3. str(minute) 로 시각 값을 문자열로 바꿔 target 에 담는다
        target = str(minute)
        # 4. make_alert 에 "트래픽 급증" · target · count · note 를 전달해 alert 에 담는다
        alert = make_alert("트래픽 급증",target,count,note)
        alerts.append(alert)                                                            # 알림을 리스트에 추가한다
    return alerts                                                                       # 트래픽 급증 알림 리스트를 리턴한다


def save_alerts(alerts, path):                                                          # 알림 리스트와 파일 경로를 받는 함수
    """알림 리스트를 JSON 파일로 저장하고 저장한 건수를 리턴한다.
    담당자와 다른 프로그램이 같은 파일로 알림을 처리하게 할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. path 파일을 쓰기 모드("w")로 열고 file 변수로 쓴다 (with open(path, "w", encoding="utf-8") as file:)
    with open(path, "w", encoding="utf-8") as file:
    # 6. json.dump 에 alerts, file 을 이 순서로 전달하고, 뒤에 ensure_ascii=False, indent=2 를 붙여 쓴다 (한글은 그대로, 줄을 나눠 저장)
        json.dump(alerts,file,ensure_ascii=False,indent=2)
    saved_count = len(alerts)                                                           # 저장한 알림이 몇 건인지 센다
    return saved_count                                                                  # 저장한 건수를 리턴한다
