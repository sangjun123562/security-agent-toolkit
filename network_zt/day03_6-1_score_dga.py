name = "p0w8rk2mzq.xyz"                # 점수를 매길 도메인 이름을 name 에 담는다
rcode = "NXDOMAIN"                     # 그 이름을 물었을 때 받은 DNS 응답을 rcode 에 담는다
parts = name.split(".")                # 도메인 이름을 점으로 나눈 리스트를 parts 에 담는다
score = 0                              # 합계 점수를 0 으로 시작한다
if len(parts[-2]) >= 10:               # 규칙 ①: TLD 바로 앞 레이블이 10글자 이상이면 아래 줄을 실행한다
    score = score + 1                  # 1점을 더한다
if parts[-1] in ["top", "xyz", "tk"]:  # 규칙 ②: TLD 가 세 값 가운데 하나이면 아래 줄을 실행한다
    score = score + 1                  # 1점을 더한다
if rcode == "NXDOMAIN":                # 규칙 ③: 응답이 NXDOMAIN 이면 아래 줄을 실행한다
    score = score + 2                  # 2점을 더한다
print(name, score, score >= 3)         # 이름 · 합계 점수 · 임계값 3 이상인지(True/False)를 출력한다
