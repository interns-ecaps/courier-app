from datetime import datetime
from decimal import Decimal
from enum import Enum
import re
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, constr, field_validator

from user.api.v1.models.users import UserType

# Enum for user roles
# class UserType(str, Enum):
#     importer_exporter = "importer_exporter"
#     supplier = "supplier"
#     super_admin = "super_admin"


# Input when user signs up (includes raw password)
class SignUpUser(BaseModel):
    first_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r"^[A-Za-z\s]+$",
            description="First name (letters and spaces only, 1–50 characters)",
        ),
    ]

    last_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r"^[A-Za-z\s]+$",
            description="Last name (letters and spaces only, 1–50 characters)",
        ),
    ]

    email: Annotated[EmailStr, Field(description="Valid email address")]

    password: Annotated[
        str,
        Field(min_length=6, max_length=128, description="Password (6–128 characters)"),
    ]

    phone_number: Annotated[
        str,
        Field(
            min_length=10,
            max_length=15,
            pattern=r"^[0-9+]+$",
            description="Phone number (10–15 digits, may include '+')",
        ),
    ]

    user_type: Annotated[
        UserType,
        Field(description="Type of user (importer_exporter, supplier, super_admin)"),
    ]

    class Config:
        from_attributes = True


# Input for internal user creation (password already hashed)
class CreateUser(BaseModel):
    first_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r"^[A-Za-z\s]+$",
            description="First name (letters and spaces only)",
        ),
    ]
    last_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r"^[A-Za-z\s]+$",
            description="Last name (letters and spaces only)",
        ),
    ]
    email: Annotated[EmailStr, Field(description="Valid email address")]
    hashed_password: Annotated[
        str, Field(min_length=6, max_length=128, description="Hashed user password")
    ]
    phone_number: Annotated[
        str,
        Field(
            min_length=10,
            max_length=15,
            pattern=r"^[0-9+]+$",
            description="Phone number (digits, may start with '+')",
        ),
    ]
    user_type: Annotated[
        UserType,
        Field(description="User role (importer_exporter, supplier, or super_admin)"),
    ]

    model_config = {"from_attributes": True}


class UpdateUser(BaseModel):
    first_name: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=50,
                pattern=r"^[A-Za-z]+$",
                description="First name",
            ),
        ]
    ] = None
    last_name: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=50,
                pattern=r"^[A-Za-z]+$",
                description="Last name",
            ),
        ]
    ] = None
    email: Optional[Annotated[EmailStr, Field(description="Valid email address")]] = (
        None
    )
    current_password: Optional[
            Annotated[
                str,
                Field(min_length=6, max_length=15, description="Password (min 6 chars)")
            ]
        ] = None
    password: Optional[
            Annotated[
                str,
                Field(min_length=6, max_length=15, description="Password (min 6 chars)")
            ]
        ] = None
    
    phone_number: Optional[
        Annotated[
            str,
            Field(
                min_length=10,
                max_length=15,
                pattern=r"^[0-9]+$",
                description="Phone number",
            ),
        ]
    ] = None
    user_type: Optional[Annotated[UserType, Field(description="User role")]] = None

    model_config = {"from_attributes": True}

    @field_validator("email")
    def validate_realistic_email(cls, v: EmailStr) -> str:
        local_part, domain = v.split("@")

        # Check domain is allowed (you can skip or expand this list)
        if domain.lower() not in ALLOWED_EMAIL_DOMAINS:
            raise ValueError(f"Only common email domains allowed, got '{domain}'")

        # Gmail-like rules:
        if local_part.startswith(".") or local_part.endswith("."):
            raise ValueError("Local part of email cannot start or end with a dot")
        if ".." in local_part:
            raise ValueError("Local part of email cannot contain consecutive dots")

        # Disallow weird characters in local part (stricter than RFC)
        if not re.fullmatch(r"[a-zA-Z0-9_.+-]+", local_part):
            raise ValueError("Local part contains invalid characters")

        return v

    @field_validator("password")
    def validate_password_complexity(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    model_config = {"from_attributes": True}


class ReplaceUser(CreateUser):
    pass  # Inherits all from CreateUser


class FetchUser(BaseModel):
    id: Annotated[int, Field(description="User ID")]
    first_name: Annotated[str, Field(description="First name")]
    last_name: Annotated[str, Field(description="Last name")]
    email: Annotated[EmailStr, Field(description="User's email")]
    phone_number: Annotated[str, Field(description="Phone number")]
    user_type: Annotated[UserType, Field(description="User role")]
    is_active: Annotated[bool, Field(description="Is the user active?")]
    created_at: Annotated[datetime, Field(description="Creation timestamp")]
    updated_at: Optional[
        Annotated[datetime, Field(description="Last updated timestamp")]
    ] = None

    model_config = {"from_attributes": True}


ALLOWED_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "yahoo.in",
    "outlook.com",
    "hotmail.com",
    "icloud.com",
    "protonmail.com",
}


