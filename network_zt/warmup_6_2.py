import ipaddress                                     # import 로 파이썬에 들어 있는 IP 계산 모듈 ipaddress 를 불러온다

routes = [("192.168.10.0/24", "직접 연결 VLAN 10"),  # 회사 망 줄을 리스트로 만든다. 튜플 하나가 (목적지 망, 다음 홉) 한 줄이고, 이 줄은 개발팀 망이다
          ("192.168.20.0/24", "직접 연결 VLAN 20"),  # 운영팀 망 줄을 넣는다. 라우터에 VLAN 20 으로 직접 이어져 있다
          ("192.168.30.0/24", "직접 연결 VLAN 30")]  # 보안팀 망 줄을 넣는다. 라우터에 VLAN 30 으로 직접 이어져 있다

dest = ipaddress.ip_address("192.168.30.5")          # ip_address() 는 주소 글자를 주소 객체로 바꿔 리턴한다. 목적지 주소 객체를 dest 에 담는다
found = False                                        # 맞는 회사 망 줄을 찾았는지 적어 두는 변수다. 아직 못 찾았으므로 False 로 시작한다

for net, hop in routes:                              # 회사 망 줄의 튜플을 하나씩 꺼내 목적지 망은 net, 다음 홉은 hop 에 나눠 담아 반복한다
    if dest in ipaddress.ip_network(net):            # 주소 in 망 은 주소가 그 망에 들어 있으면 True 가 된다. True 이면 아래 두 줄을 실행한다
        print("맞는 줄:", net, "→", hop)             # 맞는 줄의 목적지 망과 다음 홉을 출력한다
        found = True                                 # 맞는 줄을 찾았으므로 found 를 True 로 바꾼다

if found == False:                                   # 반복이 끝났는데 found 가 아직 False 이면 회사 망 줄에 하나도 맞지 않은 것이다
    print("회사 망 줄에 없음 → 기본 경로 0.0.0.0/0 (인터넷 쪽 라우터)")  # 그래서 기본 경로 줄로 보낸다고 출력한다
