POLICY_LOG = [                                                                                                 # PDP 가 남긴 정책 로그 12건
    {"rid": 101, "time": "02:14", "user": "seoyeon", "decision": "거부",     "score": 70},                      # 새벽 대량 조회를 거부한 기록
    {"rid": 102, "time": "09:02", "user": "junho",   "decision": "허용",     "score": 0},                       # 정상 요청을 허용한 기록
    {"rid": 103, "time": "09:10", "user": "seoyeon", "decision": "추가확인", "score": 30},                      # 추가 확인을 요구한 기록
    {"rid": 104, "time": "10:05", "user": "junho",   "decision": "허용",     "score": 0},                       # 정상 요청을 허용한 기록
    {"rid": 105, "time": "10:20", "user": "dami",    "decision": "거부",     "score": 0},                       # 퇴사한 계정을 거부한 기록
    {"rid": 106, "time": "11:02", "user": "gaeun",   "decision": "허용",     "score": 0},                       # 정상 요청을 허용한 기록
    {"rid": 107, "time": "11:40", "user": "gaeun",   "decision": "추가확인", "score": 30},                      # 추가 확인을 요구한 기록
    {"rid": 108, "time": "13:15", "user": "junho",   "decision": "추가확인", "score": 40},                      # 추가 확인을 요구한 기록
    {"rid": 109, "time": "14:03", "user": "junho",   "decision": "허용",     "score": 0},                       # 정상 요청을 허용한 기록
    {"rid": 110, "time": "15:22", "user": "junho",   "decision": "거부",     "score": 50},                      # 점수가 쌓여 거부한 기록
    {"rid": 111, "time": "16:45", "user": "gaeun",   "decision": "거부",     "score": 50},                      # 점수가 쌓여 거부한 기록
    {"rid": 112, "time": "17:30", "user": "junho",   "decision": "허용",     "score": 0},                       # 정상 요청을 허용한 기록
]

ACCESS_LOG = [                                                                                                 # 앱이 실제로 처리한 앱 접근 기록 13건
    {"rid": 101, "time": "02:14", "user": "seoyeon", "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 102, "time": "09:02", "user": "junho",   "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 103, "time": "09:10", "user": "seoyeon", "status": 401},                                           # 앱의 응답 번호 401
    {"rid": 104, "time": "10:05", "user": "junho",   "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 105, "time": "10:20", "user": "dami",    "status": 403},                                           # 앱의 응답 번호 403
    {"rid": 106, "time": "11:02", "user": "gaeun",   "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 107, "time": "11:40", "user": "gaeun",   "status": 401},                                           # 앱의 응답 번호 401
    {"rid": 201, "time": "12:34", "user": "seoyeon", "status": 200},                                           # 정책 로그에서 본 적 없는 요청 번호
    {"rid": 108, "time": "13:15", "user": "junho",   "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 109, "time": "14:03", "user": "junho",   "status": 200},                                           # 앱의 응답 번호 200
    {"rid": 110, "time": "15:22", "user": "junho",   "status": 403},                                           # 앱의 응답 번호 403
    {"rid": 111, "time": "16:45", "user": "gaeun",   "status": 403},                                           # 앱의 응답 번호 403
    {"rid": 112, "time": "17:30", "user": "junho",   "status": 403},                                           # 앱의 응답 번호 403
]

EXPECTED = {"허용": 200, "추가확인": 401, "거부": 403}       # PDP 결정마다 앱이 내야 하는 응답 번호
STRENGTH = {200: 0, 401: 1, 403: 2}                          # 응답 번호의 세기. 숫자가 클수록 세게 막은 것

access_status = {}                                           # 요청 번호 → 앱 응답 번호를 담을 딕셔너리
for a in ACCESS_LOG:                                         # 앱 기록을 한 줄씩 꺼낸다
    access_status[a["rid"]] = a["status"]                    # 요청 번호를 키로 앱 응답 번호를 담는다

counts = {}                                                  # 유형별 개수를 담을 딕셔너리
policy_ids = []                                              # 정책 로그에 있는 요청 번호를 모을 목록
for p in POLICY_LOG:                                         # 정책 로그를 한 줄씩 꺼낸다
    policy_ids.append(p["rid"])                              # 요청 번호를 목록에 더한다
    status = access_status.get(p["rid"])                     # 같은 요청 번호의 앱 응답 번호. 없으면 None
    expected = EXPECTED[p["decision"]]                       # 이 결정에서 앱이 냈어야 하는 응답 번호
    # 1. status 가 expected 와 다르면 아래 2 ~ 4 를 한다   # ←
    if status != expected:
        # 2. STRENGTH[status] 가 STRENGTH[expected] 보다 작으면 kind 를 "집행 누락", 아니면 "과집행" 으로 정한다   # ←
        if STRENGTH[status]<STRENGTH[expected]:
            kind="집행누락"
        else:
            kind="과집행"    
        # 3. counts 에서 kind 의 개수를 1 늘린다   # ←
        counts[kind]=counts.get(kind,0)+1
        
        # 4. "[어긋남]", p["rid"], p["user"], p["decision"], status, kind 를 출력한다   # ←
        print("[어긋남]", p["rid"], p["user"], p["decision"], status, kind)

for a in ACCESS_LOG:                                         # 앱 기록을 다시 한 줄씩 꺼낸다
    user = a["user"]                                         # 이 줄의 계정 이름
    # 5. a["rid"] 가 policy_ids 에 없으면 "[우회]", a["rid"], user, a["status"] 를 출력한다   # ←
    if a["rid"] not in policy_ids:
        print("[우회]", a["rid"], user, a["status"])
        # 6. counts 에서 "우회" 의 개수를 1 늘린다   # ←
        counts["우회"] = counts.get("우회", 0) + 1

# 7. counts 를 출력한다   # ←
