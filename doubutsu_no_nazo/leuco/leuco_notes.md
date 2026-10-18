# ロイコクロリディウム 편 — 출처·사실 확인·자체 점검 메모

> 작성: 2026-10-18. 이 환경은 외부 사이트 직접 열람이 막혀(403) **검색 결과 요약에 인용된 내용만** 근거로 삼았다. 원문(논문 본문 등)을 직접 읽어 확인한 항목은 0건이다. 영상 공개 전에 ○·△ 항목은 원문 확인을 권장한다.

## 1. 자체 점검 결과

| 점검 항목 | 결과 | 판정 |
|---|---|---|
| 자막 한 줄 18자 초과 | **0줄** (최대 18자, 평균 10.1자, 총 717줄) | ✅ |
| 여우/소년 비율 | 여우 462줄(64.4%) / 소년 255줄(35.6%) — 기준 63/37 | ✅ (±2%p) |
| 숫자의 출처 | 사용된 숫자 13종 전부 아래 3번 표에 출처 등록, **미등록 0종**. 단 ○(검색 요약 단일 출처) 10종, △(출처 문서 불명) 3종, **원문 직접 확인 0종** | ⚠️ 부분 |
| 사람이 나오는 프롬프트 | 이미지 69 + 영상 9 프롬프트 전수 검사: 금지어(person/people/man/woman/human/child/hand/face 등) **0건**, 전부 `no people` 포함 | ✅ |
| 프롬프트 형식 | 이미지 전부 지정 접미사로 끝남, 영상 전부 `no text, no people`, 영상 카메라 동작 9종 모두 다름: slow push-in, tracking sideways, orbit around, crane-up from, drone drift, gentle pull-back, slow dolly-in, handheld-style tracking, slow tilt-up | ✅ |
| 파일 참조 무결성 | cues·manifest의 subtitle_csv_row 전부 1~717 범위 | ✅ |
| 챕터 구성 | 오프닝 + ①~⑧ + まとめ (화식조 편과 동일) | ✅ |
| 인트로 구조(지침 8-2) | 이름(ロイコクロリディウム)은 35번째 줄(챕터 ①)에서 첫 공개, 수수께끼 3개 예고, 인사·잡담 없음 | ✅ |
| 예상 길이 | 717줄 × 화식조 비율(694줄=20분31초) ≈ 21분 11초 (추정, 실제 음성 길이는 VOICEVOX 결과로 확인) | 참고 |
| 연출 | 오프닝 영상 포함 영상 9개, 이미지 69장, 모션그래픽 지시 17개, 효과음 지시 13개 | 참고 |

### 챕터별 줄 수와 비율

| 챕터 | 줄 수 | 여우 | 소년 | 소년 % |
|---|---|---|---|---|
| オープニング | 32 | 21 | 11 | 34% |
| ① 正体 | 72 | 44 | 28 | 39% |
| ② 旅の始まり | 48 | 31 | 17 | 35% |
| ③ 触角の中の変身 | 86 | 52 | 34 | 40% |
| ④ なぜ明るい場所へ | 87 | 58 | 29 | 33% |
| ⑤ イモムシの罠 | 68 | 43 | 25 | 37% |
| ⑥ 鳥のお腹の中 | 62 | 38 | 24 | 39% |
| ⑦ 本当に操っている？ | 98 | 64 | 34 | 35% |
| ⑧ 他の「操る」寄生虫 | 108 | 74 | 34 | 31% |
| まとめ | 56 | 37 | 19 | 34% |

### 한 글자씩 세어 본 방법

자막 CSV의 두 번째 열 글자 수를 파이썬 `len()`으로 센 값이다(전각 기호 포함, 일본어 한 글자 = 1). 한자 수사는 별도로 목록화해 사실 수치가 아님을 확인했다: 三つ×4, 千×1, 一×12, 一つ×7, 二×1, 三×2, 二つ×1, 四つ×1, 五つ×1, 六つ×1 (모두 「謎が三つ」「一つ目」「一段目」 같은 순서·구조 표현이고, 千=千葉県).

## 2. 출처 목록

