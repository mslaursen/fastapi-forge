import pytest

from fastapi_forge.utils import string_utils


@pytest.mark.parametrize(
    "value, expected",
    [
        ("HTTPMethod", "http_method"),
        ("simpleTest", "simple_test"),
        ("already_snake", "already_snake"),
        ("", ""),
        ("A", "a"),
        ("a", "a"),
        ("ALL_CAPS", "all_caps"),
        ("CamelCase", "camel_case"),
        ("camelCase", "camel_case"),
        ("PascalCase", "pascal_case"),
        ("MixedCaseString", "mixed_case_string"),
        ("XML2JSON", "xml2_json"),
        ("JSON2XML", "json2_xml"),
        ("userID42", "user_id42"),
        ("item2Buy", "item2_buy"),
        ("HTTPServer", "http_server"),
        ("RESTAPI", "restapi"),
        ("JSONData", "json_data"),
        ("XMLParser", "xml_parser"),
        ("ABC123DEF456", "abc123_def456"),
        ("GetHTTPResponseCode", "get_http_response_code"),
        ("ProcessHTMLDocument", "process_html_document"),
        ("ABCD", "abcd"),
        ("ABCDEF", "abcdef"),
        ("ABCdEF", "ab_cd_ef"),
        ("_internalField", "_internal_field"),
        ("__privateField", "__private_field"),
        ("preserve_existing", "preserve_existing"),
        ("mixed_Case_With_Underscores", "mixed_case_with_underscores"),
    ],
)
def test_camel_to_snake(value: str, expected: str) -> None:
    assert string_utils.camel_to_snake(value) == expected
