import pytest
from table_metrics import (
    grits_top_score,
    grits_loc_score,
    grits_con_score,
    html_to_cells,
)


class TestHtmlToCells:
    def test_usual_table(self):
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
        </table>
        """
        cells = html_to_cells(html)

        assert len(cells) == 4
        cell_text = ["A", "B", "C", "D"]
        row_nums = [[0], [0], [1], [1]]
        columns_nums = [[0], [1], [0], [1]]
        for i in range(len(cells)):
            assert cells[i]["cell_text"] == cell_text[i]
            assert cells[i]["row_nums"] == row_nums[i]
            assert cells[i]["column_nums"] == columns_nums[i]
            assert cells[i]["is_column_header"] is False

    def test_empty_input(self):
        html = "<div>No table here</div>"
        cells = html_to_cells(html)
        assert cells == []

    def test_colspan(self):
        html = """
        <table>
            <tr><td colspan='2'>Spanning</td><td>Normal</td></tr>
        </table>
        """
        cells = html_to_cells(html)

        assert len(cells) == 2
        assert cells[0]["column_nums"] == [0, 1]
        assert cells[1]["column_nums"] == [2]

    def test_rowspan(self):
        html = """
        <table>
            <tr><td rowspan='2'>Spanning</td><td>A</td></tr>
            <tr><td>B</td></tr>
        </table>
        """
        cells = html_to_cells(html)

        assert len(cells) == 3
        assert cells[0]["row_nums"] == [0, 1]
        assert cells[1]["column_nums"] == [1]
        assert cells[2]["column_nums"] == [1]

    def test_thead_detection(self):
        html = """
        <table>
            <thead>
                <tr><td>Header</td></tr>
            </thead>
            <tbody>
                <tr><td>Data</td></tr>
            </tbody>
        </table>
        """
        cells = html_to_cells(html)

        assert len(cells) == 2
        assert cells[0]["is_column_header"] is True
        assert cells[1]["is_column_header"] is False

    def test_th_tag_detection(self):
        html = """
        <table>
            <tr><th>Header</th><td>Data</td></tr>
        </table>
        """
        cells = html_to_cells(html)

        assert len(cells) == 2
        assert cells[0]["is_column_header"] is True
        assert cells[1]["is_column_header"] is False

    def test_ignored_nodes(self):
        html = """
        <table>
            <tr><td>Text<sup>1</sup></td></tr>
            <tr><td>More<sub>2</sub></td></tr>
        </table>
        """
        cells = html_to_cells(html, ignored_nodes=["sup", "sub"])

        assert "Text1" in cells[0]["cell_text"]
        assert "More2" in cells[1]["cell_text"]


class TestGritsTopScore:
    def test_identical_tables(self):
        """Identical tables should have score 1.0."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
            <tr><td>C</td><td>D</td></tr>
        </table>
        """
        score = grits_top_score(html, html)
        assert score == 1.0

    def test_different_topology(self):
        true_html = """
        <table>
            <tr><td colspan='2'>Merged</td></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        pred_html = """
        <table>
            <tr><td>X</td><td>Y</td></tr>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        score = grits_top_score(true_html, pred_html)
        assert 0.0 < score < 1.0

    def test_empty_table_true(self):
        """Empty ground truth should return 0.0."""
        true_html = "<div>No table</div>"
        pred_html = "<table><tr><td>A</td></tr></table>"
        score = grits_top_score(true_html, pred_html)
        assert score == 0.0

    def test_empty_table_pred(self):
        """Empty prediction should return 0.0."""
        true_html = "<table><tr><td>A</td></tr></table>"
        pred_html = "<div>No table</div>"
        score = grits_top_score(true_html, pred_html)
        assert score == 0.0

    def test_return_components(self):
        """Should return fscore, precision, recall when requested."""
        html = """
        <table>
            <tr><td>A</td><td>B</td></tr>
        </table>
        """
        fscore, precision, recall = grits_top_score(html, html, return_components=True)

        assert fscore == 1.0
        assert precision == 1.0
        assert recall == 1.0


class TestGritsConScore:
    def test_identical_content(self):
        html = """
        <table>
            <tr><td>Alice</td><td>30</td></tr>
            <tr><td>Bob</td><td>25</td></tr>
        </table>
        """
        score = grits_con_score(html, html)
        assert score == 1.0

    def test_different_content(self):
        true_html = "<table><tr><td>A</td><td>B</td></tr></table>"
        pred_html = "<table><tr><td>B</td><td>C</td></tr></table>"

        score = grits_con_score(true_html, pred_html)
        assert 0.0 < score < 1.0

    def test_partial_match(self):
        true_html = "<table><tr><td>A</td><td>B</td></tr></table>"
        pred_html = "<table><tr><td>A</td><td>C</td></tr></table>"

        score = grits_con_score(true_html, pred_html)
        assert 0.5 == score

    def test_empty_table_content(self):
        true_html = "<div>No table</div>"
        pred_html = "<table><tr><td>A</td></tr></table>"

        score = grits_con_score(true_html, pred_html)
        assert score == 0.0


class TestGritsLocScore:
    def test_identical_bboxes(self):
        bboxes = [
            [0, 0, 100, 20],
            [0, 20, 100, 40],
            [0, 0, 50, 40],
            [50, 0, 100, 40],
        ]
        labels = [2, 2, 1, 1]  # row, row, column, column

        score = grits_loc_score(bboxes, labels, bboxes, labels)
        assert score == 1.0

    def test_different_structure(self):
        true_bboxes = [
            [0, 0, 100, 50],
            [0, 0, 100, 50],
        ]
        true_labels = [2, 1]

        pred_bboxes = [
            [0, 0, 100, 25],
            [0, 25, 100, 50],
            [0, 0, 50, 50],
            [50, 0, 100, 50],
        ]
        pred_labels = [2, 2, 1, 1]

        score = grits_loc_score(true_bboxes, true_labels, pred_bboxes, pred_labels)
        assert 0.0 < score < 1.0

    def test_with_spanning_cells(self):
        true_bboxes = [
            [0, 0, 100, 25],
            [0, 25, 100, 50],
            [0, 0, 50, 50],
            [50, 0, 100, 50],
            [10, 10, 40, 40],
        ]
        true_labels = [2, 2, 1, 1, 4]

        score = grits_loc_score(true_bboxes, true_labels, true_bboxes, true_labels)
        assert score == 1.0

    def test_empty_predictions(self):
        true_bboxes = [[0, 0, 100, 20]]
        true_labels = [2]
        pred_bboxes = []
        pred_labels = []

        score = grits_loc_score(true_bboxes, true_labels, pred_bboxes, pred_labels)
        assert score == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
