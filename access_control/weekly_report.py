from log_summary import count_by, filter_denied, deny_rate, find_heavy_users   # 3교시에 만든 집계 함수를 불러온다


def build_report(results, entries, alert, today):                # 점검 결과 · 요청 리스트 · 경고 기준 · 날짜 문자열을 받는 함수
    """점검 결과와 로그 집계를 합쳐 주간 보고서 문자열을 만든다.
    매주 정기 보고서를 만들 때 쓴다.
    """
    denied = filter_denied(entries)                              # 거부된 요청만 모은다
    total = len(entries)                                         # 전체 요청 수
    denied_count = len(denied)                                   # 거부된 요청 수
    allowed_count = total - denied_count                         # 허용된 요청 수
    rate = deny_rate(entries)                                    # 거부율(0 ~ 1)을 구한다
    percent = round(rate * 100)                                  # 거부율을 퍼센트 숫자로 바꾼다
    limit = alert["deny_rate_limit"]                             # 거부율 경고 기준(0 ~ 1)
    limit_percent = round(limit * 100)                           # 경고 기준을 퍼센트 숫자로 바꾼다
    status = "경고 없음"                                          # 먼저 경고 없음으로 둔다
    if rate >= limit:                                            # 거부율이 기준 이상이면
        status = "경고"                                           # 경고로 바꾼다
    user_limit = alert["user_denied_limit"]                      # 사용자별 거부 횟수 기준
    user_counts = count_by(denied, "user")                       # 거부된 요청을 사용자별로 센다
    heavy = find_heavy_users(user_counts, user_limit)            # 기준 이상 거부된 사용자를 찾는다

    lines = [f"# 접근통제 주간 보고서 ({today})", ""]            # 보고서 줄을 모을 리스트(제목과 빈 줄로 시작)
    lines.append("## 1. 요청 현황")                                # 첫째 절 제목
    lines.append(f"- 전체 요청: {total}건 (허용 {allowed_count}건 · 거부 {denied_count}건)")   # 요청 수
    lines.append(f"- 거부율: {percent}% (경고 기준 {limit_percent}%) -> {status}")             # 거부율과 경고 여부
    lines.append("")                                             # 빈 줄
    lines.append("## 2. 거부 사유")                                # 둘째 절 제목
    reason_counts = count_by(denied, "reason")                   # 거부된 요청을 사유별로 센다
    for reason, count in reason_counts.items():                  # 사유와 횟수를 하나씩 꺼낸다
        lines.append(f"- {reason}: {count}건")                    # 사유별 횟수를 추가한다
    lines.append("")                                             # 빈 줄
    lines.append("## 3. 점검 결과")                                # 셋째 절 제목
    for result in results:                                       # 점검 결과를 하나씩 꺼낸다
        name = result["name"]                                    # 점검 이름
        problems = result["problems"]                            # 문제가 있는 사용자 · 예외 리스트
        if len(problems) == 0:                                   # 문제가 없으면
            lines.append(f"- {name}: 통과")                       # 통과라고 추가한다
        else:                                                    # 문제가 있으면
            lines.append(f"- {name}: 실패 {problems}")            # 실패와 문제 리스트를 추가한다
    lines.append("")                                             # 빈 줄
    lines.append("## 4. 조치가 필요한 것")                          # 넷째 절 제목
    lines.append(f"- 거부 {user_limit}번 이상 사용자: {heavy}")     # 기준 이상 거부된 사용자
    for result in results:                                       # 점검 결과를 하나씩 꺼낸다
        name = result["name"]                                    # 점검 이름
        problems = result["problems"]                            # 문제가 있는 사용자 · 예외 리스트
        if len(problems) > 0:                                    # 문제가 있으면
            lines.append(f"- 확인: {name} -> {problems}")         # 확인할 것을 추가한다
    return "\n".join(lines) + "\n"                               # 줄들을 줄바꿈으로 이어 붙인 문자열을 리턴한다


def save_report(text, today):                                    # 보고서 문자열과 날짜 문자열을 받는 함수
    """보고서를 날짜가 들어간 .md 파일로 저장하고 파일 이름을 리턴한다.
    주간 보고서를 파일로 남길 때 쓴다.
    """
    file_name = f"access_control_weekly_report_{today}.md"       # 날짜가 들어간 파일 이름을 만든다
    with open(file_name, "w", encoding="utf-8") as report_file:            # 파일을 쓰기 모드("w")로 연다
        report_file.write(text)                                            # 보고서 문자열을 파일에 쓴다
    return file_name                                             # 저장한 파일 이름을 리턴한다
