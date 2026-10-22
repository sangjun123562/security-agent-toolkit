from config_loader import load_json                              # 5-1 의 안전한 읽기 함수를 불러온다

PATHS = [                                                        # 시험할 경로 세 개
    "config/users.json",                                         # 정상 파일
    "config/users_typo.json",                                    # 이름을 잘못 적은 경로(파일이 없음)
    "config/users_broken.json",                                  # 일부러 깨진 파일
]

for path in PATHS:                                               # 경로를 하나씩 꺼낸다
    users = load_json(path, {})                                  # 안전하게 읽고, 실패하면 빈 딕셔너리
    if "seoyeon" in users:                                       # seoyeon 이 있으면
        print(path, "-> 사용자", len(users), "명을 읽음, 판정을 계속한다")   # 읽은 사용자 수를 알린다
    else:                                                        # 없으면
        print(path, "-> 사용자 0 명, 등록된 사용자가 없다")   # 빈 설정이라는 것을 알린다
