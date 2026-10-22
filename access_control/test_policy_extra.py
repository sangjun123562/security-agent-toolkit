from datetime import datetime                                    # 시각을 만드는 데 쓴다
from policy import evaluate_access                               # 오전에 만든 최종 판정 함수


def at(text):                                                    # 글자를 시각으로 바꾸는 짧은 함수
    return datetime.strptime(text, "%Y-%m-%d %H:%M")             # "연-월-일 시:분" 모양 글자를 시각으로 바꿔 리턴한다


ok, reason = evaluate_access("dami", "SALES", "QUERY", at("2026-10-22 14:00"))          # 5. 팀원 제안: 퇴사자는 예외가 있어도 거부되어야 한다
assert ok == False and reason == "퇴사한 계정", "5. 퇴사자는 예외가 있어도 거부"
print("5 통과")                                                  # 5번 assert 를 지났다고 알린다

ok, reason = evaluate_access("seoyeon", "SETTLE", "QUERY", at("2026-10-22 18:00"))      # 6. 팀원 제안: 만료 정각에도 허용되어야 한다
assert ok == True, "6. 만료 정각에도 허용되어야 한다(팀원 제안)"
print("6 통과")                                                  # 6번 assert 를 지났다고 알린다
