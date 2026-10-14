LOG = [("mail.naver.com", "NOERROR"), ("x7q9pz2kd.top", "NXDOMAIN"), ("login-kbbank.xyz", "NOERROR"),   # 처음 보는 로그 5건을 (이름, 응답) 튜플의 리스트로 만든다
       ("cdn.cloudflare.com", "NOERROR"), ("zq8w4n6r1m.tk", "NXDOMAIN")]                                # 나머지 두 건이다
for name, rcode in LOG:                           # 튜플을 하나씩 꺼내 이름은 name, 응답은 rcode 에 나눠 담아 반복한다
    parts = name.split(".")                       # 이름을 점으로 나눈 리스트를 parts 에 담는다
    score = 0                                     # 이 이름의 점수를 0 으로 시작한다
    if len(parts[-2]) >= 10:                      # 규칙 ①: TLD 바로 앞 레이블이 10글자 이상이면
        score = score + 1                         # 1점을 더한다
    if parts[-1] in ["top", "xyz", "tk"]:         # 규칙 ②: TLD 가 세 값 가운데 하나이면
        score = score + 1                         # 1점을 더한다
    if rcode == "NXDOMAIN":                       # 규칙 ③: 응답이 NXDOMAIN 이면
        score = score + 2                         # 2점을 더한다
    print(name, score, score >= 3)                # 이름 · 점수 · 임계값 3 이상인지(True/False)를 출력한다
