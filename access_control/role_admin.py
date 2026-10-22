from rbac import ROLES                                           # 어제 rbac.py 가 읽어 둔 역할 딕셔너리를 불러온다


def assign_role(users, name, role):                              # 사용자 딕셔너리 · 이름 · 역할을 받는 함수
    """사용자에게 역할을 부여한다(입사 · 부서 이동). (성공 여부, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. role 이 ROLES 에 없으면 False, "없는 역할" 을 리턴한다
    if role not in ROLES:
        return False, "없는 역할"
    # 2. users[name] 을 {"role": role, "employed": True} 로 바꾼다(새 사용자도, 이동하는 사용자도 같은 줄이다)
    users[name] = {"role":role, "employed":True}
    # 3. True, "부여" 를 리턴한다
    return True, "부여"

def revoke_access(users, name):                                  # 사용자 딕셔너리 · 이름을 받는 함수
    """퇴사한 사용자의 접근을 회수한다. 역할은 남기고 `employed` 값만 바꾼다. (성공 여부, 이유)를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. name 이 users 에 없으면 False, "없는 사용자" 를 리턴한다
    if name not in users:
        return False, "없는 사용자"
    # 2. users[name]["employed"] 를 False 로 바꾼다
    users[name]["employed"] = False
    # 3. True, "회수" 를 리턴한다
    return True, "회수"
