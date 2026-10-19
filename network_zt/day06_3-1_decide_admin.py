ACCOUNTS = {                                                                      # 계정 등록 정보. 계정 이름 → 정보 딕셔너리
    "seoyeon": {"employed": True,  "device": "NB-0417", "role": "sales"},         # 재직 중, 등록 기기 NB-0417, 역할 영업
    "junho":   {"employed": True,  "device": "NB-0522", "role": "finance"},       # 재직 중, 등록 기기 NB-0522, 역할 재무
    "gaeun":   {"employed": True,  "device": "NB-0188", "role": "account_admin"}, # 재직 중, 등록 기기 NB-0188, 역할 계정 관리자
    "dami":    {"employed": False, "device": "NB-0333", "role": "sales"},         # 퇴사한 계정(employed 가 False)
}

HEALTH_POINTS = 50                                            # 기기 보안 상태 이상일 때 더할 점수. 0 을 알맞은 숫자로 바꾼다 (1줄)   # ←
MFA_POINTS = 25                                               # MFA 안 함일 때 더할 점수. 0 을 알맞은 숫자로 바꾼다 (1줄)   # ←
COUNTRY_POINTS = 25                                           # 해외에서 접속했을 때 더할 점수. 0 을 알맞은 숫자로 바꾼다 (1줄)   # ←

def decide_admin(req):                                       # 권한 변경 요청 하나를 받는 함수
    """권한 변경 요청을 판단해 (결정, 이유 목록)을 리턴한다"""
    account = ACCOUNTS.get(req["user"])                      # 요청의 계정을 등록 정보에서 찾는다. 없으면 None
    if account is None or not account["employed"]:           # 등록 정보에 없거나 퇴사한 계정이면
        return "거부", ["재직 중인 계정이 아님"]              # 바로 거부하고 함수를 끝낸다
    if req["device"] != account["device"]:                   # 요청 기기가 이 계정의 등록 기기와 다르면
        return "거부", ["이 계정에 등록된 기기가 아님"]        # 바로 거부하고 함수를 끝낸다
    # 1. account["role"] 이 "account_admin" 이 아니면 ["관리자 역할이 아님"] 을 이유로 바로 거부한다 (2줄)   # ←
    if account["role"] != "account_admin":
        return "거부", ["관리자 역할이 아님"]
    score = 0                                                # 위험 점수를 0 점에서 시작한다
    reasons = []                                             # 점수를 올린 이유를 모을 빈 목록
    if req["health"] != "ok":                                # 기기 보안 상태가 정상이 아니면
        score = score + HEALTH_POINTS                        # 위에서 정한 점수를 더하고
        reasons.append("기기 보안 상태 이상")                 # 이유를 목록에 더한다
    # 2. req["mfa"] 가 False 이면 score 에 MFA_POINTS 를 더하고 "MFA 안 함" 을 reasons 에 더한다 (3줄)   # ←
    if req["mfa"] == False:
        score = score + MFA_POINTS
        reasons.append("MFA 안 함")
    if req["country"] != "KR":                               # 국내가 아닌 곳에서 접속했으면
        score = score + COUNTRY_POINTS                       # 위에서 정한 점수를 더하고
        reasons.append("해외에서 접속")                       # 이유를 목록에 더한다
    if score >= 50:                                          # 합계가 50점 이상이면
        return "거부", reasons                                # 거부하고 이유 목록을 함께 리턴한다
    if score >= 10:                                          # 합계가 10점 이상이면
        return "추가확인", reasons                            # 추가 확인을 요구한다
    return "허용", reasons                                    # 그 아래면 허용한다

A = {"user": "gaeun", "device": "NB-0188", "health": "ok",  "country": "KR", "hour": 10, "mfa": True,  "count": 1}   # 요청 A
B = {"user": "junho", "device": "NB-0522", "health": "ok",  "country": "KR", "hour": 10, "mfa": True,  "count": 1}   # 요청 B
C = {"user": "gaeun", "device": "NB-0188", "health": "ok",  "country": "KR", "hour": 10, "mfa": False, "count": 1}   # 요청 C
D = {"user": "gaeun", "device": "NB-0188", "health": "off", "country": "KR", "hour": 10, "mfa": True,  "count": 1}   # 요청 D
E = {"user": "gaeun", "device": "NB-0188", "health": "ok",  "country": "US", "hour": 10, "mfa": True,  "count": 1}   # 요청 E
F = {"user": "gaeun", "device": "NB-0188", "health": "ok",  "country": "US", "hour": 10, "mfa": False, "count": 1}   # 요청 F
print("A", decide_admin(A))                                  # 요청 A 의 (결정, 이유 목록)을 출력한다
print("B", decide_admin(B))                                  # 요청 B 의 (결정, 이유 목록)을 출력한다
print("C", decide_admin(C))                                  # 요청 C 의 (결정, 이유 목록)을 출력한다
print("D", decide_admin(D))                                  # 요청 D 의 (결정, 이유 목록)을 출력한다
print("E", decide_admin(E))                                  # 요청 E 의 (결정, 이유 목록)을 출력한다
print("F", decide_admin(F))                                  # 요청 F 의 (결정, 이유 목록)을 출력한다
