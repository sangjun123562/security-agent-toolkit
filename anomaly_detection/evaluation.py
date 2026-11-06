import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
PROBLEMS_PATH = "problems.json"                       # 읽을 진짜 문제 파일 이름


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def pick_real_alerts(alerts):                         # 알림 표를 받는 함수
    """알림 중 조사해 보니 진짜 문제였던 것만 골라 새 표로 만든다.
    맞게 찾은 알림을 셀 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    real_alerts = alerts[is_real]                     # True 인 행만 골라 새 표로 만든다
    return real_alerts                                # 진짜 문제였던 알림 표를 리턴한다


def find_false_alarms(alerts):                        # 알림 표를 받는 함수
    """진짜 문제가 아니었는데 난 알림(오탐)을 골라 규칙별로 센다.
    어느 규칙이 오탐을 많이 내는지 볼 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. is_real 을 ~ 로 뒤집어 is_false 에 담는다
    is_false = ~is_real
    # 2. alerts 에서 is_false 가 True 인 행만 골라 false_alarms 에 담는다
    false_alarms = alerts[is_false]
    # 3. false_alarms 의 "rule" 열에서 값별 개수를 value_counts() 로 세어 false_alarm_rule_counts 에 담는다
    false_alarm_rule_counts = false_alarms["rule"].value_counts()
    return false_alarms, false_alarm_rule_counts      # 오탐 표와 규칙별 오탐 개수를 리턴한다


def find_missed(problems, real_alerts):               # 진짜 문제 표와 진짜 알림 표를 받는 함수
    """알림이 하나도 나지 않은 진짜 문제(미탐)를 골라 새 표로 만든다.
    놓친 문제를 찾을 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. real_alerts 의 "problem" 열을 꺼내 caught_ids 에 담는다
    caught_ids = real_alerts["problem"]
    is_caught = problems["id"].isin(caught_ids)       # 각 문제 번호가 그 안에 있는지 구한다
    # 5. is_caught 를 ~ 로 뒤집어 is_missed 에 담는다
    is_missed = ~is_caught
    # 6. problems 에서 is_missed 가 True 인 행만 골라 missed_problems 에 담는다
    missed_problems = problems[is_missed]
    return missed_problems                            # 놓친 문제 표를 리턴한다


def count_real_alerts(alerts):                        # 알림 표를 받는 함수
    """진짜 문제였던 알림이 몇 개인지 센다.
    알림이 얼마나 맞았는지 숫자 하나로 볼 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. is_real 의 True 개수를 .sum() 으로 세어 real_alert_count 에 담는다
    real_alert_count = is_real.sum()
    return real_alert_count                           # 진짜 문제였던 알림 수를 리턴한다
