# ZamalekSC Scraper

مشروع بسيط لعمل web scraping لموقع نادي الزمالك: `https://www.zamaleksc.com/`.

المحتويات:
- `scraper.py`: سكربر بايثون يستخرج عناوين الأخبار، روابط، تواريخ، وملخصات محتملة.
- `requirements.txt`: الحزم المطلوبة.
- `run_scraper.ps1`: سكربت PowerShell لتشغيل السكربر بسرعة.

الاعتماديات:
- Python 3.8+
- تثبيت الحزم من `requirements.txt`.

التشغيل (PowerShell):

```powershell
# إنشاء بيئة افتراضية (اختياري)
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# تثبيت الاعتماديات
pip install -r requirements.txt

# تشغيل السكربر
python scraper.py --output output.json

# أو استخدم سكربت التشغيل
.\run_scraper.ps1
```

ملاحظات:
- السكربر مرن ويجرب عدة محددات (selectors) لاستخراج الأخبار من الصفحة الرئيسية.
- بعض مواقع الويب قد تستخدم JavaScript لعرض المحتوى؛ هذا السكربر لا يقوم بتنفيذ JS. إذا لزم الأمر، يمكن إضافة دعم لـ Playwright أو Selenium.
