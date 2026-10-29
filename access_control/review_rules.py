from datetime import datetime                                    # 글자를 시각으로 바꾸는 데 쓴다
from exception_policy import TIME_FORMAT                         # 시각 글자의 형식("%Y-%m-%d %H:%M")을 불러온다


def find_stale(access_list, now):                                # 현황 목록과 지금 시각(datetime)을 받는 함수
    """규칙에 걸려 필요 없어진 권한을 리턴한다. 걸린 권한마다 "reason" 키에 이유를 적는다."""
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. 걸린 권한을 담을 빈 목록 stale 을 만든다
    stale = []
    # 2. access_list 에서 entry 를 하나씩 꺼낸다
    for entry in access_list:
    # 3.   entry.get("expires") 를 expires 에 담는다 (역할로 받은 권한에는 이 키가 없어 None 이 된다)
        expires = entry.get("expires")
    # 4.   빈 글자 ""를 reason 에 담는다
        reason = ""
    # 5.   entry["employed"] 가 False 이면(재직이 아니면) reason 을 "퇴사한 계정" 으로 정한다
        if not entry["employed"]:
            reason = "퇴사한 계정"

    # 6.   아니고(elif), expires 가 None 이 아니면서 datetime.strptime(expires, TIME_FORMAT) 이 now 와 같거나 now 보다 이전이면(<= now) reason 을 "만료된 예외" 로 정한다
        elif expires is not None and datetime.strptime(expires, TIME_FORMAT) <= now:
            reason = "만료된 예외"
    # 7.   reason 이 빈 글자가 아니면
        if reason != "":
    # 8.     entry.copy() 를 stale_entry 에 담는다
            stale_entry = entry.copy()
    # 9.     stale_entry["reason"] 을 reason 으로 정한다
            stale_entry["reason"] = reason
    # 10.    stale 에 stale_entry 를 추가한다
            stale.append(stale_entry)
    # 11. stale 을 리턴한다
    return stale