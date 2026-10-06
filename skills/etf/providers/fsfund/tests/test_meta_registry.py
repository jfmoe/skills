import unittest

from meta_registry import build_registry, format_schema


class RequiredParametersTest(unittest.TestCase):
    def test_required_flags_and_alternative_groups_remain_distinct(self):
        rows = [
            {"PATH": "EXAMPLE", "PARAM": "STDATE", "NOTNULLFLAG": "1"},
            {"PATH": "EXAMPLE", "PARAM": "currentPage", "NOTNULLFLAG": "0"},
            {"PATH": "EXAMPLE", "PARAM": "FUND_CODE", "NOTNULLFLAG": "1", "REQUIRED_GROUP_ID": "identity"},
            {"PATH": "EXAMPLE", "PARAM": "FUND_MGR", "NOTNULLFLAG": "1", "REQUIRED_GROUP_ID": "identity"},
            {"PATH": "EXAMPLE", "PARAM": "UNDOCUMENTED"},
        ]
        registry = build_registry({"get_udsp_2_api_input_param": {"result": rows}})
        output = format_schema(registry, "EXAMPLE")
        rendered = {}
        for line in output.splitlines():
            if line.startswith("| "):
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                if len(cells) == 6:
                    rendered[cells[0]] = cells[4]
        self.assertEqual(
            {name: rendered[name] for name in ("STDATE", "currentPage", "FUND_CODE", "FUND_MGR", "UNDOCUMENTED")},
            {"STDATE": "必填", "currentPage": "可选", "FUND_CODE": "组内择一", "FUND_MGR": "组内择一", "UNDOCUMENTED": "未声明"},
        )
        self.assertIn("以下入参至少填写一项 → FUND_CODE、FUND_MGR", output)


if __name__ == "__main__":
    unittest.main()
