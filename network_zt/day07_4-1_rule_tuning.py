RECORDS = [                                                  # junho 의 한 주 요청 10건 + 비교용 위험 요청 1건. 모두 등록 기기 · MFA 함
    {"no": 1,  "count": 12, "country": "KR", "kind": "정상"},    # 월 09:05 정상
    {"no": 2,  "count": 38, "country": "KR", "kind": "정상"},    # 월 14:10 마감 업무 (정상)
    {"no": 3,  "count": 41, "country": "KR", "kind": "정상"},    # 화 09:02 마감 업무 (정상)
    {"no": 4,  "count": 35, "country": "KR", "kind": "정상"},    # 화 15:30 마감 업무 (정상)
    {"no": 5,  "count": 44, "country": "KR", "kind": "정상"},    # 수 09:10 마감 업무 (정상)
    {"no": 6,  "count": 8,  "country": "KR", "kind": "정상"},    # 수 16:00 정상
    {"no": 7,  "count": 39, "country": "KR", "kind": "정상"},    # 목 09:08 마감 업무 (정상)
    {"no": 8,  "count": 52, "country": "US", "kind": "위험"},    # 목 22:40 해외에서 52건 조회 (위험)
    {"no": 9,  "count": 36, "country": "KR", "kind": "정상"},    # 금 09:15 마감 업무 (정상)
    {"no": 10, "count": 6,  "country": "KR", "kind": "정상"},    # 금 13:20 정상
    {"no": 11, "count": 49, "country": "US", "kind": "위험"},    # 비교용: 해외에서 49건 조회 (위험)
]

PLANS = [("현재", 20, 30), ("A", 50, 30), ("B", 20, 10), ("C", 20, 0)]   # (안 이름, 대량 조회 기준 건수, 대량 조회 점수)

def score(count, country, threshold, points):                # 한 요청의 점수를 계산해 리턴한다
    total = 0                                                # 점수는 0 에서 시작한다
    # 1. country 가 "KR" 이 아니면(해외) total 에 30 을 더한다   # ←
    if country !="KR":
        total+=30
    # 2. count 가 threshold 이상이면 total 에 points 를 더한다   # ←
    if count >= threshold:
        total += points
    return total                                             # 점수를 리턴한다

def decide(total):                                           # 점수로 결정을 정해 리턴한다
    # 3. 50 이상이면 "거부", 20 이상이면 "추가확인", 그 밖에는 "허용" 을 리턴한다   # ←
    if total >= 50:
        return "거부"
    elif total >= 20:
        return "추가확인"
    else:
        return "허용" 

for name, threshold, points in PLANS:                        # 안을 하나씩 꺼낸다
    false_positive = 0                                       # 오탐 개수 (정상인데 허용이 아닌 것)
    false_negative = 0                                       # 미탐 개수 (위험한데 거부가 아닌 것)
    for r in RECORDS:                                        # 요청을 하나씩 꺼낸다
        d = decide(score(r["count"], r["country"], threshold, points))   # 이 안으로 계산한 결정
        # 4. r["kind"] 가 "정상" 이고 d 가 "허용" 이 아니면 false_positive 를 1 늘린다   # ←
        if r["kind"] == "정상" and d != "허용":
            false_positive += 1
        # 5. r["kind"] 가 "위험" 이고 d 가 "거부" 가 아니면 false_negative 를 1 늘린다   # ←
        if r["kind"] == "위험" and d != "거부":
            false_negative += 1
    # 6. name, "오탐", false_positive, "미탐", false_negative 를 출력한다   # ←
    print(name, "오탐", false_positive, "미탐", false_negative)
