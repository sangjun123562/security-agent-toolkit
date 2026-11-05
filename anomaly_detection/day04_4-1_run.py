from malicious_detection import load_events, pick_web_failures, find_scan_ips, explain_scan, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
web_failures = pick_web_failures(events)                     # 웹 서버의 실패 이벤트만 골라낸다
web_failure_count = len(web_failures)                        # 웹 실패가 모두 몇 개인지 센다
print("--- 단계 1: 웹 서버의 실패 이벤트", web_failure_count, "개")  # 단계 1 시작을 알리는 줄과 개수

scan_ips, scan_counts = find_scan_ips(web_failures)          # 스캔 IP 와 IP 별 요청 횟수를 찾는다
print("--- 단계 2: 스캐너 경로를 요청한 IP 와 횟수")          # 단계 2 시작을 알리는 줄
print(scan_counts)                                           # IP 와 요청 횟수를 출력한다

print("--- 단계 3: 스캔으로 본 IP 와 이유")                   # 단계 3 시작을 알리는 줄
for ip in scan_ips:                                          # 스캔 IP 를 하나씩 꺼낸다
    request_count = scan_counts[ip]                          # 그 IP 의 요청 횟수를 꺼낸다
    scan_info = explain_scan(ip, request_count)              # 이유 설명을 만든다
    print(scan_info)                                         # 설명을 출력한다

print("--- 단계 4: 스캐너 경로가 없어 제외한 IP")              # 단계 4 시작을 알리는 줄
all_ips = web_failures["ip"].unique()                        # 웹 실패 이벤트에 나온 IP 를 중복 없이 모은다
for ip in all_ips:                                           # IP 를 하나씩 꺼낸다
    if ip not in scan_ips:                                   # 스캔 IP 에 없으면
        print(ip)                                            # 제외한 IP 를 출력한다
