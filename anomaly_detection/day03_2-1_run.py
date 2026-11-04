from baseline import load_daily_failures, average_failures, maximum_failures, make_limit, LOGIN_PATH  # 방금 만든 함수를 불러온다

daily = load_daily_failures(LOGIN_PATH)                                                               # 지난 7일 파일을 표로 읽는다
print("--- 단계 1: 지난 7일 하루 로그인 실패 횟수")                                                   # 단계 1 시작을 알리는 줄
print(daily)                                                                                          # 표를 출력한다

average = average_failures(daily)                                                                     # 하루 평균을 구한다
rounded_average = round(average, 1)                                                                   # 소수 첫째 자리까지 반올림한다
print("--- 단계 2: 하루 평균", rounded_average, "번")                                                 # 단계 2 시작을 알리는 줄과 평균

maximum = maximum_failures(daily)                                                                     # 하루 최대를 구한다
print("--- 단계 3: 하루 최대", maximum, "번")                                                         # 단계 3 시작을 알리는 줄과 최댓값

limit = make_limit(maximum)                                                                           # 알림 기준을 정한다
print("--- 단계 4: 알림 기준(임계값)", limit, "번 이상")                                              # 단계 4 시작을 알리는 줄과 알림 기준
