my_ip = "192.168.10.25"           # 변수 my_ip 에 IPv4 주소 글자를 담는다
parts = my_ip.split(".")          # .split(".") 은 글자를 점에서 나눈 리스트를 리턴한다. 마디 네 개가 담긴 리스트를 parts 에 담는다

for part in parts:                # 리스트 parts 의 마디를 앞에서부터 하나씩 part 에 담아 아래 세 줄을 반복한다
    number = int(part)            # int() 는 글자를 숫자로 바꿔 리턴한다. 마디 글자 part 를 숫자로 바꿔 number 에 담는다
    bits = format(number, "08b")  # number 를 앞자리를 0 으로 채운 8자리 2진수 글자로 바꿔 bits 에 담는다
    print(part, bits)             # 마디의 10진수 글자와 8비트 2진수 글자를 한 줄에 나란히 출력한다
