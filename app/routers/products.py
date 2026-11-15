from fastapi import APIRouter, Depends, HTTPException
from app.database import get_connection
from app.repositories.product_repo import retreive_product_details_by_id, get_products_collectively
from app.services import new_product
from app.schemas.product import RequestModelCreateProduct, ResponseModelCreateProduct, ResponseModelGetIdProductDetails, ResponseModelGetProducts

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", status_code=201, response_model=ResponseModelCreateProduct)
def create_product_endpoint(product: RequestModelCreateProduct, connection=Depends(get_connection)):
    return new_product(connection, product.name, product.description, product.price, product.quantity)

@router.get("/{id}", status_code=200, response_model=ResponseModelGetIdProductDetails)
def get_product_details_by_id_endpoint(id: int, connection=Depends(get_connection)):
    product_details = retreive_product_details_by_id(connection, id)
    if not product_details:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_details

@router.get("/", status_code=200, response_model=ResponseModelGetProducts)
def get_products_endpoint(connection=Depends(get_connection)):
    products = get_products_collectively(connection)
    if not products:
        return {"Inventory": []} 
    return {"Inventory": products}