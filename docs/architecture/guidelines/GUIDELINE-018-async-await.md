# GUIDELINE-018: Async/Await Pattern

**Category**: Design Pattern

**Applies To**: FastAPI endpoints, background tasks, concurrent operations

**Author**: architect agent

**Date Created**: 2025-10-21

**Last Updated**: 2025-10-21

**Status**: Active

**Related ADRs**: None

**Related Specs**: None

---

## Overview

This guideline describes when and how to use async/await in Python, including common patterns, error handling in async code, and testing async functions.

---

## When to Use

Use async/await when:
- Making I/O operations (database, API calls, file operations)
- Building FastAPI endpoints that call I/O operations
- Need concurrent processing of multiple requests
- Background tasks or scheduled jobs
- Handling multiple operations simultaneously

---

## When NOT to Use

Do NOT use async for:
- CPU-intensive operations (use threading or multiprocessing)
- Simple synchronous operations (use regular functions)
- When dependency doesn't support async
- Complex logic that's hard to follow asynchronously

---

## The Pattern

### Explanation

Async/await allows efficient concurrent I/O handling:

1. **async def**: Declares async function
2. **await**: Pauses function until I/O completes, allows other tasks to run
3. **asyncio.run()**: Run async code from sync context
4. **asyncio.gather()**: Wait for multiple async operations
5. **Callbacks**: Handle completion of async operations

### Principles

1. **Async All the Way**: If caller is async, function should be async
2. **Await I/O Calls**: Always await I/O operations
3. **Don't Block**: Never use sleep() or blocking calls in async
4. **Error Handling**: Async exceptions need explicit handling
5. **Testing**: Test async code with pytest.mark.asyncio

---

## How to Implement

### Step 1: Async Function Basics

```python
import asyncio

# Basic async function
async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    # Simulate I/O operation
    await asyncio.sleep(1)  # Represents HTTP request
    return {"data": "from " + url}


# Call async function (from sync context)
if __name__ == "__main__":
    result = asyncio.run(fetch_data("https://example.com"))
    print(result)
```

### Step 2: Async I/O Operations

```python
import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

# Async HTTP request
async def fetch_from_api(url: str) -> dict:
    """Fetch data from API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# Async database query
async def get_user_from_db(session: AsyncSession, user_id: str) -> dict:
    """Get user from database."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    return user.to_dict() if user else None


# Async file operation
async def read_file_async(path: str) -> str:
    """Read file asynchronously."""
    import aiofiles
    async with aiofiles.open(path, mode='r') as f:
        return await f.read()
```

### Step 3: FastAPI Async Endpoints

```python
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user by ID (async endpoint)."""
    try:
        # Fetch from database
        user = await get_user_from_db(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except Exception as e:
        logger.exception(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post("/user")
async def create_user(request: UserRequest, db: AsyncSession = Depends(get_db)):
    """Create new user (async endpoint)."""
    try:
        # Fetch from external API to validate email
        is_valid = await fetch_from_api(f"https://api.example.com/validate/{request.email}")

        if not is_valid:
            raise HTTPException(status_code=422, detail="Invalid email")

        # Create in database
        user = await db.execute(
            insert(User).values(
                email=request.email,
                name=request.name
            )
        )
        await db.commit()

        return {"id": user.lastrowid}

    except Exception as e:
        await db.rollback()
        logger.exception(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### Step 4: Running Multiple Async Operations

```python
import asyncio
from typing import List

async def fetch_multiple_users(user_ids: List[str], db: AsyncSession) -> List[dict]:
    """Fetch multiple users concurrently."""
    # Create tasks for all users
    tasks = [get_user_from_db(db, user_id) for user_id in user_ids]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out errors
    users = [r for r in results if not isinstance(r, Exception)]
    return users


async def fetch_user_and_profile(user_id: str, db: AsyncSession) -> dict:
    """Fetch user and profile concurrently."""
    # Run both operations at the same time
    user, profile = await asyncio.gather(
        get_user_from_db(db, user_id),
        get_user_profile_from_db(db, user_id)
    )

    return {
        "user": user,
        "profile": profile
    }


@router.get("/users/{user_ids}")
async def get_multiple_users(user_ids: str, db: AsyncSession = Depends(get_db)):
    """Get multiple users concurrently."""
    ids = user_ids.split(",")

    # Fetch all users concurrently
    users = await fetch_multiple_users(ids, db)

    return {"users": users}
```

### Step 5: Error Handling in Async Code

```python
import asyncio
from typing import List

async def fetch_with_retry(url: str, retries: int = 3) -> dict:
    """Fetch data with retry logic."""
    for attempt in range(retries):
        try:
            logger.info(f"Attempt {attempt + 1} to fetch {url}")
            return await fetch_from_api(url)

        except asyncio.TimeoutError:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise


