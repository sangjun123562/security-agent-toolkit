from datetime import datetime                                    # 요청 시각을 만드는 데 쓴다
from policy import evaluate_access                               # 방금 만든 최종 판정 함수를 불러온다
from exception_policy import EXCEPTIONS                          # 예외 목록을 불러온다

TODAY_LOG = [                                                    # 오늘 정산 포털 요청 기록. (시각, 사용자, 자원, 행위)
    ("09:10", "seoyeon", "SETTLE", "QUERY"),                     # 예외 1번 기간 안
    ("10:00", "dami", "SALES", "QUERY"),                         # 퇴사자(예외 3번이 남아 있음)
    ("11:40", "gaeun", "SETTLE", "QUERY"),                       # 예외 5번 기간 안
    ("12:30", "gaeun", "SETTLE", "QUERY"),                       # 예외 5번이 12:00 에 끝난 뒤
    ("13:00", "junho", "SETTLE", "QUERY"),                       # 역할 권한으로 허용되는 요청
    ("14:00", "batch-night", "SALES", "QUERY"),                  # 예외 4번 기간 안
    ("15:00", "junho", "SALES", "CHANGE"),                       # 예외 2번은 10/20(화) 에 끝남
    ("16:20", "seoyeon", "SETTLE", "QUERY"),                     # 예외 1번 기간 안
    ("18:05", "seoyeon", "SETTLE", "QUERY"),                     # 예외 1번이 18:00 에 끝난 뒤
]

counts = {}                                                      # "역할로 허용" · "예외로 허용" · "거부" → 건수
used = {}                                                        # "예외 N번" → 오늘 쓰인 건수

for time, user, resource, action in TODAY_LOG:                   # 기록을 하나씩 꺼낸다
    now = datetime.strptime("2026-10-22 " + time, "%Y-%m-%d %H:%M")   # 오늘 날짜와 그 요청의 시각을 시각으로 바꾼다
    ok, reason = evaluate_access(user, resource, action, now)    # 그 시각으로 최종 판정을 받는다
    print(time, user, resource, action, "->", ok, reason)        # 결과를 출력한다
    if ok and reason == "역할 권한":                               # 역할로 허용이면
        counts["역할로 허용"] = counts.get("역할로 허용", 0) + 1     # 역할로 허용된 건수를 1 늘린다
    elif ok:                                                     # 그 밖의 허용은 예외로 허용
        counts["예외로 허용"] = counts.get("예외로 허용", 0) + 1     # 예외로 허용된 건수를 1 늘린다
        used[reason] = used.get(reason, 0) + 1                   # 그 예외 번호의 사용 건수를 1 늘린다
    else:                                                        # 거부면
        counts["거부"] = counts.get("거부", 0) + 1                 # 거부된 건수를 1 늘린다
        if reason == "권한 없음":                                 # 거부 이유가 「권한 없음」일 때만
            for exc in EXCEPTIONS:                               # 예외 목록을 하나씩 꺼낸다
                if exc["user"] == user and exc["permission"] == resource + ":" + action:   # 같은 사람 · 같은 권한의 예외가 있으면
                    print("[만료 뒤 시도]", time, user, resource, action, "- 만료된 예외", exc["id"], exc["expires"])   # 만료 뒤 시도로 알린다

print(counts)                                                    # 방식별 건수를 출력한다
print("예외 사용", used)                                          # 예외 번호별 사용 건수를 출력한다
