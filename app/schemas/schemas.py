from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict

TriText = Dict[str, str]        # {"fr": "...", "en": "...", "ar": "..."}
TriList = Dict[str, List[str]]  # {"fr": [...], "en": [...], "ar": [...]}


class SocialLink(BaseModel):
    label: str
    url: str


# ---------- Product ----------

class ProductIn(BaseModel):
    name: TriText
    description: Optional[TriText] = None
    price: Optional[TriText] = None
    position: int = 0


class ProductOut(ProductIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_path: Optional[str] = None


# ---------- Media ----------

class MediaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    file_path: str
    alt_text: Optional[TriText] = None
    position: int = 0


# ---------- Cooperative ----------

class CooperativeIn(BaseModel):
    slug: str
    template_id: str = "classic"
    activity_type: Optional[str] = None
    founded_year: Optional[str] = None
    name: TriText
    tagline_short: Optional[TriText] = None
    eyebrow: Optional[TriText] = None
    tagline: Optional[TriText] = None
    province: Optional[TriText] = None
    member_count_label: Optional[TriText] = None
    about_paragraphs: Optional[TriList] = None
    facts: Optional[TriList] = None
    contact_intro: Optional[TriText] = None
    hero_photo_alt: Optional[TriText] = None
    hero_caption: Optional[TriText] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    social_links: Optional[List[SocialLink]] = None


class CooperativeUpdate(CooperativeIn):
    slug: Optional[str] = None
    name: Optional[TriText] = None


class CooperativeOut(CooperativeIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    products: List[ProductOut] = []
    media: List[MediaOut] = []