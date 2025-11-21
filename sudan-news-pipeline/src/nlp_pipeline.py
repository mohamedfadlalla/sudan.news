import os
import json
import google.generativeai as genai
from dotenv import dotenv_values

import logging
from pathlib import Path
import sys

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

# Configure Google GenAI
genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemma-3-27b-it')

logger = logging.getLogger(__name__)

def analyze_text(text: str) -> str:
    """
    تحليل النص باستخدام Google GenAI لاستخراج الكيانات المحددة وتصنيف الموضوع.

    Args:
        text (str): النص المراد تحليله (العنوان + الوصف).

    Returns:
        str: سلسلة نصية بتنسيق JSON تحتوي على المفاتيح التالية: people, cities, regions,
             countries, organizations, political_parties_and_militias, brands, job_titles, category.
             في حالة حدوث خطأ، يتم إرجاع بنية JSON فارغة.
    """
    prompt = f"""
مهمتك هي تحليل النص الإخباري العربي التالي واستخراج الكيانات المحددة بدقة.
يجب أن تكون إجابتك عبارة عن كائن JSON صالح فقط، بدون أي نصوص إضافية قبله أو بعده.

النص:
"{text}"

---

الكيانات المطلوب استخراجها:
1.  "people": أسماء الأشخاص المذكورين.
2.  "cities": أسماء المدن المذكورة (مثل: الفاشر، الخرطوم).
3.  "regions": أسماء الأقاليم أو الولايات (مثل: دارفور، شمال كردفان).
4.  "countries": أسماء الدول (مثل: السودان، الإمارات).
5.  "organizations": أسماء المنظمات والهيئات الرسمية أو الدولية (مثل: الأمم المتحدة، الاتحاد السوداني لكرة القدم).
6.  "political_parties_and_militias": أسماء الأحزاب السياسية، الحركات المسلحة، أو الميليشيات (مثل: قوات الدعم السريع، الإخوان المسلمون، حركة تحرير السودان).
7.  "brands": أسماء العلامات التجارية التجارية (مثل: تويتر، فيسبوك).
8.  "job_titles": المسميات الوظيفية والمناصب (مثل: رئيس مجلس السيادة، حاكم إقليم، سفير).
9.  "category": اختر **فئة واحدة فقط** من القائمة التالية التي تصف الموضوع الرئيسي للنص بشكل أفضل.

قائمة الفئات (اختر واحدة فقط):
- سياسة
- أمن وعسكر
- اقتصاد
- رياضة
- مجتمع وثقافة
- مقالات رأي

إذا لم تجد أي كيان من فئة معينة، أرجع قائمة فارغة `[]` لها، أما بالنسبة للفئة `category`، أرجع سلسلة نصية فارغة `""`.

أرجع المخرجات بتنسيق JSON التالي:
{{
  "people": [],
  "cities": [],
  "regions": [],
  "countries": [],
  "organizations": [],
  "political_parties_and_militias": [],
  "brands": [],
  "job_titles": [],
  "category": ""
}}
"""

    # تعريف البنية الفارغة للاستجابات أو في حالة حدوث خطأ
    empty_structure = {
        "people": [],
        "cities": [],
        "regions": [],
        "countries": [],
        "organizations": [],
        "political_parties_and_militias": [],
        "brands": [],
        "job_titles": [],
        "category": ""
    }

    try:
        # افتراض وجود نموذج مهيأ مسبقًا (model)
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # إزالة علامات markdown إذا كانت موجودة
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # تحليل JSON
        result = json.loads(response_text)

        # التحقق من البنية
        expected_keys = {
            'people', 'cities', 'regions', 'countries', 'organizations',
            'political_parties_and_militias', 'brands', 'job_titles', 'category'
        }
        if not isinstance(result, dict) or not expected_keys.issubset(result.keys()):
            logger.warning(f"Invalid response structure from model: {result}")
            return json.dumps(empty_structure, ensure_ascii=False, indent=4)

        # التأكد من أن جميع القيم (باستثناء الفئة) هي قوائم
        for key in expected_keys:
            if key != 'category' and not isinstance(result.get(key), list):
                result[key] = []

        # التأكد من أن الفئة هي سلسلة نصية
        if not isinstance(result.get('category'), str):
            result['category'] = ""

        # إرجاع النتيجة كسلسلة JSON مع ضمان عرض الحروف العربية بشكل صحيح
        return json.dumps(result, ensure_ascii=False, indent=4)

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response from model: {e}")
        logger.debug(f"Response text: {response_text}")
        return json.dumps(empty_structure, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error calling Google GenAI: {e}")
        return json.dumps(empty_structure, ensure_ascii=False, indent=4)
