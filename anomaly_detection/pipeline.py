import json                                                                                # 보고서를 JSON 파일로 저장하기 위해 json 을 불러온다
from access_detection import load_events, EVENTS_PATH                                      # 11/5 오전 : 이벤트 파일을 읽는 함수를 불러온다
from correlation import find_chains_in_events                                              # 11/5 오후 : 서로 다른 로그를 연결하는 함수를 불러온다
from risk_scores import collect_findings, score_findings, collect_reasons, make_records, save_records, RISK_PATH  # 11/5 오후 : 탐지 · 점수 함수를 불러온다
from event_summary import pick_records_to_summarize, summarize_record, FAIL_TEXT           # 오늘 2교시 : Gemini API 를 활용한 AI 요약 함수를 불러온다

REPORT_DATE = "2026-11-02"                                                                 # 샘플 이벤트의 날짜
REPORT_PATH = "anomaly_detection_report_" + REPORT_DATE + ".json"                          # 보고서를 저장할 파일 이름


def analyze_events(events):                                                                # 이벤트 표를 받는 함수
    """이벤트에서 연결된 사건을 찾고, 탐지된 규칙을 모아 대상별 점수 기록을 만든다.
    11/5 에 하나씩 실행한 단계를 한 함수에서 이어 쓸 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 1. events 를 find_chains_in_events 에 전달해 연결된 사건을 구해 chains 에 담는다
    chains = find_chains_in_events(events)
    # 2. events 와 chains 를 collect_findings 에 전달해 탐지된 규칙 리스트를 구해 findings 에 담는다
    findings = collect_findings(events, chains)
    # 3. findings 를 score_findings 에 전달해 대상별 점수를 구해 totals 에 담는다
    totals = score_findings(findings)
    # 4. findings 를 collect_reasons 에 전달해 대상별 규칙 이름을 구해 reasons 에 담는다
    reasons = collect_reasons(findings)
    records = make_records(totals, reasons)                                                # 점수 · 등급 · 이유 기록을 만든다 — 미리 채운 줄
    return findings, records                                                               # 탐지된 규칙 리스트와 기록을 리턴한다


def summarize_records(records):                                                            # 점수 기록 리스트를 받는 함수
    """요약할 대상을 고르고 대상마다 Gemini API 를 활용한 AI 요약을 받아 리스트로 모은다.
    요약에 실패한 대상은 FAIL_TEXT 가 들어가서 나머지 결과가 그대로 이어지게 할 때 쓴다.
    """
    picked = pick_records_to_summarize(records)                                            # 요약할 대상을 고른다
    summaries = []                                                                         # 요약을 담을 빈 리스트
    for record in picked:                                                                  # 대상을 하나씩 꺼낸다
        summary = summarize_record(record)                                                 # AI 에게 요약을 시킨다
        item = {"entity": record["entity"], "grade": record["grade"], "summary": summary}  # 대상 · 등급 · 요약을 딕셔너리로 만든다
        summaries.append(item)                                                             # 요약 리스트에 추가한다
    return summaries                                                                       # 요약 리스트를 리턴한다


def count_failed(summaries):                                                               # 요약 리스트를 받는 함수
    """요약 가운데 AI 호출이 실패한 것이 몇 개인지 센다.
    실패가 있으면 담당자가 그 대상은 점수와 이유를 직접 읽어야 하므로 알릴 때 쓴다.
    """
    failed = 0                                                                             # 실패한 개수를 0 으로 시작한다
    for item in summaries:                                                                 # 요약을 하나씩 꺼낸다
        if item["summary"] == FAIL_TEXT:                                                   # 실패 문장이면
            failed = failed + 1                                                            # 실패 개수를 1 늘린다
    return failed                                                                          # 실패한 개수를 리턴한다


def build_report(events, findings, records, summaries):                                    # 이벤트 표 · 탐지된 규칙 · 점수 기록 · 요약을 받는 함수
    """분석 결과를 담당자가 읽는 보고서 딕셔너리 하나로 모은다.
    분석 결과를 파일 하나로 전달할 때 쓴다.
    """
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. events 의 "source" 열을 꺼내 .value_counts() 를 붙여 로그 종류마다 이벤트 수를 구해 source_event_counts 에 담는다
    source_event_counts = events["source"].value_counts()
    # 6. source_event_counts 에 .to_dict() 를 붙여 JSON 에 저장할 수 있는 딕셔너리로 바꿔 source_count_dict 에 담는다
    source_count_dict = source_event_counts.to_dict()
    # 7. 키 "date" 에 REPORT_DATE, "event_count" 에 len(events), "source_event_counts" 에 source_count_dict, "finding_count" 에 len(findings), "records" 에 records, "summaries" 에 summaries 를 담은 딕셔너리를 report 에 담는다
    report = {
        "date": REPORT_DATE,
        "event_count": len(events),
        "source_event_counts": source_count_dict,
        "finding_count": len(findings),
        "records": records,
        "summaries": summaries
    }
    return report                                                                          # 보고서 딕셔너리를 리턴한다


def save_report(report, path):                                                             # 보고서 딕셔너리와 파일 경로를 받는 함수
    """보고서를 JSON 파일로 저장한다.
    담당자와 다른 프로그램이 같은 파일을 읽게 할 때 쓴다.
    """
    with open(path, "w", encoding="utf-8") as file:                                        # path 파일을 쓰기 모드로 연다
        json.dump(report, file, ensure_ascii=False, indent=2)                              # 한글은 그대로, 줄을 나눠 저장한다


def run_pipeline():                                                                        # 인자가 없는 함수
    """읽기 → 분석 → 점수 저장 → Gemini API 를 활용한 AI 요약 → 보고서 저장을 차례로 실행하고 단계마다 결과를 출력한다.
    탐지부터 보고서까지 한 번에 돌릴 때 쓴다.
    """
    events = load_events(EVENTS_PATH)                                                      # 이벤트 파일을 표로 읽는다
    print("--- 단계 1: 읽은 이벤트", len(events), "개")                                    # 단계 1 : 읽은 이벤트 수

    findings, records = analyze_events(events)                                             # 연결 · 탐지 · 점수를 한 번에 실행한다
    saved_count = save_records(records, RISK_PATH)                                         # 점수 기록을 파일에 저장한다
    print("--- 단계 2: 탐지된 규칙", len(findings), "건 → 점수 기록", saved_count, "건을", RISK_PATH, "에 저장")  # 단계 2 : 탐지 · 점수

    summaries = summarize_records(records)                                                 # 대상마다 Gemini API 를 활용한 AI 요약을 받는다
    failed_count = count_failed(summaries)                                                 # 요약에 실패한 것이 몇 개인지 센다
    print("--- 단계 3: Gemini API 를 활용한 AI 요약", len(summaries), "건 (실패", failed_count, "건)")  # 단계 3 : Gemini API 를 활용한 AI 요약
    for item in summaries:                                                                 # 요약을 하나씩 꺼낸다
        print(item["entity"], ":", item["summary"])                                        # 대상과 요약 문장을 출력한다

    report = build_report(events, findings, records, summaries)                            # 보고서 딕셔너리를 만든다
    save_report(report, REPORT_PATH)                                                       # 보고서를 파일에 저장한다
    print("--- 단계 4: 보고서를", REPORT_PATH, "에 저장")                                  # 단계 4 : 보고서 저장

    print("--- 단계 5: 확인할 순서")                                                       # 단계 5 : 담당자가 볼 순서
    for record in records:                                                                 # 점수 기록을 하나씩 꺼낸다
        print(record["grade"], record["entity"], record["score"])                          # 등급 · 대상 · 점수를 출력한다
