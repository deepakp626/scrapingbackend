from fastapi import APIRouter, Depends, UploadFile, File, Form,Body
from fastapi.responses import JSONResponse
from services.blogServices import createBlog as create_blog_service ,getBlogBySlug, updateBlogService,deleteBlogService,get_paginated_blogs
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import date
from database.db import get_db

router = APIRouter()

class BlogResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    html_content: str
    date: date
    thumbnail_image_url:str
    thumbnail_image_name:str
    # class Config:
    #     from_attributes = True # Allows Pydantic to read SQLAlchemy models

class BlogCreate(BaseModel):
    slug: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    title: str
    description: str
    html_content: str
    thumbnail_image_name: str

    @classmethod
    def as_form(
        cls,
        slug: str = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        html_content: str = Form(...),
        thumbnail_image_name: str = Form(...),
    ):
        return cls(
            slug=slug.strip(),
            title=title.strip(),
            description=description.strip(),
            html_content=html_content.strip(),
            thumbnail_image_name=thumbnail_image_name.strip(),
        )

@router.post("/createBlog",response_model=BlogResponse)
async def createBlog(
    blog_data: BlogCreate = Depends(BlogCreate.as_form),
    thumbnail_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    print("test here")
    # image_bytes = None
    # image_name = None
    # if thumbnail_image:
    #     image_bytes = await thumbnail_image.read()
    #     image_name = blog_data.thumbnail_image_name
    # else:
    #     return JSONResponse(content={"message":"Thumbnail image is required"},status_code=400)
    
    #  here upload image and store image data in database or compress image size with  utils
    blogData = await create_blog_service(
        db=db,
        slug=blog_data.slug,
        title=blog_data.title,
        description=blog_data.description,
        html_content=blog_data.html_content,
        thumbnail_image=await thumbnail_image.read(),
    )

    return JSONResponse(
        content={
            "data":blogData,
            "message":"Blog created successfully"
            },
        status_code=201
    )




@router.get("/getBlogBySlug",response_model=BlogResponse)
async def getLBog(slug:str,db: AsyncSession = Depends(get_db)):

    slug = slug.strip()
    if (slug == None or slug == ""):
        return JSONResponse(content={"message":"Blog slug is required"},status_code=400)
    
    blogData = await getBlogBySlug(db=db,slug=slug)

    if (blogData == None):
        return JSONResponse(content={"message":"Blog not found"},status_code=404)

    return JSONResponse(content=blogData,status_code=200)



class BlogUpdate(BaseModel):
    slug: str = Field(..., min_length=3)
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    html_content: str = Field(..., min_length=1)
    thumbnail_image_name: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        slug: str = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        html_content: str = Form(...),
        thumbnail_image_name: Optional[str] = Form(None),
    ):
        return cls(
            slug=slug.strip(),
            title=title.strip(),
            description=description.strip(),
            html_content=html_content.strip(),
            thumbnail_image_name=thumbnail_image_name.strip() if thumbnail_image_name else None,
        )

@router.put("/updateBlog",response_model=BlogResponse)
async def updateBlog(blog_data: BlogUpdate = Depends(BlogUpdate.as_form),thumbnail_image: UploadFile = File(...),db: AsyncSession = Depends(get_db)):
    update_blog = await updateBlogService(
        db=db,
        slug=blog_data.slug,
        title=blog_data.title,
        description=blog_data.description,
        html_content=blog_data.html_content,
        thumbnail_image=await thumbnail_image.read(),
        thumbnail_image_name=blog_data.thumbnail_image_name,
    )
    if update_blog == None:
        return JSONResponse(content={"message":"Blog not found"},status_code=404)

    return JSONResponse(content=update_blog,
                        status_code=200
                        )


@router.delete("/deleteBlog")
async def deleteBlog(slug:str,db:AsyncSession = Depends(get_db)):

    slug = slug.strip()
    if(slug == None or slug == ""):
        return JSONResponse(content={"message":"Blog slug is required"},status_code=400)
    
    deleted_blog  = await deleteBlogService(db=db,slug=slug)

    if  deleted_blog == None:
        return JSONResponse(content={"message":"Blog not found"},status_code=404)
    
    return JSONResponse(content=deleted_blog,status_code=200)



@router.get("/getPaginatedBlog")
async def getPaginatedBLog(page:int=1,limit:int=10,db:AsyncSession = Depends(get_db)):
    try:
        blogs = await get_paginated_blogs(db,page,limit)
        
        return JSONResponse(content=blogs,status_code=200)
    except Exception as e:
        return JSONResponse(content={"message":str(e)},status_code=500)  