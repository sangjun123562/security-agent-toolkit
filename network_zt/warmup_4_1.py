import ipaddress                                  # import 로 파이썬에 들어 있는 IP 계산 모듈 ipaddress 를 불러온다

parent = ipaddress.ip_network("192.168.50.0/24")  # 나눌 전체 망 192.168.50.0/24 를 망 객체로 바꿔 parent 에 담는다

# .subnets(new_prefix=25) 는 망을 /25 크기로 나눈 블록을 앞에서부터 하나씩 리턴한다. 그 블록을 sub 에 담아 반복한다
for sub in parent.subnets(new_prefix=25):
    print(sub)                                    # 나눈 블록을 「네트워크 주소/CIDR」 꼴로 출력한다
