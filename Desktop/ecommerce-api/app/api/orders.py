from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Order, OrderItem, CartItem, Product, User, UserRole, OrderStatus
from app.schemas.schemas import OrderCreate, OrderResponse, OrderItemResponse, PaymentIntentResponse
from app.core.security import verify_token
from app.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import stripe

router = APIRouter()
security = HTTPBearer()
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    try:
        user_id = verify_token(credentials.credentials)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.post("/", response_model=PaymentIntentResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.product.name}")
        total += item.product.price * item.quantity
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency="usd",
            metadata={"user_id": user.id}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    order = Order(
        user_id=user.id,
        total=total,
        shipping_address=order_data.shipping_address,
        payment_intent_id=payment_intent.id,
        status=OrderStatus.PENDING
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.add(order_item)
        item.product.stock -= item.quantity
    
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    
    return PaymentIntentResponse(client_secret=payment_intent.client_secret, order_id=order.id)

@router.post("/{order_id}/confirm")
async def confirm_payment(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(order.payment_intent_id)
        if payment_intent.status == "succeeded":
            order.status = OrderStatus.PAID
            db.commit()
            return {"message": "Payment confirmed", "status": "paid"}
        else:
            return {"message": "Payment not completed", "status": payment_intent.status}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return [_format_order(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return _format_order(order)

@router.patch("/{order_id}/status")
async def update_order_status(order_id: int, new_status: OrderStatus, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = new_status
    db.commit()
    return {"message": "Order status updated", "status": new_status}

def _format_order(order: Order) -> OrderResponse:
    items = []
    for item in order.items:
        items.append(OrderItemResponse(
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            price=item.price,
            subtotal=item.price * item.quantity
        ))
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        items=items,
        total=order.total,
        status=order.status,
        shipping_address=order.shipping_address,
        payment_intent_id=order.payment_intent_id,
        created_at=order.created_at
    ) 