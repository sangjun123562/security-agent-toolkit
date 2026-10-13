mac_table = {}                              # 빈 딕셔너리로 MAC 주소 표를 만든다. 처음에는 아무 MAC 주소도 모른다
mac_table["AA"] = 1                         # ① AA 가 1번 포트로 프레임을 보냈다. 출발지 AA 를 1번 포트로 적는다
dest = "AA"                                 # 달라진 줄: 목적지 MAC 주소를 AA 로 바꿨다. 첫 파일은 표에 적히지 않은 BB 였다

if dest in mac_table:                       # ② dest 가 MAC 주소 표의 키에 있으면 아래 줄을 실행한다
    print("포트", mac_table[dest], "로만")  # ③ 표에서 꺼낸 포트 번호를 넣어 출력한다
else:                                       # else 는 위 if 의 조건이 False 일 때 아래 줄을 실행한다
    print("모든 포트로")                    # ③ 표에 없으면 플러딩한다고 출력한다
