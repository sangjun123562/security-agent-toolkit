LOG = [                                                         # VPN 로그인 기록을 (출발 IP, 사용자, 결과) 튜플의 리스트로 LOG 에 담는다
    ("185.220.101.4", "kim",  "fail"),                          # 해외 IP 하나에서 kim 계정 로그인이 실패했다
    ("185.220.101.4", "lee",  "fail"),                          # 같은 IP 에서 lee 계정도 실패했다
    ("185.220.101.4", "park", "fail"),                          # 같은 IP 에서 park 계정도 실패했다
    ("185.220.101.4", "choi", "fail"),                          # 같은 IP 에서 choi 계정도 실패했다
    ("211.36.10.7",   "kim",  "success"),                       # 집 IP 에서 kim 이 성공했다
    ("121.134.5.9",   "lee",  "fail"),                          # 다른 IP 에서 lee 가 실패했다
    ("121.134.5.9",   "lee",  "fail"),                          # 같은 계정으로 또 실패했다
    ("121.134.5.9",   "lee",  "success"),                       # 세 번째에 성공했다
    ("45.155.205.9",  "han",  "fail"),                          # 또 다른 해외 IP 에서 han 이 실패했다
    ("45.155.205.9",  "seo",  "fail"),                          # 같은 IP 에서 seo 도 실패했다
]                                                               # 리스트를 닫는다
failed = {}                                                     # IP 마다 「로그인에 실패한 계정」 목록을 담을 빈 딕셔너리를 failed 에 만든다
for ip, user, result in LOG:                                    # 기록을 한 줄씩 꺼내 출발 IP · 사용자 · 결과에 나눠 담아 반복한다
    if result == "fail":                                        # 결과가 fail 이면 아래를 실행한다
        users = failed.get(ip, [])                              # 이 IP 의 계정 목록을 꺼낸다. 처음 보는 IP 면 빈 리스트 [] 를 리턴한다
        if user not in users:                                   # 이 계정이 목록에 아직 없으면
            users.append(user)                                  # 목록 끝에 더한다. 같은 계정이 또 실패해도 한 번만 들어간다
        failed[ip] = users                                      # 바뀐 목록을 이 IP 의 값으로 다시 담는다
for ip in failed:                                               # IP 를 하나씩 꺼내
    if len(failed[ip]) >= 2:                                    # 달라진 줄: 기준을 서로 다른 2개 이상으로 낮췄다. 첫 파일은 3개였다
        print(ip, len(failed[ip]), failed[ip])                  # IP · 계정 수 · 계정 목록을 출력한다
