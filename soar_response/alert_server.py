from flask import Flask, request                              # 10/2 에 쓴 웹 서버 도구

app = Flask(__name__)                                         # 서버를 하나 만든다


@app.route("/alert", methods=["POST"])                        # /alert 로 POST 가 오면 아래 함수가 받는다
def alert():                                                  # 알림을 받는 함수
    data = request.get_json()                                 # 보낸 JSON 을 딕셔너리로 꺼낸다
    print("[알림 받음]", data["text"])                         # 터미널에 알림 내용을 보여 준다
    return {"ok": True}                                       # 받았다고 답한다 (상태 코드 200)


app.run(port=5001)                                            # 5001 번 포트에서 기다린다
