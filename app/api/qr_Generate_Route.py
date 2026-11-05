"""
QR Code Generation API — 20 Feature Routes
==========================================
All routes accept a structured JSON body with three top-level sections:

  {
    "type"   : "<qr-type>",          // identifies the QR variant
    "content": { ... },              // QR-specific payload fields
    "design" : {                     // optional visual customisation
        "foreground" : "#000000",    // QR module color   (default black)
        "background" : "#FFFFFF",    // QR background     (default white)
        "box_size"   : 10,           // pixels per module (default 10)
        "border"     : 4             // quiet-zone width  (default 4)
    },
    "output" : {                     // optional output settings
        "format"   : "png"           // only "png" is supported for now
    }
  }

POST /qr/url           → Website / URL QR
POST /qr/whatsapp      → WhatsApp QR
POST /qr/vcard         → vCard / Contact QR
POST /qr/wifi          → WiFi QR
POST /qr/google-review → Google Review QR
POST /qr/menu          → Restaurant Menu QR
POST /qr/pdf           → PDF QR
POST /qr/upi           → UPI Payment QR
POST /qr/text          → Plain Text QR
POST /qr/email         → Email QR
POST /qr/phone         → Phone QR
POST /qr/sms           → SMS QR
POST /qr/location      → Location / Maps QR
POST /qr/social        → Social Media QR
POST /qr/event         → Event / Calendar QR
POST /qr/app-download  → App Download QR
POST /qr/image         → Image QR
POST /qr/google-form   → Google Forms QR
POST /qr/multi-link    → Multi-Link / Landing-page QR
POST /qr/crypto        → Bitcoin / Crypto QR
"""

import io
import re
from enum import Enum
from typing import Literal, Optional
from urllib.parse import quote

import qrcode
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from pydantic import BaseModel, Field, field_validator

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# ① SHARED OPTION MODELS  (design + output — reused by every request)
# ══════════════════════════════════════════════════════════════════════════════

class DesignOptions(BaseModel):
    """Visual customisation applied to every QR code.

    Add new design fields here as the product grows (e.g. logo_url, gradient,
    rounded_modules, eye_shape …).
    """
    foreground: str = Field(
        "black",
        description="QR module color — CSS color name or hex string (e.g. '#1A1A2E').",
    )
    background: str = Field(
        "white",
        description="QR background color — CSS color name or hex string (e.g. '#FFFFFF').",
    )
    box_size: int = Field(
        10,
        ge=1,
        le=50,
        description="Size of each QR module in pixels (1–50). Default 10.",
    )
    border: int = Field(
        4,
        ge=0,
        le=20,
        description="Quiet-zone width in modules (0–20). Default 4 (spec minimum).",
    )


class OutputOptions(BaseModel):
    """Output / export settings.

    Add new fields here as more formats are supported (e.g. svg, pdf, base64).
    """
    format: Literal["png"] = Field(
        "png",
        description="Output image format. Currently only 'png' is supported.",
    )


