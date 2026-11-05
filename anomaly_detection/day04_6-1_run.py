from access_detection import load_events, EVENTS_PATH  # 2교시 함수를 불러온다
from correlation import find_chains_in_events          # 5교시 함수를 불러온다
from risk_scores import collect_findings, score_findings, collect_reasons, make_records, save_records, RISK_PATH  # 방금 만든 함수를 불러온다

events = load_events(EVENTS_PATH)                      # 이벤트 파일을 표로 읽는다
chains = find_chains_in_events(events)                 # 5교시에서 만든 연결된 사건을 찾는다
findings = collect_findings(events, chains)            # 오전 탐지와 연결 결과에서 탐지된 규칙을 모은다
finding_count = len(findings)                          # 탐지된 규칙이 모두 몇 건인지 센다
print("--- 단계 1: 탐지된 규칙", finding_count, "건")    # 단계 1 시작을 알리는 줄과 건수

totals = score_findings(findings)                      # 대상마다 점수를 더한다
print("--- 단계 2: 대상별 점수")                       # 단계 2 시작을 알리는 줄
print(totals)                                          # 점수가 높은 순으로 출력한다

reasons = collect_reasons(findings)                    # 대상마다 탐지된 규칙 이름을 모은다
records = make_records(totals, reasons)                # 점수 · 등급 · 이유를 담은 기록을 만든다
saved_count = save_records(records, RISK_PATH)         # 기록을 파일에 저장한다
print("--- 단계 3:", RISK_PATH, "에", saved_count, "건 저장")  # 단계 3 시작을 알리는 줄과 건수

print("--- 단계 4: 등급 · 대상 · 점수 · 이유")         # 단계 4 시작을 알리는 줄
for record in records:                                 # 기록을 하나씩 꺼낸다
    print(record["grade"], record["entity"], record["score"], record["reasons"])  # 등급 · 대상 · 점수 · 이유를 출력한다
