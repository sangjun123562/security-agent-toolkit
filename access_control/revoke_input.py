from datetime import datetime                                    # 문자열을 시각으로 바꾸는 데 쓴다
from review_list import build_access_list                        # 10/29(목) 오전 2교시에 만든 현황 함수를 불러온다
from review_rules import find_stale                              # 10/29(목) 오전 3교시에 만든 규칙 점검 함수를 불러온다
from review_unused import load_last_used, find_unused            # 10/29(목) 오전 4교시에 만든 안 쓴 권한 점검 함수를 불러온다
from overprivilege import generate_report                        # 10/29(목) 5교시에 만든 리포트 함수를 불러온다
from report_exclude import load_exclude_map, split_by_exclude    # 10/29(목) 6교시에 만든 회수 제외 함수를 불러온다

REVIEW_TIME = datetime.strptime("2026-10-29 14:00", "%Y-%m-%d %H:%M")   # 어제 점검한 시각(고정). 같은 결과를 얻으려고 어제 시각을 쓴다
TIME_FORMAT = "%Y-%m-%d %H:%M"                                   # 시각 문자열의 형식


def load_to_revoke():                                            # 어제 점검 결과를 다시 만드는 함수
    """어제(10/29(목)) 5 · 6교시와 같은 방법으로 점검해서 「회수 대상」 리스트(8건)를 리턴한다."""
    access_list = build_access_list()                            # 현황을 만든다
    stale = find_stale(access_list, REVIEW_TIME)                 # 규칙에 걸린 권한을 찾는다
    last_used_map = load_last_used()                             # 마지막 사용 시각 딕셔너리를 읽는다
    unused = find_unused(access_list, last_used_map, REVIEW_TIME, 90)  # 90일 넘게 안 쓴 권한을 찾는다
    generated_at = REVIEW_TIME.strftime(TIME_FORMAT)             # 리포트를 만든 시각을 문자열로 바꾼다
    report = generate_report(access_list, stale, unused, 90, generated_at)  # 후보 리포트를 만든다
    exclude_map = load_exclude_map("config/exclude_list.json")   # 회수 제외 리스트를 읽는다
    to_revoke, excluded = split_by_exclude(report["findings"], exclude_map)   # 후보를 회수 대상과 회수 제외로 나눈다
    return to_revoke                                             # 회수 대상 리스트만 리턴한다
