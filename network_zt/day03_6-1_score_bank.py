name = "bnk-secure-login.xyz"          # 달라진 줄: 은행을 사칭한 이름으로 바꿨다. 첫 파일은 p0w8rk2mzq.xyz 였다
rcode = "NOERROR"                      # 달라진 줄: 공격자가 등록해 둔 이름이라 응답이 NOERROR 다. 첫 파일은 NXDOMAIN 이었다
parts = name.split(".")                # 도메인 이름을 점으로 나눈 리스트를 parts 에 담는다
score = 0                              # 합계 점수를 0 으로 시작한다
if len(parts[-2]) >= 10:               # 규칙 ①: TLD 바로 앞 레이블이 10글자 이상이면 아래 줄을 실행한다
    score = score + 1                  # 1점을 더한다
if parts[-1] in ["top", "xyz", "tk"]:  # 규칙 ②: TLD 가 세 값 가운데 하나이면 아래 줄을 실행한다
    score = score + 1                  # 1점을 더한다
if rcode == "NXDOMAIN":                # 규칙 ③: 응답이 NXDOMAIN 이면 아래 줄을 실행한다
    score = score + 2                  # 2점을 더한다
print(name, score, score >= 3)         # 이름 · 합계 점수 · 임계값 3 이상인지(True/False)를 출력한다
