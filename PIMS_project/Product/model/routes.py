from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from shared.database import get_db
import Product.model.models as models, Product.model.schemas as schemas
from starlette import status
from shared.security import user_access
from Product.model.services import check_product, validate_and_process_product
from Product.model.models import Product
from Users.model.models import Users
from sqlalchemy import func
from Product.model.schemas import filter_products
from shared.send_mail import send_email
from datetime import datetime
import csv, os

router = APIRouter(prefix='/products', tags=['products'])


@router.get("/view/products/")
def viewproduct(session: Session=Depends(get_db),
                current_user: Users = Depends(user_access)):

    if current_user.role == "admin":
        product = session.query(Product).order_by(Product.name).all()
        
    else:
        product = session.query(Product).filter(Product.owner_id == current_user.id).order_by(Product.name).all()
        if not product:
            return {"message": "You have added nothing yet."}
    
    return product

@router.get("/view/product/{product_id}")
def viewproduct_byid(product_id : int, 
                session: Session=Depends(get_db),
                current_user: Users = Depends(user_access)):
    
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product with id {product_id} doesn't exist") 
    
    check_product(product, current_user)
    return product
    
@router.post("/add/products/")
def addproduct(item: schemas.product,
               session: Session=Depends(get_db),
               current_user: Users = Depends(user_access)):

    product = session.query(Product).filter(
        func.lower(Product.name) == func.lower(item.name),
        Product.category == item.category,
        Product.description == item.description,
        Product.owner_id == current_user.id
    ).first()
    
    if product:
        raise HTTPException(status_code=status.HTTP_302_FOUND,
                            detail="This product already exists")
        
    new_product = Product(
        name= item.name.lower(),  
        category = item.category, 
        description = item.description,
        price = item.price,
        stock = item.stock,
        owner_id = current_user.id
    )

    if new_product.stock < 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Stock should be greater than zero.")
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return {f"Product {new_product.name} with id {new_product.id} added successfully"}

@router.put("/update/products/{product_id}")
def updateproducts(product_id: int,
                   item: schemas.product,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)
                  ):
    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"product with {product_id} not found.")
    
    check_product(product, current_user)
    
    if item.name:
        product.name = item.name.lower()  
    if item.category:
        product.category = item.category
    if item.description:
        product.description = item.description
    if item.price:
        product.price = item.price
    if item.stock:
        product.stock = item.stock
    if item.image_url:
        product.image_url = item.image_url

    if product.stock < 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Stock should be greater than zero.")

    session.commit()
    session.refresh(product)
    
    return {"message": "product has been updated successfully."}

@router.delete("/delete/products/{product_id}")
def deleteproducts(product_id:int,
                   session: Session=Depends(get_db),
                   current_user: Users = Depends(user_access)):
   
   product = session.query(Product).filter(Product.id == product_id).first()

   if not product:
       raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} doesn't exist"
        )
   
   
   if product and (product.owner_id == current_user.id or current_user.role == "admin"):
       session.delete(product)
       session.commit()
       return {f"Product {product_id} was successfully deleted."}
       
   check_product(product, current_user)
   
@router.post("/order")
def sale(stock: schemas.SaleSchema, 
         session: Session = Depends(get_db),
         current_user: Users = Depends(user_access)):
   
    product = session.query(Product).filter(
        func.lower(Product.name) == func.lower(stock.name)
    ).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    validate_and_process_product(product, stock)

    threshold = 60
    if product.stock < threshold:
        low_stock_message = f"""
        Subject: Low Stock Alert

        Hello,

        This is an automated notification to inform you that the stock for {product.name} has dropped below the set threshold.

        Remaining Stock: {product.stock} units
        Threshold: {threshold} units

        Please review the stock levels and take necessary action to restock as needed.

        Thank you.

        Best regards,
        Inventory Team
        """
        send_email(
            "syedaghazalzehra89@gmail.com",
            stock.email,
            f"Low Stock Alert: {product.name}",
            low_stock_message
        )
    session.commit()

    sale_confirmation_message = f"""
    Subject: Sale Confirmation

    Hello,

    We are pleased to inform you that a sale has been successfully processed for the product "{product.name}".

    Details of the sale:
    Product Name: {product.name}
    Quantity Purchased: {stock.stock} units
    Total Price: {product.price * stock.stock} rupees
    Sale Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Thank you for choosing our service.

    Best regards,
    Your Company Name
    Sales Team
    """
    send_email(
        "syedaghazalzehra89@gmail.com",
        stock.email,
        "Sale Confirmation",
        sale_confirmation_message
    )

    return {"message": "Thank you for your purchase! You'll receive a sale confirmation email shortly."}
  
@router.post("/search")
async def search_products(
    search_params: dict,  
    session: Session = Depends(get_db),
    current_user: Users = Depends(user_access)
):

    name = search_params.get('name')
    category = search_params.get('category')

    if not name and not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Provide at least one search parameter"
        )

    query = session.query(Product)

    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))

    filtered_products = query.all()

    if not filtered_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No products found for search parameters"
        )
    
    return filtered_products


@router.post("/filter")
def get_products(
    product: filter_products, 
    session: Session = Depends(get_db),
    current_user: Users = Depends(user_access)
):

    search_params = {
        "min_price": product.min_price,
        "max_price": product.max_price,
        "min_stock": product.min_stock,
        "max_stock": product.max_stock
    }
    

    query = session.query(Product)

    if search_params.get("min_price"):
        query = query.filter(Product.price >= search_params["min_price"])
    if search_params.get("max_price"):
        query = query.filter(Product.price <= search_params["max_price"])
    if search_params.get("min_stock"):
        query = query.filter(Product.stock >= search_params["min_stock"])
    if search_params.get("max_stock"):
        query = query.filter(Product.stock <= search_params["max_stock"])

    products = query.all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found matching the criteria")
    
    return {"products": products}

@router.get("/export/inventory/")
def export_inventory(session: Session = Depends(get_db),
                     current_user: Users = Depends(user_access)):
    
    inventory_items = session.query(Product).all()

    new_directory = r"C:\Users\s\apivenv\PIMS_project\Product\product_inventory"

    os.makedirs(new_directory, exist_ok=True)

    file_name = os.path.join(new_directory, f"inventory_export_{datetime.now().strftime('%Y-%m-%d')}.csv")

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID", "Name", "Description", "Price", "Stock", "Category", "Image URL", "Created At", "Updated At", "is_sold"
        ])

        for item in inventory_items:
            writer.writerow([
                item.id, item.name, item.description, item.price, item.stock,
                item.category, item.image_url, item.created_at, item.updated_at
            ])
    
    return {"message": f"Inventory data has been exported to {file_name}"} 
   

   

