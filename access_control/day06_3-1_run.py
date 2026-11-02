import json                                                      # 경고 기준 파일을 읽는 데 쓴다
from log_summary import read_log, count_by, filter_denied, deny_rate, find_heavy_users   # 방금 만든 집계 함수를 불러온다

LOG_PATH = "week_log.jsonl"                                      # 집계할 로그 파일 이름
with open("config/alert.json", encoding="utf-8") as alert_file:           # 경고 기준 파일을 연다
    ALERT = json.load(alert_file)                                         # 경고 기준 딕셔너리로 읽는다

entries = read_log(LOG_PATH)                                     # 로그를 읽어 요청 리스트로 만든다
denied = filter_denied(entries)                                  # 거부된 요청만 모은다
rate = deny_rate(entries)                                        # 거부율(0 ~ 1)을 구한다
percent = round(rate * 100)                                      # 거부율을 퍼센트 숫자로 바꾼다
limit = ALERT["deny_rate_limit"]                                 # 거부율 경고 기준(0 ~ 1)
limit_percent = round(limit * 100)                               # 경고 기준을 퍼센트 숫자로 바꾼다
user_limit = ALERT["user_denied_limit"]                          # 사용자별 거부 횟수 기준

entry_count = len(entries)                                       # 요청이 모두 몇 건인지 센다
print("--- 단계 1: 집계 - 요청", entry_count, "건")              # 단계 1 시작을 알리는 줄
denied_count = len(denied)                                       # 거부된 요청이 몇 건인지 센다
allowed_count = entry_count - denied_count                       # 허용된 요청 수
print("허용", allowed_count, "· 거부", denied_count, "· 거부율", f"{percent}%")  # 허용 · 거부 · 거부율을 출력한다
print("--- 단계 2: 거부 사유별")                                    # 단계 2 시작을 알리는 줄
reason_counts = count_by(denied, "reason")                       # 거부된 요청을 사유별로 센다
for reason, count in reason_counts.items():                      # 사유와 횟수를 하나씩 꺼낸다
    print(reason, count)                                         # 거부 사유와 횟수를 출력한다
print("--- 단계 3: 경고 기준")                                      # 단계 3 시작을 알리는 줄
if rate >= limit:                                                # 거부율이 기준 이상이면
    print(f"거부율 {percent}% >= 기준 {limit_percent}% -> 경고")    # 경고라고 출력한다
else:                                                            # 기준보다 낮으면
    print(f"거부율 {percent}% < 기준 {limit_percent}% -> 경고 없음")   # 경고 없음이라고 출력한다
user_counts = count_by(denied, "user")                           # 거부된 요청을 사용자별로 센다
heavy = find_heavy_users(user_counts, user_limit)                # 기준 이상 거부된 사용자를 찾는다
print("거부", user_limit, "번 이상 사용자:", heavy)                  # 사용자 이름을 출력한다
