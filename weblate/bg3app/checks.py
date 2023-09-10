import re
from typing import Iterable

from weblate.checks.base import TargetCheck
from weblate.checks.format import BaseFormatCheck, name_format_is_position_based

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from weblate.trans.models import Unit

LSTAG_MATCH = re.compile(r"<LSTag(?:[^>]*)?\/>|<LSTag(?:[^>]*)>[^<]*<\/LSTag>")

SQUARE_BRACKET_MATCH = re.compile(r"\[(\d+)\]")

SQUARE_BRACKET_KEY_MATCH = re.compile(r"\[IE_[A-Za-z0-9]+\]")


class KoreanMisspellCheck(TargetCheck):
    """한글 맞춤법 검사."""

    check_id = "korean_misspell"
    name = "한글 맞춤법 검사"
    description = "다양한 한글 맞춤법 오류를 검사합니다."

    mapping: Iterable[tuple[str, str]] = (
        ("떄", "때"),
        ("됬", "됐"),
        ("되요", "돼요"),
        ("되서", "돼서"),
        ("돼었", "되었"),
        ("어떡게", "어떻게"),
        ("웬지", "왠지"),
        ("오랫만", "오랜만"),
        ("희안", "희한"),
        ("우겨 넣", "욱여 넣"),
        ("우겨넣", "욱여넣"),
        ("뜷", "뚫"),
        ("는게", "는 게"),
        ("는것", "는 것"),
        ("는거", "는 거"),
        ("는건", "는 건"),
    )

    def get_description(self, check_obj):
        result = []
        unit = check_obj.unit
        for a, b in self.mapping:
            if re.search(a, unit.target):
                result.append(f"{a} -> {b}")
        
        return "\n".join(result)

    def check_single(self, source: str, target: str, unit):
        """if any of mapping[n][0] in source return true"""
        for a, b in self.mapping:
            if a in target:
                return True
        return False

    def get_fixup(self, unit):
        return self.mapping


class ItalicTagCheck(TargetCheck):
    """이탤릭 태그 체크."""

    check_id = "italic_tag"
    name = "이탤릭 태그"
    description = "이탤릭 태그 오류를 검사합니다."

    def check_single(self, source, target, unit):
        """check if <i> </i> tags are properly used in target"""
        
        if "<i>" not in target and "</i>" not in target:
            return False
        
        return target.count("<i>") != target.count("</i>")


class BoldTagCheck(TargetCheck):
    """볼드 태그 체크."""

    check_id = "bold_tag"
    name = "볼드 태그"
    description = "볼드 태그 오류를 검사합니다."

    def check_single(self, source: str, target: str, unit: "Unit"):
        """check if <b> </b> tags are properly used in target"""
        
        if "<b>" not in target and "</b>" not in target:
            return False
        
        return target.count("<b>") != target.count("</b>")


class BG3LSTagCheck(BaseFormatCheck):
    """Check for Python format string."""

    check_id = "bg3-lstag-format"
    name = "BG3 LSTag"
    description = "BG3 LSTag check"
    regexp = LSTAG_MATCH

    def is_position_based(self, string):
        return name_format_is_position_based(string)

    def format_string(self, string):
        return "{%s}" % string

    def check_target(self, sources, targets, unit):
        return False


class BG3SquareBracketCheck(BaseFormatCheck):
    check_id = "square_bracket"
    name = "Square bracket format"
    description = "The square brackets do not match source"
    regexp = SQUARE_BRACKET_MATCH

    def is_position_based(self, string):
        return False

    def format_string(self, string):
        return "[%s]" % string
