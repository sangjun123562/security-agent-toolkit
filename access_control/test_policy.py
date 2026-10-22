from datetime import datetime                                    # 시각을 만드는 데 쓴다
from policy import evaluate_access                               # 오전에 만든 최종 판정 함수
from config_loader import load_json                              # 5교시에 만든 안전한 읽기 함수


def at(text):                                                    # "2026-10-22 14:00" 같은 글자를 받아
    return datetime.strptime(text, "%Y-%m-%d %H:%M")             # "연-월-일 시:분" 모양 글자를 시각으로 바꿔 리턴한다


# 1. 정상 허용 — 예시로 써 둔 테스트
ok, reason = evaluate_access("junho", "SETTLE", "QUERY", at("2026-10-22 14:00"))   # 재무의 정산 조회를 판정한다
assert ok == True and reason == "역할 권한", "1. 정상 허용"       # 허용이고 이유가 「역할 권한」이어야 한다

# ← 아래를 직접 씁니다 (6.1 의 표를 보고 씁니다)
# 2. seoyeon 의 ACCOUNT CHANGE 를 14:00 에 판정해 ok, reason 으로 받고, 거부이며 이유가 "권한 없음" 인지 assert 한다
ok, reason = evaluate_access("seoyeon", "ACCOUNT", "CHANGE", at("2026-10-22 14:00"))
assert ok == False and reason == "권한 없음", "2. 권한 없음"
# 3. seoyeon 의 SETTLE QUERY 를 17:59 에 판정해 ok, reason 으로 받고, 허용이며 이유가 "예외 1번" 인지 assert 한다
#    같은 요청을 18:00 에 판정해 ok, reason 으로 다시 받고, 거부인지 assert 한다
ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 17:59"))
assert ok == True and reason == "예외 1번", "3-1. 만료 1분 전 허용"
ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 18:00"))
assert ok == False, "3-2. 만료 정각 거부"
# 4. load_json 으로 "config/no_such.json" 을 기본값 {} 로 읽어 users 에 담고,
#    "seoyeon" 이 users 에 없는지(in 의 반대는 not in) assert 한다
users = load_json("config/no_such.json", {})
assert "seoyeon" not in users, "4. 설정 고장이면 사용자 없음"

print("테스트 4개 모두 통과")                                     # 위 assert 가 모두 지나가면 출력된다
