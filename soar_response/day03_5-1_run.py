from incident import load_json                                                     # 월요일 파일의 함수를 불러온다
from containment_store import load_state, LOG_PATH                                 # 4교시가 저장한 상태 · 기록 파일을 읽는 함수를 불러온다
from ip_actions import block_ip, DEFAULT_TTL                                       # 오전 3교시의 IP 차단 함수를 불러온다
from rollback import rollback_incident                                             # 방금 만든 되돌리기 함수를 불러온다

state = load_state()                                                               # 4교시가 저장한 연습용 시스템 상태를 읽는다
# ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
# 9. load_json(LOG_PATH) 의 결과를 log 에 저장한다 (4교시가 저장한 조치 기록을 읽는다)
log = load_json(LOG_PATH)
print("--- 단계 1: 4교시가 남긴 파일")                                             # 단계 1 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                         # 잠긴 계정을 출력한다
print("조치 기록:", len(log), "건")                                                # 기록 수를 출력한다
log.append(block_ip("198.51.100.90", state, "INC-005", "경로 스캔", DEFAULT_TTL))  # INC-005 의 IP 차단을 이 실행에서 추가한다
print("차단한 IP:", state["blocked_ips"])                                          # 차단한 IP 를 출력한다

for incident_id, title in [("INC-001", "단계 2: INC-001 은 오탐으로 확인됨 — 되돌리기"), ("INC-006", "단계 3: INC-006 도 오탐으로 확인됨 — 되돌리기"), ("INC-005", "단계 4: INC-005 도 오탐으로 확인됨 — 되돌리기")]:  # 되돌릴 인시던트 3건 : (번호, 제목)
    print("---", title)                                                            # 단계 제목을 출력한다
    for record in rollback_incident(incident_id, log, state):                      # 되돌리기 기록을 하나씩 꺼낸다
        print(record["incident"], record["target"], "·", record["action"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 5: 되돌린 뒤 상태")                                                # 단계 5 시작을 알리는 줄
print("잠긴 계정:", state["locked_users"])                                         # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                          # 차단한 IP 를 출력한다
