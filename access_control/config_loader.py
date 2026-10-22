import json                                                      # JSON 파일을 읽는 모듈을 불러온다


def load_json(path, default):                                    # 파일 경로와 실패했을 때 쓸 기본값을 받는 함수
    """JSON 파일을 읽어 리턴한다. 파일이 없거나 깨졌으면 경고를 출력하고 default 를 리턴한다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. try: 로 시작한다
    try:
    # 2.   with open(path, encoding="utf-8") as f: 로 path 를 열어
        with open(path, encoding="utf-8") as f:
    # 3.     json.load 로 읽은 내용을 바로 리턴한다
            return json.load(f)
    # 4. except FileNotFoundError: 로 파일이 없을 때를 받는다
    except FileNotFoundError:
    # 5.   "[경고] 설정 파일 없음:" 과 path 를 출력하고
        print("[경고] 설정 파일 없음:",path)
    # 6.   default 를 리턴한다
        return default
    # 7. except json.JSONDecodeError: 로 JSON 이 깨졌을 때를 받는다
    except json.JSONDecodeError:
    # 8.   "[경고] 설정 파일 깨짐:" 과 path 를 출력하고
        print("[경고] 설정 파일 깨짐:",path)
    # 9.   default 를 리턴한다
    return default 
