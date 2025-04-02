import time

def analyze_bid(price_sheet_file, sow_file, reference_price_file=None):
    # محاكاة تحليل السعر المقدم من المقاول مقارنةً بالتقدير الذكي
    # سيتم لاحقاً ربطه فعلياً بالذكاء وسعر البنود
    time.sleep(2)

    analysis_result = {
        "السعر الإجمالي المقدم": "601,200,000 ريال",
        "السعر المرجعي الذكي": "523,750,000 ريال",
        "فرق السعر": "+77,450,000 ريال (+14.8%)",
        "الحكم": "مرتفع",
        "أمثلة على البنود المرتفعة": [
            "محولات الطاقة: مرتفعة بنسبة 22%",
            "نظام الحماية: مرتفع بنسبة 18%",
            "أعمال التأسيس: مرتفعة بنسبة 25%"
        ],
        "تعليق الذكاء": (
            "تم تصنيف العطاء على أنه مرتفع نظراً لارتفاع عدة بنود أساسية،"
            " مع وجود ظروف سوقية لا تبرر هذا الفارق الكبير."
        )
    }

    return analysis_result