# ══════════════════════════════════════════════════════════════════════════════
# ② INTERNAL HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _qr_to_png_bytes(
    data: str,
    design: DesignOptions,
    error_correction: int = qrcode.constants.ERROR_CORRECT_M,
) -> bytes:
    """Encode *data* into a QR code and return PNG bytes."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=design.box_size,
        border=design.border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img: Image.Image = qr.make_image(
        fill_color=design.foreground,
        back_color=design.background,
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _stream_response(png_bytes: bytes, filename: str = "qrcode.png") -> StreamingResponse:
    """Wrap raw PNG bytes in a StreamingResponse with correct headers."""
    return StreamingResponse(
        io.BytesIO(png_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


def _validate_http_url(url: str, field_name: str = "url") -> str:
    """Raise HTTP 422 if *url* is not a valid http/https URL."""
    pattern = re.compile(
        r"^https?://"
        r"(?:[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+)$"
    )
    if not url or not pattern.match(url.strip()):
        raise HTTPException(
            status_code=422,
            detail=f"'{field_name}' must be a valid http:// or https:// URL.",
        )
    return url.strip()


# ══════════════════════════════════════════════════════════════════════════════
# ③ ROUTE MODELS + ENDPOINTS
#    Pattern for every route:
#      class <Type>Content(BaseModel): ...   ← QR-specific payload
#      class <Type>Request(BaseModel):       ← top-level envelope
#          type   : Literal["<type>"]
#          content: <Type>Content
#          design : DesignOptions
#          output : OutputOptions
#      @router.post("/...")
#      async def generate_...(body: <Type>Request): ...
# ══════════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────────────────────
# 1. Website / URL QR
# ─────────────────────────────────────────────────────────────────────────────

class URLContent(BaseModel):
    """Payload fields for a plain website / URL QR code."""
    url: str = Field(..., min_length=5, max_length=2048, description="A valid http/https URL.")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        _validate_http_url(v, "url")
        return v


class URLRequest(BaseModel):
    type: Literal["url"] = Field("url", description="QR type identifier.")
    content: URLContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "url",
                "content": {"url": "https://example.com"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/url", summary="Website / URL QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_url_qr(body: URLRequest):
    """Generate a QR code that opens any website / URL when scanned."""
    try:
        png = _qr_to_png_bytes(body.content.url, design=body.design)
        return _stream_response(png, "url_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. WhatsApp QR
# ─────────────────────────────────────────────────────────────────────────────

class WhatsAppContent(BaseModel):
    """Payload fields for a WhatsApp deep-link QR code."""
    phone: str = Field(
        ..., min_length=7, max_length=15,
        description="Phone in international format without '+' (e.g. 919876543210).",
    )
    message: Optional[str] = Field(None, max_length=4096, description="Optional pre-filled message.")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().lstrip("+").replace(" ", "").replace("-", "")
        if not v.isdigit():
            raise ValueError("Phone must contain digits only (no spaces, dashes, or '+').")
        if not (7 <= len(v) <= 15):
            raise ValueError("Phone must be 7-15 digits in international format (e.g. 919876543210).")
        return v


class WhatsAppRequest(BaseModel):
    type: Literal["whatsapp"] = Field("whatsapp", description="QR type identifier.")
    content: WhatsAppContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "whatsapp",
                "content": {"phone": "919876543210", "message": "Hello!"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/whatsapp", summary="WhatsApp QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_whatsapp_qr(body: WhatsAppRequest):
    """Generate a WhatsApp deep-link QR code. Scanning opens WhatsApp with the number pre-filled."""
    try:
        payload = f"https://wa.me/{body.content.phone}"
        if body.content.message:
            payload += f"?text={quote(body.content.message)}"
        png = _qr_to_png_bytes(payload, design=body.design)
        return _stream_response(png, "whatsapp_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. vCard / Contact QR
# ─────────────────────────────────────────────────────────────────────────────

class VCardContent(BaseModel):
    """Payload fields for a vCard 3.0 contact QR code."""
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=254)
    organization: Optional[str] = Field(None, max_length=128)
    title: Optional[str] = Field(None, max_length=128)
    url: Optional[str] = Field(None, max_length=2048)
    address: Optional[str] = Field(None, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v.strip()):
            raise ValueError("email must be a valid e-mail address.")
        return v.strip()


class VCardRequest(BaseModel):
    type: Literal["vcard"] = Field("vcard", description="QR type identifier.")
    content: VCardContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "vcard",
                "content": {
                    "first_name": "John", "last_name": "Doe",
                    "phone": "+919876543210", "email": "john@example.com",
                    "organization": "Acme Inc", "title": "Developer",
                },
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/vcard", summary="vCard / Contact QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_vcard_qr(body: VCardRequest):
    """Generate a vCard 3.0 QR code so the scanner can save the contact directly."""
    try:
        c = body.content
        full_name = f"{c.first_name} {c.last_name or ''}".strip()
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{full_name}",
            f"N:{c.last_name or ''};{c.first_name};;;",
        ]
        if c.phone:       lines.append(f"TEL;TYPE=CELL:{c.phone}")
        if c.email:       lines.append(f"EMAIL:{c.email}")
        if c.organization:lines.append(f"ORG:{c.organization}")
        if c.title:       lines.append(f"TITLE:{c.title}")
        if c.url:         lines.append(f"URL:{c.url}")
        if c.address:     lines.append(f"ADR:;;{c.address};;;;")
        lines.append("END:VCARD")
        payload = "\n".join(lines)
        png = _qr_to_png_bytes(payload, design=body.design, error_correction=qrcode.constants.ERROR_CORRECT_L)
        return _stream_response(png, "vcard_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. WiFi QR
# ─────────────────────────────────────────────────────────────────────────────

class WiFiEncryptionEnum(str, Enum):
    WPA = "WPA"
    WEP = "WEP"
    nopass = "nopass"


class WiFiContent(BaseModel):
    """Payload fields for a WiFi network QR code."""
    ssid: str = Field(..., min_length=1, max_length=32, description="WiFi network name (SSID).")
    password: Optional[str] = Field(None, max_length=63, description="WiFi password. Omit for open networks.")
    encryption: WiFiEncryptionEnum = Field(
        WiFiEncryptionEnum.WPA,
        description="Encryption type: WPA | WEP | nopass.",
    )
    hidden: Optional[bool] = Field(False, description="Set true if the SSID is not broadcast.")


class WiFiRequest(BaseModel):
    type: Literal["wifi"] = Field("wifi", description="QR type identifier.")
    content: WiFiContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "wifi",
                "content": {"ssid": "MyWiFi", "password": "12345678", "encryption": "WPA", "hidden": False},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/wifi", summary="WiFi QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_wifi_qr(body: WiFiRequest):
    """Generate a WiFi QR code. Scanning it connects the device automatically."""
    try:
        def _esc(s: str) -> str:
            for ch in ('\\', ';', ',', '"', ':'):
                s = s.replace(ch, f'\\{ch}')
            return s

        c = body.content
        ssid   = _esc(c.ssid)
        pwd    = _esc(c.password or "")
        hidden = "true" if c.hidden else "false"
        payload = f"WIFI:T:{c.encryption.value};S:{ssid};P:{pwd};H:{hidden};;"
        png = _qr_to_png_bytes(payload, design=body.design)
        return _stream_response(png, "wifi_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Google Review QR
# ─────────────────────────────────────────────────────────────────────────────

class GoogleReviewContent(BaseModel):
    """Payload fields for a Google Business review QR code."""
    review_url: str = Field(..., min_length=10, max_length=2048, description="Google Business review URL.")

    @field_validator("review_url")
    @classmethod
    def validate_review_url(cls, v: str) -> str:
        _validate_http_url(v, "review_url")
        return v


class GoogleReviewRequest(BaseModel):
    type: Literal["google-review"] = Field("google-review", description="QR type identifier.")
    content: GoogleReviewContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "google-review",
                "content": {"review_url": "https://g.page/r/XXXXXXXXXXXXXXXX/review"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/google-review", summary="Google Review QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_google_review_qr(body: GoogleReviewRequest):
    """Generate a QR code that takes customers directly to your Google Review page."""
    try:
        png = _qr_to_png_bytes(body.content.review_url, design=body.design)
        return _stream_response(png, "google_review_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Restaurant Menu QR
# ─────────────────────────────────────────────────────────────────────────────

class MenuContent(BaseModel):
    """Payload fields for a restaurant menu QR code."""
    menu_url: str = Field(..., min_length=5, max_length=2048, description="Link to the digital menu (PDF or web page).")

    @field_validator("menu_url")
    @classmethod
    def validate_menu_url(cls, v: str) -> str:
        _validate_http_url(v, "menu_url")
        return v


class MenuRequest(BaseModel):
    type: Literal["menu"] = Field("menu", description="QR type identifier.")
    content: MenuContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "menu",
                "content": {"menu_url": "https://restaurant.com/menu.pdf"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/menu", summary="Restaurant Menu QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_menu_qr(body: MenuRequest):
    """Generate a QR code that links to a restaurant's digital menu."""
    try:
        png = _qr_to_png_bytes(body.content.menu_url, design=body.design)
        return _stream_response(png, "menu_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. PDF QR
# ─────────────────────────────────────────────────────────────────────────────

class PDFContent(BaseModel):
    """Payload fields for a PDF document QR code."""
    pdf_url: str = Field(..., min_length=5, max_length=2048, description="Direct URL to the PDF file.")

    @field_validator("pdf_url")
    @classmethod
    def validate_pdf_url(cls, v: str) -> str:
        _validate_http_url(v, "pdf_url")
        return v


class PDFRequest(BaseModel):
    type: Literal["pdf"] = Field("pdf", description="QR type identifier.")
    content: PDFContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "pdf",
                "content": {"pdf_url": "https://example.com/document.pdf"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/pdf", summary="PDF QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_pdf_qr(body: PDFRequest):
    """Generate a QR code that links directly to a PDF document."""
    try:
        png = _qr_to_png_bytes(body.content.pdf_url, design=body.design)
        return _stream_response(png, "pdf_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. UPI Payment QR
# ─────────────────────────────────────────────────────────────────────────────

class UPIContent(BaseModel):
    """Payload fields for a UPI payment QR code."""
    upi_id: str = Field(..., min_length=5, max_length=128, description="UPI VPA address (e.g. name@okicici).")
    payee_name: str = Field(..., min_length=1, max_length=128, description="Name of the payee.")
    amount: Optional[float] = Field(None, ge=0.01, le=10_000_000, description="Amount in INR (optional).")
    currency: Optional[str] = Field("INR", max_length=3, description="Currency code — default INR.")
    note: Optional[str] = Field(None, max_length=128, description="Transaction note / remarks.")

    @field_validator("upi_id")
    @classmethod
    def validate_upi_id(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("upi_id must be a valid VPA in the format name@bank (e.g. john@okicici).")
        return v.strip()


class UPIRequest(BaseModel):
    type: Literal["upi"] = Field("upi", description="QR type identifier.")
    content: UPIContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "upi",
                "content": {
                    "upi_id": "merchant@okicici",
                    "payee_name": "Merchant Name",
                    "amount": 99.00,
                    "currency": "INR",
                    "note": "Order #1234",
                },
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/upi", summary="UPI Payment QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_upi_qr(body: UPIRequest):
    """Generate a UPI payment QR code compatible with GPay, PhonePe, Paytm, etc."""
    try:
        c = body.content
        payload = (
            f"upi://pay?"
            f"pa={quote(c.upi_id)}"
            f"&pn={quote(c.payee_name)}"
            f"&cu={c.currency or 'INR'}"
        )
        if c.amount is not None:
            payload += f"&am={c.amount:.2f}"
        if c.note:
            payload += f"&tn={quote(c.note)}"
        png = _qr_to_png_bytes(payload, design=body.design)
        return _stream_response(png, "upi_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Plain Text QR
# ─────────────────────────────────────────────────────────────────────────────

class PlainTextContent(BaseModel):
    """Payload fields for a plain-text QR code."""
    text: str = Field(..., min_length=1, max_length=4296, description="Any plain text to encode.")


class PlainTextRequest(BaseModel):
    type: Literal["text"] = Field("text", description="QR type identifier.")
    content: PlainTextContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "text",
                "content": {"text": "Hello, World!"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/text", summary="Plain Text QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_text_qr(body: PlainTextRequest):
    """Generate a QR code that encodes arbitrary plain text (max 4 296 chars)."""
    try:
        png = _qr_to_png_bytes(body.content.text, design=body.design, error_correction=qrcode.constants.ERROR_CORRECT_L)
        return _stream_response(png, "text_qr.png")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 10. Email QR
# ─────────────────────────────────────────────────────────────────────────────

class EmailContent(BaseModel):
    """Payload fields for a mailto: QR code."""
    to: str = Field(..., max_length=254, description="Recipient e-mail address.")
    subject: Optional[str] = Field(None, max_length=998, description="Email subject line.")
    body: Optional[str] = Field(None, max_length=4096, description="Email body text.")

    @field_validator("to")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v.strip()):
            raise ValueError("'to' must be a valid e-mail address.")
        return v.strip()


class EmailRequest(BaseModel):
    type: Literal["email"] = Field("email", description="QR type identifier.")
    content: EmailContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "email",
                "content": {
                    "to": "hello@example.com",
                    "subject": "Inquiry",
                    "body": "Hi, I have a question …",
                },
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/email", summary="Email QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_email_qr(body: EmailRequest):
    """Generate a mailto: QR code that opens the mail app with pre-filled fields."""
    try:
        c = body.content
        payload = f"mailto:{quote(c.to)}"
        params = []
        if c.subject:
            params.append(f"subject={quote(c.subject)}")
        if c.body:
            params.append(f"body={quote(c.body)}")
        if params:
            payload += "?" + "&".join(params)
        png = _qr_to_png_bytes(payload, design=body.design, error_correction=qrcode.constants.ERROR_CORRECT_L)
        return _stream_response(png, "email_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 11. Phone QR
# ─────────────────────────────────────────────────────────────────────────────

class PhoneContent(BaseModel):
    """Payload fields for a tel: QR code."""
    phone: str = Field(
        ..., min_length=7, max_length=20,
        description="Phone number with country code (e.g. +919876543210).",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("phone must contain 7-15 digits, optionally prefixed with '+'.")
        return cleaned


class PhoneRequest(BaseModel):
    type: Literal["phone"] = Field("phone", description="QR type identifier.")
    content: PhoneContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "phone",
                "content": {"phone": "+919876543210"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/phone", summary="Phone QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_phone_qr(body: PhoneRequest):
    """Generate a tel: QR code that initiates a phone call when scanned."""
    try:
        png = _qr_to_png_bytes(f"tel:{body.content.phone}", design=body.design)
        return _stream_response(png, "phone_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 12. SMS QR
# ─────────────────────────────────────────────────────────────────────────────

class SMSContent(BaseModel):
    """Payload fields for an sms: QR code."""
    phone: str = Field(..., min_length=7, max_length=20, description="Recipient phone with country code.")
    message: Optional[str] = Field(None, max_length=1600, description="Pre-filled SMS body.")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("phone must contain 7-15 digits, optionally prefixed with '+'.")
        return cleaned


class SMSRequest(BaseModel):
    type: Literal["sms"] = Field("sms", description="QR type identifier.")
    content: SMSContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "sms",
                "content": {"phone": "+919876543210", "message": "Hi there!"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/sms", summary="SMS QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_sms_qr(body: SMSRequest):
    """Generate an sms: QR code that opens the SMS app with a pre-filled number and message."""
    try:
        c = body.content
        payload = f"sms:{c.phone}"
        if c.message:
            payload += f"?body={quote(c.message)}"
        png = _qr_to_png_bytes(payload, design=body.design, error_correction=qrcode.constants.ERROR_CORRECT_L)
        return _stream_response(png, "sms_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 13. Location / Maps QR
# ─────────────────────────────────────────────────────────────────────────────

class LocationContent(BaseModel):
    """Payload fields for a Google Maps location QR code."""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (−90 to 90).")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (−180 to 180).")
    label: Optional[str] = Field(None, max_length=128, description="Optional human-readable place name.")


class LocationRequest(BaseModel):
    type: Literal["location"] = Field("location", description="QR type identifier.")
    content: LocationContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "location",
                "content": {"latitude": 28.6139, "longitude": 77.2090, "label": "New Delhi"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/location", summary="Location / Maps QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_location_qr(body: LocationRequest):
    """Generate a Google Maps QR code for a specific geographic coordinate."""
    try:
        c = body.content
        if c.label:
            payload = f"https://maps.google.com/?q={c.latitude},{c.longitude}({quote(c.label)})"
        else:
            payload = f"https://maps.google.com/?q={c.latitude},{c.longitude}"
        png = _qr_to_png_bytes(payload, design=body.design)
        return _stream_response(png, "location_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 14. Social Media QR
# ─────────────────────────────────────────────────────────────────────────────

class SocialPlatformEnum(str, Enum):
    instagram = "instagram"
    twitter   = "twitter"
    linkedin  = "linkedin"
    facebook  = "facebook"
    youtube   = "youtube"
    tiktok    = "tiktok"
    github    = "github"
    custom    = "custom"


class SocialContent(BaseModel):
    """Payload fields for a social media profile QR code."""
    platform: SocialPlatformEnum = Field(..., description="Social media platform.")
    profile_url: str = Field(..., min_length=5, max_length=2048, description="Full profile / page URL.")

    @field_validator("profile_url")
    @classmethod
    def validate_profile_url(cls, v: str) -> str:
        _validate_http_url(v, "profile_url")
        return v


class SocialRequest(BaseModel):
    type: Literal["social"] = Field("social", description="QR type identifier.")
    content: SocialContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "social",
                "content": {"platform": "instagram", "profile_url": "https://instagram.com/yourprofile"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/social", summary="Social Media QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_social_qr(body: SocialRequest):
    """Generate a QR code linking to a social media profile."""
    try:
        png = _qr_to_png_bytes(body.content.profile_url, design=body.design)
        return _stream_response(png, f"{body.content.platform.value}_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 15. Event / Calendar QR
# ─────────────────────────────────────────────────────────────────────────────

class EventContent(BaseModel):
    """Payload fields for an iCalendar VEVENT QR code."""
    title: str = Field(..., min_length=1, max_length=256, description="Event title / summary.")
    start_datetime: str = Field(
        ..., min_length=8, max_length=16,
        description="Event start — YYYYMMDDTHHMMSS or YYYYMMDD (e.g. 20261231T180000).",
    )
    end_datetime: str = Field(
        ..., min_length=8, max_length=16,
        description="Event end — YYYYMMDDTHHMMSS or YYYYMMDD.",
    )
    location: Optional[str] = Field(None, max_length=256, description="Venue address or name.")
    description: Optional[str] = Field(None, max_length=1024, description="Event details.")

    @field_validator("start_datetime", "end_datetime")
    @classmethod
    def validate_datetime(cls, v: str) -> str:
        v = v.strip().replace("-", "").replace(":", "")
        if not re.match(r"^\d{8}(T\d{6})?$", v):
            raise ValueError("Datetime must be YYYYMMDD or YYYYMMDDTHHMMSS (e.g. 20261231T090000).")
        return v


class EventRequest(BaseModel):
    type: Literal["event"] = Field("event", description="QR type identifier.")
    content: EventContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "event",
                "content": {
                    "title": "Annual Meetup",
                    "start_datetime": "20261231T180000",
                    "end_datetime": "20261231T210000",
                    "location": "Mumbai, India",
                    "description": "Year-end developer meetup",
                },
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/event", summary="Event / Calendar QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_event_qr(body: EventRequest):
    """Generate an iCalendar (VEVENT) QR code. Scanning adds the event to the phone's calendar."""
    try:
        c = body.content
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "BEGIN:VEVENT",
            f"SUMMARY:{c.title}",
            f"DTSTART:{c.start_datetime}",
            f"DTEND:{c.end_datetime}",
        ]
        if c.location:    lines.append(f"LOCATION:{c.location}")
        if c.description: lines.append(f"DESCRIPTION:{c.description}")
        lines += ["END:VEVENT", "END:VCALENDAR"]
        payload = "\r\n".join(lines)
        png = _qr_to_png_bytes(payload, design=body.design, error_correction=qrcode.constants.ERROR_CORRECT_L)
        return _stream_response(png, "event_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 16. App Download QR
# ─────────────────────────────────────────────────────────────────────────────

class AppDownloadContent(BaseModel):
    """Payload fields for an app download QR code."""
    app_url: str = Field(..., min_length=5, max_length=2048, description="App Store, Play Store, or universal link.")

    @field_validator("app_url")
    @classmethod
    def validate_app_url(cls, v: str) -> str:
        _validate_http_url(v, "app_url")
        return v


class AppDownloadRequest(BaseModel):
    type: Literal["app-download"] = Field("app-download", description="QR type identifier.")
    content: AppDownloadContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "app-download",
                "content": {"app_url": "https://play.google.com/store/apps/details?id=com.example.app"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/app-download", summary="App Download QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_app_download_qr(body: AppDownloadRequest):
    """Generate a QR code linking to an app's download page (Play Store, App Store, etc.)."""
    try:
        png = _qr_to_png_bytes(body.content.app_url, design=body.design)
        return _stream_response(png, "app_download_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 17. Image QR
# ─────────────────────────────────────────────────────────────────────────────

class ImageContent(BaseModel):
    """Payload fields for an image-link QR code."""
    image_url: str = Field(..., min_length=5, max_length=2048, description="Publicly accessible image URL.")

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        _validate_http_url(v, "image_url")
        return v


class ImageRequest(BaseModel):
    type: Literal["image"] = Field("image", description="QR type identifier.")
    content: ImageContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "image",
                "content": {"image_url": "https://example.com/photo.jpg"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/image", summary="Image QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_image_qr(body: ImageRequest):
    """Generate a QR code that links to an image URL. Scanning opens the image in the browser."""
    try:
        png = _qr_to_png_bytes(body.content.image_url, design=body.design)
        return _stream_response(png, "image_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 18. Google Forms QR
# ─────────────────────────────────────────────────────────────────────────────

class GoogleFormContent(BaseModel):
    """Payload fields for a Google Forms QR code."""
    form_url: str = Field(..., min_length=5, max_length=2048, description="Google Form shareable URL.")

    @field_validator("form_url")
    @classmethod
    def validate_form_url(cls, v: str) -> str:
        _validate_http_url(v, "form_url")
        return v


class GoogleFormRequest(BaseModel):
    type: Literal["google-form"] = Field("google-form", description="QR type identifier.")
    content: GoogleFormContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "google-form",
                "content": {"form_url": "https://docs.google.com/forms/d/e/XXXXXX/viewform"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/google-form", summary="Google Forms QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_google_form_qr(body: GoogleFormRequest):
    """Generate a QR code that links directly to a Google Form."""
    try:
        png = _qr_to_png_bytes(body.content.form_url, design=body.design)
        return _stream_response(png, "google_form_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 19. Multi-Link / Landing-page QR
# ─────────────────────────────────────────────────────────────────────────────

class MultiLinkContent(BaseModel):
    """Payload fields for a multi-link landing-page QR code."""
    landing_url: str = Field(..., min_length=5, max_length=2048, description="Multi-link landing page URL.")

    @field_validator("landing_url")
    @classmethod
    def validate_landing_url(cls, v: str) -> str:
        _validate_http_url(v, "landing_url")
        return v


class MultiLinkRequest(BaseModel):
    type: Literal["multi-link"] = Field("multi-link", description="QR type identifier.")
    content: MultiLinkContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "multi-link",
                "content": {"landing_url": "https://linktr.ee/yourprofile"},
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/multi-link", summary="Multi-Link QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_multi_link_qr(body: MultiLinkRequest):
    """Generate a QR code for a multi-link landing page (Linktree, Beacons, Bento, etc.)."""
    try:
        png = _qr_to_png_bytes(body.content.landing_url, design=body.design)
        return _stream_response(png, "multi_link_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# 20. Bitcoin / Crypto QR
# ─────────────────────────────────────────────────────────────────────────────

class CryptoNetworkEnum(str, Enum):
    bitcoin  = "bitcoin"
    ethereum = "ethereum"
    litecoin = "litecoin"
    dogecoin = "dogecoin"
    custom   = "custom"


class CryptoContent(BaseModel):
    """Payload fields for a BIP-21 cryptocurrency payment QR code."""
    network: CryptoNetworkEnum = Field(
        CryptoNetworkEnum.bitcoin,
        description="Blockchain network: bitcoin | ethereum | litecoin | dogecoin | custom.",
    )
    address: str = Field(..., min_length=20, max_length=128, description="Recipient wallet address.")
    amount: Optional[float] = Field(None, gt=0, description="Optional coin amount to request.")
    label: Optional[str] = Field(None, max_length=128, description="Optional merchant / label name.")
    message: Optional[str] = Field(None, max_length=256, description="Optional payment note.")

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 20:
            raise ValueError("Wallet address must be at least 20 characters long.")
        return v


class CryptoRequest(BaseModel):
    type: Literal["crypto"] = Field("crypto", description="QR type identifier.")
    content: CryptoContent
    design: DesignOptions = Field(default_factory=DesignOptions)
    output: OutputOptions = Field(default_factory=OutputOptions)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "crypto",
                "content": {
                    "network": "bitcoin",
                    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf",
                    "amount": 0.001,
                    "label": "Donation",
                    "message": "Thank you!",
                },
                "design": {"foreground": "#000000", "background": "#FFFFFF", "box_size": 10, "border": 4},
                "output": {"format": "png"},
            }
        }
    }


@router.post("/crypto", summary="Bitcoin / Crypto QR", tags=["QR Code"],
    responses={
        200: {
            "description": "QR code PNG image generated successfully.",
            "content": {"image/png": {"schema": {"type": "string", "format": "binary"}}},
        },
        422: {
            "description": "Validation error — one or more request fields are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {"loc": ["body", "content", "field"], "msg": "error message", "type": "value_error"}
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error during QR generation.",
            "content": {
                "application/json": {
                    "example": {"detail": "QR generation failed: <reason>"}
                }
            },
        },
    }
)
async def generate_crypto_qr(body: CryptoRequest):
    """Generate a BIP-21 compatible cryptocurrency payment QR code."""
    try:
        c = body.content
        scheme = c.network.value if c.network != CryptoNetworkEnum.custom else "bitcoin"
        payload = f"{scheme}:{c.address}"
        params = []
        if c.amount  is not None: params.append(f"amount={c.amount}")
        if c.label:               params.append(f"label={quote(c.label)}")
        if c.message:             params.append(f"message={quote(c.message)}")
        if params:
            payload += "?" + "&".join(params)
        png = _qr_to_png_bytes(payload, design=body.design)
        return _stream_response(png, "crypto_qr.png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QR generation failed: {exc}")
