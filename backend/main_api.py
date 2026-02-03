import uvicorn
import os, json
import time as time_module
import logging
from fastapi import Depends, FastAPI, HTTPException, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic_classes import *
from sql_alchemy import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

############################################
#
#   Initialize the database
#
############################################

def init_db():
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/Class_Diagram.db")
    # Ensure local SQLite directory exists (safe no-op for other DBs)
    os.makedirs("data", exist_ok=True)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return SessionLocal

app = FastAPI(
    title="Class_Diagram API",
    description="Auto-generated REST API with full CRUD operations, relationship management, and advanced features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "System", "description": "System health and statistics"},
        {"name": "Record", "description": "Operations for Record entities"},
        {"name": "Record Relationships", "description": "Manage Record relationships"},
        {"name": "Record Methods", "description": "Execute Record methods"},
        {"name": "User", "description": "Operations for User entities"},
        {"name": "User Relationships", "description": "Manage User relationships"},
    ]
)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################################
#
#   Middleware
#
############################################

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time_module.time()
    response = await call_next(request)
    process_time = time_module.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

############################################
#
#   Exception Handlers
#
############################################

# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "Invalid input data provided"
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    
    # Extract more detailed error information
    error_detail = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": "Data conflict occurred",
            "detail": error_detail
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error", 
            "message": "Database operation failed",
            "detail": "An internal database error occurred"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": exc.detail,
            "detail": f"HTTP {exc.status_code} error occurred"
        }
    )

# Initialize database session
SessionLocal = init_db()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        logger.error("Database session rollback due to exception")
        raise
    finally:
        db.close()

############################################
#
#   Global API endpoints
#
############################################

@app.get("/", tags=["System"])
def root():
    """Root endpoint - API information"""
    return {
        "name": "Class_Diagram API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


@app.get("/statistics", tags=["System"])
def get_statistics(database: Session = Depends(get_db)):
    """Get database statistics for all entities"""
    stats = {}
    stats["record_count"] = database.query(Record).count()
    stats["user_count"] = database.query(User).count()
    stats["total_entities"] = sum(stats.values())
    return stats

############################################
#
#   Record functions
#
############################################
 
 

@app.get("/record/", response_model=None, tags=["Record"])
def get_all_record(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload
    
    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(Record)
        query = query.options(joinedload(Record.user))
        record_list = query.all()
        
        # Serialize with relationships included
        result = []
        for record_item in record_list:
            item_dict = record_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)
            
            # Add many-to-one relationships (foreign keys for lookup columns)
            if record_item.user:
                related_obj = record_item.user
                related_dict = related_obj.__dict__.copy()
                related_dict.pop('_sa_instance_state', None)
                item_dict['user'] = related_dict
            else:
                item_dict['user'] = None
            
            
            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(Record).all()


@app.get("/record/count/", response_model=None, tags=["Record"])
def get_count_record(database: Session = Depends(get_db)) -> dict:
    """Get the total count of Record entities"""
    count = database.query(Record).count()
    return {"count": count}


@app.get("/record/paginated/", response_model=None, tags=["Record"])
def get_paginated_record(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of Record entities"""
    total = database.query(Record).count()
    record_list = database.query(Record).offset(skip).limit(limit).all()
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": record_list
    }


@app.get("/record/search/", response_model=None, tags=["Record"])
def search_record(
    database: Session = Depends(get_db)
) -> list:
    """Search Record entities by attributes"""
    query = database.query(Record)
    
    
    results = query.all()
    return results


@app.get("/record/{record_id}/", response_model=None, tags=["Record"])
async def get_record(record_id: int, database: Session = Depends(get_db)) -> Record:
    db_record = database.query(Record).filter(Record.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    response_data = {
        "record": db_record,
}
    return response_data



@app.post("/record/", response_model=None, tags=["Record"])
async def create_record(record_data: RecordCreate, database: Session = Depends(get_db)) -> Record:

    if record_data.user is not None:
        db_user = database.query(User).filter(User.id == record_data.user).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
    else:
        raise HTTPException(status_code=400, detail="User ID is required")

    db_record = Record(
        numberOfPushups=record_data.numberOfPushups,        date=record_data.date,        user_id=record_data.user        )

    database.add(db_record)
    database.commit()
    database.refresh(db_record)



    
    return db_record


@app.post("/record/bulk/", response_model=None, tags=["Record"])
async def bulk_create_record(items: list[RecordCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple Record entities at once"""
    created_items = []
    errors = []
    
    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            if not item_data.user:
                raise ValueError("User ID is required")
            
            db_record = Record(
                numberOfPushups=item_data.numberOfPushups,                date=item_data.date,                user_id=item_data.user            )
            database.add(db_record)
            database.flush()  # Get ID without committing
            created_items.append(db_record.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})
    
    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})
    
    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} Record entities"
    }


