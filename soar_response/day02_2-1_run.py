from incident import load_json, INCIDENTS_PATH                 # 월요일 파일의 함수를 불러온다
from enrichment import enrich_incident                         # 방금 만든 함수를 불러온다

incidents = load_json(INCIDENTS_PATH)                          # 인시던트 파일을 리스트로 읽는다
users_info = load_json("users_info.json")                      # 계정 정보 파일을 딕셔너리로 읽는다
source_ips = load_json("source_ips.json")                      # 알림이 난 접속의 IP 파일을 딕셔너리로 읽는다
trusted_ips = load_json("trusted_ips.json")                    # 신뢰 IP 파일을 리스트로 읽는다
incident_count = len(incidents)                                # 인시던트가 몇 건인지 센다
user_count = len(users_info)                                   # 계정 정보가 몇 명인지 센다
trusted_count = len(trusted_ips)                               # 신뢰 IP 가 몇 개인지 센다
print("--- 단계 1: 불러온 알림", incident_count, "건 · 계정 정보", user_count, "명 · 신뢰 IP", trusted_count, "개")  # 단계 1 시작을 알리는 줄

print("--- 단계 2: 알림마다 붙인 정보(재직 · VIP · 접속 IP)")  # 단계 2 시작을 알리는 줄
for incident in incidents:                                     # 인시던트를 하나씩 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 7. enrich_incident(incident, users_info, source_ips, trusted_ips) 를 호출한다 (인시던트에 맥락이 붙는다)
    enrich_incident(incident, users_info, source_ips, trusted_ips)
    context = incident["context"]                              # 붙은 맥락을 꺼낸다
    if context["account_known"]:                               # 계정 정보가 있으면
        if context["employed"]:                                # 재직 중이면
            employed_text = "재직"                             # 재직이라고 적는다
        else:                                                  # 아니면
            employed_text = "퇴사"                             # 퇴사라고 적는다
    else:                                                      # 계정 정보가 없으면
        employed_text = "계정 아님"                            # 계정이 아니라고 적는다
    vip_text = "아니오"                                        # 처음에는 아니오로 적는다
    if context["vip"]:                                         # VIP 이면
        vip_text = "예"                                        # 예라고 적는다
    ip_text = "없음"                                           # 처음에는 없음으로 적는다
    if context["source_ip"]:                                   # 접속 IP 가 있으면
        ip_text = context["source_ip"]                         # 그 IP 를 적는다
    trusted_text = "아니오"                                    # 처음에는 아니오로 적는다
    if context["ip_trusted"]:                                  # 신뢰 IP 이면
        trusted_text = "예"                                    # 예라고 적는다
    print(incident["id"], incident["entity"], "· 재직:", employed_text, "· VIP:", vip_text, "· 접속 IP:", ip_text, "· 신뢰 IP:", trusted_text)  # 한 줄로 출력한다

print("--- 단계 3: VIP 계정 알림 수")                          # 단계 3 시작을 알리는 줄
vip_count = 0                                                  # VIP 계정 알림 수 : 처음에는 0 이다
for incident in incidents:                                     # 인시던트를 하나씩 꺼낸다
    context = incident["context"]                              # 붙은 맥락을 꺼낸다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 8. context 의 "vip" 가 참이면 (if)
    if context["vip"]:
    # 9.   vip_count 에 vip_count + 1 을 담는다 (1 늘린다)
        vip_count = vip_count + 1
print("VIP 계정 알림", vip_count, "건")                        # VIP 계정 알림 수를 출력한다
