from enum import StrEnum


class ErrorType(StrEnum):

    # ================= SUCCESS =================
    SUC_200_OK = "SUC_200_OK"
    SUC_201_CREATED = "SUC_201_CREATED"

    # ================= VALIDATION =================
    VAL_400_INVALID_PARAMETERS = "VAL_400_INVALID_PARAMETERS"
    VAL_400_USERNAME_EXISTS = "VAL_400_USERNAME_EXISTS"

    # ================= AUTH =================
    AUTH_401_INVALID_CREDENTIALS = "AUTH_401_INVALID_CREDENTIALS"
    AUTH_401_TOKEN_EXPIRED = "AUTH_401_TOKEN_EXPIRED"

    AUTH_403_ACCESS_DENIED = "AUTH_403_ACCESS_DENIED"

    # ================= RESOURCE =================
    RES_404_NOT_FOUND = "RES_404_NOT_FOUND"

    # ================= SYSTEM =================
    SYS_500_INTERNAL_ERROR = "SYS_500_INTERNAL_ERROR"