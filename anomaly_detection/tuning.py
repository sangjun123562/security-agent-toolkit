import pandas as pd                                   # 판다스를 pd 라는 짧은 이름으로 불러온다

ALERTS_PATH = "alerts.json"                           # 읽을 알림 파일 이름
IP_RULE = "SaaS 평소와 다른 IP"                       # 예외를 적용할 규칙 이름
TRUSTED_IPS = ["203.0.113.80"]                        # 믿는 IP 리스트 : 협력사 사무실 IP 한 개


def load_table(path):                                 # 파일 경로를 받는 함수
    """JSON 파일을 표로 읽는다.
    분석을 시작할 때 맨 먼저 쓴다.
    """
    table = pd.read_json(path)                        # 파일 속 내용을 표 한 개로 읽는다
    return table                                      # 표를 리턴한다


def count_false_alarms(alerts):                       # 알림 표를 받는 함수
    """진짜 문제가 아니었는데 난 알림(오탐)이 몇 개인지 센다.
    튜닝 전과 후를 비교할 때 쓴다.
    """
    is_real = alerts["real"]                          # real 열(진짜 문제이면 True)을 꺼낸다
    is_false = ~is_real                               # 문제가 아니었던 알림을 True 로 만든다
    false_alarms = alerts[is_false]                   # True 인 행만 골라 새 표로 만든다
    false_alarm_count = len(false_alarms)             # 오탐이 몇 개인지 센다
    return false_alarm_count                          # 오탐 개수를 리턴한다


def apply_exception(alerts):                          # 알림 표를 받는 함수
    """IP 규칙 알림 중 믿는 IP 에서 온 것만 빼낸다.
    오탐을 줄이는 예외 규칙을 적용할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. alerts 의 "rule" 열이 IP_RULE 과 같은지 비교해 is_ip_rule 에 담는다
    is_ip_rule = alerts["rule"] == IP_RULE
    # 2. alerts 의 "ip" 열이 TRUSTED_IPS 안에 있는지 isin 으로 구해 is_trusted 에 담는다
    is_trusted = alerts["ip"].isin(TRUSTED_IPS)
    # 3. is_ip_rule 과 is_trusted 가 모두 True 인 행을 & 로 구해 is_removed 에 담는다
    is_removed = is_ip_rule & is_trusted
    removed_alerts = alerts[is_removed]               # 빼낼 알림만 골라 새 표로 만든다
    is_kept = ~is_removed                             # 빼지 않을 알림을 True 로 만든다
    # 4. alerts 에서 is_kept 가 True 인 행만 골라 kept_alerts 에 담는다
    kept_alerts = alerts[is_kept]
    return removed_alerts, kept_alerts                # 빼낸 알림 표와 남은 알림 표를 리턴한다


def count_real_removed(removed_alerts):               # 빼낸 알림 표를 받는 함수
    """빼낸 알림 중 진짜 문제였던 것이 몇 개인지 센다.
    예외 규칙이 진짜 문제를 지우지 않았는지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. removed_alerts 의 "real" 열을 꺼내 is_real_removed 에 담는다
    is_real_removed = removed_alerts["real"]
    # 6. removed_alerts 에서 is_real_removed 가 True 인 행만 골라 real_removed 에 담는다
    real_removed = removed_alerts[is_real_removed]
    real_removed_count = len(real_removed)            # 진짜 문제였던 알림이 몇 개 빠졌는지 센다
    return real_removed_count                         # 그 개수를 리턴한다


def find_removed_users(removed_alerts):               # 빼낸 알림 표를 받는 함수
    """빼낸 알림에 나온 사용자를 중복 없이 모은다.
    예외로 빠진 알림이 누구의 것인지 확인할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. removed_alerts 의 "user" 열에서 같은 값은 한 번씩만 .unique() 로 꺼내 removed_users 에 담는다
    removed_users = removed_alerts["user"].unique()
    return removed_users                              # 중복 없는 사용자 이름을 리턴한다

