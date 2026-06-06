from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        }
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.anyio
async def test_create_user_success(client:AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "image_path" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_upload_profile_picture(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    test_image_path = Path(__file__).parent / "test_image.jpg"
    image_bytes = test_image_path.read_bytes()

    response = await client.patch(
        f"/api/users/{user['id']}/picture",
        files={"file": ("profile.jpg", BytesIO(image_bytes), "image/jpeg")},
        headers=auth_header(token),
    )

    try:
        assert response.status_code == 200
        data = response.json()
        assert data["image_file"] is not None
        assert data["image_file"].endswith(".jpg")
    finally:
        uploaded_file = Path("media/profile_pics") / data["image_file"]                        # clears up test images from disk
        if uploaded_file.exists():
            uploaded_file.unlink()


@pytest.mark.anyio
async def test_forgot_password_sends_email(client:AsyncClient):
    await create_test_user(client)

    with patch(                                               # we use unittest.mock patch as context manager to temporarily replace send_password_reset_email with AsyncMock instead
        "routers.users.send_password_reset_email",            # pytest's monkeypatch wasn't used coz unittest.mock gives mock objects that track how they were called which is needed
        new_callable=AsyncMock,                               # here, to verify that function was actually awaited and with what args. AsyncMock coz email func is async
    ) as mock_send:
        response = await client.post(
            "/api/users/forgot-password",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 202
        mock_send.assert_awaited_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == "test@example.com"
        assert call_kwargs["username"] == "testuser"
        assert "token" in call_kwargs

# Common gotcha with python mocking

# send_password_reset_email actually lives in email_utils.py, but we're patching routers.users. Here's why:

# When routers/users.py does "from email_utils (import)", that doesnt create magic live link to email_utils.py, it instead
# grabs a reference to that function and creates a new name for it inside routers.users namespace. Now at that point there would be two names pointing to the same function
# the original in email_utils.py and local reference at routers.users namespace. So when route handlers runs and calls this "routers.users.send_password_reset_email" it 
# looks up that name in local namespace which is routers.users. If we patched email.utils.send_password_reset_email we'd be replacing the original, but route handler would
# still use its local reference and call the real function and mock would never actually get touched

# Rule is: when you are mocking something, you patch where the name is looked up NOT where the function is defined. Patch where it's used not where it's defined.