from log_parse import parse_line                      # 5교시에 만든 로그 한 줄 읽기 함수를 불러온다
from log_classify import label_entries, count_groups  # 방금 만든 분류 함수를 불러온다


def show_request(item):                               # 분류를 적은 요청 한 개를 받는 함수
    """분류를 적은 요청 한 개의 주소 · 방법 · 경로 · 상태 코드를 출력한다.
    의심 · 오류로 분류한 요청을 한 줄씩 보여 줄 때 쓴다.
    """
    ip_address = item["ip"]                           # 접속자 주소를 꺼낸다
    method = item["method"]                           # 요청 방법을 꺼낸다
    path = item["path"]                               # 요청 경로를 꺼낸다
    status = item["status"]                           # 상태 코드를 꺼낸다
    print(ip_address, method, path, status)           # 주소 · 방법 · 경로 · 상태 코드를 출력한다


entries = []                                          # 읽은 요청을 모을 리스트
with open("access_sample.log", encoding="utf-8") as log_file:  # 샘플 로그 파일을 연다
    for line in log_file:                             # 파일에서 한 줄씩 꺼낸다
        entry = parse_line(line)                      # 한 줄을 읽어 딕셔너리로 바꾼다
        if entry is not None:                         # 읽을 수 있는 줄이면
            entries.append(entry)                     # 요청 리스트에 추가한다

labeled = label_entries(entries)                      # 요청마다 분류를 적는다
counts = count_groups(labeled)                        # 분류별 요청 수를 센다
total = len(labeled)                                  # 전체 요청 수를 센다
normal_count = counts["정상"]                         # 정상 요청 수를 꺼낸다
error_count = counts["오류"]                          # 오류 요청 수를 꺼낸다
suspicious_count = counts["의심"]                     # 의심 요청 수를 꺼낸다
print("--- 단계 1: 분류별 요청 수 - 전체", total, "개")  # 단계 1 시작을 알리는 줄
print("정상", normal_count, "· 오류", error_count, "· 의심", suspicious_count)  # 분류별 요청 수를 출력한다
print("--- 단계 2: 의심으로 분류한 요청")             # 단계 2 시작을 알리는 줄
for item in labeled:                                  # 분류를 적은 요청을 하나씩 꺼낸다
    if item["group"] == "의심":                       # 의심으로 분류한 요청이면
        show_request(item)                            # 주소 · 방법 · 경로 · 상태 코드를 출력한다
print("--- 단계 3: 오류로 분류한 요청")               # 단계 3 시작을 알리는 줄
for item in labeled:                                  # 분류를 적은 요청을 하나씩 꺼낸다
    if item["group"] == "오류":                       # 오류로 분류한 요청이면
        show_request(item)                            # 주소 · 방법 · 경로 · 상태 코드를 출력한다
