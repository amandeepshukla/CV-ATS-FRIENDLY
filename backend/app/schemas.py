from typing import Literal

from pydantic import BaseModel


class KeywordMatch(BaseModel):
    matched: list[str]
    missing: list[str]


class FormattingIssue(BaseModel):
    severity: Literal["high", "medium", "low"]
    issue: str
    fix: str


class ScoreResult(BaseModel):
    ats_score: int
    summary: str
    keyword_match: KeywordMatch
    formatting_issues: list[FormattingIssue]
    recommendations: list[str]
