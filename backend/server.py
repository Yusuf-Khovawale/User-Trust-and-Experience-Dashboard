from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import random
from faker import Faker
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize Faker and Sentiment Analyzer
fake = Faker()
analyzer = SentimentIntensityAnalyzer()

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    region: str
    join_date: datetime
    total_orders: int = 0
    satisfaction_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Seller(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    business_type: str
    region: str
    category: str
    join_date: datetime
    trust_index: float = 0.0
    fulfillment_rate: float = 0.0
    return_rate: float = 0.0
    complaint_ratio: float = 0.0
    total_orders: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    seller_id: str
    amount: float
    status: str
    category: str
    region: str
    order_date: datetime
    fulfillment_date: Optional[datetime] = None
    is_disputed: bool = False
    is_returned: bool = False
    fraud_flag: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    user_id: str
    seller_id: str
    rating: int
    review_text: str
    sentiment_score: float = 0.0
    sentiment_label: str = ""
    review_date: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Dispute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    user_id: str
    seller_id: str
    dispute_type: str
    amount: float
    status: str
    resolution: Optional[str] = None
    dispute_date: datetime
    resolution_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrustMetrics(BaseModel):
    trust_index: float
    dispute_rate: float
    refund_ratio: float
    policy_breach_rate: float
    repeat_purchase_uplift: float
    user_satisfaction_avg: float
    fraud_detection_rate: float
    seller_performance_avg: float

class DataGenerationRequest(BaseModel):
    num_users: int = 1000
    num_sellers: int = 200
    num_orders: int = 5000
    num_reviews: int = 3000
    num_disputes: int = 250
    seed: int = 42

# Data Generation Functions
def analyze_sentiment(text: str) -> tuple[float, str]:
    """Analyze sentiment using VADER"""
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        label = 'positive'
    elif compound <= -0.05:
        label = 'negative'
    else:
        label = 'neutral'
    
    return compound, label

def generate_review_text(rating: int) -> str:
    """Generate realistic review text based on rating"""
    positive_reviews = [
        "Excellent product! Fast delivery and great quality.",
        "Amazing seller, highly recommended!",
        "Perfect transaction, will buy again.",
        "Outstanding service and communication.",
        "Great value for money, very satisfied.",
        "Quick shipping, exactly as described.",
        "Professional seller, smooth transaction.",
        "High quality product, exceeded expectations."
    ]
    
    negative_reviews = [
        "Product not as described, very disappointed.",
        "Terrible quality, waste of money.",
        "Slow delivery, poor communication.",
        "Item arrived damaged, seller unresponsive.",
        "Complete scam, avoid this seller.",
        "Poor quality, not worth the price.",
        "Bad experience, would not recommend.",
        "Item never arrived, no refund given."
    ]
    
    neutral_reviews = [
        "Product is okay, nothing special.",
        "Average quality, decent price.",
        "It's fine, does what it's supposed to do.",
        "Not bad, but could be better.",
        "Reasonable quality for the price.",
        "Standard product, no complaints.",
        "It works, but not impressive.",
        "Fair transaction, average seller."
    ]
    
    if rating >= 4:
        return random.choice(positive_reviews)
    elif rating <= 2:
        return random.choice(negative_reviews)
    else:
        return random.choice(neutral_reviews)

async def calculate_trust_metrics() -> TrustMetrics:
    """Calculate comprehensive trust metrics"""
    # Get all collections data
    orders = await db.orders.find().to_list(None)
    reviews = await db.reviews.find().to_list(None)
    disputes = await db.disputes.find().to_list(None)
    sellers = await db.sellers.find().to_list(None)
    users = await db.users.find().to_list(None)
    
    if not orders:
        return TrustMetrics(
            trust_index=0,
            dispute_rate=0,
            refund_ratio=0,
            policy_breach_rate=0,
            repeat_purchase_uplift=0,
            user_satisfaction_avg=0,
            fraud_detection_rate=0,
            seller_performance_avg=0
        )
    
    total_orders = len(orders)
    disputed_orders = len([o for o in orders if o.get('is_disputed', False)])
    returned_orders = len([o for o in orders if o.get('is_returned', False)])
    fraud_orders = len([o for o in orders if o.get('fraud_flag', False)])
    
    # Calculate metrics
    dispute_rate = (disputed_orders / total_orders) * 100 if total_orders > 0 else 0
    refund_ratio = (returned_orders / total_orders) * 100 if total_orders > 0 else 0
    fraud_detection_rate = (fraud_orders / total_orders) * 100 if total_orders > 0 else 0
    
    # User satisfaction from reviews
    avg_rating = sum([r.get('rating', 0) for r in reviews]) / len(reviews) if reviews else 0
    user_satisfaction_avg = (avg_rating / 5) * 100
    
    # Seller performance average
    seller_trust_scores = [s.get('trust_index', 0) for s in sellers]
    seller_performance_avg = sum(seller_trust_scores) / len(seller_trust_scores) if seller_trust_scores else 0
    
    # Trust index calculation (weighted composite score)
    trust_index = (
        (user_satisfaction_avg * 0.3) +
        ((100 - dispute_rate) * 0.25) +
        ((100 - refund_ratio) * 0.2) +
        (seller_performance_avg * 0.15) +
        ((100 - fraud_detection_rate) * 0.1)
    )
    
    # Policy breach rate (simplified)
    policy_breach_rate = dispute_rate * 0.7  # Assume 70% of disputes are policy related
    
    # Repeat purchase uplift (mock calculation)
    user_orders = {}
    for order in orders:
        user_id = order.get('user_id')
        if user_id in user_orders:
            user_orders[user_id] += 1
        else:
            user_orders[user_id] = 1
    
    repeat_customers = len([uid for uid, count in user_orders.items() if count > 1])
    repeat_purchase_uplift = (repeat_customers / len(user_orders)) * 100 if user_orders else 0
    
    return TrustMetrics(
        trust_index=round(trust_index, 2),
        dispute_rate=round(dispute_rate, 2),
        refund_ratio=round(refund_ratio, 2),
        policy_breach_rate=round(policy_breach_rate, 2),
        repeat_purchase_uplift=round(repeat_purchase_uplift, 2),
        user_satisfaction_avg=round(user_satisfaction_avg, 2),
        fraud_detection_rate=round(fraud_detection_rate, 2),
        seller_performance_avg=round(seller_performance_avg, 2)
    )

# API Routes
@api_router.get("/")
async def root():
    return {"message": "User Trust & Experience Dashboard API"}

@api_router.post("/generate-data")
async def generate_sample_data(request: DataGenerationRequest):
    """Generate comprehensive sample data for the dashboard"""
    random.seed(request.seed)
    fake.seed_instance(request.seed)
    
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania']
    categories = ['Electronics', 'Fashion', 'Home & Garden', 'Books', 'Sports', 'Automotive', 'Health', 'Toys']
    business_types = ['Individual', 'Small Business', 'Enterprise', 'Startup']
    
    # Clear existing data
    await db.users.delete_many({})
    await db.sellers.delete_many({})
    await db.orders.delete_many({})
    await db.reviews.delete_many({})
    await db.disputes.delete_many({})
    
    # Generate Users
    users = []
    for _ in range(request.num_users):
        user = User(
            name=fake.name(),
            email=fake.email(),
            region=random.choice(regions),
            join_date=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.utc),
            total_orders=random.randint(0, 50),
            satisfaction_score=random.uniform(1.0, 5.0)
        )
        users.append(user.dict())
    
    await db.users.insert_many(users)
    
    # Generate Sellers
    sellers = []
    for _ in range(request.num_sellers):
        fulfillment_rate = random.uniform(0.7, 1.0)
        return_rate = random.uniform(0.0, 0.3)
        complaint_ratio = random.uniform(0.0, 0.2)
        
        # Calculate trust index based on performance metrics
        trust_index = (fulfillment_rate * 40) + ((1 - return_rate) * 30) + ((1 - complaint_ratio) * 30)
        
        seller = Seller(
            name=fake.company(),
            business_type=random.choice(business_types),
            region=random.choice(regions),
            category=random.choice(categories),
            join_date=fake.date_time_between(start_date='-3y', end_date='now', tzinfo=timezone.utc),
            trust_index=round(trust_index, 2),
            fulfillment_rate=round(fulfillment_rate, 3),
            return_rate=round(return_rate, 3),
            complaint_ratio=round(complaint_ratio, 3),
            total_orders=random.randint(0, 1000)
        )
        sellers.append(seller.dict())
    
    await db.sellers.insert_many(sellers)
    
    # Get inserted users and sellers for order generation
    user_docs = await db.users.find().to_list(None)
    seller_docs = await db.sellers.find().to_list(None)
    
    # Generate Orders
    orders = []
    statuses = ['completed', 'pending', 'cancelled', 'returned']
    for _ in range(request.num_orders):
        user = random.choice(user_docs)
        seller = random.choice(seller_docs)
        
        order_date = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
        fulfillment_date = order_date + timedelta(days=random.randint(1, 14)) if random.random() > 0.1 else None
        
        order = Order(
            user_id=user['id'],
            seller_id=seller['id'],
            amount=round(random.uniform(10.0, 1000.0), 2),
            status=random.choice(statuses),
            category=seller['category'],
            region=user['region'],
            order_date=order_date,
            fulfillment_date=fulfillment_date,
            is_disputed=random.random() < 0.05,  # 5% dispute rate
            is_returned=random.random() < 0.08,  # 8% return rate
            fraud_flag=random.random() < 0.02    # 2% fraud rate
        )
        orders.append(order.dict())
    
    await db.orders.insert_many(orders)
    
    # Generate Reviews
    order_docs = await db.orders.find().to_list(None)
    reviews = []
    for _ in range(min(request.num_reviews, len(order_docs))):
        order = random.choice(order_docs)
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
        review_text = generate_review_text(rating)
        sentiment_score, sentiment_label = analyze_sentiment(review_text)
        
        review = Review(
            order_id=order['id'],
            user_id=order['user_id'],
            seller_id=order['seller_id'],
            rating=rating,
            review_text=review_text,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            review_date=fake.date_time_between(start_date=order['order_date'], end_date='now', tzinfo=timezone.utc)
        )
        reviews.append(review.dict())
    
    await db.reviews.insert_many(reviews)
    
    # Generate Disputes
    disputed_orders = [o for o in order_docs if o.get('is_disputed', False)]
    disputes = []
    dispute_types = ['Product Quality', 'Delivery Issues', 'Billing Dispute', 'Seller Fraud', 'Refund Request']
    dispute_statuses = ['open', 'resolved', 'escalated', 'closed']
    
    for order in disputed_orders[:request.num_disputes]:
        resolution_date = fake.date_time_between(
            start_date=order['order_date'], 
            end_date='now', 
            tzinfo=timezone.utc
        ) if random.random() > 0.3 else None
        
        dispute = Dispute(
            order_id=order['id'],
            user_id=order['user_id'],
            seller_id=order['seller_id'],
            dispute_type=random.choice(dispute_types),
            amount=order['amount'],
            status=random.choice(dispute_statuses),
            resolution=fake.sentence() if resolution_date else None,
            dispute_date=fake.date_time_between(start_date=order['order_date'], end_date='now', tzinfo=timezone.utc),
            resolution_date=resolution_date
        )
        disputes.append(dispute.dict())
    
    await db.disputes.insert_many(disputes)
    
    return {
        "message": "Sample data generated successfully",
        "stats": {
            "users": len(users),
            "sellers": len(sellers),
            "orders": len(orders),
            "reviews": len(reviews),
            "disputes": len(disputes)
        }
    }

