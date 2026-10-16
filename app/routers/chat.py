from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.chat import FAQ, ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
)
from app.utils.text_similarity import find_best_faq
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])


# ============================================
# شماره و اطلاعات پشتیبانی
# ============================================
SUPPORT_INFO = {
    "phone": "۰۲۱-۱۲۳۴۵۶۷۸",
    "mobile": "۰۹۱۲-۱۲۳۴۵۶۷",
    "email": "info@fitclub.ir",
    "whatsapp": "۰۹۱۲-۱۲۳۴۵۶۷",
    "hours": "شنبه تا پنجشنبه، ۹:۰۰ تا ۱۸:۰۰",
}


# ============================================
# آستانه‌ی اعتماد
# ============================================
# اگه امتیاز >= 0.4 باشه → جواب از FAQ
# اگه امتیاز < 0.4 باشه → ارجاع به پشتیبانی
CONFIDENCE_THRESHOLD = 0.4


# ============================================
# پیام‌های ارجاع به پشتیبانی
# ============================================
def get_support_referral_message(reason: str = "general") -> str:
    """پیام ارجاع به پشتیبانی."""
    
    if reason == "complex":
        intro = "این سؤال نیاز به مشاوره‌ی تخصصی داره. 🤝"
        advice = "مربیان و کارشناسان FitClub آماده‌ی کمکت هستن."
    elif reason == "unknown":
        intro = "متأسفم، نتونستم پاسخ دقیقی پیدا کنم. 🤔"
        advice = "برای دریافت پاسخ حرفه‌ای و کامل، با پشتیبانی ما در تماس باش:"
    else:
        intro = "برای این سؤال، بهتره با پشتیبانی ما تماس بگیری. 📞"
        advice = "کارشناسان ما آماده‌ی راهنمایی رایگان هستن:"
    
    return f"""{intro}

{advice}

📞 **تلفن:** {SUPPORT_INFO['phone']}
📱 **موبایل:** {SUPPORT_INFO['mobile']}
✉️ **ایمیل:** {SUPPORT_INFO['email']}
💬 **واتساپ:** {SUPPORT_INFO['whatsapp']}

⏰ **ساعت پاسخگویی:** {SUPPORT_INFO['hours']}

👇 یا از گزینه‌های زیر استفاده کن:
• 🎓 «مشاهده دوره‌ها»
• 👨‍🏫 «رزرو مشاوره با مربی»
• 💬 «ارسال تیکت پشتیبانی»"""


def get_keyword_referral_message() -> str:
    """اگه کلیدواژه‌های حساس پیدا شد."""
    return f"""این موضوع نیاز به بررسی تخصصی داره. 🔍

برای پاسخ دقیق و حرفه‌ای، لطفاً با تیم پشتیبانی FitClub در تماس باش:

📞 **تلفن:** {SUPPORT_INFO['phone']}
✉️ **ایمیل:** {SUPPORT_INFO['email']}

⏰ {SUPPORT_INFO['hours']}

تیم ما در اسرع وقت پاسخگوی شما خواهد بود. 🙏"""


# ============================================
# کلیدواژه‌های حساس (نیاز به پشتیبانی)
# ============================================
SENSITIVE_KEYWORDS = [
    # مشکلات فنی
    "مشکل", "خطا", "کار نمی‌کنه", "کار نمیکنه", "خراب", "باز نمی‌شه",
    "باگ", "ارور", "error",
    
    # مالی
    "پول کم شد", "پرداخت ناموفق", "برنگشت", "کسر", "دوبار کم",
    "فاکتور", "رسید", "شماره پیگیری", "تراکنش",
    
    # پزشکی
    "بیماری", "مریض", "دیسک", "آسیب", "زخم", "درد شدید",
    "دارو", "قرص", "بیمار",
    
    # شکایات
    "شکایت", "ناراضی", "بد بود", "بهترین نبود", "افتضاح",
    "کلاهبرداری", "تقلب",
    
    # درخواست‌های خاص
    "همکاری", "اسپانسر", "تبلیغات", "شرکت", "سرمایه‌گذاری",
    "شعبه", "نمایندگی", "فرانشیز",
    
    # حقوقی
    "قانونی", "شکایت حقوقی", "وکیل", "دادگاه",
    
    # امنیت
    "هک", "دزدی", "امنیت", "رمز دوم", "فیشینگ",
]


