from database.db import engine

from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,Date
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Blog(Base):
    __tablename__ = "blogs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    slug:Mapped[str] = mapped_column(String(255),unique=True,index=True,nullable=False)
    title: Mapped[str] = mapped_column(String(100),nullable=False)
    description:Mapped[str] = mapped_column(String(500))
    html_content: Mapped[str] = mapped_column(String)
    date:Mapped[Date]=mapped_column(Date,default=datetime.now())

    thumbnail_image_url:Mapped[str | None] = mapped_column(String,nullable=True)
    thumbnail_image_name:Mapped[str] = mapped_column(String,nullable=True)
    



# Base.metadata.create_all(engine)
