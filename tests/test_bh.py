from click.testing import CliRunner

from bashhub import bh as bh_module
from bashhub.bh import bh
from bashhub.model.min_command import MinCommand


def test_bh_accepts_number_within_range():
    def search(**kwargs):
        assert kwargs["limit"] == 10000
        return [MinCommand("echo ok", 1700000000000, "uuid-1")]

    bh_module.rest_client.search = search

    result = CliRunner().invoke(bh, ["--number", "10000"])

    assert result.exit_code == 0
    assert result.output == "echo ok\n"


def test_bh_rejects_number_below_range():
    result = CliRunner().invoke(bh, ["--number", "0"])

    assert result.exit_code == 2
    assert "0 is not in the range 1<=x<=10000" in result.output


def test_bh_rejects_number_above_range():
    result = CliRunner().invoke(bh, ["--number", "10001"])

    assert result.exit_code == 2
    assert "10001 is not in the range 1<=x<=10000" in result.output