def has_sensitive_keyword(text: str) -> bool:
    """چک کن متن کلیدواژه‌ی حساس داره یا نه."""
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in SENSITIVE_KEYWORDS)


# ============================================
# Session Management
# ============================================
def get_or_create_session(
    db: Session,
    session_token: str = None,
    user_id: int = None,
) -> ChatSession:
    """گرفتن یا ساخت session."""
    if session_token:
        session = db.query(ChatSession).filter(
            ChatSession.session_token == session_token
        ).first()
        if session:
            return session

    new_token = str(uuid.uuid4())
    session = ChatSession(
        session_token=new_token,
        user_id=user_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ============================================
# Endpoints
# ============================================
@router.post("/message", response_model=ChatResponse)
def send_message(
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
):
    """ارسال پیام به چت‌بات."""
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="پیام نمی‌تونه خالی باشه")

    content = data.content.strip()

    # ساخت/گرفتن session
    session = get_or_create_session(db, data.session_token)

    # ذخیره‌ی پیام کاربر
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=content,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # ============================================
    # ۱. چک کردن کلیدواژه‌های حساس
    # ============================================
    if has_sensitive_keyword(content):
        bot_content = get_keyword_referral_message()
        matched_faq_id = None
        similarity = 0.0

    else:
        # ============================================
        # ۲. تطبیق با FAQ
        # ============================================
        faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
        best_faq, similarity = find_best_faq(content, faqs)

        # ============================================
        # ۳. تصمیم بر اساس امتیاز
        # ============================================
        if best_faq and similarity >= CONFIDENCE_THRESHOLD:
            # جواب از FAQ
            bot_content = best_faq.answer
            matched_faq_id = best_faq.id

        elif best_faq and similarity >= 0.2:
            # امتیاز متوسط → جواب + ارجاع
            bot_content = f"""{best_faq.answer}

━━━━━━━━━━━━━━━━━━━━━━

💡 **برای پاسخ کامل‌تر و تخصصی، با پشتیبانی ما در تماس باش:**

📞 {SUPPORT_INFO['phone']}
✉️ {SUPPORT_INFO['email']}"""
            matched_faq_id = best_faq.id

        else:
            # امتیاز پایین → ارجاع به پشتیبانی
            bot_content = get_support_referral_message("unknown")
            matched_faq_id = None

    # ذخیره‌ی پاسخ ربات
    bot_msg = ChatMessage(
        session_id=session.id,
        role="bot",
        content=bot_content,
        matched_faq_id=matched_faq_id,
        similarity=similarity,
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)

    return ChatResponse(
        session_token=session.session_token,
        user_message=ChatMessageResponse.model_validate(user_msg),
        bot_message=ChatMessageResponse.model_validate(bot_msg),
    )


@router.get("/history/{session_token}", response_model=ChatHistoryResponse)
def get_history(
    session_token: str,
    db: Session = Depends(get_db),
):
    """تاریخچه‌ی چت."""
    session = db.query(ChatSession).filter(
        ChatSession.session_token == session_token
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return ChatHistoryResponse(
        session_token=session.session_token,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )


@router.get("/faqs")
def get_faqs(
    category: str = None,
    db: Session = Depends(get_db),
):
    """لیست FAQ."""
    query = db.query(FAQ).filter(FAQ.is_active == True)
    if category:
        query = query.filter(FAQ.category == category)
    faqs = query.order_by(FAQ.priority.desc()).all()

    return [
        {
            "id": f.id,
            "category": f.category,
            "question": f.question,
            "answer": f.answer,
        }
        for f in faqs
    ]


@router.get("/suggestions")
def get_suggestions():
    """پیشنهاد سوالات برای شروع."""
    return [
        {"icon": "🎓", "text": "قیمت دوره‌ها چنده؟"},
        {"icon": "👨‍🏫", "text": "چطور با مربی رزرو کنم؟"},
        {"icon": "🛒", "text": "هزینه ارسال چقدره؟"},
        {"icon": "🍎", "text": "قبل از تمرین چی بخورم؟"},
        {"icon": "💪", "text": "برای حجم چه تمرینیه؟"},
        {"icon": "📞", "text": "شماره پشتیبانی چنده؟"},
    ]


@router.get("/support-info")
def get_support_info():
    """اطلاعات پشتیبانی (برای Frontend)."""
    return SUPPORT_INFO