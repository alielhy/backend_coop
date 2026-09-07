import datetime as dt

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class Cooperative(Base):
    __tablename__ = "cooperatives"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    template_id = Column(String, default="classic", nullable=False)

    # created_by is unused today (no auth yet) but present so adding
    # ownership later is a migration, not a schema redesign.
    created_by = Column(Integer, nullable=True)

    activity_type = Column(String, nullable=True)  # e.g. "agriculture", "artisanat"
    founded_year = Column(String, nullable=True)

    # trilingual fields: {"fr": "...", "en": "...", "ar": "..."}
    name = Column(JSON, nullable=False)
    tagline_short = Column(JSON, nullable=True)
    eyebrow = Column(JSON, nullable=True)
    tagline = Column(JSON, nullable=True)
    province = Column(JSON, nullable=True)
    member_count_label = Column(JSON, nullable=True)
    about_paragraphs = Column(JSON, nullable=True)  # {"fr": [...], "en": [...], "ar": [...]}
    facts = Column(JSON, nullable=True)              # {"fr": [...], "en": [...], "ar": [...]}
    contact_intro = Column(JSON, nullable=True)
    hero_photo_alt = Column(JSON, nullable=True)
    hero_caption = Column(JSON, nullable=True)

    # not translated: addresses/phone numbers are the same in every language
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    email = Column(String, nullable=True)
    social_links = Column(JSON, nullable=True)  # [{"label": "Facebook", "url": "..."}]

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    products = relationship("Product", back_populates="cooperative", cascade="all, delete-orphan", order_by="Product.position")
    media = relationship("Media", back_populates="cooperative", cascade="all, delete-orphan", order_by="Media.position")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id"), nullable=False)

    name = Column(JSON, nullable=False)
    description = Column(JSON, nullable=True)
    price = Column(JSON, nullable=True)  # {"fr": "90 DH", "en": "90 MAD", "ar": "90 درهم"}
    image_path = Column(String, nullable=True)
    position = Column(Integer, default=0)

    cooperative = relationship("Cooperative", back_populates="products")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    cooperative_id = Column(Integer, ForeignKey("cooperatives.id"), nullable=False)

    type = Column(String, nullable=False)  # "logo" | "gallery"
    file_path = Column(String, nullable=False)
    alt_text = Column(JSON, nullable=True)
    position = Column(Integer, default=0)

    cooperative = relationship("Cooperative", back_populates="media")