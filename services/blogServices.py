from fastapi import HTTPException,status
from models.blog import Blog
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from sqlalchemy import select, func
from math import ceil
from database.storage import upload_image,delete_image,replace_image
from storage3.exceptions import StorageApiError

# from fastapi.response import JSONResponse

# Database Instance / session factory
# db = SessionLocal()

def _normalize_meta_keywords(meta_keywords: str | list[str] | None) -> list[str] | None:
    if meta_keywords is None:
        return None

    keywords = meta_keywords.split(",") if isinstance(meta_keywords, str) else meta_keywords
    return [keyword.strip() for keyword in keywords if keyword.strip()]


def _serialize_meta_keywords(meta_keywords: list[str] | None) -> str | None:
    return ", ".join(meta_keywords) if meta_keywords else None


async def createBlog(
    db: AsyncSession,
    slug: str,
    title: str,
    description: str,
    html_content: str,
    thumbnail_image: bytes | None = None,
    thumbnail_image_name: str | None = None,
    meta_title: str | None = None,
    meta_description: str | None = None,
    image_alt: str | None = None,
    meta_keywords: str | list[str] | None = None,
):
    """
    Create a new blog with optional thumbnail image.

    Flow:
    1. Check slug.
    2. Upload image if provided.
    3. Create DB record.
    4. Rollback + cleanup image if DB operation fails.
    """

    slug = slug.strip()

    if not slug:
        raise HTTPException(
            status_code=400,
            detail="Slug cannot be empty."
        )

    # ---------------------------------------------------------
    # 1. Check whether blog slug already exists
    # ---------------------------------------------------------
    result = await db.execute(
        select(Blog.id).where(Blog.slug == slug)
    )

    existing_blog_id = result.scalar_one_or_none()

    if existing_blog_id:
        raise HTTPException(
            status_code=409,
            detail=f"Blog slug already exists: {slug}, create unique slug"
        )

    # ---------------------------------------------------------
    # 2. Upload thumbnail
    # ---------------------------------------------------------
    thumbnail_image_url = None
    image_uploaded = False

    if thumbnail_image:
        try:
            upload_result = upload_image(
                slug=slug,
                file_bytes=thumbnail_image,
            )

            if not upload_result:
                raise HTTPException(
                    status_code=500,
                    detail="Image upload returned empty response."
                )

            thumbnail_image_url = upload_result.get("url")

            if not thumbnail_image_url:
                raise HTTPException(
                    status_code=500,
                    detail="Image uploaded but URL was not returned."
                )

            image_uploaded = True

        except StorageApiError as e:

            # -------------------------------------------------
            # IMPORTANT:
            # Image already exists in Supabase.
            #
            # Instead of returning 409, get/reuse the existing
            # image URL if your storage function supports it.
            # -------------------------------------------------

            raise HTTPException(
                status_code=409,
                detail=f"Image already exists or storage error: {str(e)}"
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload thumbnail: {str(e)}"
            )

    # ---------------------------------------------------------
    # 3. Create Blog object
    # ---------------------------------------------------------
    new_blog = Blog(
        slug=slug,
        title=title,
        description=description,
        html_content=html_content,
        thumbnail_image_url=thumbnail_image_url,
        thumbnail_image_name=thumbnail_image_name,
        meta_title=meta_title,
        meta_description=meta_description,
        image_alt=image_alt,
        meta_keywords=_normalize_meta_keywords(meta_keywords),
    )

    try:

        db.add(new_blog)

        await db.commit()

        await db.refresh(new_blog)

        return {
            "id": new_blog.id,
            "slug": new_blog.slug,
            "title": new_blog.title,
            "description": new_blog.description,
            "html_content": new_blog.html_content,
            "date": str(new_blog.date),
            "thumbnail_image_url": new_blog.thumbnail_image_url,
            "thumbnail_image_name": new_blog.thumbnail_image_name,
            "meta_title": new_blog.meta_title,
            "meta_description": new_blog.meta_description,
            "image_alt": new_blog.image_alt,
            "meta_keywords": _serialize_meta_keywords(new_blog.meta_keywords),
        }

    except IntegrityError as e:

        await db.rollback()

        # -----------------------------------------------------
        # DB failed after image was uploaded.
        # Remove uploaded image to avoid orphaned files.
        # -----------------------------------------------------

        if image_uploaded:
            try:
                delete_image(slug)
            except Exception:
                # Do not hide the original DB error
                pass

        raise HTTPException(
            status_code=409,
            detail=f"Blog slug already exists or violates a database constraint: {str(e.orig)}"
        )

    except SQLAlchemyError as e:

        await db.rollback()

        if image_uploaded:
            try:
                delete_image(slug)
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


