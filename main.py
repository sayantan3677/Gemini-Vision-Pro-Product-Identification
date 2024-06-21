import os
from typing import List

from dotenv import load_dotenv


from llama_index.multi_modal_llms.gemini import GeminiMultiModal
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls


from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# creating FastAPI application
app = FastAPI()

# Linking template directory using Jinja Template
templates = Jinja2Templates(directory="templates")

# Mounting Static files from static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Loading environment from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Pydantic Product data model
class Product(BaseModel):
    id: int
    product_name: str
    color: str
    category: str
    description: str


# Pydantic Product list data model
class ExtractedProductsResponse(BaseModel):
    products: List[Product]


# Pydantic data model for requesting image
class ImageRequest(BaseModel):
    url: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    # "url": "https://assets.vogue.com/photos/65666c175a40ab86bc7abdaa/master/w_1280,c_limit/ITEMS-VUITTON-SPEEDY_HR001.jpg",
                    "url": "https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
                }
            ]
        }
    )


# Prompt template for extracting information from image
prompt_template_str = """\
                You are an expert system designed to extract products from images for\
                an ecommerce application. Please provide the product name, product color,\
                product category and a descriptive query to search for the product.\
                Accurtely identify every product in an image and provide a descriptive\
                query to search for the product. You just return a correctly formatted\
                JSON object with the product name, product color, product category and\
                description for each product in the image\
"""


# Extracting product information from image using Gemini Pro Vision model APIs
def gemini_extractor(model_name, output_class, image_documents, prompt_template_str):
    gemini_llm = GeminiMultiModal(api_key=GOOGLE_API_KEY, model_name=model_name)

    llm_program = MultiModalLLMCompletionProgram.from_defaults(
        output_parser=PydanticOutputParser(output_class),
        image_documents=image_documents,
        prompt_template_str=prompt_template_str,
        multi_modal_llm=gemini_llm,
        verbose=True,
    )

    response = llm_program()
    return response


# Landing page for the application
@app.get("/", response_class=HTMLResponse)
def landingpage(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})


# Simple storing response data to list
all_products = []


# Endpoint to extract products from images
@app.post("/extracted_products")
def extracted_products(image_request: ImageRequest):
    responses = gemini_extractor(
        model_name="models/gemini-pro-vision",
        output_class=ExtractedProductsResponse,
        image_documents=load_image_urls([image_request.url]),
        prompt_template_str=prompt_template_str,
    )
    all_products.append(responses)
    return responses


# Endpoint to return all products in JSON format
@app.get("/api/products/", response_model=list[ExtractedProductsResponse])
async def get_all_products_api():
    return all_products