class SignUpRequest(BaseModel):
    email: Annotated[EmailStr, Field(description="Valid email address")]
    password: Annotated[
        str, Field(min_length=6, max_length=15, description="Password (min 6 chars)")
    ]
    first_name: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=50,
                pattern=r"^[A-Za-z]+$",
                description="First name",
            ),
        ]
    ] = None
    last_name: Optional[
        Annotated[
            str,
            Field(
                min_length=1,
                max_length=50,
                pattern=r"^[A-Za-z]+$",
                description="Last name",
            ),
        ]
    ] = None
    phone_number: Optional[
        Annotated[
            str,
            Field(
                min_length=10,
                max_length=10,
                pattern=r"^[0-9+]+$",
                description="Phone number",
            ),
        ]
    ] = None
    user_type: Optional[Annotated[UserType, Field(description="User type")]] = None

    @field_validator("email")
    def validate_realistic_email(cls, v: EmailStr) -> str:
        local_part, domain = v.split("@")

        # Check domain is allowed (you can skip or expand this list)
        if domain.lower() not in ALLOWED_EMAIL_DOMAINS:
            raise ValueError(f"Only common email domains allowed, got '{domain}'")

        # Gmail-like rules:
        if local_part.startswith(".") or local_part.endswith("."):
            raise ValueError("Local part of email cannot start or end with a dot")
        if ".." in local_part:
            raise ValueError("Local part of email cannot contain consecutive dots")

        # Disallow weird characters in local part (stricter than RFC)
        if not re.fullmatch(r"[a-zA-Z0-9_.+-]+", local_part):
            raise ValueError("Local part contains invalid characters")

        return v

    @field_validator("password")
    def validate_password_complexity(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    model_config = {"from_attributes": True}


# ====================== ADDRESS ========================

from pydantic import BaseModel, Field, constr
from typing import Optional


class CreateAddress(BaseModel):
    label: Optional[
        Annotated[
            str,
            Field(
                max_length=50,
                pattern=r"^[A-Za-z0-9\s\-_,.]*$",
                description="Optional label for the address (e.g., 'Home', 'Office'). Only letters, numbers, spaces, hyphens, commas, periods allowed.",
            ),
        ]
    ]

    street_address: Annotated[
        str,
        Field(
            min_length=5,
            max_length=255,
            pattern=r"^[A-Za-z0-9\s\-_,.]+$",
            description="Street address (e.g., '123 MG Road'). Must be 5–255 characters long and can include letters, numbers, spaces, hyphens, commas, periods.",
        ),
    ]

    city: Annotated[
        str,
        Field(
            min_length=2,
            max_length=100,
            pattern=r"^[A-Za-z\s]+$",
            description="City name (letters and spaces only, e.g., 'Bangalore'). 2–100 characters.",
        ),
    ]

    state: Annotated[
        str,
        Field(
            min_length=2,
            max_length=100,
            pattern=r"^[A-Za-z\s]+$",
            description="State name (letters and spaces only, e.g., 'Karnataka'). 2–100 characters.",
        ),
    ]

    postal_code: Annotated[
        str,
        Field(
            min_length=4,
            max_length=10,
            pattern=r"^[A-Za-z0-9\-]+$",
            description="Postal code (e.g., '560001'). Alphanumeric with optional hyphens. 4–10 characters.",
        ),
    ]

    country_code: Annotated[
        int,
        Field(
            ge=1,
            description="Country ID (foreign key to countries table). Must be a positive integer.",
        ),
    ]

    landmark: Optional[
        Annotated[
            str,
            Field(
                max_length=255,
                description="Optional landmark description (e.g., 'Near Mall', 'Next to station'). Max 255 characters.",
            ),
        ]
    ] = None

    latitude: Optional[
        Annotated[
            float,
            Field(
                ge=-90,
                le=90,
                description="Latitude of the location. Must be between -90 and 90.",
            ),
        ]
    ] = None

    longitude: Optional[
        Annotated[
            float,
            Field(
                ge=-180,
                le=180,
                description="Longitude of the location. Must be between -180 and 180.",
            ),
        ]
    ] = None

    is_default: bool = Field(
        default=False,
        description="Whether this is the default address for the user.",
    )

    model_config = {"from_attributes": True}


class FetchAddress(CreateAddress):
    id: int

    model_config = {"from_attributes": True}


from typing import Optional, Annotated
from pydantic import BaseModel, Field


class UpdateAddress(BaseModel):
    label: Optional[
        Annotated[str, Field(max_length=50, pattern=r"^[A-Za-z0-9\s\-_,.]*$")]
    ] = None

    street_address: Optional[
        Annotated[
            str, Field(min_length=5, max_length=255, pattern=r"^[A-Za-z0-9\s\-_,.]+$")
        ]
    ] = None

    city: Optional[
        Annotated[str, Field(min_length=2, max_length=100, pattern=r"^[A-Za-z\s]+$")]
    ] = None

    state: Optional[
        Annotated[str, Field(min_length=2, max_length=100, pattern=r"^[A-Za-z\s]+$")]
    ] = None

    postal_code: Optional[
        Annotated[str, Field(min_length=4, max_length=10, pattern=r"^[A-Za-z0-9\-]+$")]
    ] = None

    country_code: Optional[Annotated[int, Field(ge=1)]] = None

    landmark: Optional[Annotated[str, Field(max_length=255)]] = None

    latitude: Optional[Annotated[float, Field(ge=-90, le=90)]] = None

    longitude: Optional[Annotated[float, Field(ge=-180, le=180)]] = None

    is_default: Optional[bool] = None
    is_deleted: Optional[bool] = None

    model_config = {"from_attributes": True}


class ReplaceAddress(CreateAddress):
    pass


# ===================== COUNTRIES ======================


class CreateCountry(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=100,
            pattern=r"^[A-Za-z\s]+$",
            description="Country name (letters and spaces only, 2–100 characters)",
        ),
    ]

    model_config = {"from_attributes": True}


class FetchCountry(CreateCountry):
    id: Annotated[int, Field(description="Country ID")]
    name: Annotated[str, Field(description="Country name")]
    is_deleted: Annotated[bool, Field(description="Soft-delete flag")]
    created_at: Optional[
        Annotated[datetime, Field(description="Creation timestamp")]
    ] = None
    updated_at: Optional[
        Annotated[datetime, Field(description="Last updated timestamp")]
    ] = None

    model_config = {"from_attributes": True}


class UpdateCountry(BaseModel):
    name: Optional[
        Annotated[
            str,
            Field(
                min_length=2,
                max_length=100,
                pattern=r"^[A-Za-z\s]+$",
                description="Updated country name",
            ),
        ]
    ] = None
    is_deleted: Optional[
        Annotated[bool, Field(description="Mark country as deleted")]
    ] = None

    model_config = {"from_attributes": True}


class ReplaceCountry(BaseModel):
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=100,
            pattern=r"^[A-Za-z\s]+$",
            description="Country name",
        ),
    ]
    is_deleted: Annotated[bool, Field(description="Soft-delete flag")]

    model_config = {"from_attributes": True}


class ForgetPasswordRequest(BaseModel):
    email: EmailStr

class ResetForgetPassword(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str
