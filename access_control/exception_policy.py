import json                                                      # JSON 파일을 읽는 모듈을 불러온다
from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다

with open("config/exceptions.json", encoding="utf-8") as f:      # 예외 파일을 연다
    EXCEPTIONS = json.load(f)                                    # 예외 딕셔너리들의 목록으로 읽는다

TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 만료 시각 글자의 형식


def find_exception(user, permission, now):                       # 사용자 · "자원:행위" · 지금 시각을 받는 함수
    """now 시각에 유효한 예외가 있으면 (True, 예외 번호), 없으면 (False, None)을 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. EXCEPTIONS 에서 예외 exc 를 하나씩 꺼낸다
    for exc in EXCEPTIONS:
    # 2.   exc 의 "user" 가 user 와 같고 "permission" 이 permission 과 같으면
        if exc["user"] == user and exc["permission"] == permission:
    # 3.     exc 의 "expires" 를 TIME_FORMAT 으로 시각으로 바꿔 expires 에 담는다
            expires = datetime.strptime(exc["expires"], TIME_FORMAT)
    # 4.     now 가 expires 보다 앞이면 True 와 exc 의 "id" 를 리턴한다
            if now < expires:
                return  True, exc["id"]
    # 5. 반복이 끝날 때까지 못 찾았으면 False, None 을 리턴한다
    return False, None
