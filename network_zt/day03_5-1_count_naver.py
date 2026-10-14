name = "www.naver.com"                    # 달라진 줄: 정상 도메인 이름으로 바꿨다. 첫 파일은 p0w8rk2mzq.xyz 였다
label = name.split(".")[-2]               # 점으로 나눈 리스트에서 끝에서 둘째 요소(TLD 바로 앞 레이블)를 label 에 담는다
digits = 0                                # 숫자 개수를 셀 변수를 0 으로 시작한다
vowels = 0                                # 모음 개수를 셀 변수를 0 으로 시작한다
for ch in label:                          # 레이블에서 한 글자씩 꺼내 ch 에 담아 반복한다
    if ch in "0123456789":                # ch 가 숫자이면 아래 줄을 실행한다
        digits = digits + 1               # 숫자 개수에 1 을 더한다
    if ch in "aeiou":                     # ch 가 모음이면 아래 줄을 실행한다
        vowels = vowels + 1               # 모음 개수에 1 을 더한다
print(label, len(label), digits, vowels)  # 레이블 · 글자 수 · 숫자 수 · 모음 수를 출력한다
