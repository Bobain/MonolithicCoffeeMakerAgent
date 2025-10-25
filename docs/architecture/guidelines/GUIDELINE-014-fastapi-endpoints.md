# GUIDELINE-014: FastAPI Endpoint Pattern

**Category**: Design Pattern

**Applies To**: All FastAPI endpoints in coffee_maker/api/routes/

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes the standard structure for FastAPI endpoints, including decorators, async functions, request/response models, error handling, and documentation.

---

## When to Use

Use this pattern when:
- Creating new FastAPI endpoints
- Implementing REST API routes
- Adding new endpoints to existing routers
- Modifying existing endpoints

---

## When NOT to Use

Do NOT use this pattern for:
- WebSocket connections (use @router.websocket)
- Server-Sent Events (use @router.get with StreamingResponse)
- Background tasks (use BackgroundTasks)
- File uploads (though pattern still applies with File/UploadFile)

---

## The Pattern

### Explanation

Standard FastAPI endpoint structure includes:

1. **Router Setup**: Module-level router creation
2. **Endpoint Decorators**: HTTP method and path
3. **Async Function**: Always use async for scalability
4. **Type Hints**: Request and response types
5. **Docstring**: Clear endpoint documentation
6. **Request Validation**: Use Pydantic models
7. **Error Handling**: Raise HTTPException for errors
8. **Response Model**: Specify response structure

### Principles

1. **Always Async**: Use async/await for all endpoints
2. **Type Everything**: All parameters and return values have types
3. **Document Well**: Docstring explains what endpoint does
4. **Validate Input**: Use Pydantic models for request bodies
5. **Error Clarity**: Return meaningful error messages
6. **Logging**: Log important operations
7. **Consistent Structure**: All endpoints follow same pattern

---

## How to Implement

### Step 1: Create Router Module

Create a new router file in `coffee_maker/api/routes/`:

```python
# coffee_maker/api/routes/example.py

"""Example endpoints."""

import logging
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query, Path

logger = logging.getLogger(__name__)
router = APIRouter()
```

### Step 2: Define Request/Response Models

Use Pydantic models for validation:

```python
from pydantic import BaseModel, Field

class ExampleRequest(BaseModel):
    """Request model for example endpoint."""
    name: str = Field(..., description="Name of the example")
    count: int = Field(default=1, ge=1, le=100, description="Number of items")

    class Config:
        examples = {
            "name": "test",
            "count": 5
        }

class ExampleResponse(BaseModel):
    """Response model for example endpoint."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the example")
    status: str = Field(..., description="Current status")

    class Config:
        examples = {
            "id": "uuid-123",
            "name": "test",
            "status": "active"
        }
```

### Step 3: Implement GET Endpoint (Read)

```python
@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(
    example_id: str = Path(..., description="Example ID to retrieve")
) -> ExampleResponse:
    """
    Retrieve a specific example by ID.

    Args:
        example_id: The ID of the example to retrieve

    Returns:
        ExampleResponse with example details

    Raises:
        HTTPException: If example not found (404)
    """
    logger.info(f"Retrieving example: {example_id}")

    # Validate input
    if not example_id:
        raise HTTPException(status_code=400, detail="Example ID cannot be empty")

    # Fetch from database/service
    example = service.get_example(example_id)
    if not example:
        raise HTTPException(status_code=404, detail=f"Example {example_id} not found")

    logger.info(f"Retrieved example: {example_id}")
    return ExampleResponse(**example)
```

### Step 4: Implement POST Endpoint (Create)

```python
@router.post("/", response_model=ExampleResponse, status_code=201)
async def create_example(
    request: ExampleRequest
) -> ExampleResponse:
    """
    Create a new example.

    Args:
        request: Example creation request

    Returns:
        ExampleResponse with created example details

    Raises:
        HTTPException: If creation fails (422 or 500)
    """
    logger.info(f"Creating example: {request.name}")

    try:
        # Validate business logic
        if service.example_exists(request.name):
            raise HTTPException(
                status_code=409,
                detail=f"Example '{request.name}' already exists"
            )

        # Create and save
        example = service.create_example(request.name, request.count)
        logger.info(f"Created example: {example.id}")

        return ExampleResponse(**example.dict())

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to create example: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Step 5: Implement PUT Endpoint (Update)

```python
@router.put("/{example_id}", response_model=ExampleResponse)
async def update_example(
    example_id: str = Path(..., description="Example ID to update"),
    request: ExampleRequest = None
) -> ExampleResponse:
    """
    Update an existing example.

    Args:
        example_id: The ID of the example to update
        request: Update request with new values

    Returns:
        ExampleResponse with updated example details

    Raises:
        HTTPException: If not found (404) or update fails (422, 500)
    """
    logger.info(f"Updating example: {example_id}")

    try:
        # Check existence
        example = service.get_example(example_id)
        if not example:
            raise HTTPException(status_code=404, detail=f"Example {example_id} not found")

        # Update
        updated = service.update_example(example_id, **request.dict())
        logger.info(f"Updated example: {example_id}")

        return ExampleResponse(**updated.dict())

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to update example: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Step 6: Implement DELETE Endpoint (Delete)

