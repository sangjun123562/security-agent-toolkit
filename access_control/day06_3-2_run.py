import json                                                      # 경고 기준 파일을 읽는 데 쓴다
from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from checklist import TIME_FORMAT, load_state, run_checklist     # 2교시에 만든 점검 함수를 불러온다
from log_summary import read_log                                 # 3교시에 만든 로그 읽기 함수를 불러온다
from weekly_report import build_report, save_report             # 붙여 넣은 보고서 함수를 불러온다

TODAY = "2026-11-02"                                             # 보고서 날짜
NOW = datetime.strptime(TODAY + " 10:00", TIME_FORMAT)           # 점검하는 시각
with open("config/alert.json", encoding="utf-8") as alert_file:           # 경고 기준 파일을 연다
    ALERT = json.load(alert_file)                                         # 경고 기준 딕셔너리로 읽는다

print("--- 단계 1: 모으기 - 점검 결과와 요청 로그")                    # 단계 1 시작을 알리는 줄
state = load_state("config/week_state.json")                     # 점검할 데이터 파일을 읽는다
results = run_checklist(state, NOW)                              # 점검 세 가지를 실행한다
entries = read_log("week_log.jsonl")                             # 요청 로그를 읽는다
result_count = len(results)                                      # 점검이 몇 가지인지 센다
entry_count = len(entries)                                       # 요청이 몇 건인지 센다
print("점검", result_count, "가지 · 요청", entry_count, "건")    # 모은 양을 출력한다
print("--- 단계 2: 보고서 만들기와 저장")                              # 단계 2 시작을 알리는 줄
text = build_report(results, entries, ALERT, TODAY)              # 보고서 문자열을 만든다
file_name = save_report(text, TODAY)                             # 파일로 저장한다
print("저장한 파일:", file_name)                                    # 저장한 파일 이름을 출력한다
print("--- 단계 3: 저장한 보고서 내용")                                # 단계 3 시작을 알리는 줄
print(text)                                                      # 보고서 내용을 출력한다
