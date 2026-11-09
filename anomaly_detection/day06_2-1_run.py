from event_summary import load_records, pick_records_to_summarize, summarize_record, build_prompt, RISK_PATH, SUMMARY_LIMIT  # 방금 만든 함수를 불러온다

records = load_records(RISK_PATH)                                                 # 점수 파일을 기록 리스트로 읽는다
record_count = len(records)                                                       # 기록이 모두 몇 건인지 센다
print("--- 단계 1: 불러온 점수 기록", record_count, "건")                         # 단계 1 시작을 알리는 줄과 건수

picked = pick_records_to_summarize(records)                                       # 요약할 기록을 고른다
picked_count = len(picked)                                                        # 고른 기록이 몇 건인지 센다
print("--- 단계 2: 요약할 대상", picked_count, "명 (최대", SUMMARY_LIMIT, "명)")  # 단계 2 시작을 알리는 줄과 인원
for record in picked:                                                             # 고른 기록을 하나씩 꺼낸다
    print(record["grade"], record["entity"], record["score"])                     # 등급 · 대상 · 점수를 출력한다

print("--- 단계 3: AI 에게 보내는 글 (seoyeon)")                                  # 단계 3 시작을 알리는 줄
seoyeon_record = picked[1]                                                        # 두 번째 기록(seoyeon)을 꺼낸다
prompt = build_prompt(seoyeon_record)                                             # seoyeon 에게 보낼 글을 만든다
print(prompt)                                                                     # AI 에게 보내는 글을 출력한다

print("--- 단계 4: Gemini API 를 활용한 AI 요약")                                 # 단계 4 시작을 알리는 줄
for record in picked:                                                             # 고른 기록을 하나씩 꺼낸다
    summary = summarize_record(record)                                            # AI 에게 요약을 시킨다
    print(record["entity"], ":", summary)                                         # 대상과 요약 문장을 출력한다
