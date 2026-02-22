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
    MessageCode.ORDER_CREATED: {
        "en": "Order created successfully",
        "ar": "تم إنشاء الطلب بنجاح",
        "hi": "ऑर्डर सफलतापूर्वक बनाया गया",
    },
    MessageCode.ORDERS_FETCHED: {
        "en": "Orders fetched successfully",
        "ar": "تم جلب الطلبات بنجاح",
        "hi": "ऑर्डर सफलतापूर्वक प्राप्त किए गए",
    },
    MessageCode.ORDER_FETCHED: {
        "en": "Order fetched successfully",
        "ar": "تم جلب الطلب بنجاح",
        "hi": "ऑर्डर सफलतापूर्वक प्राप्त किया गया",
    },
    MessageCode.ORDER_NOT_FOUND: {
        "en": "Order not found",
        "ar": "الطلب غير موجود",
        "hi": "ऑर्डर नहीं मिला",
    },
    MessageCode.ORDER_STATUS_UPDATED: {
        "en": "Order status updated successfully",
        "ar": "تم تحديث حالة الطلب بنجاح",
        "hi": "ऑर्डर की स्थिति सफलतापूर्वक अपडेट की गई",
    },
}
