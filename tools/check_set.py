#!/usr/bin/env python3
"""썸네일·나레이션 자동 검수 (가이드 5·7·11장).

사용: python3 tools/check_set.py --l1 "1줄" --l2 "2줄" --sub "보조" --narr "나레이션" [--hook "후킹"] [--hero 김상욱]
"""
import argparse, re, sys

NAMES = {"김상욱", "우성빈"}
JOSA = sorted("은 는 이 가 을 를 에 의 도 만 까지 로 으로 와 과 한테 께서 마저 부터 처럼 이다 에서 이라더니 이래 이야 냐 다".split(), key=len, reverse=True)

def count(s):
    return len(re.sub(r"\s", "", s))

def stems(s):
    out = set()
    for t in re.findall(r"[가-힣A-Za-z0-9]+", s):
        if t in NAMES:
            continue
        st = t
        for j in JOSA:
            if st.endswith(j) and len(st) - len(j) >= 2:
                st = st[: -len(j)]
                break
        if len(st) >= 2:
            out.add(st)
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--l1", required=True); p.add_argument("--l2", required=True)
    p.add_argument("--sub", required=True); p.add_argument("--narr", required=True)
    p.add_argument("--hook", default=""); p.add_argument("--hero", default="김상욱")
    a = p.parse_args()
    errs = []
    for name, text, lim in (("1줄", a.l1, 13), ("2줄", a.l2, 13), ("보조", a.sub, 8)):
        n = count(text)
        print(f"{name}: {text} ({n}자)")
        if n > lim:
            errs.append(f"{name} {n}자 > {lim}자")
    if not (a.l2.endswith(a.hero) or a.l2.endswith("이유")):
        errs.append(f"2줄이 '{a.hero}' 또는 '이유'로 안 끝남")
    if a.narr.count(",") != 1:
        errs.append(f"나레이션 쉼표 {a.narr.count(',')}개 (1개여야 함)")
    if re.search(r"[.?!]\s*\S", a.narr.strip()):
        errs.append("나레이션이 두 문장 이상 (중간에 . ? !)")
    if a.hero not in a.narr:
        errs.append(f"나레이션에 '{a.hero}' 없음")
    if re.search(r"(울산)?시장", a.narr):
        errs.append("나레이션에 '시장' 호칭")
    parts = {"1줄": a.l1, "2줄": a.l2, "보조": a.sub, "나레이션": a.narr}
    keys = list(parts)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            # 어미가 붙은 꼴(계약/계약한)도 잡도록 앞부분이 같으면 겹침으로 본다
            common = {min(x, y, key=len) for x in stems(parts[keys[i]]) for y in stems(parts[keys[j]])
                      if x.startswith(y) or y.startswith(x)}
            if common:
                errs.append(f"단어 겹침 {keys[i]}↔{keys[j]}: {', '.join(sorted(common))}")
    if a.hook and (stems(a.hook) >= stems(a.l1) or a.l1.strip('"?') in a.hook):
        errs.append("후킹이 1줄과 같은 문장")
    print("\n" + ("통과" if not errs else "실패:\n- " + "\n- ".join(errs)))
    sys.exit(1 if errs else 0)

if __name__ == "__main__":
    main()