async def getBlogBySlug(db: AsyncSession, slug: str):
    """
    Fetches a single blog by its slug with validation and proper HTTP exceptions 
    when not found or when the input is invalid.
    """
    # 1. Validate slug input
    if not slug or not slug.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog slug provided."
        )

    # 2. Query the database
    result = await db.execute(select(Blog).where(Blog.slug == slug.strip()))
    blog = result.scalar_one_or_none()
    
    print("blog ------------>>> ",blog,slug)
    # 3. Handle not found case using HTTPException
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with slug '{slug}' not found."
        )

    # 4. Return structured response
    return {
        "success": True,
        "status_code": 200,
        "message": "Blog fetched successfully.",
        "data": {
            "id": blog.id,
            "slug": blog.slug,
            "title": blog.title,
            "description": blog.description,
            "html_content": blog.html_content,
            "date": str(blog.date),
            "thumbnail_image_url": blog.thumbnail_image_url,
            "thumbnail_image_name": blog.thumbnail_image_name,
            "meta_title": blog.meta_title,
            "meta_description": blog.meta_description,
            "image_alt": blog.image_alt,
            "meta_keywords": _serialize_meta_keywords(blog.meta_keywords),
        }
    }


async def updateBlogService(
    db: AsyncSession,
    slug: str,
    title: str,
    description: str,
    html_content: str,
    thumbnail_image: bytes | None = None,
    thumbnail_image_name: str | None = None,
    meta_title: str | None = None,
    meta_description: str | None = None,
    image_alt: str | None = None,
    meta_keywords: str | list[str] | None = None,
):
    result = await db.execute(select(Blog).where(Blog.slug == slug))
    blog = result.scalar_one_or_none()

    if blog is None:
        return None

    if thumbnail_image:
        try:
            upload_result = replace_image(
                slug,
                new_file_bytes=thumbnail_image,
            )
        except StorageApiError as e:
            raise HTTPException(
                status_code=409,
                detail=f"Image already exists : {str(e)}"
            )

        blog.thumbnail_image_url = upload_result["url"]

    blog.title = title
    blog.description = description
    blog.html_content = html_content
    blog.thumbnail_image_name = thumbnail_image_name
    if meta_title is not None:
        blog.meta_title = meta_title
    if meta_description is not None:
        blog.meta_description = meta_description
    if image_alt is not None:
        blog.image_alt = image_alt
    if meta_keywords is not None:
        blog.meta_keywords = _normalize_meta_keywords(meta_keywords)
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
        "thumbnail_image_name":blog.thumbnail_image_name,
        "meta_title": blog.meta_title,
        "meta_description": blog.meta_description,
        "image_alt": blog.image_alt,
        "meta_keywords": _serialize_meta_keywords(blog.meta_keywords),
    }




async def deleteBlogService(db: AsyncSession, slug: str, current_user_id: int = None, is_admin: bool = False):
    """
    Deletes a blog post by its slug with robust validation, authorization checks, 
    and returns a standardized response for the frontend.
    """
    # 1. Validate slug format
    if not slug or not slug.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog slug provided."
        )

    # 2. Fetch blog from database
    result = await db.execute(select(Blog).where(Blog.slug == slug))
    blog = result.scalar_one_or_none()

    # 3. Check if blog exists
    if blog is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with slug '{slug}' not found."
        )

    # 4. Optional: Authorization check (ensure owner or admin is deleting)
    if current_user_id and not is_admin and blog.author_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this blog."
        )

    # 5. Handle image deletion safely
    try:
        delete_image(slug)
    except Exception as e:
        # Log the error properly in a production environment instead of just print
        print(f"Warning: Image deletion failed for slug '{slug}': {e}")
        # Depending on your business logic, you can choose to abort the deletion 
        # or proceed. Here we proceed with database deletion, but warn the frontend/logs.

    # 6. Delete from database and commit
    try:
        await db.delete(blog)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the blog from the database."
        )

    # 7. Return structured success response for frontend
    return {
        "success": True,
        "status_code": 200,
        "message": f"Blog with slug '{slug}' deleted successfully.",
        "data": {
            "slug": slug
        }
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
        "meta_title": blog.meta_title,
        "meta_description": blog.meta_description,
        "image_alt": blog.image_alt,
        "meta_keywords": _serialize_meta_keywords(blog.meta_keywords),
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
