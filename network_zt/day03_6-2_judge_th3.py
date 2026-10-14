LOG = [("www.naver.com", "NOERROR", "정상"), ("mail.google.com", "NOERROR", "정상"),                # 로그를 (이름, 응답, 실제) 튜플의 리스트로 만든다. 이 줄은 정상 도메인 두 개다
       ("update.microsoft.com", "NOERROR", "정상"), ("e6030.a.akamaiedge.net", "NOERROR", "정상"),  # 정상 도메인 두 개다. 「실제」는 채점할 때 쓰는 실제 분류다
       ("cdn.jsdelivr.net", "NOERROR", "정상"), ("xn--3e0b707e.kr", "NOERROR", "정상"),             # 정상 도메인 두 개다
       ("kxq3vz9a.top", "NXDOMAIN", "의심"), ("p0w8rk2mzq.xyz", "NXDOMAIN", "의심"),                # DGA 이름 두 개다
       ("qwrtpzkx7v.com", "NOERROR", "의심"), ("zzx9q2lk.top", "NXDOMAIN", "의심"),                 # DGA 이름 두 개다
       ("bnk-secure-login.xyz", "NOERROR", "의심"), ("www.example.com", "NOERROR", "정상")]         # 사칭 이름 하나와 정상 이름 하나다
THRESHOLD = 3                                                                                       # 임계값을 3 으로 정한다
print("| 이름 | 응답 | 점수 | 판정 | 실제 |")                                                       # 마크다운 표의 머리 줄을 출력한다
print("|---|---|---|---|---|")                                                                      # 마크다운 표의 구분 줄을 출력한다
for name, rcode, truth in LOG:                                                                      # 튜플을 하나씩 꺼내 이름 · 응답 · 실제를 나눠 담아 반복한다
    parts = name.split(".")                                                                         # 도메인 이름을 점으로 나눈 리스트를 parts 에 담는다
    score = 0                                                                                       # 이 이름의 점수를 0 으로 시작한다
    if len(parts[-2]) >= 10:                                                                        # 규칙 ①: TLD 바로 앞 레이블이 10글자 이상이면
        score = score + 1                                                                           # 1점을 더한다
    if parts[-1] in ["top", "xyz", "tk"]:                                                           # 규칙 ②: TLD 가 세 값 가운데 하나이면
        score = score + 1                                                                           # 1점을 더한다
    if rcode == "NXDOMAIN":                                                                         # 규칙 ③: 응답이 NXDOMAIN 이면
        score = score + 2                                                                           # 2점을 더한다
    if score >= THRESHOLD:                                                                          # 점수가 임계값 이상이면 아래 줄을 실행한다
        judged = "의심"                                                                             # 판정을 「의심」으로 정한다
    else:                                                                                           # 임계값보다 작으면 아래 줄을 실행한다
        judged = "정상"                                                                             # 판정을 「정상」으로 정한다
    print(f"| {name} | {rcode} | {score} | {judged} | {truth} |")                                   # f-string 으로 값을 넣어 표 한 줄을 출력한다
