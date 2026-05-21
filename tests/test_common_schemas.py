"""通用数据模型测试，验证 ApiResponse 与 PageData 序列化行为。"""

from app.schemas.common import ApiResponse, PageData


def test_api_response_serializes_wrapped_data() -> None:
    """验证 ApiResponse 正确序列化包装数据。"""
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
    """验证 PageData 正确序列化分页字段。"""
    page = PageData[str](items=["one"], page=1, page_size=20, total=1)

    assert page.model_dump() == {
        "items": ["one"],
        "page": 1,
        "page_size": 20,
        "total": 1,
    }
