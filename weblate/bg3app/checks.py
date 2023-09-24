from dataclasses import dataclass
import re
from typing import Iterable

from weblate.checks.base import TargetCheck
from weblate.checks.format import BaseFormatCheck, name_format_is_position_based

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from weblate.checks.models import Check
    from weblate.trans.models import Unit

LSTAG_MATCH = re.compile(r"<LSTag(?:[^>]*)?\/>|<LSTag(?:[^>]*)>[^<]*<\/LSTag>")

SQUARE_BRACKET_MATCH = re.compile(r"\[(\d+)\]")

SQUARE_BRACKET_KEY_MATCH = re.compile(r"\[IE_[A-Za-z0-9]+\]")


mapping: list[tuple[str, str]] = [
    (r"떄", "때"),
    (r"됬", "됐"),
    (r"되요", "돼요"),
    (r"되서", "돼서"),
    (r"돼었", "되었"),
    (r"되\.", "돼."),
    (r"어떡게", "어떻게"),
    (r"웬지", "왠지"),
    (r"오랫만", "오랜만"),
    (r"희안", "희한"),
    (r"깊숙히", "깊숙이"),
    (r"우겨 넣", "욱여 넣"),
    (r"우겨넣", "욱여넣"),
    (r"뜷", "뚫"),
    (r"갯수", "개수"),
    (r"바래\.", "바라."),
    (r"지마\.", "지 마."),
    (r"바래요", "바라요"),
    (r"쳐먹", "처먹"),
    # (r"거에요", "거예요"),
    (r"어떻하", "어떡하"),
    (r"아니예요", "아니에요"),
    (r"는게", "는 게"),
    (r"는것", "는 것"),
    (r"는거", "는 거"),
    (r"는건", "는 건"),
    (r"은게", "은 게"),
    (r"을수([는가])", r"을 수\1"),
    (r"줄수([는가])", r"줄 수\1"),
    (r"할수([는가])", r"할 수\1"),
    (r"릴수([는가])", r"릴 수\1"),
    (r"한게", r"한 게"),
    (r"인겁", r"인 겁"),
    (r"한겁", r"한 겁"),
    (r"인거", r"인 거"),
    (r"신경쓰", r"신경 쓰"),
    (r"일텐", r"일 텐"),
    (r"할텐", r"할 텐"),
    (r"을텐", r"을 텐"),
    (r"일만큼", r"일 만큼"),
    (r"할만큼", r"할 만큼"),
    (r"을만큼", r"을 만큼"),
    (r"는만큼", r"는 만큼"),
    (r"안되", r"안 되"),
    (r"지않", r"지 않"),
    (r"다음 번", r"다음번"),
    (r"하지마", r"하지 마"),
    (r"야될", r"야 될"),
    (r"\b그 쪽", r"그쪽"),
    (r"\b이 쪽", r"이쪽"),
    (r"\b저 쪽", r"저쪽"),
    (r"\b그 다음", r"그다음"),
]


class SpellCheckItem:
    """맞춤법 검사 결과 항목."""
    src: str
    src_re: re.Pattern[str]
    dst: str

    def __init__(self, src: str, dst: str):
        self.src = src
        self.src_re = re.compile(src)
        self.dst = dst
    
    def check(self, text: str) -> bool:
        return self.src_re.search(text) is not None
    
    def get_replace_pair_list(self, text: str) -> list[tuple[str, str]]:
        result = {}
        for m in self.src_re.finditer(text):
            replaced = self.src_re.sub(self.dst, m.group(0))
            result[m.group(0)] = replaced
        return [(k, v) for k, v in result.items()]


check_list: list[SpellCheckItem] = [SpellCheckItem(a, b) for a, b in mapping]


class KoreanMisspellCheck(TargetCheck):
    """한글 맞춤법 검사."""

    check_id = "korean_misspell"
    name = "한글 맞춤법 검사"
    description = "다양한 한글 맞춤법 오류를 검사합니다."

    def get_description(self, check_obj: "Check"):
        unit: "Unit" = check_obj.unit
        result = []
        for c in check_list:
            for src, dst in c.get_replace_pair_list(unit.target):
                result.append(f"{src} -> {dst}")
        return "\n".join(result)

    def check_single(self, source: str, target: str, unit):
        return any(x.check(target) for x in check_list)

    def get_fixup(self, unit: "Unit"):
        result = [(x.src, x.dst) for x in check_list if x.check(unit.target)]        
        return result    


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
