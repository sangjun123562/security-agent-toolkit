# 야간 보안 관제 보고 (2026-10-07)

## 건별 내역
- [brute_force] E01 211.45.12.9 에서 admin 로그인 실패 4회
- [night_login] E02 실패 4회 직후 같은 IP 에서 admin 로그인 성공
- [password_spraying] E03 한 IP 가 계정 4개에 차례로 로그인 실패
- [brute_force] E04 198.51.100.23 에서 root 로그인 실패 6회
- [permission_denied] E05 svc_backup 이 /etc/sudoers 접근 시도, 거부됨
- [failed_login] E06 kim01 로그인 실패 1회
- [failed_login] E07 park.js 로그인 실패 1회 뒤 바로 성공
- [night_login] E08 deploy 계정 토큰 만료 경고
- [brute_force] E09 203.0.113.61 에서 guest 로그인 실패 5회
- [new_ip_login] E10 lee.yh 가 처음 보는 IP 192.0.2.17 에서 로그인
- [failed_login] E11 choi.mk 로그인 실패 2회
- [permission_denied] E12 guest01 이 /etc/shadow 접근 시도, 거부됨
- [port_scan] E13 한 IP 가 1분 동안 포트 120개에 접속 시도
- [failed_login] E14 jung.hw 로그인 실패 1회
- [night_login] E15 svc_batch 새벽 로그인 실패
- [account_created] E16 admin 로그인 직후 관리자 권한 계정 tmp_admin 생성
- [failed_login] E17 kim.cs 로그인 실패 1회
- [config_changed] E18 점검 시간에 ops.kim 이 방화벽 규칙 1개 수정
