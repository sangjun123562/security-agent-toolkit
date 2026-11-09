import json                                             # JSON 파일을 읽기 위해 json 을 불러온다
from llm_client import call_llm                         # 1과목에서 만든 LLM 호출 함수를 불러온다

RISK_PATH = "day03_risk_scores.json"                    # 읽을 점수 파일 이름(11/5 에 저장한 파일)
SUMMARY_LIMIT = 3                                       # AI 에게 요약을 시킬 대상의 최대 수
FAIL_TEXT = "(요약 실패 — 점수와 이유를 직접 확인)"     # AI 호출이 실패했을 때 대신 쓰는 문장
RULE_MEANING = {                                        # 탐지된 규칙 이름마다 사실 한 문장
    "퇴사한 계정": "퇴사한 사람의 계정으로 서버에 요청함",
    "권한 없음": "역할에 없는 권한을 서버에 요청함",
    "규칙은 허용인데 서버가 거절": "규칙으로는 허용되는 요청을 서버가 거절함",
    "업무 시간 밖 로그인": "업무 시간 밖에 SaaS 에 로그인함",
    "평소와 다른 IP": "평소와 다른 IP 에서 SaaS 에 접속함",
    "대량 다운로드": "SaaS 에서 파일을 한꺼번에 많이 내려받음",
    "경로 스캔": "없는 주소를 연달아 요청해 서버에 무엇이 있는지 확인함",
    "여러 로그 연결": "서로 다른 로그에서 한 사용자의 이벤트가 짧은 시간 안에 확인됨",
}
PROMPT_RULES = (                                        # AI 에게 주는 지시문 : 사실만 쓰게 하는 규칙
    "당신은 보안 관제 담당자를 돕는 도우미입니다. 아래 [사실]만 사용해 한국어 두 문장 이하로 요약하세요. "
    "[사실]에 없는 내용은 지어내지 말고, 공격이라고 단정하지 마세요. 먼저 확인할 것을 한 가지 제안하세요.\n"
)


def load_records(path):                                 # 점수 파일 경로를 받는 함수
    """점수 파일(JSON)을 읽어 기록 리스트로 리턴한다.
    11/5 에 저장한 대상별 점수 · 등급 · 이유를 다시 쓸 때 쓴다.
    """
    with open(path, encoding="utf-8") as file:          # 파일을 읽기 모드로 연다
        records = json.load(file)                       # JSON 글자를 리스트로 바꾼다
    return records                                      # 기록 리스트를 리턴한다


def pick_records_to_summarize(records):                 # 기록 리스트를 받는 함수
    """low 가 아닌 대상 중 앞에서부터 SUMMARY_LIMIT 명만 고른다.
    기록은 점수가 높은 순으로 저장돼 있어서, 먼저 확인할 대상부터 요약할 때 쓴다.
    """
    picked = []                                         # 고른 기록을 담을 빈 리스트
    for record in records:                              # 기록을 하나씩 꺼낸다
        # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
        # 1. record["grade"] 가 "low" 가 아니고(!=) 그리고(and) picked 의 개수(len)가 SUMMARY_LIMIT 보다 작으면 (if)
        if record["grade"] != "low" and len(picked) < SUMMARY_LIMIT:
        # 2.   picked 에 record 를 추가한다
            picked.append(record)
    return picked                                       # 고른 기록을 리턴한다


def describe_reasons(reasons):                          # 탐지된 규칙 이름 리스트를 받는 함수
    """규칙 이름마다 사실 한 문장을 찾아 세미콜론으로 이어 붙인 문자열을 리턴한다.
    AI 에게 보낼 [사실]에 탐지된 내용을 넣을 때 쓴다.
    """
    meanings = []                                       # 사실 문장을 담을 빈 리스트
    for rule in reasons:                                # 규칙 이름을 하나씩 꺼낸다
        meanings.append(RULE_MEANING[rule])             # 그 규칙의 사실 문장을 추가한다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 3. "; " 에 .join(meanings) 를 붙여 사실 문장을 이어 붙인 결과를 meaning_text 에 담는다
    meaning_text = "; ".join(meanings)
    return meaning_text                                 # 이어 붙인 문자열을 리턴한다


def build_prompt(record):                               # 기록 하나를 받는 함수
    """AI 에게 보낼 글(지시문 + 사실)을 만든다.
    점수 파일의 값만 넣어서 AI 가 다른 내용을 지어내지 못하게 할 때 쓴다.
    """
    entity = record["entity"]                           # 대상(사용자 또는 IP)
    grade = record["grade"]                             # 등급
    score = record["score"]                             # 점수
    meaning_text = describe_reasons(record["reasons"])  # 탐지된 내용을 사실 문장으로 바꾼다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 4. f-문자열 f"[사실] 대상: {entity} / 등급: {grade} / 점수: {score}점 / 탐지된 내용: {meaning_text}" 의 결과를 facts 에 담는다
    facts = f"[사실] 대상: {entity} / 등급: {grade} / 점수: {score}점 / 탐지된 내용: {meaning_text}"
    prompt = PROMPT_RULES + facts                       # 지시문과 사실을 이어 붙인다 — 미리 채운 줄
    return prompt                                       # AI 에게 보낼 글을 리턴한다


def summarize_record(record):                           # 기록 하나를 받는 함수
    """AI 에게 기록 하나의 요약을 시키고, 호출이 실패하면 FAIL_TEXT 를 리턴한다.
    AI 호출이 실패해도 나머지 작업이 멈추지 않게 할 때 쓴다.
    """
    prompt = build_prompt(record)                       # AI 에게 보낼 글을 만든다
    # ← 아래를 직접 씁니다 (주석은 두고 각 주석 바로 아래 줄에 씁니다)
    # 5. call_llm(prompt) 의 결과를 summary 에 담는다
    summary = call_llm(prompt)
    # 6. summary 가 빈 문자열("")이면 (if)
    if summary == "":
    # 7.   FAIL_TEXT 를 summary 에 담는다
        summary = FAIL_TEXT
    return summary                                      # 요약 문장을 리턴한다
