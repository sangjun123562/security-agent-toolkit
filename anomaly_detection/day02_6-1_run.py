import pandas as pd                            # 저장한 파일을 다시 읽을 수 있게 판다스를 불러온다
from events_time import load_events, add_hour, pick_failed, count_by_user, count_by_hour, save_failed, EVENTS_PATH, FAILED_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)              # 이벤트 파일을 표로 읽는다
events = add_hour(events)                      # 시각을 바꾸고 hour 열을 더한다
failed = pick_failed(events)                   # 실패한 이벤트만 골라낸다

by_user = count_by_user(failed)                # 실패 횟수를 사용자별로 센다
print("--- 단계 1: 사용자별 실패 횟수")        # 단계 1 시작을 알리는 줄
print(by_user)                                 # 많은 순서로 출력한다

by_hour = count_by_hour(failed)                # 실패 횟수를 시간대별로 센다
print("--- 단계 2: 시간대별 실패 횟수")        # 단계 2 시작을 알리는 줄
print(by_hour)                                 # 시간대 순서로 출력한다

save_failed(failed, FAILED_PATH)               # 실패한 이벤트를 CSV 로 저장한다
saved = pd.read_csv(FAILED_PATH)               # 저장한 파일을 다시 읽어 확인한다
saved_count = len(saved)                       # 저장된 행이 몇 개인지 센다
print("--- 단계 3: 저장한 파일", FAILED_PATH)  # 단계 3 시작을 알리는 줄
print("저장된 행", saved_count, "개")          # 저장된 행 수를 출력한다
