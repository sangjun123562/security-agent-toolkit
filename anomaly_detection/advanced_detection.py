from access_detection import load_events, pick_server_failures, pick_suspicious, EVENTS_PATH  # 2교시 함수를 불러온다
from saas_detection import pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users  # 3교시 함수를 불러온다
from malicious_detection import pick_web_failures, find_scan_ips  # 4교시 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다

server_failures = pick_server_failures(events)               # 판정 서버 실패 이벤트를 고른다
suspicious = pick_suspicious(server_failures)                # 실패가 반복된 사용자의 이벤트를 고른다
suspicious_count = len(suspicious)                           # 그 이벤트가 몇 개인지 센다
print("판정 서버: 먼저 확인할 실패 이벤트", suspicious_count, "개")  # 판정 서버 탐지 결과를 출력한다

saas = pick_saas(events)                                     # SaaS 이벤트를 고른다
logins = pick_logins(saas)                                   # 로그인 이벤트를 고른다
off_hours_logins = find_off_hours_logins(logins)             # 업무 시간 밖 로그인을 찾는다
off_hours_users = list(off_hours_logins["user"])             # 그 로그인의 사용자 이름만 리스트로 만든다
new_ip_users = find_new_ip_users(logins)                     # 평소와 다른 IP 로 로그인한 사용자를 찾는다
bulk_users = find_bulk_download_users(saas)                  # 대량 다운로드 사용자를 찾는다
print("SaaS: 업무 시간 밖", off_hours_users, "· 평소와 다른 IP", new_ip_users, "· 대량 다운로드", bulk_users)  # SaaS 탐지 결과를 출력한다

web_failures = pick_web_failures(events)                     # 웹 서버 실패 이벤트를 고른다
scan_ips, scan_counts = find_scan_ips(web_failures)          # 스캔으로 본 IP 를 찾는다
print("웹 서버: 스캔으로 본 IP", scan_ips)                   # 웹 탐지 결과를 출력한다
