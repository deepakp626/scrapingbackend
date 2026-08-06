from fastapi import HTTPException
from models.blog import Blog
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func
from math import ceil
from database.storage import upload_image,delete_image,replace_image
from storage3.exceptions import StorageApiError

# from fastapi.response import JSONResponse

# Database Instance / session factory
# db = SessionLocal()


async def  createBlog(db: AsyncSession,slug: str, title: str,description: str,html_content: str, thumbnail_image: bytes | None = None,
    thumbnail_image_name: str | None = None):


    result = await db.execute(select(Blog).where(Blog.slug == slug))
    blog = result.scalar_one_or_none()
    if blog:
        raise HTTPException(
            status_code=409,
            detail=f"Blog slug already exists slug: {slug} create new unique slug"
        )

    thumbnail_image_url = None
    if thumbnail_image:
        try:
            thumbnail_image_url = upload_image(
                slug,
                file_bytes=thumbnail_image,
            )
        except StorageApiError as e:
            raise HTTPException(
                status_code=409,
                detail=f"Image already exists : {str(e)}"
            )
    try:
        newBlog = Blog(
            slug=slug,
            title=title,
            description=description,
            html_content=html_content,
            # thumbnail_image_name=thumbnail_image_name,
            thumbnail_image_url=thumbnail_image_url.get("url"),
        )

        db.add(newBlog)

        await db.commit()
        await db.refresh(newBlog)

        return {
            "id": newBlog.id,
            "slug": newBlog.slug,
            "title": newBlog.title,
            "description": newBlog.description,
            "html_content": newBlog.html_content,
            "date": str(newBlog.date),
            # "thumbnail_image_name":newBlog.thumbnail_image_name,
            "thumbnail_image_url":newBlog.thumbnail_image_url
        }

    except SQLAlchemyError:
        await db.rollback()
        raise


async def getBlogBySlug(db:AsyncSession,slug:str):

    blog = await db.execute(select(Blog).where(Blog.slug == slug.strip()))
    blog = blog.scalar_one_or_none()
    
    if blog == None:
        return None
        

    return {
        "id": blog.id,
        "slug": blog.slug,
        "title": blog.title,
        "description": blog.description,
        "html_content": blog.html_content,
        "date": str(blog.date),
        "thumbnail_image_url":blog.thumbnail_image_url,
        "thumbnail_image_name":blog.thumbnail_image_name
    }


async def updateBlogService(db:AsyncSession, slug:str,title:str,description:str,html_content:str,thumbnail_image:bytes | None = None,thumbnail_image_name:str | None = None):
    result = await  db.execute(select(Blog).where(Blog.slug == slug))
    blog = result.scalar_one_or_none()
    
    thumbnail_image_url = blog.thumbnail_image_url
    if thumbnail_image:
        try:
            thumbnail_image_url = replace_image(
                slug,
                new_file_bytes=thumbnail_image,
            )
        except StorageApiError as e:
            raise HTTPException(
                status_code=409,
                detail=f"Image already exists : {str(e)}"
            )

    if blog == None:
        return None

    blog.title = title
    blog.description = description
    blog.html_content = html_content
    blog.thumbnail_image_url = thumbnail_image_url.get("url")
    blog.thumbnail_image_name = thumbnail_image_name
    await db.commit()
    await db.refresh(blog)
    return {
        "id": blog.id,
        "slug": blog.slug,
        "title": blog.title,
        "description": blog.description,
        "html_content": blog.html_content,
        "date": str(blog.date),
        "thumbnail_image_url":blog.thumbnail_image_url,
        "thumbnail_image_name":blog.thumbnail_image_name
    }




async def deleteBlogService(db: AsyncSession, slug: str):

    result = await db.execute(
        select(Blog).where(Blog.slug == slug)
    )

    blog = result.scalar_one_or_none()

    if blog is None:
        return None

    try:
        delete_image(slug)
    except Exception as e:
        print(f"Image delete failed: {e} : so also blog noy deleting image : {slug}")

    await db.delete(blog)
    await db.commit()

    return {
        "message": "Blog deleted successfully slug: {slug}"
    }


async def get_paginated_blogs(db: AsyncSession,page: int = 1,limit: int = 10,):
    offset = (page - 1) * limit

    # Total records
    total_result = await db.execute(
        select(func.count()).select_from(Blog)
    )
    total = total_result.scalar_one()

    # Fetch paginated blogs
    result = await db.execute(
        select(Blog)
        .order_by(Blog.id.desc())
        .offset(offset)
        .limit(limit)
    )

    blogs = result.scalars().all()
    
    blog_list = [
    {
        "id": blog.id,
        "slug": blog.slug,
        "title": blog.title,
        "description": blog.description,
        "html_content": blog.html_content,
        "date": blog.date.isoformat() if blog.date else None,
        "thumbnail_image_url": blog.thumbnail_image_url,
        "thumbnail_image_name": blog.thumbnail_image_name,
    }
    for blog in blogs
]

    return {
        "data": blog_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_records": total,
            "total_pages": ceil(total / limit) if total else 0,
            "has_next": page * limit < total,
            "has_previous": page > 1,
        },
    }