@app.delete("/record/bulk/", response_model=None, tags=["Record"])
async def bulk_delete_record(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple Record entities at once"""
    deleted_count = 0
    not_found = []
    
    for item_id in ids:
        db_record = database.query(Record).filter(Record.id == item_id).first()
        if db_record:
            database.delete(db_record)
            deleted_count += 1
        else:
            not_found.append(item_id)
    
    database.commit()
    
    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} Record entities"
    }

@app.put("/record/{record_id}/", response_model=None, tags=["Record"])
async def update_record(record_id: int, record_data: RecordCreate, database: Session = Depends(get_db)) -> Record:
    db_record = database.query(Record).filter(Record.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    setattr(db_record, 'numberOfPushups', record_data.numberOfPushups)
    setattr(db_record, 'date', record_data.date)
    if record_data.user is not None:
        db_user = database.query(User).filter(User.id == record_data.user).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="User not found")
        setattr(db_record, 'user_id', record_data.user)
    database.commit()
    database.refresh(db_record)
    
    return db_record


@app.delete("/record/{record_id}/", response_model=None, tags=["Record"])
async def delete_record(record_id: int, database: Session = Depends(get_db)):
    db_record = database.query(Record).filter(Record.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    database.delete(db_record)
    database.commit()
    return db_record



############################################
#   Record Method Endpoints
############################################


@app.post("/record/{record_id}/methods/update_record/", response_model=None, tags=["Record Methods"])
async def execute_record_update_record(
    record_id: int,
    params: dict = Body(default=None, embed=True),
    database: Session = Depends(get_db)
):
    """
    Execute the update_record method on a Record instance.
    
    Parameters:
    - record: Any    """
    # Retrieve the entity from the database
    _record_object = database.query(Record).filter(Record.id == record_id).first()
    if _record_object is None:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Prepare method parameters
    record = params.get('record')

    # Execute the method
    try:        
        # Capture stdout to include print outputs in the response
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        """Add your docstring here."""
        # Add your implementation here
    	_record_object.numberOfPushups =_record_object.numberOfPushups+ record
        pass

        # Commit DB
        database.commit()
        database.refresh(_record_object)

        # Restore stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # Determine result (last statement or None)
        result = None
        
        return {
            "record_id": record_id,
            "method": "update_record",
            "status": "executed",
            "result": str(result) if result is not None else None,
            "output": output if output else None
        }
    except Exception as e:
        sys.stdout = sys.__stdout__
        raise HTTPException(status_code=500, detail=f"Method execution failed: {str(e)}")



############################################
#
#   User functions
#
############################################
 
 

@app.get("/user/", response_model=None, tags=["User"])
def get_all_user(detailed: bool = False, database: Session = Depends(get_db)) -> list:
    from sqlalchemy.orm import joinedload
    
    # Use detailed=true to get entities with eagerly loaded relationships (for tables with lookup columns)
    if detailed:
        # Eagerly load all relationships to avoid N+1 queries
        query = database.query(User)
        user_list = query.all()
        
        # Serialize with relationships included
        result = []
        for user_item in user_list:
            item_dict = user_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)
            
            # Add many-to-one relationships (foreign keys for lookup columns)
            
            # Add many-to-many and one-to-many relationship objects (full details)
            record_list = database.query(Record).filter(Record.user_id == user_item.id).all()
            item_dict['hasRecords'] = []
            for record_obj in record_list:
                record_dict = record_obj.__dict__.copy()
                record_dict.pop('_sa_instance_state', None)
                item_dict['hasRecords'].append(record_dict)
            
            result.append(item_dict)
        return result
    else:
        # Default: return flat entities (faster for charts/widgets without lookup columns)
        return database.query(User).all()


@app.get("/user/count/", response_model=None, tags=["User"])
def get_count_user(database: Session = Depends(get_db)) -> dict:
    """Get the total count of User entities"""
    count = database.query(User).count()
    return {"count": count}


@app.get("/user/paginated/", response_model=None, tags=["User"])
def get_paginated_user(skip: int = 0, limit: int = 100, detailed: bool = False, database: Session = Depends(get_db)) -> dict:
    """Get paginated list of User entities"""
    total = database.query(User).count()
    user_list = database.query(User).offset(skip).limit(limit).all()
    # By default, return flat entities (for charts/widgets)
    # Use detailed=true to get entities with relationships
    if not detailed:
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": user_list
        }
    
    result = []
    for user_item in user_list:
        hasRecords_ids = database.query(Record.id).filter(Record.user_id == user_item.id).all()
        item_data = {
            "user": user_item,
            "hasRecords_ids": [x[0] for x in hasRecords_ids]        }
        result.append(item_data)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": result
    }


@app.get("/user/search/", response_model=None, tags=["User"])
def search_user(
    database: Session = Depends(get_db)
) -> list:
    """Search User entities by attributes"""
    query = database.query(User)
    
    
    results = query.all()
    return results


@app.get("/user/{user_id}/", response_model=None, tags=["User"])
async def get_user(user_id: int, database: Session = Depends(get_db)) -> User:
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    hasRecords_ids = database.query(Record.id).filter(Record.user_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "hasRecords_ids": [x[0] for x in hasRecords_ids]}
    return response_data



@app.post("/user/", response_model=None, tags=["User"])
async def create_user(user_data: UserCreate, database: Session = Depends(get_db)) -> User:


    db_user = User(
        email=user_data.email,        name=user_data.name        )

    database.add(db_user)
    database.commit()
    database.refresh(db_user)

    if user_data.hasRecords:
        # Validate that all Record IDs exist
        for record_id in user_data.hasRecords:
            db_record = database.query(Record).filter(Record.id == record_id).first()
            if not db_record:
                raise HTTPException(status_code=400, detail=f"Record with id {record_id} not found")
        
        # Update the related entities with the new foreign key
        database.query(Record).filter(Record.id.in_(user_data.hasRecords)).update(
            {Record.user_id: db_user.id}, synchronize_session=False
        )
        database.commit()


    
    hasRecords_ids = database.query(Record.id).filter(Record.user_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "hasRecords_ids": [x[0] for x in hasRecords_ids]    }
    return response_data


@app.post("/user/bulk/", response_model=None, tags=["User"])
async def bulk_create_user(items: list[UserCreate], database: Session = Depends(get_db)) -> dict:
    """Create multiple User entities at once"""
    created_items = []
    errors = []
    
    for idx, item_data in enumerate(items):
        try:
            # Basic validation for each item
            
            db_user = User(
                email=item_data.email,                name=item_data.name            )
            database.add(db_user)
            database.flush()  # Get ID without committing
            created_items.append(db_user.id)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})
    
    if errors:
        database.rollback()
        raise HTTPException(status_code=400, detail={"message": "Bulk creation failed", "errors": errors})
    
    database.commit()
    return {
        "created_count": len(created_items),
        "created_ids": created_items,
        "message": f"Successfully created {len(created_items)} User entities"
    }


@app.delete("/user/bulk/", response_model=None, tags=["User"])
async def bulk_delete_user(ids: list[int], database: Session = Depends(get_db)) -> dict:
    """Delete multiple User entities at once"""
    deleted_count = 0
    not_found = []
    
    for item_id in ids:
        db_user = database.query(User).filter(User.id == item_id).first()
        if db_user:
            database.delete(db_user)
            deleted_count += 1
        else:
            not_found.append(item_id)
    
    database.commit()
    
    return {
        "deleted_count": deleted_count,
        "not_found": not_found,
        "message": f"Successfully deleted {deleted_count} User entities"
    }

@app.put("/user/{user_id}/", response_model=None, tags=["User"])
async def update_user(user_id: int, user_data: UserCreate, database: Session = Depends(get_db)) -> User:
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    setattr(db_user, 'email', user_data.email)
    setattr(db_user, 'name', user_data.name)
    if user_data.hasRecords is not None:
        # Clear all existing relationships (set foreign key to NULL)
        database.query(Record).filter(Record.user_id == db_user.id).update(
            {Record.user_id: None}, synchronize_session=False
        )
        
        # Set new relationships if list is not empty
        if user_data.hasRecords:
            # Validate that all IDs exist
            for record_id in user_data.hasRecords:
                db_record = database.query(Record).filter(Record.id == record_id).first()
                if not db_record:
                    raise HTTPException(status_code=400, detail=f"Record with id {record_id} not found")
            
            # Update the related entities with the new foreign key
            database.query(Record).filter(Record.id.in_(user_data.hasRecords)).update(
                {Record.user_id: db_user.id}, synchronize_session=False
            )
    database.commit()
    database.refresh(db_user)
    
    hasRecords_ids = database.query(Record.id).filter(Record.user_id == db_user.id).all()
    response_data = {
        "user": db_user,
        "hasRecords_ids": [x[0] for x in hasRecords_ids]    }
    return response_data


@app.delete("/user/{user_id}/", response_model=None, tags=["User"])
async def delete_user(user_id: int, database: Session = Depends(get_db)):
    db_user = database.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    database.delete(db_user)
    database.commit()
    return db_user







############################################
# Maintaining the server
############################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