async def fetch_multiple_with_error_handling(
    urls: List[str]
) -> dict:
    """Fetch multiple URLs with error handling."""
    tasks = {url: fetch_with_retry(url) for url in urls}

    results = {}
    for url, task in tasks.items():
        try:
            results[url] = await task
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            results[url] = None

    return results


async def fetch_with_timeout(url: str, timeout: int = 30) -> dict:
    """Fetch data with timeout."""
    try:
        return await asyncio.wait_for(
            fetch_from_api(url),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching {url} after {timeout}s")
        raise
```

### Step 6: Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    """Async context manager for database session."""
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()


# Usage
async def process_users():
    """Process multiple users."""
    async with get_db_session() as session:
        users = await session.execute(select(User))
        for user in users.scalars():
            await process_user(user, session)
```

---

## Anti-Patterns to Avoid

❌ **Don't use sleep() in async code**
```python
# BAD: Blocks entire event loop
async def fetch_with_delay(url: str):
    time.sleep(2)  # ❌ Blocks all other tasks!
    return await fetch_from_api(url)
```
**Better**: Use asyncio.sleep
```python
async def fetch_with_delay(url: str):
    await asyncio.sleep(2)  # ✅ Allows other tasks to run
    return await fetch_from_api(url)
```

❌ **Don't forget to await**
```python
# BAD: Function not awaited
async def get_data():
    result = fetch_from_api(url)  # ❌ Coroutine not awaited!
    return result
```
**Better**: Always await async calls
```python
async def get_data():
    result = await fetch_from_api(url)  # ✅ Awaited
    return result
```

❌ **Don't mix sync and async without care**
```python
# BAD: Calling async from sync directly
def get_user(user_id: str):
    return await get_user_async(user_id)  # ❌ SyntaxError: await outside async
```
**Better**: Use asyncio.run()
```python
def get_user(user_id: str):
    return asyncio.run(get_user_async(user_id))  # ✅ Works from sync
```

❌ **Don't leave coroutines unfinished**
```python
# BAD: Coroutine created but not awaited
async def process_users():
    tasks = [get_user_async(id) for id in user_ids]
    # ❌ Tasks created but not awaited - warning!
```
**Better**: Await or gather tasks
```python
async def process_users():
    tasks = [get_user_async(id) for id in user_ids]
    results = await asyncio.gather(*tasks)  # ✅ All tasks executed
```

❌ **Don't ignore exceptions in concurrent operations**
```python
# BAD: Exceptions silently ignored
async def fetch_multiple(urls):
    results = await asyncio.gather(
        *[fetch_from_api(url) for url in urls]
    )  # ❌ One failure stops all!
```
**Better**: Handle exceptions properly
```python
async def fetch_multiple(urls):
    results = await asyncio.gather(
        *[fetch_from_api(url) for url in urls],
        return_exceptions=True  # ✅ Returns exceptions as values
    )
    # Handle exceptions individually
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Request failed: {result}")
```

---

## Testing Approach

### Test Async Functions

```python
import pytest

# Mark test as async
@pytest.mark.asyncio
async def test_fetch_data():
    """Test async function."""
    result = await fetch_data("https://example.com")
    assert result["data"] is not None


@pytest.mark.asyncio
async def test_fetch_multiple_users():
    """Test concurrent operations."""
    users = await fetch_multiple_users(
        ["user1", "user2", "user3"],
        db=AsyncMock()
    )
    assert len(users) == 3


@pytest.mark.asyncio
async def test_fetch_with_error():
    """Test error handling in async."""
    with pytest.raises(Exception):
        await fetch_with_retry("bad-url", retries=1)
```

### Mock Async Functions

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_mocked_async():
    """Test using mocked async function."""
    mock_db = AsyncMock()
    mock_db.get_user.return_value = {"id": "123", "name": "Test"}

    result = await get_user_from_db(mock_db, "123")

    assert result["id"] == "123"
    mock_db.get_user.assert_called_once_with("123")
```

---

## Related Guidelines

- [GUIDELINE-016: Testing Strategy](./GUIDELINE-016-testing-strategy.md)
- [GUIDELINE-014: FastAPI Endpoints](./GUIDELINE-014-fastapi-endpoints.md)

---

## Examples in Codebase

- `coffee_maker/api/routes/` (async endpoints)
- `coffee_maker/services/` (async service methods)
- `tests/` (async test examples)

---

## References

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Async Support](https://fastapi.tiangolo.com/async-sql-databases/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-21 | Initial async/await pattern guideline |
