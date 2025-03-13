from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import crud, schemas
from ..database import get_db
from ..core.auth import get_current_user
from ..models import User

router = APIRouter()

@router.post("/", response_model=schemas.Dork)
def create_dork(
    dork: schemas.DorkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dork query"""
    return crud.create_dork(db=db, dork=dork)

@router.get("/", response_model=List[schemas.Dork])
def read_dorks(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of dorks with optional filtering"""
    dorks = crud.get_dorks(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        user_id=current_user.id
    )
    return dorks

@router.get("/{dork_id}", response_model=schemas.Dork)
def read_dork(
    dork_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific dork by ID"""
    dork = crud.get_dork(db=db, dork_id=dork_id)
    if dork is None:
        raise HTTPException(status_code=404, detail="Dork not found")
    if dork.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return dork

@router.put("/{dork_id}", response_model=schemas.Dork)
def update_dork(
    dork_id: int,
    dork: schemas.DorkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a dork query"""
    db_dork = crud.get_dork(db=db, dork_id=dork_id)
    if db_dork is None:
        raise HTTPException(status_code=404, detail="Dork not found")
    if db_dork.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_dork(db=db, dork_id=dork_id, dork=dork)

@router.delete("/{dork_id}")
def delete_dork(
    dork_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dork query"""
    db_dork = crud.get_dork(db=db, dork_id=dork_id)
    if db_dork is None:
        raise HTTPException(status_code=404, detail="Dork not found")
    if db_dork.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.delete_dork(db=db, dork_id=dork_id)

@router.get("/categories/", response_model=List[str])
def get_dork_categories(
    db: Session = Depends(get_db)
):
    """Get list of available dork categories"""
    return crud.get_dork_categories(db=db)

@router.post("/search/", response_model=List[dict])
def search_with_dork(
    dork_query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a dork query and return results"""
    # Check subscription status
    if not current_user.subscription or current_user.subscription.status != "active":
        raise HTTPException(status_code=403, detail="Active subscription required")
    
    # Execute dork query and get results
    results = crud.execute_dork_query(dork_query)
    
    # Save to search history
    crud.create_search_history(
        db=db,
        user_id=current_user.id,
        search_type="dork",
        query=dork_query,
        results=results
    )
    
    return results 