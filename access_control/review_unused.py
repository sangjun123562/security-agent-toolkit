from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from config_loader import load_json                              # 10/22(목)에 만든 안전한 읽기 함수를 불러온다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def load_last_used():                                            # 사용 이력 파일을 읽어 「마지막 사용 시각」 딕셔너리를 만드는 함수
    """「사용자:권한」 글자를 키로, 마지막으로 쓴 시각 글자를 값으로 하는 딕셔너리를 리턴한다."""
    last_used_map = {}                                           # 빈 딕셔너리로 시작한다
    for log in load_json("config/access_log.json", []):          # 사용 이력을 한 건씩 꺼낸다(파일이 없으면 빈 목록)
        key = f"{log['user']}:{log['permission']}"               # 「사용자:권한」 글자를 키로 만든다
        last_used_map[key] = log["last_used"]                    # 그 키의 값에 마지막 사용 시각 글자를 담는다
    return last_used_map                                         # 딕셔너리를 리턴한다


def make_unused(entry, used_text):                               # 현황의 권한 한 건과 마지막 사용 시각 글자를 받는 함수
    """권한 한 건을 복사해 "last_used" 키(마지막 사용 시각, 이력이 없으면 None)를 적어 리턴한다. 원래 권한은 바꾸지 않는다."""
    unused_entry = entry.copy()                                  # 원래 권한은 바꾸지 않고 복사한다
    unused_entry["last_used"] = used_text                        # 복사본에 마지막 사용 시각(없으면 None)을 적는다
    return unused_entry                                          # 복사본을 리턴한다


def days_since(used_text, now):                                  # 마지막 사용 시각 글자와 지금 시각을 받는 함수
    """마지막 사용 시각 글자를 시각으로 바꿔, 지금까지 안 쓴 일 수를 리턴한다."""
    used_at = datetime.strptime(used_text, TIME_FORMAT)          # 글자를 시각으로 바꾼다
    return (now - used_at).days                                  # 지금 - 마지막 사용 시각의 일 수를 리턴한다


def find_unused(access_list, last_used_map, now, limit_days):    # 현황 · 마지막 사용 시각 딕셔너리 · 지금 시각 · 기준 일 수를 받는 함수
    """마지막 사용이 limit_days 일보다 오래됐거나 사용 이력이 없는 권한을 리턴한다. 후보마다 "last_used" 키에 마지막 사용 시각(없으면 None)을 적는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 후보를 담을 빈 목록 unused 를 만든다
    unused = []
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    for entry in access_list:
    # 3.   f"{entry['user']}:{entry['permission']}" 를 key 에 담는다
        key = f"{entry['user']}:{entry['permission']}"
    # 4.   last_used_map.get(key) 를 used_text 에 담는다 (이력이 없으면 None)
        used_text = last_used_map.get(key)
    # 5.   used_text 가 None 이면 (is None, 사용 이력이 없음)
        if used_text is None:
    # 6.     make_unused(entry, None) 을 unused 에 추가한다
            unused.append(make_unused(entry, None))
    # 7.   아니고(elif), days_since(used_text, now) 가 limit_days 보다 크면 (>)
        elif days_since(used_text, now) > limit_days:
    # 8.     make_unused(entry, used_text) 를 unused 에 추가한다
            unused.append(make_unused(entry, used_text))
    # 9. unused 를 리턴한다
    return unused