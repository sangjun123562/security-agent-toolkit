import json                                                   # JSON 문자열 ↔ 딕셔너리를 바꾸는 도구
from llm_client import call_llm, parse_llm_json               # llm_client.py 의 두 함수를 꺼내 쓴다

SIZE = 6                                                      # 한 묶음에 넣을 경보 수
# 요약 지시 — 출력 형식(JSON 배열)과 키 이름을 정한다
instruction = "다음 보안 경보 목록을 읽고, 경보마다 id, risk_level, summary 세 키를 가진 JSON 배열로만 답하세요. "
# 위험도 세 단어와 요약 길이를 정한다. 뒤에 경보 목록이 붙는다
instruction = instruction + "risk_level 은 high, medium, low 중 하나입니다. summary 는 한국어 한 문장으로 짧게 씁니다. 경보 목록: "


def summarize_batch(batch):                                   # 묶음 하나를 LLM 으로 요약하는 함수
    # 묶음을 JSON 문자열로 바꿔 지시와 함께 보낸다
    text = call_llm(instruction + json.dumps(batch, ensure_ascii=False))
    result = parse_llm_json(text)                             # 답을 딕셔너리로 바꾼다. 못 읽으면 None
    if result is None:                                        # JSON 으로 읽지 못했으면
        return []                                             # 실패하면 빈 리스트 — 다음 묶음은 계속한다
    return result                                             # 요약 리스트를 리턴한다


def summarize_events(events):                                 # 경보 전체를 묶음으로 나눠 요약하는 함수
    summaries = []                                            # 요약을 모을 빈 리스트
    for start in range(0, len(events), SIZE):                 # 0, 6, 12 … 묶음의 시작 번호
        # 묶음 하나를 요약해 한 건씩 꺼낸다
        for item in summarize_batch(events[start:start + SIZE]):
            summaries.append(item)                            # 요약 하나를 모은다
    return summaries                                          # 모은 요약을 리턴한다


def sort_by_risk(summaries):                                  # 요약을 high → medium → low 순서로 정렬하는 함수
    sorted_summaries = []                                     # 위험도순으로 모을 빈 리스트
    for level in ["high", "medium", "low"]:                   # 이 순서대로 모은다
        for s in summaries:                                   # 요약을 하나씩 꺼낸다
            if s["risk_level"].lower() == level:              # 소문자로 맞춰 지금 위험도와 같으면
                sorted_summaries.append(s)                    # 정렬 결과에 넣는다
    return sorted_summaries                                   # 정렬한 요약을 리턴한다
