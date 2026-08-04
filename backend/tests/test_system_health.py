from app.routers.system import health_check


class _Response:
    status_code = 200


def test_health_check_reports_database_availability():
    response = _Response()

    result = health_check(response)

    assert response.status_code == 200
    assert result["status"] == "ok"
    assert result["checks"]["database"] == "ok"
    assert "storage" in result
