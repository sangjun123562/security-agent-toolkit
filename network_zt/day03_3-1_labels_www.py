name = "www.example.com"      # 레이블로 나눠 볼 도메인 이름을 name 에 담는다
parts = name.split(".")       # split(".") 로 이름을 점마다 잘라 리스트를 parts 에 담는다
print(parts[-1])              # 리스트[-1] 로 마지막 요소를 꺼내 출력한다
print(".".join(parts[-2:]))   # 끝의 두 요소를 꺼내 점으로 이어 붙인 글자를 출력한다
print(list(reversed(parts)))  # 요소를 뒤에서부터 꺼낸 리스트를 출력한다
