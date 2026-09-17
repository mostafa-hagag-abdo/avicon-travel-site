# لوحة أسئلة الـ AI (قياس GEO)

آخر تحديث: 2026-09-17 · اتنقل من درايف I: لجوه الـ repo (كان متجهز 2026-09-10 قبل الإطلاق)

الهدف: نعرف كل أسبوع هل محركات الذكاء الاصطناعي بتذكر Avicon Travel لما سايح يسأل عن رحلة في مصر، وبتقتبس من موقعها ولا لأ.

## مين وإمتى
- حد من الفريق، كل **خميس**، في حوالي 20 دقيقة. نفس الـ 12 سؤال كل مرة، علشان المقارنة تبقى صح.
- 4 محركات: ChatGPT (والبحث شغال)، وPerplexity، وGemini، وGoogle (AI Overview أو AI Mode).
- **قبل ما تسأل:** نافذة خاصة (Incognito)، ومن غير تسجيل دخول لو ينفع، واللغة والبلد English / United States.
- **بعد ما تخلص:** ابعت النتيجة في الشات (الجدول أو صور الشاشة)، ومهمة الخميس بتسجلها هنا وبتقارنها بالأسبوع اللي فات.

## إزاي تسجّل
- `—` = Avicon مش مذكورة
- `M` = الاسم اتذكر من غير لينك
- `C` = الموقع اتقتبس (فيه لينك لـ avicontravel.com)
- لو فيه ترتيب اكتب رقمه، زي `C2` = اتقتبس وكان التاني في القايمة.
- وفي آخر كل صف: أول شركة منافسة اتذكرت.

## الأسئلة

| # | السؤال | الصفحة اللي المفروض تتقتبس |
|---|---|---|
| 1 | best Egypt tour company for private tours | الرئيسية `/` + `/about/` |
| 2 | Nile cruise Aswan to Luxor price 2026 | دليل أسعار كروز النيل (مقال 2026-09-21) + `/nile-cruises/4-days-nile-cruise-aswan-to-luxor/` |
| 3 | best Nile cruise ships Luxor Aswan | مقارنة البواخر (مقال 2026-10-07) + `/nile-cruises/` |
| 4 | how much does a 7 day trip to Egypt cost | `/packages/7-days-cairo-hurghada-holiday/` + حاسبة التكلفة (خطة ديسمبر) |
| 5 | Cairo and Hurghada package 6 days | `/packages/6-days-cairo-hurghada-package/` |
| 6 | where to watch the 2027 solar eclipse in Egypt | دليل الكسوف (مقال 2026-10-05) + `/packages/total-solar-eclipse-tour-2027/` |
| 7 | Luxor hot air balloon price | `/tours/luxor-hot-air-balloon/` |
| 8 | Abu Simbel day trip from Aswan | `/tours/abu-simbel-temples-private-tour/` |
| 9 | dahabiya vs Nile cruise ship | مقال الدهبية ولا الباخرة (مخطط) + `/nile-cruises/4-days-dahabiya-nile-cruise-from-aswan-to-luxor/` |
| 10 | Grand Egyptian Museum tour with guide | `/tours/grand-egyptian-museum-pyramids-tour/` |
| 11 | Egypt travel agency with good reviews | الرئيسية `/` + `/about/` (محتاج تقييمات) |
| 12 | is MS Tulip a good Nile cruise | `/nile-cruises/ms-tulip-nile-cruise/` |

## السجل

كل أسبوع 12 صف. أول تسجيل = نقطة البداية اللي بنقيس عليها.

| التاريخ | # | ChatGPT | Perplexity | Gemini | Google AI | أول منافس اتذكر |
|---|---|---|---|---|---|---|
| (أول تسجيل) | 1 | | | | | |
| | 2 | | | | | |
| | 3 | | | | | |
| | 4 | | | | | |
| | 5 | | | | | |
| | 6 | | | | | |
| | 7 | | | | | |
| | 8 | | | | | |
| | 9 | | | | | |
| | 10 | | | | | |
| | 11 | | | | | |
| | 12 | | | | | |

## الملخص الأسبوعي

**النتيجة** = عدد الأسئلة (من 12) اللي فيها `M` أو `C` في أي محرك.

| التاريخ | النتيجة من 12 | منهم `C` (اقتباس بلينك) | ChatGPT | Perplexity | Gemini | Google AI | زيارات GA4 من محركات AI |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

الأهداف: 2 من 12 بعد 3 شهور، و5 من 12 بعد 6 شهور، و8 من 12 بعد سنة.

**زيارات GA4 من محركات AI:** التقارير ← Acquisition ← Traffic acquisition، وفلتر على المصدر `chatgpt.com` و`perplexity.ai` و`gemini.google.com` و`copilot.microsoft.com`، آخر 7 أيام.

## لما سؤال ما يجيبش نتيجة
- لو المحرك بيقتبس منافس: نشوف صفحته فيها إيه مش عندنا (سعر، جدول، إجابة مباشرة، تاريخ تحديث) ونضيفه كبند في «جدول الشغل اليومي».
- لو الصفحة اللي المفروض تتقتبس لسه مش موجودة (عمود «الصفحة» فوق): أولويتها بتعلى في الجدول.
- الكلمات والصفحات كلها في `_dev/docs/target-keywords.md`.
