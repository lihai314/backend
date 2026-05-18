from app.schemas.common import ApiResponse, PageData


def test_api_response_serializes_wrapped_data() -> None:
    response = ApiResponse[dict[str, str]](
        code="OK",
        message="ok",
        data={"id": "123"},
    )

    assert response.model_dump() == {
        "code": "OK",
        "message": "ok",
        "data": {"id": "123"},
    }


def test_page_data_serializes_pagination_fields() -> None:
    page = PageData[str](items=["one"], page=1, page_size=20, total=1)

    assert page.model_dump() == {
        "items": ["one"],
        "page": 1,
        "page_size": 20,
        "total": 1,
    }