@api_router.get("/trust-metrics", response_model=TrustMetrics)
async def get_trust_metrics():
    """Get comprehensive trust metrics"""
    return await calculate_trust_metrics()

@api_router.get("/dashboard-stats")
async def get_dashboard_stats():
    """Get key dashboard statistics"""
    trust_metrics = await calculate_trust_metrics()
    
    # Get additional stats
    total_users = await db.users.count_documents({})
    total_sellers = await db.sellers.count_documents({})
    total_orders = await db.orders.count_documents({})
    total_reviews = await db.reviews.count_documents({})
    total_disputes = await db.disputes.count_documents({})
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_orders = await db.orders.count_documents({"order_date": {"$gte": thirty_days_ago}})
    recent_disputes = await db.disputes.count_documents({"dispute_date": {"$gte": thirty_days_ago}})
    
    return {
        "trust_metrics": trust_metrics.dict(),
        "totals": {
            "users": total_users,
            "sellers": total_sellers,
            "orders": total_orders,
            "reviews": total_reviews,
            "disputes": total_disputes
        },
        "recent_activity": {
            "orders_30d": recent_orders,
            "disputes_30d": recent_disputes
        }
    }

@api_router.get("/sellers-performance")
async def get_sellers_performance(limit: int = Query(50, le=200)):
    """Get seller performance data"""
    sellers = await db.sellers.find({}, {"_id": 0}).sort("trust_index", -1).limit(limit).to_list(None)
    return {"sellers": sellers}

