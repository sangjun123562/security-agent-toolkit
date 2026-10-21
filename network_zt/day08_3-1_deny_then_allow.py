import json                                                  # JSON 글자를 읽는 도구(9/28(월))

LOG = [                                                                                                                      # 정책 로그 20줄. 각 줄은 JSON 글자 하나
'{"time": "02:10", "user": "seoyeon", "device": "NB-7741", "decision": "거부", "reason": "미등록 기기"}',                      # 02:10 seoyeon 이 등록되지 않은 기기로 시도해 거부
'{"time": "02:13", "user": "seoyeon", "device": "NB-0417", "decision": "허용", "reason": "-"}',                               # 02:13 seoyeon 이 등록 기기로 허용
'{"time": "08:55", "user": "junho", "device": "NB-0522", "decision": "허용", "reason": "-"}',                                 # 08:55 junho 허용
'{"time": "09:02", "user": "dami", "device": "NB-0333", "decision": "거부", "reason": "퇴사 계정"}',                            # 09:02 퇴사한 dami 거부
'{"time": "09:03", "user": "dami", "device": "NB-0333", "decision": "거부", "reason": "퇴사 계정"}',                            # 09:03 퇴사한 dami 거부
'{"time": "09:20", "user": "gaeun", "device": "NB-0188", "decision": "허용", "reason": "-"}',                                 # 09:20 gaeun 허용
'{"time": "09:41", "user": "junho", "device": "NB-0522", "decision": "거부", "reason": "MFA 안 함"}',                          # 09:41 junho 가 MFA 없이 시도해 거부
'{"time": "09:44", "user": "junho", "device": "NB-0522", "decision": "허용", "reason": "-"}',                                 # 09:44 junho 허용
'{"time": "10:30", "user": "dami", "device": "NB-0333", "decision": "거부", "reason": "퇴사 계정"}',                            # 10:30 퇴사한 dami 거부
'{"time": "11:15", "user": "gaeun", "device": "NB-0188", "decision": "허용", "reason": "-"}',                                 # 11:15 gaeun 허용
'{"time": "11:50", "user": "seoyeon", "device": "NB-0417", "decision": "허용", "reason": "-"}',                               # 11:50 seoyeon 허용
'{"time": "13:05", "user": "junho", "device": "NB-0522", "decision": "허용", "reason": "-"}',                                 # 13:05 junho 허용
'{"time": "14:00", "user": "jiho", "device": "NB-0610", "decision": "거부", "reason": "해외 접속"}',                            # 14:00 jiho 해외 접속으로 거부
'{"time": "14:40", "user": "jiho", "device": "NB-0610", "decision": "허용", "reason": "-"}',                                  # 14:40 jiho 허용
'{"time": "15:20", "user": "seoyeon", "device": "NB-7741", "decision": "거부", "reason": "미등록 기기"}',                       # 15:20 seoyeon 이 다시 미등록 기기로 시도해 거부
'{"time": "15:48", "user": "gaeun", "device": "NB-0188", "decision": "허용", "reason": "-"}',                                 # 15:48 gaeun 허용
'{"time": "16:05", "user": "dami", "device": "NB-0333", "decision": "거부", "reason": "퇴사 계정"}',                            # 16:05 퇴사한 dami 거부
'{"time": "16:30", "user": "junho", "device": "NB-0522", "decision": "허용", "reason": "-"}',                                 # 16:30 junho 허용
'{"time": "17:10", "user": "jiho", "device": "NB-0610", "decision": "허용", "reason": "-"}',                                  # 17:10 jiho 허용
'{"time": "17:55", "user": "gaeun", "device": "NB-0188", "decision": "허용", "reason": "-"}',                                 # 17:55 gaeun 허용
]

def to_min(t):                                               # "09:10" 같은 시각을 분 숫자로 바꾸는 함수
    h, m = t.split(":")                                      # ":" 로 나눈 두 값을 h(시)와 m(분)에 한꺼번에 담는다(.split 은 10/13(화))
    return int(h) * 60 + int(m)                              # 시 × 60 + 분

last = {}                                                    # 계정 → (마지막 결정, 그 시각(분))을 기억할 딕셔너리
deny_reasons = {}                                            # 거부 이유 → 건수를 셀 딕셔너리
for text in LOG:                                             # 로그 글자를 한 줄씩 꺼낸다
    line = json.loads(text) # 1. 임시 값입니다. text 를 json.loads 로 딕셔너리로 바꾼 값으로 바꾼다   # ←
    user = line["user"]                                      # 이 줄의 계정
    now = to_min(line["time"])                               # 이 줄의 시각(분)
    # 2. user 가 last 에 있고, last[user][0] 이 "거부" 이고, line["decision"] 이 "허용" 이고, now - last[user][1] 이 10 이하이면 "[거부 후 허용]", user, line["time"], line["device"] 를 출력한다   # ←
    if user in last and last[user][0] == "거부" and line["decision"] == "허용" and (now - last[user][1]) <= 10:
        print("[거부 후 허용]", user, line["time"], line["device"])

    # 3. last[user] 에 (line["decision"], now) 를 기억한다   # ←

    if line["decision"] == "거부":                            # 거부 줄이면
        deny_reasons[line["reason"]] = deny_reasons.get(line["reason"], 0) + 1   # 그 이유의 건수를 1 늘린다(10/14(수)에 배운 방식)
    last[user] = (line["decision"], now)
for reason in deny_reasons:                                  # 이유를 하나씩 꺼낸다
    count = deny_reasons[reason]                             # 그 이유의 건수
    # 4. reason, "#" 를 count 만큼 반복한 글자, count 를 출력한다   # ←
    print(reason, "#" * count, count)