import json                                                   # JSON 문자열 ↔ 딕셔너리를 바꾸는 도구
from datetime import date                                     # 오늘 날짜를 얻는 도구

import llm_client                                             # 오전에 만든 llm_client.py 를 불러온다
import event_summarizer                                       # 오전에 만든 event_summarizer.py 를 불러온다
import report_generator                                       # 오후에 만든 report_generator.py 를 불러온다
import notifier                                               # 3교시에 만든 notifier.py 를 불러온다


def run_report(events, today):                                # 요약 → 정렬 → 총평 → 저장을 묶은 함수
    summaries = event_summarizer.summarize_events(events)     # 묶음으로 나눠 요약한다 — LLM
    # 위험도순으로 정렬한다
    sorted_summaries = event_summarizer.sort_by_risk(summaries)
    # 총평을 받는다 — LLM 한 번
    overview = report_generator.make_overview(sorted_summaries)
    # 틀 · 숫자 · 총평으로 보고서를 만든다
    report = report_generator.build_report(sorted_summaries, overview, today)
    filename = report_generator.save_report(report, today)    # 날짜가 든 파일로 저장한다
    # 결과 둘을 딕셔너리 하나로 리턴한다
    return {"filename": filename, "summaries": sorted_summaries}


def run_pipeline(config_path, today):                         # 설정 → 보고서 → 세기 → 알림을 차례로 부르는 함수
    config = notifier.load_config(config_path)                # 설정을 검사하며 읽는다
    if config is None:                                        # 설정에 빠진 키가 있으면
        print("[중단] config.json 을 고친 뒤 다시 실행하세요")             # 왜 멈췄는지 알린다
        return                                                # 더 가지 않고 함수를 끝낸다

    llm_client.MODEL = config["model"]                        # 모델 이름도 설정 파일에서 온다
    with open("events_1008.json", encoding="utf-8") as f:     # 오늘 처리할 경보 파일을 연다
        events = json.load(f)                                 # 경보 목록을 리스트로 읽는다
    result = run_report(events, today)                        # 보고서를 만든다 — LLM 두 번

    approve = 0                                               # 사람 확인이 필요한 건수. 0 에서 시작
    for s in result["summaries"]:                             # 정렬된 요약을 하나씩
        if notifier.needs_approval(s["risk_level"], config):  # 사람에게 확인받을 위험도면
            approve = approve + 1                             # 하나 센다

    # 알림으로 보낼 한 줄
    message = f"[보고서] {result['filename']} 저장 · 사람 확인 필요 {approve}건"
    notifier.notify(message, config["webhook_url"])           # 알림 — 실패해도 멈추지 않는다
    print(message)                                            # 보낸 알림을 화면에도 보여 준다


if __name__ == "__main__":                                    # python pipeline.py 로 직접 실행할 때만
    run_pipeline("config.json", str(date.today()))            # 오늘 날짜로 처음부터 끝까지 돌린다