@api_router.get("/category-analysis")
async def get_category_analysis():
    """Get performance analysis by category"""
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "avg_dispute_rate": {"$avg": "$complaint_ratio"},
                "avg_fulfillment_rate": {"$avg": "$fulfillment_rate"},
                "avg_trust_index": {"$avg": "$trust_index"},
                "total_sellers": {"$sum": 1}
            }
        },
        {"$sort": {"avg_trust_index": -1}}
    ]
    
    result = await db.sellers.aggregate(pipeline).to_list(None)
    return {"categories": result}

@api_router.get("/regional-analysis")
async def get_regional_analysis():
    """Get performance analysis by region"""
    pipeline = [
        {
            "$group": {
                "_id": "$region",
                "avg_satisfaction": {"$avg": "$satisfaction_score"},
                "total_users": {"$sum": 1},
                "avg_orders": {"$avg": "$total_orders"}
            }
        },
        {"$sort": {"avg_satisfaction": -1}}
    ]
    
    result = await db.users.aggregate(pipeline).to_list(None)
    return {"regions": result}

@api_router.get("/dispute-trends")
async def get_dispute_trends():
    """Get dispute trends over time"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dispute_date"},
                    "month": {"$month": "$dispute_date"},
                    "type": "$dispute_type"
                },
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    result = await db.disputes.aggregate(pipeline).to_list(None)
    return {"trends": result}

@api_router.get("/policy-simulation")
async def policy_simulation(
    min_fulfillment_rate: float = Query(0.9, ge=0.0, le=1.0),
    max_complaint_ratio: float = Query(0.1, ge=0.0, le=1.0),
    min_trust_index: float = Query(70, ge=0, le=100)
):
    """Simulate policy impact on seller ecosystem"""
    # Get all sellers
    all_sellers = await db.sellers.find().to_list(None)
    
    # Apply policy filters
    compliant_sellers = []
    non_compliant_sellers = []
    
    for seller in all_sellers:
        if (seller['fulfillment_rate'] >= min_fulfillment_rate and 
            seller['complaint_ratio'] <= max_complaint_ratio and 
            seller['trust_index'] >= min_trust_index):
            compliant_sellers.append(seller)
        else:
            non_compliant_sellers.append(seller)
    
    # Calculate impact
    total_sellers = len(all_sellers)
    compliant_count = len(compliant_sellers)
    non_compliant_count = len(non_compliant_sellers)
    
    # Estimate order impact (sellers who would be affected)
    affected_orders = sum([s['total_orders'] for s in non_compliant_sellers])
    total_orders = sum([s['total_orders'] for s in all_sellers])
    
    return {
        "policy_parameters": {
            "min_fulfillment_rate": min_fulfillment_rate,
            "max_complaint_ratio": max_complaint_ratio,
            "min_trust_index": min_trust_index
        },
        "impact_analysis": {
            "total_sellers": total_sellers,
            "compliant_sellers": compliant_count,
            "non_compliant_sellers": non_compliant_count,
            "compliance_rate": round((compliant_count / total_sellers) * 100, 2) if total_sellers > 0 else 0,
            "orders_at_risk": affected_orders,
            "order_impact_percentage": round((affected_orders / total_orders) * 100, 2) if total_orders > 0 else 0
        },
        "recommendations": {
            "action": "stricter_onboarding" if non_compliant_count > total_sellers * 0.2 else "maintain_current",
            "estimated_trust_improvement": min(15, (non_compliant_count / total_sellers) * 30) if total_sellers > 0 else 0
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()