```python
@router.delete("/{example_id}", status_code=204)
async def delete_example(
    example_id: str = Path(..., description="Example ID to delete")
) -> None:
    """
    Delete an example.

    Args:
        example_id: The ID of the example to delete

    Raises:
        HTTPException: If not found (404) or delete fails (500)
    """
    logger.info(f"Deleting example: {example_id}")

    try:
        # Check existence
        example = service.get_example(example_id)
        if not example:
            raise HTTPException(status_code=404, detail=f"Example {example_id} not found")

        # Delete
        service.delete_example(example_id)
        logger.info(f"Deleted example: {example_id}")

    except Exception as e:
        logger.exception(f"Failed to delete example: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Step 7: Register Router in Main App

```python
# coffee_maker/api/main.py

from fastapi import FastAPI
from coffee_maker.api.routes import example

app = FastAPI()

# Register routers with API prefix
app.include_router(
    example.router,
    prefix="/api/examples",
    tags=["Examples"]
)
```

---

## Anti-Patterns to Avoid

❌ **Don't use sync endpoints**
```python
# BAD
@router.get("/")
def get_status():  # ❌ Missing async
    return service.get_status()
```
**Better**: Always use async
```python
@router.get("/")
async def get_status():
    return service.get_status()
```

❌ **Don't skip error handling**
```python
# BAD
@router.get("/{id}")
async def get_item(id: str):
    return service.get(id)  # ❌ Will crash if service.get fails
```
**Better**: Use try/except and HTTPException
```python
@router.get("/{id}")
async def get_item(id: str):
    try:
        return service.get(id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

❌ **Don't skip type hints**
```python
# BAD
@router.post("/")
async def create(request):  # ❌ No type hints
    return service.create(request)
```
**Better**: Use Pydantic models
```python
@router.post("/", response_model=ResponseModel)
async def create(request: RequestModel) -> ResponseModel:
    return service.create(request)
```

❌ **Don't return raw exceptions**
```python
# BAD
@router.get("/{id}")
async def get_item(id: str):
    try:
        return service.get(id)
    except Exception:
        raise  # ❌ Returns 500 with internal error details
```
**Better**: Map exceptions to appropriate HTTP status codes
```python
@router.get("/{id}")
async def get_item(id: str):
    try:
        item = service.get(id)
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return item
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

❌ **Don't log too much or too little**
```python
# BAD - No logging
@router.post("/")
async def create(request: RequestModel):
    return service.create(request)

# BAD - Too much logging
@router.post("/")
async def create(request: RequestModel):
    logger.debug(f"Received: {request}")
    logger.debug(f"Processing: {request.name}")
    logger.debug(f"About to create: {request.name}")
    logger.debug(f"Created: ...")
    logger.debug(f"Returning: ...")
```
**Better**: Log key operations
```python
@router.post("/")
async def create(request: RequestModel):
    logger.info(f"Creating: {request.name}")
    try:
        result = service.create(request)
        logger.info(f"Created: {result.id}")
        return result
    except Exception as e:
        logger.exception(f"Failed to create: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

---

## Testing Approach

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient
from coffee_maker.api.main import app

client = TestClient(app)

def test_get_example_success():
    """Test successful retrieval."""
    response = client.get("/api/examples/123")
    assert response.status_code == 200
    assert response.json()["id"] == "123"

def test_get_example_not_found():
    """Test retrieval of non-existent example."""
    response = client.get("/api/examples/nonexistent")
    assert response.status_code == 404

def test_create_example_success():
    """Test successful creation."""
    response = client.post("/api/examples/", json={
        "name": "test",
        "count": 5
    })
    assert response.status_code == 201
    assert response.json()["name"] == "test"

def test_create_example_invalid_input():
    """Test creation with invalid input."""
    response = client.post("/api/examples/", json={
        "name": "",  # Invalid
        "count": 200  # Out of range
    })
    assert response.status_code == 422
```

### Integration Tests

```python
def test_create_and_get_example():
    """Test create followed by get."""
    # Create
    create_response = client.post("/api/examples/", json={
        "name": "test",
        "count": 5
    })
    example_id = create_response.json()["id"]

    # Get
    get_response = client.get(f"/api/examples/{example_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == example_id
```

---

## Related Guidelines

- [GUIDELINE-016: Testing Strategy](./GUIDELINE-016-testing-strategy.md)
- [GUIDELINE-001: Error Handling](./GUIDELINE-001-error-handling.md)

---

## Examples in Codebase

- `coffee_maker/api/routes/status.py` (GET endpoints)
- `coffee_maker/api/routes/daemon.py` (Control endpoints)
- `coffee_maker/api/routes/files.py` (File endpoints)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial FastAPI endpoint pattern guideline |
