import json                                                   # JSON 문자열 ↔ 딕셔너리를 바꾸는 도구
import os                                                     # 폴더 · 파일을 다루는 도구
import requests                                               # 인터넷으로 요청을 보내는 도구 (9/30)

# Gemini 에 요청을 보낼 주소
URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
MODEL = "gemini-3.5-flash-lite"                               # 쓸 모델 이름


def find_env():                                               # .env 를 지금 폴더부터 위쪽으로 찾는 함수
    folder = os.getcwd()                                      # 지금 폴더에서 시작한다
    for i in range(5):                          # 지금 폴더에서 다섯 칸 위까지 찾습니다
        path = os.path.join(folder, ".env")                   # 그 폴더 안의 .env 경로를 만든다
        if os.path.exists(path):                              # 그 파일이 있으면
            return path                                       # 찾은 경로를 리턴한다
        folder = os.path.dirname(folder)        # 한 칸 위 폴더
    return None                                               # None 을 리턴하고 여기서 끝낸다


def read_api_key():                                           # .env 에서 키를 읽어 리턴하는 함수
    api_key = None                                            # 키를 못 찾으면 None 으로 남는다
    with open(find_env(), encoding="utf-8") as f:             # .env 를 찾아 읽기로 연다
        for line in f:                                        # 파일을 한 줄씩 꺼낸다
            parts = line.strip().split("=", 1)                # 줄 끝 공백을 지우고 = 에서 둘로 나눈다
            if parts[0] == "GEMINI_API_KEY":                  # = 앞부분이 키 이름이면
                api_key = parts[1]                            # = 뒷부분이 키 값이다
    return api_key                                            # 읽은 키를 리턴한다


def call_llm(question):                                       # 질문을 받아 답 문장을 리턴하는 함수
    # 요청 헤더 — .env 에서 읽은 키를 넣는다
    headers = {"Authorization": "Bearer " + read_api_key(), "Content-Type": "application/json"}
    # 요청 본문 — 모델 · temperature 0 · 질문
    body = {"model": MODEL, "temperature": 0, "messages": [{"role": "user", "content": question}]}
    # POST 요청을 보낸다. 30초 안에 답이 없으면 멈춘다
    response = requests.post(URL, headers=headers, json=body, timeout=30)
    if response.status_code != 200:                           # 200(성공)이 아니면
        print("[LLM 호출 실패] 상태 코드", response.status_code)      # 429 면 1분 기다린 뒤 다시 실행
        return ""                                             # 실패하면 빈 문자열을 리턴한다
    data = response.json()                                    # 응답(JSON 문자열)을 딕셔너리로 바꾼다
    return data["choices"][0]["message"]["content"]           # 답 문장만 리턴한다


def parse_llm_json(text):                                     # LLM 의 답을 딕셔너리로 바꾸는 함수. 못 읽으면 None
    clean = text.replace("```json", "")                       # 코드 블록 표시 ```json 을 지운다
    clean = clean.replace("```", "")                          # 남은 ``` 를 지운다
    clean = clean.strip()                                     # 앞뒤 공백 · 줄바꿈을 지운다

    try:                                                      # 아래 줄을 해 본다
        return json.loads(clean)                              # 문자열을 딕셔너리로 바꿔 리턴한다
    except json.JSONDecodeError:                              # JSON 으로 읽지 못하면 여기로 온다
        return None                                           # None 을 리턴하고 여기서 끝낸다
