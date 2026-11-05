import json                                                      # JSON 파일을 읽는 모듈을 불러온다

with open("config/roles.json", encoding="utf-8") as roles_file:  # 역할 파일을 연다
    ROLES = json.load(roles_file)                                # 역할 → 권한 리스트 딕셔너리로 읽는다
with open("config/users.json", encoding="utf-8") as users_file:  # 사용자 파일을 연다
    USERS = json.load(users_file)                                # 사용자 → 정보 딕셔너리로 읽는다


def check_permission(user, resource, action):                    # 사용자 · 자원 · 행위를 받는 함수
    """요청을 허용할지 (허용 여부, 이유)로 리턴한다. 요청이 들어올 때 가장 먼저 쓰는 판정이고, 허용 리스트에 없으면 모두 거부한다."""
    if user not in USERS:                                        # 사용자 파일에 없는 계정이면
        return False, "등록되지 않은 사용자"                     # 바로 거부하고 함수를 끝낸다
    if not USERS[user]["employed"]:                              # 재직 중이 아니면
        return False, "퇴사한 계정"                              # 거부하고 함수를 끝낸다
    role = USERS[user]["role"]                                   # 이 사용자의 역할을 꺼낸다
    if role not in ROLES:                                        # 역할 파일에 없는 역할이면
        return False, "역할이 없음"                              # 거부하고 함수를 끝낸다
    permission = f"{resource}:{action}"                          # "자원:행위" 모양 문자열로 합친다
    if permission not in ROLES[role]:                            # 그 역할의 권한 리스트에 없으면
        return False, "권한 없음"                                # 거부하고 함수를 끝낸다
    return True, "허용"                                          # 모든 검사를 지나면 허용한다
