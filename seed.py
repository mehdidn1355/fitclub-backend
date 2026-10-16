"""
اسکریپت پر کردن دیتابیس با داده‌های نمونه.
اجرا: python seed.py
"""
from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.course import Course, Lesson
from app.models.product import Product
from app.models.exercise import Exercise
from app.auth.password import hash_password


def seed():
    # ساخت جداول
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # پاک کردن داده‌های قبلی
        if db.query(User).count() > 0:
            print("پاک کردن داده‌های قبلی...")
            db.query(Lesson).delete()
            db.query(Course).delete()
            db.query(Product).delete()
            db.query(Exercise).delete()
            db.query(User).delete()
            db.commit()

        # ============ USERS ============
        print("ساخت کاربران...")

        admin = User(
            email="admin@fitclub.ir",
            hashed_password=hash_password("admin123"),
            full_name="مدیر سیستم",
            role=UserRole.ADMIN,
            avatar="👑",
        )
        db.add(admin)

        trainer1 = User(
            email="ali@fitclub.ir",
            hashed_password=hash_password("trainer123"),
            full_name="علی رضایی",
            role=UserRole.TRAINER,
            specialty="بدنسازی و فیتنس",
            bio="۱۰ سال تجربه در بدنسازی",
            avatar="💪",
            rating=5,
            sessions_count=250,
        )
        db.add(trainer1)

        trainer2 = User(
            email="sara@fitclub.ir",
            hashed_password=hash_password("trainer123"),
            full_name="سارا محمدی",
            role=UserRole.TRAINER,
            specialty="یوگا و پیلاتس",
            bio="مربی بین‌المللی یوگا",
            avatar="🧘",
            rating=5,
            sessions_count=180,
        )
        db.add(trainer2)

        trainer3 = User(
            email="reza@fitclub.ir",
            hashed_password=hash_password("trainer123"),
            full_name="رضا کریمی",
            role=UserRole.TRAINER,
            specialty="کراس‌فیت",
            bio="قهرمان کراس‌فیت ایران",
            avatar="🔥",
            rating=5,
            sessions_count=220,
        )
        db.add(trainer3)

        customer1 = User(
            email="user@fitclub.ir",
            hashed_password=hash_password("user123"),
            full_name="محمد احمدی",
            role=UserRole.CUSTOMER,
            avatar="🏃",
            plan="gold",
        )
        db.add(customer1)

        customer2 = User(
            email="sara.user@fitclub.ir",
            hashed_password=hash_password("user123"),
            full_name="سارا رضایی",
            role=UserRole.CUSTOMER,
            avatar="🏃‍♀️",
            plan="silver",
        )
        db.add(customer2)

        db.commit()
        print("✓ کاربران ساخته شدند")

        # ============ COURSES ============
        print("ساخت دوره‌ها...")

        courses_data = [
            {
                "title": "بدنسازی مقدماتی",
                "description": "اصول پایه بدنسازی، تمرینات و تغذیه برای شروع",
                "category": "بدنسازی",
                "level": "مبتدی",
                "price": 490000,
                "price_old": 690000,
                "duration": "۸ ساعت",
                "lessons_count": 24,
                "rating": 4.9,
                "students_count": 12400,
                "icon": "💪",
                "is_bestseller": True,
            },
            {
                "title": "برنامه تمرینی حجم",
                "description": "برنامه تخصصی افزایش حجم عضلانی در ۱۲ هفته",
                "category": "بدنسازی",
                "level": "متوسط",
                "price": 690000,
                "duration": "۱۲ ساعت",
                "lessons_count": 36,
                "rating": 4.8,
                "students_count": 8200,
                "icon": "🏋️",
                "is_new": True,
            },
            {
                "title": "تغذیه ورزشی",
                "description": "اصول تغذیه، مکمل‌ها و برنامه غذایی ورزشکاران",
                "category": "تغذیه",
                "level": "مبتدی",
                "price": 390000,
                "duration": "۶ ساعت",
                "lessons_count": 18,
                "rating": 4.9,
                "students_count": 15300,
                "icon": "🥗",
                "is_bestseller": True,
            },
            {
                "title": "کراس‌فیت حرفه‌ای",
                "description": "تمرینات ترکیبی کراس‌فیت برای ورزشکاران جدی",
                "category": "کراس‌فیت",
                "level": "پیشرفته",
                "price": 890000,
                "duration": "۱۵ ساعت",
                "lessons_count": 42,
                "rating": 4.7,
                "students_count": 5100,
                "icon": "🔥",
            },
            {
                "title": "یوگا و انعطاف",
                "description": "تمرینات یوگا، تنفس و افزایش انعطاف‌پذیری",
                "category": "یوگا",
                "level": "مبتدی",
                "price": 420000,
                "duration": "۷ ساعت",
                "lessons_count": 21,
                "rating": 5.0,
                "students_count": 9800,
                "icon": "🧘",
            },
            {
                "title": "کاهش وزن اصولی",
                "description": "برنامه علمی کاهش وزن بدون از دست دادن عضله",
                "category": "تغذیه",
                "level": "متوسط",
                "price": 590000,
                "duration": "۱۰ ساعت",
                "lessons_count": 30,
                "rating": 4.8,
                "students_count": 11200,
                "icon": "⚖️",
            },
        ]

        for c in courses_data:
            db.add(Course(**c))

        db.commit()
        print(f"✓ {len(courses_data)} دوره ساخته شد")

        # ============ LESSONS ============
        lessons_data = [
            {"title": "معرفی دوره", "duration": "5:30", "order": 1, "is_free": True},
            {"title": "اصول پایه بدنسازی", "duration": "15:20", "order": 2, "is_free": True},
            {"title": "تمرینات عملی", "duration": "20:15", "order": 3},
            {"title": "تکنیک‌های پیشرفته", "duration": "25:40", "order": 4},
            {"title": "برنامه تمرینی هفتگی", "duration": "30:10", "order": 5},
            {"title": "تغذیه و مکمل‌ها", "duration": "18:00", "order": 6},
            {"title": "جمع‌بندی و نتیجه", "duration": "10:25", "order": 7},
        ]

        for l in lessons_data:
            db.add(Lesson(course_id=1, **l))

        db.commit()
        print("✓ درس‌های دوره اول ساخته شدند")

        # ============ PRODUCTS ============
        print("ساخت محصولات...")

        products_data = [
            {"title": "دمبل قابل تنظیم", "category": "تجهیزات", "price": 2800000, "rating": 4.9, "stock": 12, "icon": "🏋️", "tag": "پرفروش"},
            {"title": "کتل‌بل ۱۶ کیلویی", "category": "تجهیزات", "price": 1650000, "rating": 4.8, "stock": 8, "icon": "🔔", "tag": "جدید"},
            {"title": "بطری استیل", "category": "لوازم", "price": 420000, "rating": 4.7, "stock": 50, "icon": "🍶"},
            {"title": "دستکش تمرین", "category": "پوشاک", "price": 380000, "rating": 4.6, "stock": 30, "icon": "🥊"},
            {"title": "کفش ورزشی حرفه‌ای", "category": "پوشاک", "price": 3200000, "rating": 4.9, "stock": 15, "icon": "👟", "tag": "تخفیف"},
            {"title": "پروتئین وی ۲ کیلویی", "category": "مکمل", "price": 2450000, "rating": 4.8, "stock": 25, "icon": "🥤"},
            {"title": "تشک یوگا", "category": "لوازم", "price": 890000, "rating": 4.7, "stock": 20, "icon": "🧘"},
            {"title": "طناب پرش حرفه‌ای", "category": "تجهیزات", "price": 250000, "rating": 4.5, "stock": 40, "icon": "🪢"},
        ]

        for p in products_data:
            db.add(Product(**p))

        db.commit()
        print(f"✓ {len(products_data)} محصول ساخته شد")

        # ============ EXERCISES ============
        print("ساخت حرکات...")

        exercises_data = [
            # سینه
            {"name": "پرس سینه", "name_en": "Bench Press", "muscle_group": "سینه", "animation_key": "bench_press", "icon": "🏋️", "difficulty": "متوسط", "equipment_needed": "full", "related_product_ids": "1,6"},
            {"name": "پرس بالا سینه", "name_en": "Incline Bench Press", "muscle_group": "سینه", "animation_key": "incline_press", "icon": "🏋️", "equipment_needed": "full", "related_product_ids": "1,6"},
            {"name": "قفسه سینه", "name_en": "Chest Fly", "muscle_group": "سینه", "animation_key": "chest_fly", "icon": "💪", "equipment_needed": "basic", "related_product_ids": "1"},
            {"name": "شنا سوئدی", "name_en": "Push Up", "muscle_group": "سینه", "animation_key": "push_up", "icon": "🤸", "equipment_needed": "none", "related_product_ids": "4"},

            # پشت
            {"name": "بارفیکس", "name_en": "Pull Up", "muscle_group": "پشت", "animation_key": "pull_up", "icon": "🏋️", "equipment_needed": "basic", "related_product_ids": "4"},
            {"name": "زیربغل هالتر", "name_en": "Barbell Row", "muscle_group": "پشت", "animation_key": "barbell_row", "icon": "🏋️", "equipment_needed": "full", "related_product_ids": "1,6"},
            {"name": "زیربغل سیم‌کش", "name_en": "Cable Row", "muscle_group": "پشت", "animation_key": "cable_row", "icon": "🎣", "equipment_needed": "full", "related_product_ids": "6"},

            # پا
            {"name": "اسکات", "name_en": "Squat", "muscle_group": "پا", "animation_key": "squat", "icon": "🦵", "difficulty": "متوسط", "equipment_needed": "basic", "related_product_ids": "5,7"},
            {"name": "پرس پا", "name_en": "Leg Press", "muscle_group": "پا", "animation_key": "leg_press", "icon": "🦵", "equipment_needed": "full", "related_product_ids": "5"},
            {"name": "جلو پا", "name_en": "Leg Extension", "muscle_group": "پا", "animation_key": "leg_extension", "icon": "🦵", "equipment_needed": "full", "related_product_ids": "5"},
            {"name": "پشت پا", "name_en": "Leg Curl", "muscle_group": "پا", "animation_key": "leg_curl", "icon": "🦵", "equipment_needed": "full", "related_product_ids": "5"},
            {"name": "ساق پا", "name_en": "Calf Raise", "muscle_group": "پا", "animation_key": "calf_raise", "icon": "🦶", "equipment_needed": "none", "related_product_ids": "5"},

            # سرشانه
            {"name": "پرس سرشانه", "name_en": "Shoulder Press", "muscle_group": "سرشانه", "animation_key": "shoulder_press", "icon": "🏋️", "equipment_needed": "basic", "related_product_ids": "1,6"},
            {"name": "نشر جانبی", "name_en": "Lateral Raise", "muscle_group": "سرشانه", "animation_key": "lateral_raise", "icon": "🙆", "equipment_needed": "basic", "related_product_ids": "1"},
            {"name": "نشر از جلو", "name_en": "Front Raise", "muscle_group": "سرشانه", "animation_key": "front_raise", "icon": "🙆", "equipment_needed": "basic", "related_product_ids": "1"},

            # بازو
            {"name": "جلو بازو", "name_en": "Bicep Curl", "muscle_group": "بازو", "animation_key": "bicep_curl", "icon": "💪", "equipment_needed": "basic", "related_product_ids": "1,6"},
            {"name": "پشت بازو", "name_en": "Tricep Pushdown", "muscle_group": "بازو", "animation_key": "tricep_pushdown", "icon": "💪", "equipment_needed": "full", "related_product_ids": "6"},
            {"name": "همر", "name_en": "Hammer Curl", "muscle_group": "بازو", "animation_key": "hammer_curl", "icon": "🔨", "equipment_needed": "basic", "related_product_ids": "1,4"},

            # شکم
            {"name": "کرانچ", "name_en": "Crunch", "muscle_group": "شکم", "animation_key": "crunch", "icon": "🎯", "equipment_needed": "none", "related_product_ids": "7"},
            {"name": "پلانک", "name_en": "Plank", "muscle_group": "شکم", "animation_key": "plank", "icon": "🧘", "equipment_needed": "none", "related_product_ids": "7"},
            {"name": "زیر شکم", "name_en": "Leg Raise", "muscle_group": "شکم", "animation_key": "leg_raise", "icon": "🦵", "equipment_needed": "none", "related_product_ids": "7"},
        ]

        for ex in exercises_data:
            db.add(Exercise(**ex))

        db.commit()
        print(f"✓ {len(exercises_data)} حرکت ساخته شد")

        print("")
        print("=" * 50)
        print("✅ دیتابیس با موفقیت پر شد!")
        print("=" * 50)
        print("")
        print("🔑 اطلاعات ورود:")
        print("  👑 ادمین:")
        print("     ایمیل: admin@fitclub.ir")
        print("     رمز: admin123")
        print("")
        print("  👨‍🏫 مربی:")
        print("     ایمیل: ali@fitclub.ir")
        print("     رمز: trainer123")
        print("")
        print("  👤 کاربر عادی:")
        print("     ایمیل: user@fitclub.ir")
        print("     رمز: user123")
        print("")

    except Exception as e:
        print(f"❌ خطا: {e}")
        db.rollback()
        raise
            # ============ FAQ ============
        print("ساخت FAQ...")
        from app.models.chat import FAQ

        faqs_data = [
            # دوره‌ها
            {
                "category": "courses",
                "question": "قیمت دوره‌ها چنده؟",
                "answer": "قیمت دوره‌های FitClub از ۳۹۰,۰۰۰ تومان شروع می‌شه:\n\n• بدنسازی مقدماتی: ۴۹۰,۰۰۰ (با تخفیف از ۶۹۰,۰۰۰)\n• برنامه تمرینی حجم: ۶۹۰,۰۰۰\n• تغذیه ورزشی: ۳۹۰,۰۰۰\n• کراس‌فیت حرفه‌ای: ۸۹۰,۰۰۰\n• یوگا و انعطاف: ۴۲۰,۰۰۰\n• کاهش وزن اصولی: ۵۹۰,۰۰۰\n\nبرای مشاهده جزئیات، به صفحه دوره‌ها برو: /courses",
                "keywords": "قیمت,دوره,هزینه,تومان,چند",
                "priority": 10,
            },
            {
                "category": "courses",
                "question": "چطور دوره بخرم؟",
                "answer": "برای خرید دوره:\n\n۱. وارد حساب کاربری‌ت شو (یا ثبت‌نام کن)\n۲. به صفحه دوره‌ها برو (/courses)\n۳. دوره‌ی مورد نظرت رو انتخاب کن\n۴. روی «شروع دوره» کلیک کن\n۵. پرداخت رو انجام بده\n۶. دسترسی فوری به دوره فعال می‌شه ✅",
                "keywords": "خرید,دوره,ثبت نام,پرداخت,چطور",
                "priority": 9,
            },
            {
                "category": "courses",
                "question": "آیا مدرک می‌دین؟",
                "answer": "بله! بعد از اتمام هر دوره، یه **مدرک پایان دوره‌ی FitClub** بهت داده می‌شه که می‌تونی توی رزومه‌ات استفاده کنی. 🎓",
                "keywords": "مدرک,گواهی,پایان دوره,مدرک",
                "priority": 8,
            },

            # مربیان
            {
                "category": "trainers",
                "question": "چطور با مربی رزرو کنم؟",
                "answer": "برای رزرو با مربی:\n\n۱. برو به صفحه مربیان (/trainers)\n۲. مربی مورد نظرت رو انتخاب کن\n۳. روی «رزرو نوبت» کلیک کن\n۴. تاریخ و ساعت رو انتخاب کن\n۵. تایید کن\n\n✨ هزینه‌ی مشاوره‌ی اولیه رایگانه!",
                "keywords": "رزرو,مربی,نوبت,وقت,مشاوره",
                "priority": 10,
            },
            {
                "category": "trainers",
                "question": "هزینه مشاوره با مربی چقدره؟",
                "answer": "هزینه‌ی مشاوره با مربی:\n\n🎁 **اولین مشاوره: رایگان**\n💰 مشاوره‌های بعدی: ۱۵۰,۰۰۰ تومان\n🎯 پکیج ۵ جلسه: ۶۵۰,۰۰۰ تومان (۲۰٪ تخفیف)\n🎯 پکیج ۱۰ جلسه: ۱,۲۰۰,۰۰۰ تومان (۳۰٪ تخفیف)",
                "keywords": "هزینه,مشاوره,مربی,قیمت,رایگان",
                "priority": 9,
            },

            # محصولات
            {
                "category": "products",
                "question": "هزینه ارسال چقدره؟",
                "answer": "هزینه‌ی ارسال:\n\n✅ **سفارش‌های بالای ۵۰۰,۰۰۰ تومان: ارسال رایگان**\n🚚 سفارش‌های کمتر: ۳۵,۰۰۰ تومان\n📍 ارسال به سراسر ایران: ۲-۵ روز کاری",
                "keywords": "ارسال,هزینه,پست,تحویل,رایگان",
                "priority": 10,
            },
            {
                "category": "products",
                "question": "روش‌های پرداخت چیه؟",
                "answer": "روش‌های پرداخت:\n\n💳 پرداخت آنلاین (زرین‌پال)\n💰 پرداخت در محل (فقط تهران)\n🏦 کارت به کارت\n\nپرداخت آنلاین امن‌ترین روشه. 🔒",
                "keywords": "پرداخت,روش,آنلاین,کارت,زرین پال",
                "priority": 9,
            },
            {
                "category": "products",
                "question": "آیا امکان مرجوعی هست؟",
                "answer": "بله! ✅\n\n🔄 **۷ روز ضمانت بازگشت**\n- اگه محصول مشکل داشت\n- اگه با توضیحات مطابقت نداشت\n- اگه آسیب‌دیده به دستت رسید\n\nکافیه با پشتیبانی تماس بگیری: 📞 ۰۲۱-۱۲۳۴۵۶۷۸",
                "keywords": "مرجوعی,بازگشت,ضمانت,گارانتی",
                "priority": 8,
            },

            # حساب کاربری
            {
                "category": "account",
                "question": "چطور ثبت‌نام کنم؟",
                "answer": "ثبت‌نام خیلی ساده‌ست:\n\n۱. روی «ورود / ثبت‌نام» کلیک کن\n۲. تب «ثبت‌نام» رو انتخاب کن\n۳. ایمیل، نام کامل و رمز عبور رو وارد کن\n۴. روی «ثبت‌نام» بزن\n\n✅ تمام! حالا عضو FitClub هستی!",
                "keywords": "ثبت نام,ثبتنام,عضویت,اکانت,حساب",
                "priority": 10,
            },
            {
                "category": "account",
                "question": "رمزمو فراموش کردم، چیکار کنم؟",
                "answer": "برای بازیابی رمز:\n\n۱. توی صفحه ورود، روی «فراموشی رمز» کلیک کن\n۲. ایمیلت رو وارد کن\n۳. لینک بازیابی به ایمیلت ارسال می‌شه\n۴. روی لینک کلیک کن و رمز جدید بذار\n\n⚠️ اگه ایمیل نیومد، اسپم رو چک کن یا با پشتیبانی تماس بگیر.",
                "keywords": "رمز,فراموشی,بازیابی,پسورد,password",
                "priority": 9,
            },

            # بدنسازی
            {
                "category": "fitness",
                "question": "برای حجم چه تمرینیه؟",
                "answer": "برای افزایش حجم عضلانی:\n\n💪 **تمرینات اصلی:**\n• پرس سینه، اسکات، ددلیفت (تمرینات پایه)\n• ۴-۶ ست × ۸-۱۲ تکرار\n• وزنه‌ی سنگین (۷۰-۸۵٪ ۱RM)\n• استراحت ۹۰-۱۲۰ ثانیه بین ست‌ها\n\n🍎 **تغذیه:**\n• کالری مازاد (۳۰۰-۵۰۰ کالری بیشتر)\n• پروتئین: ۱.۶-۲.۲ گرم به ازای هر کیلو وزن\n• ۵-۶ وعده در روز\n\n😴 **استراحت:** ۷-۹ ساعت خواب",
                "keywords": "حجم,عضله,بدنسازی,تمرین,برنامه",
                "priority": 10,
            },
            {
                "category": "fitness",
                "question": "برای کاهش وزن چیکار کنم؟",
                "answer": "برای کاهش وزن اصولی:\n\n💪 **تمرینات:**\n• ترکیب هوازی + مقاومتی\n• ۳-۵ جلسه در هفته\n• HIIT (اینتروال شدید) برای چربی‌سوزی\n\n🍎 **تغذیه:**\n• کالری کسری (۳۰۰-۵۰۰ کالری کمتر)\n• پروتئین بالا (برای حفظ عضله)\n• کاهش قند و کربوهیدرات ساده\n• آب کافی (۲-۳ لیتر)\n\n⚖️ **سرعت:** ۰.۵-۱ کیلو در هفته\n\n⚠️ رژیم‌های سریع ممنوع!",
                "keywords": "کاهش وزن,لاغری,چربی سوزی,رژیم",
                "priority": 10,
            },

            # تغذیه
            {
                "category": "nutrition",
                "question": "قبل از تمرین چی بخورم؟",
                "answer": "🍎 **قبل از تمرین (۱-۲ ساعت قبل):**\n\n• موز + کره بادام‌زمینی\n• جو دو سر + پروتئین\n• نان سبوس‌دار + پنیر + گردو\n• برنج قهوه‌ای + مرغ\n\n💧 **آب کافی بنوش**\n\n⏰ **نزدیک تمرین (۳۰ دقیقه قبل):**\n• یه میوه یا آبمیوه طبیعی",
                "keywords": "قبل تمرین,تغذیه,غذا,قبل از تمرین",
                "priority": 9,
            },
            {
                "category": "nutrition",
                "question": "بعد از تمرین چی بخورم؟",
                "answer": "🍎 **بعد از تمرین (۳۰-۶۰ دقیقه):**\n\n• **پروتئین:** ۲۰-۴۰ گرم (وی، مرغ، تخم‌مرغ)\n• **کربوهیدرات:** برای جبران انرژی\n• **آب:** برای هیدراته کردن\n\nمثال‌های عالی:\n• شیک پروتئین + موز\n• مرغ + برنج\n• تخم‌مرغ + نان سبوس‌دار\n\n⏰ **پنجره‌ی طلایی:** ۳۰-۶۰ دقیقه بعد از تمرین",
                "keywords": "بعد تمرین,تغذیه,ریکاوری,پروتئین",
                "priority": 9,
            },
            {
                "category": "nutrition",
                "question": "چقدر پروتئین نیاز دارم؟",
                "answer": "📊 **پروتئین مورد نیاز روزانه:**\n\n• **افراد عادی:** ۰.۸ گرم به ازای هر کیلو وزن\n• **ورزشکاران:** ۱.۲-۱.۷ گرم\n• **بدنسازان (حجم):** ۱.۶-۲.۲ گرم\n• **کاهش وزن:** ۱.۸-۲.۴ گرم (برای حفظ عضله)\n\n**مثال:**\nوزن ۷۵ کیلو، هدف حجم\n→ ۷۵ × ۲ = ۱۵۰ گرم پروتئین در روز\n\n🥤 منابع: مرغ، ماهی، تخم‌مرغ، لبنیات، پروتئین وی",
                "keywords": "پروتئین,مقدار,نیاز,گرم,روزانه",
                "priority": 9,
            },

            # عمومی
            {
                "category": "general",
                "question": "شماره پشتیبانی چنده؟",
                "answer": "📞 **راه‌های ارتباطی FitClub:**\n\n☎️ تلفن: ۰۲۱-۱۲۳۴۵۶۷۸\n📱 موبایل: ۰۹۱۲-۱۲۳۴۵۶۷\n✉️ ایمیل: info@fitclub.ir\n💬 واتساپ: ۰۹۱۲-۱۲۳۴۵۶۷\n\n⏰ **ساعت پاسخگویی:**\nشنبه تا پنجشنبه: ۹:۰۰ - ۱۸:۰۰\nجمعه: تعطیل",
                "keywords": "پشتیبانی,تماس,شماره,تلفن,ارتباط",
                "priority": 10,
            },
            {
                "category": "general",
                "question": "ساعت کاری باشگاه چیه؟",
                "answer": "🕐 **ساعات کاری FitClub:**\n\n📍 **باشگاه اصلی:**\nشنبه تا پنجشنبه: ۶:۰۰ - ۲۳:۰۰\nجمعه: ۸:۰۰ - ۱۴:۰۰\n\n💻 **پشتیبانی آنلاین:**\nشنبه تا پنجشنبه: ۹:۰۰ - ۱۸:۰۰\n\n🌐 **سایت:** ۲۴/۷ فعال",
                "keywords": "ساعت کاری,ساعت,زمان,باز,تعطیل",
                "priority": 8,
            },
            {
                "category": "general",
                "question": "آدرس باشگاه کجاست؟",
                "answer": "📍 **آدرس FitClub:**\n\nتهران، خیابان ولیعصر،\nپلاک ۱۲۳، طبقه ۴، واحد ۵\n\n🗺 **دسترسی:**\n🚇 مترو: ایستگاه ولیعصر (۵ دقیقه پیاده)\n🚌 اتوبوس: خط ۱۲۳\n🚗 پارکینگ رایگان برای اعضا\n\n📞 تلفن: ۰۲۱-۱۲۳۴۵۶۷۸",
                "keywords": "آدرس,کجا,مکان,موقعیت,باشگاه",
                "priority": 9,
            },
        ]

        for f in faqs_data:
            db.add(FAQ(**f))

        db.commit()
        print(f"✓ {len(faqs_data)} سوال/جواب (FAQ) ساخته شد")
    finally:
        db.close()


if __name__ == "__main__":
    seed()