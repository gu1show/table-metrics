import pytest
from table_metrics import teds


def test_empty_strings():
    assert teds("", "") == 0


def test_same_table():
    html_table = """
    <table>
    <tr><td>A</td><td>B</td></tr>
    </table>
    """
    assert teds(html_table, html_table) == 1


def test_structure_only():
    html1 = """
    <table>
    <tr><td>A</td><td>B</td></tr>
    </table>
    """
    html2 = """
    <table>
    <tr><td>C</td><td>D</td></tr>
    </table>
    """
    assert teds(html1, html2, structure_only=True) == 1


def test_text_difference():
    html1 = "<table><tr><td>A</td></tr></table>"
    html2 = "<table><tr><td>B</td></tr></table>"
    score = teds(html1, html2)
    assert score == 0.5


def test_ignored_nodes():
    html1 = "<table><tr><td>A</td><td><i>B</i></td></tr></table>"
    html2 = "<table><tr><td>A</td><td><b>B</b></td></tr></table>"
    score_with_ignore = teds(html1, html2, ignored_nodes=["i", "b"])
    assert score_with_ignore == 1


def test_empty_table():
    html1 = "<table></table>"
    html2 = "<table></table>"
    assert teds(html1, html2) == 1


def test_multiple_tables():
    html1 = "<table><tr><td>A</td></tr></table><table><tr><td>B</td></tr></table>"
    html2 = "<table><tr><td>A</td></tr></table><table><tr><td>C</td></tr></table>"
    assert teds(html1, html2) == 1
