from incident import load_json, save_json, INCIDENTS_PATH                                 # 월요일 파일의 함수를 불러온다
from containment_store import new_state                                                   # 오전 2교시의 처음 상태 함수를 불러온다
from drill import handle_incident                                                         # 방금 만든 사건 처리 함수를 불러온다
from shift_report import summarize, is_failure                                            # 방금 만든 근무 보고 함수를 불러온다

extra_incidents = [{"id": "INC-008", "entity": "192.0.2.41", "grade": "low", "score": 30, "reasons": ["경로 스캔"], "status": "탐지됨"}, {"id": "INC-009", "entity": "192.0.2.10", "grade": "low", "score": 30, "reasons": ["경로 스캔"], "status": "탐지됨"}, {"id": "INC-010", "entity": "gaeun", "grade": "high", "score": 60, "reasons": ["퇴사한 계정"], "status": "탐지됨"}]  # 오늘 추가로 들어온 알림 3건 : 인사 오류로 퇴사자로 잘못 표시된 VIP, 함께 쓰는 IP, 점검 서버
incidents = load_json(INCIDENTS_PATH) + extra_incidents                                   # 월요일에 만든 알림 5건에 오늘 알림 3건을 이어 붙인다
refs = {"users_info": load_json("users_info.json"), "source_ips": load_json("source_ips.json"), "trusted_ips": load_json("trusted_ips.json"), "vip_accounts": load_json("config/vip_accounts.json"), "allowlist_ips": load_json("config/allowlist_ips.json"), "ip_users": load_json("ip_users.json")}  # 판단에 쓰는 참고 데이터를 한 딕셔너리로 모은다
state = new_state()                                                                       # 처음 상태에서 시작한다
log = []                                                                                  # 이번 실행의 조치 기록을 모을 빈 리스트
statuses = {}                                                                             # 인시던트별 처리 결과를 모을 딕셔너리

print("--- 단계 1: 알림 8건 처리")                                                        # 단계 1 시작을 알리는 줄
for incident in incidents:                                                                # 알림을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 9. handle_incident(incident, state, refs) 가 리턴한 두 값을 status 와 records 에 한 번에 받는다
    status, records = handle_incident(incident, state, refs)
    statuses[incident["id"]] = status                                                     # 처리 결과를 모아 둔다
    for record in records:                                                                # 조치 기록을 하나씩 꺼낸다
        log.append(record)                                                                # 이번 근무의 기록에 모은다
    print(incident["id"], incident["entity"], "->", status, "(조치 기록 " + str(len(records)) + "건)")  # 한 줄로 출력한다

save_json(log, "shift_log.json")                                                          # 이번 근무의 기록을 따로 저장한다 (4교시가 저장한 기록 파일은 건드리지 않는다)
print("--- 단계 2: 조치 기록")                                                            # 단계 2 시작을 알리는 줄
for record in log:                                                                        # 기록을 하나씩 꺼낸다
    print(record["incident"], record["target"], "·", record["action"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 3: 근무 보고 요약")                                                       # 단계 3 시작을 알리는 줄
print(summarize(log))                                                                     # 조치 결과를 종류별로 센 요약을 출력한다
print("잠긴 계정:", state["locked_users"])                                                # 잠긴 계정을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                 # 차단한 IP 를 출력한다

print("--- 단계 4: 담당자 확인이 필요한 건")                                              # 단계 4 시작을 알리는 줄
for incident in incidents:                                                                # 알림을 하나씩 꺼낸다
    if statuses[incident["id"]] == "승인 대기" and incident["context"]["vip"]:            # 승인 대기이고 VIP 계정이면
        print(incident["id"], incident["entity"], ": VIP 계정이라 담당자 승인이 필요함")  # 이유와 함께 출력한다
for record in log:                                                                        # 기록을 하나씩 꺼낸다
    if "승인 필요" in record["reason"]:                                                   # 이유에 「승인 필요」가 들어 있으면
        print(record["incident"], record["target"], ":", record["reason"])                # 이유와 함께 출력한다
    if is_failure(record):                                                                # 조치 후 확인에 실패한 기록이면
        print(record["incident"], record["target"], ": 조치 후 확인 실패 —", record["reason"])  # 이유와 함께 출력한다
