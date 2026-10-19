ACCOUNTS = {                                                                      # 계정 등록 정보. 계정 이름 → 정보 딕셔너리
    "seoyeon": {"employed": True,  "device": "NB-0417", "role": "sales"},         # 재직 중, 등록 기기 NB-0417, 역할 영업
    "junho":   {"employed": True,  "device": "NB-0522", "role": "finance"},       # 재직 중, 등록 기기 NB-0522, 역할 재무
    "gaeun":   {"employed": True,  "device": "NB-0188", "role": "account_admin"}, # 재직 중, 등록 기기 NB-0188, 역할 계정 관리자
    "dami":    {"employed": False, "device": "NB-0333", "role": "sales"},         # 퇴사한 계정(employed 가 False)
}

def decide_settlement(req):                                  # 정산 내역 조회 요청 하나를 받는 함수 (3.2 와 같다)
    """정산 내역 조회 요청을 판단해 (결정, 이유 목록)을 리턴한다"""
    account = ACCOUNTS.get(req["user"])                      # 요청의 계정을 등록 정보에서 찾는다. 없으면 None
    if account is None or not account["employed"]:           # 등록 정보에 없거나 퇴사한 계정이면
        return "거부", ["재직 중인 계정이 아님"]              # 바로 거부하고 함수를 끝낸다
    if req["device"] != account["device"]:                   # 요청 기기가 이 계정의 등록 기기와 다르면
        return "거부", ["이 계정에 등록된 기기가 아님"]        # 바로 거부하고 함수를 끝낸다
    score = 0                                                # 위험 점수를 0 점에서 시작한다
    reasons = []                                             # 점수를 올린 이유를 모을 빈 목록
    if req["health"] != "ok":                                # 기기 보안 상태가 정상이 아니면
        score = score + 40                                   # 40 점을 더하고
        reasons.append("기기 보안 상태 이상 (+40)")           # 이유를 목록에 더한다
    if req["country"] != "KR":                               # 국내가 아닌 곳에서 접속했으면
        score = score + 30                                   # 30 점을 더하고
        reasons.append("해외에서 접속 (+30)")                 # 이유를 목록에 더한다
    if req["hour"] < 6:                                      # 새벽(6시 전)이면
        score = score + 20                                   # 20 점을 더하고
        reasons.append("새벽 접속 (+20)")                     # 이유를 목록에 더한다
    if req["mfa"] == False:                                  # MFA 를 하지 않았으면
        score = score + 20                                   # 20 점을 더하고
        reasons.append("MFA 안 함 (+20)")                     # 이유를 목록에 더한다
    if req["count"] >= 20:                                   # 20건 이상 조회하려 하면
        score = score + 30                                   # 30 점을 더하고
        reasons.append("대량 조회 (+30)")                     # 이유를 목록에 더한다
    if score >= 50:                                          # 합계가 50점 이상이면
        return "거부", reasons                                # 거부하고 이유 목록을 함께 리턴한다
    if score >= 20:                                          # 합계가 20점 이상이면
        return "추가확인", reasons                            # 추가 확인을 요구한다
    return "허용", reasons                                    # 그 아래면 허용한다

REQUESTS = [                                                                                                        # 지난 한 시간 동안의 요청 7건
    {"id": 1, "user": "junho",   "device": "NB-0522", "health": "ok",  "country": "KR", "hour": 14, "mfa": True,  "count": 12},   # 1번 요청
    {"id": 2, "user": "seoyeon", "device": "NB-0417", "health": "ok",  "country": "KR", "hour": 10, "mfa": True,  "count": 25},   # 2번 요청
    {"id": 3, "user": "seoyeon", "device": "NB-7741", "health": "ok",  "country": "KR", "hour": 2,  "mfa": False, "count": 40},   # 3번 요청
    {"id": 4, "user": "dami",    "device": "NB-0333", "health": "ok",  "country": "KR", "hour": 11, "mfa": True,  "count": 3},    # 4번 요청
    {"id": 5, "user": "junho",   "device": "NB-0522", "health": "off", "country": "KR", "hour": 11, "mfa": True,  "count": 5},    # 5번 요청
    {"id": 6, "user": "junho",   "device": "NB-0522", "health": "ok",  "country": "US", "hour": 3,  "mfa": True,  "count": 8},    # 6번 요청
    {"id": 7, "user": "seoyeon", "device": "NB-7741", "health": "ok",  "country": "KR", "hour": 3,  "mfa": False, "count": 35},   # 7번 요청
]

counts = {"허용": 0, "추가확인": 0, "거부": 0}               # 결정별 건수를 0 에서 시작해 센다
reason_counts = {}                                           # 거부 이유별 건수를 담을 빈 딕셔너리
for req in REQUESTS:                                         # 요청을 하나씩 꺼내 req 에 담는다
    decision, reasons = decide_settlement(req)               # 결정과 이유 목록을 한 번에 받는다
    # 1. counts 에서 decision 키의 값을 1 늘린다 (1줄)   # ←
counts[decision] = counts[decision] + 1
    # 2. decision 이 "거부" 이면 "[거부]", req["id"], req["user"], reasons 를 출력하고, reasons 의 이유마다 reason_counts[이유] 를 1 늘린다 (4줄: if, 출력, for, 늘리기)   # ←
if decision == "거부":
        print("[거부]", req["id"], req["user"], reasons)
        for r in reasons:
            reason_counts[r] = reason_counts.get(r, 0) + 1



    # 3. decision 이 "추가확인" 이면 "[추가확인]", req["id"], req["user"], reasons 를 출력한다 (2줄)   # ←
if decision == "추가확인":
        print("[추가확인]", req["id"], req["user"], reasons)

print("허용", counts["허용"], "건 / 추가확인", counts["추가확인"], "건 / 거부", counts["거부"], "건")   # 결정별 건수를 한 줄로 출력한다
print("거부 이유별 건수", reason_counts)                      # 거부 이유별 건수를 출력한다
