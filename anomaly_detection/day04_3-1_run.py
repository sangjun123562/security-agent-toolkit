from saas_detection import load_events, pick_saas, pick_logins, find_off_hours_logins, find_new_ip_users, find_bulk_download_users, EVENTS_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                            # 이벤트 파일을 표로 읽는다
saas = pick_saas(events)                                     # SaaS 이벤트만 골라낸다
logins = pick_logins(saas)                                   # 로그인 이벤트만 골라낸다

off_hours_logins = find_off_hours_logins(logins)             # 업무 시간 밖 로그인만 골라낸다
off_hours_count = len(off_hours_logins)                      # 업무 시간 밖 로그인이 몇 건인지 센다
print("--- 단계 1: 업무 시간 밖 로그인", off_hours_count, "건")  # 단계 1 시작을 알리는 줄과 건수
print(off_hours_logins)                                      # 그 로그인 표를 출력한다

new_ip_users = find_new_ip_users(logins)                     # 평소와 다른 IP 로 로그인한 사용자를 찾는다
print("--- 단계 2: 평소와 다른 IP 로 로그인한 사용자", new_ip_users)  # 단계 2 시작을 알리는 줄과 사용자

bulk_users = find_bulk_download_users(saas)                  # 파일을 대량으로 내려받은 사용자를 찾는다
print("--- 단계 3: 파일을 5번 이상 내려받은 사용자", bulk_users)  # 단계 3 시작을 알리는 줄과 사용자
