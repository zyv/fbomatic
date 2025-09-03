import httpx
import pytest
import respx

from fbomatic.vereinsflieger import (
    HttpClient,
    VereinsfliegerApiSession,
    VereinsfliegerAuthError,
    VereinsfliegerError,
    VereinsfliegerUser,
)

pytestmark = pytest.mark.respx(base_url="https://www.vereinsflieger.de")


@pytest.fixture
def vf_session() -> VereinsfliegerApiSession:
    return VereinsfliegerApiSession("app_key", "username", "password")


@pytest.fixture
def respx_mock_sign_in(respx_mock: respx.mock) -> respx.mock:
    respx_mock.post(url="/interface/rest/auth/accesstoken", params="").respond(json={"accesstoken": "foo"})
    respx_mock.post(
        url="/interface/rest/auth/signin",
        params={
            "accesstoken": "foo",
            "username": "username",
            "password": "5f4dcc3b5aa765d61d8327deb882cf99",
            "cid": 0,
            "appkey": "app_key",
            "auth_secret": "",
        },
    ) % httpx.codes.OK

    return respx_mock


def test_sign_in_raise_for_status_access_token(respx_mock: respx.mock, vf_session: VereinsfliegerApiSession):
    respx_mock.post(url="/interface/rest/auth/accesstoken") % httpx.codes.FORBIDDEN

    with pytest.raises(VereinsfliegerAuthError):
        vf_session.sign_in()

    assert vf_session._access_token_hook is None
    with pytest.raises(VereinsfliegerError, match="not signed in"):
        vf_session.get_user()

    with pytest.raises(VereinsfliegerAuthError):
        vf_session.sign_in()

    assert vf_session._access_token_hook is None
    assert respx_mock.calls.call_count == 2


def test_sign_in_raise_for_status_sign_in(respx_mock: respx.mock, vf_session: VereinsfliegerApiSession):
    respx_mock.post(url="/interface/rest/auth/accesstoken").respond(json={"accesstoken": "foo"})
    respx_mock.post(url="/interface/rest/auth/signin") % httpx.codes.FORBIDDEN

    with pytest.raises(VereinsfliegerAuthError):
        vf_session.sign_in()

    assert vf_session._access_token_hook is None
    with pytest.raises(VereinsfliegerError, match="not signed in"):
        vf_session.get_user()

    assert respx_mock.calls.call_count == 2


def test_raise_if_not_signed_in(vf_session: VereinsfliegerApiSession):
    with pytest.raises(VereinsfliegerError, match="not signed in"):
        vf_session.sign_out()

    with pytest.raises(VereinsfliegerError, match="not signed in"):
        vf_session.get_user()


def test_sign_out(respx_mock_sign_in: respx.mock, vf_session: VereinsfliegerApiSession):
    respx_mock_sign_in.delete(url="/interface/rest/auth/signout/foo", params={"accesstoken": "foo"}) % httpx.codes.OK
    vf_session.sign_in()
    vf_session.sign_out()


def test_session_context_manager(respx_mock_sign_in: respx.mock):
    respx_mock_sign_in.delete(url="/interface/rest/auth/signout/foo", params={"accesstoken": "foo"}) % httpx.codes.OK

    with VereinsfliegerApiSession("app_key", "username", "password") as vs:
        assert isinstance(vs, VereinsfliegerApiSession)
        assert vs._access_token_hook.args == ("foo",)

    assert vs._access_token_hook is None
    assert HttpClient.raise_if_not_signed_in in vs._http_client.event_hooks["request"]
    assert respx_mock_sign_in.calls.call_count == 3


def test_get_user(respx_mock_sign_in: respx.mock):
    respx_mock_sign_in.get(url="/interface/rest/auth/getuser").respond(
        content="""{
  "uid": "12345",
  "firstname": "Foo",
  "lastname": "Bar",
  "memberid": "12345",
  "status": "aktiv",
  "cid": "1445",
  "roles": [
    "Mitglied",
    "News"
  ],
  "email": "foo@bar.quux",
  "httpstatuscode": 200
}"""
    )
    respx_mock_sign_in.delete(url="/interface/rest/auth/signout/foo", params={"accesstoken": "foo"}) % httpx.codes.OK

    with VereinsfliegerApiSession("app_key", "username", "password") as vs:
        assert vs.get_user() == VereinsfliegerUser(
            uid="12345",
            firstname="Foo",
            lastname="Bar",
            email="foo@bar.quux",
        )