- **S1** National Geographic「New study upholds reputation of classic parasite」(2013-12-02) https://www.nationalgeographic.com/science/phenomena/2013/12/02/new-study-upholds-reputation-of-classic-parasite/ — 1922年ドイツ論文の主張(データなし)・2013年研究 [검색 요약으로만 확인, 원문 직접 열람 불가(403)]
- **S2** Wesołowska & Wesołowski, "Do Leucochloridium sporocysts manipulate the behaviour of their snail hosts?", J. Zool. 292(3), 2014, doi:10.1111/jzo.12094 (UWr digilab https://digilab.uwr.edu.pl/en/dlibra/publication/115739/ / PDF写し https://oikosistemata.yolasite.com/resources/jz-wesolowska-leucochloridiumsnail.pdf) — 초록 수준(ビャウォヴィエジャ・Succinea putris・感染/非感染の比較・「操作の実証は不足」) [검색 요약 인용, 본문 미열람]
- **S3** Live Science "Green-banded broodsac: The brain-hijacking parasite that creates disco zombie snails" https://livescience.com/animals/snails/green-banded-broodsac-the-brain-hijacking-parasite-that-creates-disco-zombie-snails — 「ディスコゾンビ」呼称・仕組み不明 [검색 요약, 원문 열람 불가]
- **S4** Wikipedia "Leucochloridium paradoxum" https://en.wikipedia.org/wiki/Leucochloridium_paradoxum — 生活環・ブルードサック・触角 [검색 요약, 원문 열람 불가]
- **S5** GIGAZINE (2007) https://www.gigazine.net/news/20070106_leucochloridium/ — 日本語紹介(目立つ場所へ移動) [검색 요약]
- **S6** 現代ビジネス「寄生虫すごいぜ！」 https://gendai.media/articles/-/57396 — 鳥の腸管で成虫・卵はフンで排出・人には寄生しない [검색 요약]
- **S7** カラパイア https://karapaia.com/archives/51364117.html — 台湾の映像が話題 [검색 요약]
- **S8** 目黒寄生虫館 イベント情報 https://www.kiseichu.org/event/tags/開催終了/page/11 — 千葉県採集の幼虫を展示(2023年) [검색 요약]
- **S9** 学術文献の抜粋(検索結果。北大 JJVR59 https://eprints.lib.hokudai.ac.jp/repo/huscap/all/47150/JJVR59-2&3_4.pdf 等) — メタセルカリア約1.2×0.8mm・1袋に約100〜250個、日本でのオカモノアラガイ触角からの発見 [어느 문서의 수치인지 특정 불가, 원문 미열람 → △]
- **S10** Rząd et al. 2013 https://sbwp.ug.edu.pl/wp-content/uploads/2016/03/RZAD2013A.pdf — シジュウカラが宿主として調べられた [검색 요약]
- **S11** Hughes et al., BMC Ecology 11:13 (2011) https://www.biomedcentral.com/1472-6785/11/13 および ESA Blog https://esa.org/esablog/?p=5122 — ゾンビアリ: 約25cm・正午ごろ・約6時間・2〜3日後・あごの筋萎縮 [검색 요약]
- **S12** 京都大学 研究ニュース (2026-09-25) https://www.kyoto-u.ac.jp/ja/research-news/2026-09-25-1 — ハリガネムシ(成虫は数cm〜40cm)、Sawada et al. 2024 PNAS Nexus(偏光)、Mishina et al. 2023 Current Biology(遺伝子) [검색 요약]

## 3. 숫자 등록부 (대본·연출 지시에 쓴 모든 숫자)

확인 수준: ○ = 단일 2차 출처(검색 요약) / △ = 출처 문서를 특정하지 못함·단일 연구 보고 / ◎ = 원문 직접 확인(해당 없음)

| 숫자 | 의미 | 사용 횟수 | 출처 | 수준 |
|---|---|---|---|---|
| 1.2 | 幼虫1匹 約1.2mm(報告) | 1 | S9 | △ |
| 2 | 2〜3日後: 子実体が出るまで | 2 | S11 | ○ |
| 3 | 2〜3日後: 子実体が出るまで | 2 | S11 | ○ |
| 6 | 約6時間: 噛みついた後の生存時間 | 2 | S11 | ○ |
| 25 | 約25cm: ゾンビアリが死ぬ葉の高さ | 3 | S11 | ○ |
| 40 | ハリガネムシ成虫は数cm〜40cm | 3 | S12 | ○ |
| 100 | 1つの袋に100〜250匹(ある研究) | 2 | S9 | △ |
| 250 | 1つの袋に100〜250匹(ある研究) | 1 | S9 | △ |
| 1922 | 1922年: ドイツの論文の主張(データなし) | 6 | S1 | ○ |
| 2011 | 2011年: BMC Ecology(ゾンビアリ) | 1 | S11 | ○ |
| 2013 | 2013年: ポーランド野外研究(論文集の掲載号は2014年) | 6 | S1, S2 | ○ |
| 2023 | 2023年: 目黒寄生虫館の展示 / 2023年: Mishina他(ハリガネムシ遺伝子) | 3 | S8, S12 | ○ |
| 2024 | 2024年: Sawada他 PNAS Nexus(偏光) | 2 | S12 | ○ |

- 「100年」은 1922年から現在までの計算(100年以上前)이며 별도 출처 불필요. 「1つ」「1匹」은 단위 표현이다.
- 2013年: 언론은 2013年 말에 보도했고 논문집 게재 호는 2014年(vol.292)이다. 대본은 「2013年」로 썼다. 영상 공개 전에 어느 표기를 쓸지 확인할 것.
- 2023年은 두 가지 의미(① 目黒寄生虫館の展示 ② Mishina他の論文)로 쓰였다.
- △ 항목(100〜250匹, 1.2ミリ)은 대본에서 「ある研究では」「報告」 표현과 그래픽 주석(「ある研究の報告・個体差あり」)으로 한정했다.

## 4. 일부러 쓰지 않은 내용 (출처 불분명)

- 맥박 수(분당 40~75회), 달팽이가 3배 빨리 움직인다, 운동 뉴런을 장악한다, 맥박이 빛 세기에 맞춰 변한다, 발견 연도(1835년), 사망 사례 주장.
- 일본 내 분포·감염률, 새에게 주는 부담: 확인하지 못해 대본에도 「確認できなかった」로 명시.

## 5. 확인이 필요한 곳 (공개 전)

1. 논문 본문(S2)에서 감염/비감염 비교의 수치(이동 거리·높이·밝기)와 표본 수. 대본은 수치를 쓰지 않고 방향만 말함.
2. S9의 100〜250匹・1.2mm가 어느 문헌의 수치인지(종 L. paradoxum 기준인지).
3. 目黒寄生虫館의 展示 연도(2023年)와 「千葉県で採集」 내용(관장·館 공식 페이지).
4. ハリガネムシ(S12)와 BMC Ecology(S11) 수치 원문.
5. 일본 내 보고(オカモノアラガイ, Succinea lauta)의 출처 논문명.
