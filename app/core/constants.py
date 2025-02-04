# -*- coding: utf-8 -*-
"""
الثوابت الأساسية للنظام
"""

from typing import Dict, Final

# ألوان خطورة التنبيهات
SEVERITY_COLORS: Final[Dict[str, str]] = {
    "CRITICAL": "#FF0000",    # أحمر
    "HIGH": "#FF4B4B",        # أحمر فاتح
    "MEDIUM": "#FFA500",      # برتقالي
    "LOW": "#FFFF00",         # أصفر
    "INFO": "#0066CC",        # أزرق
    "DEFAULT": "#666666"      # رمادي
}

# أنواع الأحداث المسموحة
EVENT_TYPES: Final[Dict[str, str]] = {
    "LOGIN": "تسجيل الدخول",
    "USB": "جهاز USB",
    "NETWORK": "شبكة",
    "FILE": "ملف",
    "PROCESS": "عملية",
    "SYSTEM": "نظام"
}

# إعدادات التحديث التلقائي
REFRESH_INTERVALS: Final[Dict[str, int]] = {
    "FAST": 15,     # ثانية
    "NORMAL": 30,
    "SLOW": 60
}

# ثوابت التحليل
ANALYSIS_CONSTANTS: Final[Dict[str, float]] = {
    "ANOMALY_THRESHOLD": 0.85,  # حد الشذوذ
    "MAX_DATA_POINTS": 1000     # الحد الأقصى للبيانات
}


# ألوان لاستخدامات عامة
COLOR_PALETTE: Final[Dict[str, str]] = {
    "PRIMARY": "#306998",    # أزرق بايثون
    "SECONDARY": "#FFD43B",  # أصفر بايثون
    "SUCCESS": "#4CAF50",    # أخضر
    "WARNING": "#FFC107",    # أصفر تحذير
    "DANGER": "#DC3545"      # أحمر خطر
}

# إعدادات الرسوم البيانية
CHART_CONFIG: Final[Dict[str, str]] = {
    "BG_COLOR": "#FFFFFF",
    "FONT": "Arial",
    "AXIS_COLOR": "#666666"
}

