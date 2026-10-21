from rbac import check_permission                                # rbac.py 의 판정 함수를 불러온다

REQUESTS = [                                                     # 판정할 요청 목록. (사용자, 자원, 행위)
    ("seoyeon", "SALES", "QUERY"),                               # 영업이 영업 실적 조회
    ("seoyeon", "SETTLE", "QUERY"),                              # 영업이 정산 조회 (10/19(월) 사건)
    ("junho", "SETTLE", "QUERY"),                                # 재무가 정산 조회
    ("junho", "SALES", "CHANGE"),                                # 재무가 영업 실적 변경
    ("dami", "SALES", "QUERY"),                                  # 퇴사자가 영업 실적 조회
    ("minsu", "SALES", "QUERY"),                                 # 사용자 파일에 없는 계정
    ("gaeun", "ACCOUNT", "CHANGE"),                              # 계정 관리자가 권한 변경
    ("batch-night", "SETTLE", "QUERY"),                          # 서비스 계정이 정산 집계
    ("tester", "SALES", "QUERY"),                                # 역할 파일에 없는 역할(intern)
]

for user, resource, action in REQUESTS:                          # 요청을 하나씩 꺼낸다
    ok, reason = check_permission(user, resource, action)        # 판정 결과와 이유를 나눠 받는다
    print(user, resource, action, "->", ok, reason)              # 사용자 · 자원 · 행위 -> 결과 이유 를 출력한다
