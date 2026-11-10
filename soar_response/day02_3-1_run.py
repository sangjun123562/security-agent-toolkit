from incident import load_json, INCIDENTS_PATH                      # 월요일 파일의 함수를 불러온다
from enrichment import enrich_incident                              # 2교시에 만든 함수를 불러온다
from routing import decide_route, apply_route                       # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                               # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                           # 계정 정보 파일을 읽는다
source_ips = load_json("source_ips.json")                           # 알림이 난 접속의 IP 파일을 읽는다
trusted_ips = load_json("trusted_ips.json")                         # 신뢰 IP 파일을 읽는다
incident_log = []                                                   # 경로 기록을 담을 빈 리스트
route_counts = {"기본": 0, "승인 필요": 0, "오탐 종료": 0}          # 경로마다 몇 건인지 셀 딕셔너리

print("--- 단계 1: 알림마다 정한 처리 경로 · 이유 · 상태")          # 단계 1 시작을 알리는 줄
for incident in incidents:                                          # 인시던트를 하나씩 꺼낸다
    enrich_incident(incident, users_info, source_ips, trusted_ips)  # 맥락을 붙인다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. decide_route(incident) 가 리턴한 두 값을 route 와 reason 에 한 번에 받는다
    route, reason = decide_route(incident)
    apply_route(incident, route, reason, incident_log)              # 경로를 적용하고 기록한다
    # 9. route_counts[route] 에 route_counts[route] + 1 을 담는다 (그 경로의 건수를 1 늘린다)
    route_counts[route] = route_counts[route] + 1
    print(incident["id"], incident["entity"], incident["grade"], "->", route, "·", reason, "(상태: " + incident["status"] + ")")  # 한 줄로 출력한다

print("--- 단계 2: 경로별 건수")                                    # 단계 2 시작을 알리는 줄
for route in route_counts:                                          # 경로를 하나씩 꺼낸다
    print(route, route_counts[route], "건")                         # 경로와 건수를 출력한다
