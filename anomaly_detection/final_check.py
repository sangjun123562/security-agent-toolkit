import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
LOGIN_ALERTS_PATH = "login_alerts.json"               # 읽을 로그인 규칙 알림 파일 이름
PROBLEMS_PATH = "problems.json"                       # 읽을 진짜 문제 파일 이름
IP_RULE = "SaaS 평소와 다른 IP"                       # 예외를 적용할 규칙 이름
TRUSTED_IPS = ["203.0.113.80"]                        # 믿는 IP 리스트 : 협력사 사무실 IP 한 개


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def apply_exception(alerts):                          # 알림 표를 받는 함수
    """IP 규칙 알림 중 믿는 IP 에서 온 것만 빼낸다.
    3교시에서 만든 예외 규칙을 다시 적용할 때 쓴다.
    """
    is_ip_rule = alerts["rule"] == IP_RULE            # 각 알림이 IP 규칙의 알림인지 비교한다
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)       # 각 알림의 IP 가 믿는 IP 리스트에 있는지 구한다
    is_removed = is_ip_rule & is_trusted              # IP 규칙의 알림이면서 믿는 IP 에서 온 것만 True 로 만든다
    removed_alerts = alerts[is_removed]               # 빼낼 알림만 골라 새 표로 만든다
    is_kept = ~is_removed                             # 빼지 않을 알림을 True 로 만든다
    kept_alerts = alerts[is_kept]                     # True 인 행만 골라 새 표로 만든다
    return removed_alerts, kept_alerts                # 빼낸 알림 표와 남은 알림 표를 리턴한다


def merge_alerts(alerts, login_alerts):               # 알림 표 두 개를 받는 함수
    """두 규칙 묶음의 알림 표를 위아래로 이어 하나로 만든다.
    새 규칙의 알림까지 한꺼번에 평가할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. pd.concat 에 두 표를 대괄호 리스트로 묶어 전달하고, 합친 표를 all_alerts 에 담는다 (모양: pd.concat([표1, 표2]))
    all_alerts = pd.concat([alerts, login_alerts])
    return all_alerts                                 # 합친 알림 표를 리턴한다


def evaluate(all_alerts, problems):                   # 알림 표와 진짜 문제 표를 받는 함수
    """합친 알림에서 오탐 수와 놓친 문제를 구한다.
    튜닝을 마친 뒤 결과를 마지막으로 평가할 때 쓴다.
    """
    is_real = all_alerts["real"]                      # real 열(진짜 문제이면 True)을 꺼낸다
    is_false = ~is_real                               # 문제가 아니었던 알림을 True 로 만든다
    false_alarms = all_alerts[is_false]               # True 인 행만 골라 새 표로 만든다
    false_alarm_count = len(false_alarms)             # 오탐이 몇 개인지 센다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 2. all_alerts 의 "problem" 열에서 빈 값을 .dropna() 로 지워 caught_ids 에 담는다
    caught_ids = all_alerts["problem"].dropna()
    # 3. problems 의 "id" 열이 caught_ids 안에 있는지 isin 으로 구해 is_caught 에 담는다
    is_caught = problems["id"].isin(caught_ids)
    # 4. is_caught 를 ~ 로 뒤집어 is_missed 에 담는다
    is_missed = ~is_caught
    # 5. problems 에서 is_missed 가 True 인 행만 골라 missed_problems 에 담는다
    missed_problems = problems[is_missed]
    return false_alarm_count, missed_problems         # 오탐 수와 놓친 문제 표를 리턴한다


def make_summary(alert_count, false_alarm_count, missed_count):  # 세 개수를 받는 함수
    """알림 수 · 오탐 수 · 놓친 문제 수를 한 문장으로 만든다.
    평가 결과를 보고서에 한 줄로 적을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 6. "알림 " 과 알림 수, "개 중 오탐 " 과 오탐 수, "개 · 놓친 문제 " 와 놓친 문제 수, "개" 를 + 로 이어 summary 에 담는다 (숫자는 str() 로 문자열로 바꿔서 이어 붙인다)
    summary = "알림 " + str(alert_count) + "개 중 오탐 " + str(false_alarm_count) + "개 · 놓친 문제 " + str(missed_count) + "개"
    return summary                                    # 한 문장을 리턴한다
