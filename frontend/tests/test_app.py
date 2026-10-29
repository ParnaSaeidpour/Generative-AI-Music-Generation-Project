import os

import pytest

import app as music_app

WEATHER = {
    "temperature": 4.5, "humidity": 80, "wind_speed": 6.0, "cloudiness": 75,
    "precipitation": 3, "precipitation_mm": 1.2,
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(music_app, "GENERATED_DIR", str(tmp_path))
    monkeypatch.setattr(music_app, "SOUNDFONT_PATH", str(tmp_path / "missing.sf2"))
    monkeypatch.setattr(music_app, "get_weather_data_by_city", lambda city: dict(WEATHER))
    music_app.app.config["TESTING"] = True
    with music_app.app.test_client() as client:
        yield client


def test_home_page_lists_the_cities(client):
    page = client.get("/").get_data(as_text=True)
    for city in music_app.CITIES:
        assert city in page


def test_generates_music_for_a_city(client, tmp_path):
    res = client.post("/generate", data={"city": "Malmö"})
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == "success"
    assert "Rain: Yes" in data["message"]
    assert data["midi_url"].startswith("/static/generated/malmo_")
    assert data["wav_url"] is None  # no soundfont in the test environment
    assert len(list(tmp_path.glob("malmo_*.mid"))) == 1


def test_missing_city_returns_400(client):
    res = client.post("/generate", data={})
    assert res.status_code == 400
    assert res.get_json()["message"] == "City is required"


@pytest.mark.parametrize("city", ["Paris", "../../etc/passwd", "Stockholm/../x"])
def test_unknown_city_is_rejected_and_writes_no_files(client, tmp_path, city):
    res = client.post("/generate", data={"city": city})
    assert res.status_code == 400
    assert os.listdir(tmp_path) == []


def test_weather_service_failure_returns_a_clear_message(client, monkeypatch):
    def fail(city):
        raise ConnectionError("internal details")
    monkeypatch.setattr(music_app, "get_weather_data_by_city", fail)

    res = client.post("/generate", data={"city": "Kiruna"})
    assert res.status_code == 502
    assert "internal details" not in res.get_data(as_text=True)


def test_weather_endpoint(client):
    assert client.get("/weather/Uppsala").get_json()["data"]["humidity"] == 80
    assert client.get("/weather/Narnia").status_code == 404


def test_play_does_not_leave_the_generated_folder(client):
    assert client.get("/play/..%2Fapp.py").status_code == 404
