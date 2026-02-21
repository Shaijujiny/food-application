from app.core.error.message_codes import MessageCode

MESSAGES: dict[MessageCode, dict[str, str]] = {
    MessageCode.CUSTOMER_CREATED: {
        "en": "Customer created successfully",
        "ar": "تم إنشاء العميل بنجاح",
        "hi": "ग्राहक सफलतापूर्वक बनाया गया",
    },
    MessageCode.LOGIN_SUCCESS: {
        "en": "Login successful",
        "ar": "تم تسجيل الدخول بنجاح",
        "hi": "लॉगिन सफल हुआ",
    },
    MessageCode.INVALID_CREDENTIALS: {
        "en": "Invalid credentials",
        "ar": "بيانات اعتماد غير صالحة",
        "hi": "अमान्य क्रेडेंशियल",
    },
    MessageCode.USERNAME_EXISTS: {
        "en": "Username already exists",
        "ar": "اسم المستخدم موجود بالفعل",
        "hi": "उपयोगकर्ता नाम पहले से मौजूद है",
    },
    MessageCode.PROFILE_FETCHED: {
        "en": "Profile fetched successfully",
        "ar": "تم جلب الملف الشخصي بنجاح",
        "hi": "प्रोफ़ाइल सफलतापूर्वक प्राप्त की गई",
    },
    MessageCode.USERS_FETCHED: {
        "en": "Users fetched successfully",
        "ar": "تم جلب المستخدمين بنجاح",
        "hi": "उपयोगकर्ताओं को सफलतापूर्वक प्राप्त किया गया",
    },
    MessageCode.USER_FETCHED: {
        "en": "User fetched successfully",
        "ar": "تم جلب المستخدم بنجاح",
        "hi": "उपयोगकर्ता सफलतापूर्वक प्राप्त किया गया",
    },
    MessageCode.USER_UPDATED: {
        "en": "User updated successfully",
        "ar": "تم تحديث المستخدم بنجاح",
        "hi": "उपयोगकर्ता सफलतापूर्वक अपडेट किया गया",
    },
    MessageCode.USER_DELETED: {
        "en": "User deleted successfully",
        "ar": "تم حذف المستخدم بنجاح",
        "hi": "उपयोगकर्ता सफलतापूर्वक हटा दिया गया",
    },
    MessageCode.USER_NOT_FOUND: {
        "en": "User not found",
        "ar": "المستخدم غير موجود",
        "hi": "उपयोगकर्ता नहीं मिला",
    },
}
