from incident import load_json                                                           # 월요일 파일의 함수를 불러온다
from containment_store import new_state, save_state, load_state, reset_log, append_log, make_record  # 상태 · 기록 함수를 불러온다
from ip_actions import check_ip_policy, block_ip, expire_blocks, DEFAULT_TTL             # 방금 만든 IP 조치 함수를 불러온다

allowlist_ips = load_json("config/allowlist_ips.json")                                   # 허용 목록을 읽는다
ip_users = load_json("ip_users.json")                                                    # IP 별 사용 계정을 읽는다
requests = [("INC-005", "198.51.100.90", "경로 스캔"), ("INC-009", "192.0.2.10", "경로 스캔"), ("INC-008", "192.0.2.41", "경로 스캔")]  # 차단 요청 3건 : (인시던트 번호, IP, 이유)
state = new_state()                                                                      # 처음 상태에서 시작한다
reset_log()                                                                              # 기록 파일을 비운다

print("--- 단계 1: 차단 요청 3건")                                                       # 단계 1 시작을 알리는 줄
for incident_id, ip, reason in requests:                                                 # 요청을 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. check_ip_policy(ip, allowlist_ips, ip_users) 의 결과를 refusal 에 저장한다
    refusal = check_ip_policy(ip, allowlist_ips, ip_users)
    record = make_record("IP 차단", ip, incident_id, "변경 없음", "변경 없음", refusal)  # 먼저 「바꾸지 않음」 기록을 만들어 두고 — 미리 채운 줄
    # 8. refusal 이 빈 글자("")이면 (if, ==)
    if refusal == "":
    # 9.   block_ip(ip, state, incident_id, reason, DEFAULT_TTL) 의 결과를 record 에 저장한다 (실제로 차단한 기록으로 바꾼다)
        record = block_ip(ip, state, incident_id, reason, DEFAULT_TTL)
    append_log(record)    
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다

print("--- 단계 2: 차단 뒤 차단한 IP 와 끝나는 시각")                                    # 단계 2 시작을 알리는 줄
print("차단한 IP:", state["blocked_ips"])                                                # 차단한 IP 를 출력한다
print("차단이 끝나는 시각(분):", state["block_expiry"])                                  # 끝나는 시각을 출력한다

print("--- 단계 3: 시계를 120분 뒤로 옮기고 시간이 끝난 차단 풀기")                      # 단계 3 시작을 알리는 줄
state["clock"] = state["clock"] + 120                                                    # 모의 시스템의 시계를 120분 뒤로 옮긴다
for record in expire_blocks(state, "INC-005"):                                           # 끝난 차단의 해제 기록을 하나씩 꺼낸다
    append_log(record)                                                                   # 해제 기록도 남긴다
    print(record["incident"], record["target"], "·", record["before"], "→", record["after"], "·", record["reason"])  # 기록 한 건을 출력한다
print("차단한 IP:", state["blocked_ips"])                                                # 해제 뒤 차단한 IP 를 출력한다

save_state(state)                                                                        # 상태를 파일에 저장한다
print("--- 단계 4: 파일에 저장된 값 다시 읽기")                                          # 단계 4 시작을 알리는 줄
print("차단한 IP:", load_state()["blocked_ips"])                                         # 저장된 차단 IP 를 출력한다
print("조치 기록:", len(load_json("containment_log.json")), "건")                        # 저장된 기록 수를 출력한다
