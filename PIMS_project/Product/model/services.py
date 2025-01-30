from fastapi import HTTPException
from starlette import status

def check_product(product, current_user):
    if product.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are not the owner of this item."
        )
    
def validate_and_process_product(product, stock):

    if product.stock == 0:
        product.is_sold = True
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is sold out."
        )

    if product.stock < stock.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough stock available."
        )
    
    if stock.stock < 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Stock should be greater than zero.")

    product.stock -= stock.stock
    if product.stock == 0:
        product.is_sold = True

    return product 


