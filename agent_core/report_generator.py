from llm_client import call_llm                               # llm_client.py 의 call_llm 을 꺼내 쓴다

# 총평 지시 — 숫자는 코드가 세므로 쓰지 말라고 한다
overview_instruction = "다음은 밤사이 보안 경보 요약입니다. 팀장에게 보고할 총평을 한국어 두세 문장으로 쓰세요. 숫자는 쓰지 마세요. 요약: "


def make_lines(sorted_summaries):                             # 정렬된 요약을 목록 줄로 만드는 함수
    lines = ""                                                # 목록 줄을 모을 빈 문자열
    for s in sorted_summaries:                                # 정렬된 요약을 하나씩 꺼낸다
        # 「- [HIGH] E01 요약」 한 줄을 붙인다
        lines = lines + f"- [{s['risk_level'].upper()}] {s['id']} {s['summary']}\n"
    return lines                                              # 목록 줄을 리턴한다


def make_overview(sorted_summaries):                          # 정렬된 요약으로 총평을 받는 함수
    # 요약 줄을 지시와 함께 보내 총평을 받는다
    text = call_llm(overview_instruction + make_lines(sorted_summaries))
    if text == "":                                            # 답을 받지 못했으면 (한도 초과 등)
        return "총평을 만들지 못했습니다. 건별 내역을 먼저 확인하세요."              # 실패를 숨기지 않고 알린다
    return text.strip()                                       # 앞뒤 공백을 지운 총평을 리턴한다


def build_report(sorted_summaries, overview, today):          # 틀 · 숫자는 코드로, 총평은 받은 문장으로 보고서를 만드는 함수
    total = len(sorted_summaries)                             # 전체 건수 — 코드가 센다
    high_count = 0                                            # high 건수. 0 에서 시작
    for s in sorted_summaries:                                # 정렬된 요약을 하나씩 꺼낸다
        if s["risk_level"].lower() == "high":                 # 소문자로 맞춰 high 인지 본다
            high_count = high_count + 1                       # high 하나를 센다

    warning = ""                                              # 기본은 경고 없음
    if high_count >= 3:                                       # high 가 3건 이상이면
        # 경고 줄 — 보고서 맨 위 「한눈에 보기」에 들어간다
        warning = f"- **주의: high 경보 {high_count}건 — 건별 내역을 먼저 확인할 것**\n"

    report = f"# 야간 보안 관제 보고 ({today})\n\n"                   # 제목 — 날짜만 바뀐다
    # 건수 줄과 경고 줄 — 코드가 센 값
    report = report + "## 한눈에 보기\n" + f"- 처리한 경보: {total}건 (high {high_count}건)\n" + warning
    report = report + "\n## 총평\n" + overview + "\n"           # 총평 — LLM 이 쓴 문장
    # 정렬한 목록 줄
    report = report + "\n## 건별 내역 (위험한 것부터)\n" + make_lines(sorted_summaries)
    return report                                             # 완성한 보고서 문자열을 리턴한다


def save_report(report, today):                               # 보고서를 날짜가 든 파일로 저장하는 함수
    filename = f"daily_report_{today.replace('-', '')}.md"    # 날짜의 - 를 빼서 파일 이름을 만든다 — daily_report_20261007.md
    with open(filename, "w", encoding="utf-8") as f:          # 보고서 파일을 쓰기로 연다 (있으면 덮어쓴다)
        f.write(report)                                       # 보고서 문자열을 파일에 쓴다
    return filename                                           # 저장한 파일 이름을 리턴한다
