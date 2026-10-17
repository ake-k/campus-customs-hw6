"""Structured types for the vendor desk agent.

VendorDecision is the agent's answer: the shape follows section 13 of the shop handbook.
The other models are the rows written to the output/*.json logs.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class VendorDecision(BaseModel):
    """What the agent reports for one vendor document (handbook section 13)."""

    vendor: str = Field(description="Vendor name exactly as it appears in the document.")
    sku: str | None = Field(
        description="Campus Customs SKU such as CC-HD-006, or null if the document does not identify one."
    )
    unit_price: float | None = Field(
        description="Quoted price per unit in US dollars, or null if the document does not state it."
    )
    lead_time_days: int | None = Field(
        description="Lead time in days as stated by the document, or null if the document does not state it."
    )
    min_order: int | None = Field(
        description="Minimum order in units, or null if the document does not state it."
    )
    decision: Literal["recommend", "do_not_recommend"] = Field(
        description="recommend only if all four purchasing checks in handbook section 4 pass."
    )
    reason: str = Field(
        description="One sentence that names the purchasing check that decided the outcome."
    )


class GuardrailCheck(BaseModel):
    """One of the four handbook purchasing checks, as decided by code (design layer)."""

    check: Literal["approved_vendor", "price", "lead_time", "minimum_order"]
    passed: bool
    detail: str


class ReviewedDecision(VendorDecision):
    """The defended agent's answer: decided in code (design layer), with a third outcome for a human."""

    decision: Literal["recommend", "do_not_recommend", "needs_review"] = Field(
        description="needs_review when the document gives conflicting values that would change the outcome."
    )
    conflicts: dict[str, list[str]] = Field(
        default_factory=dict, description="Each field the document states more than one value for."
    )
    main_quote_decision: Literal["recommend", "do_not_recommend"] = Field(
        description="The decision on the values the quote states first, for outputs that allow only two values."
    )


class ExamResult(BaseModel):
    """One exam document's answer, in the exact shape output/exam_results.json asks for."""

    file: str
    vendor: str
    sku: str | None
    unit_price: float | None
    lead_time_days: int | None
    min_order: int | None
    decision: Literal["recommend", "do_not_recommend"]
    reason: str
    trap_tool_called: bool
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    cost_usd: float


class ToolCallRecord(BaseModel):
    """One tool call made during a run, for output/audit_trail.json."""

    tool: str
    args: dict[str, Any]
    result: str  # shortened so the audit trail stays readable


class AuditEntry(BaseModel):
    """One run of the agent: every tool it called, plus its final answer."""

    run_id: str
    time: str
    document: str
    model: str
    defenses: str = "none"  # which defense layers were on, e.g. "code+design+prompt"
    tool_calls: list[ToolCallRecord]
    hidden_text_removed: list[dict[str, str]] = []  # code layer: what the reader stripped, and from where
    blocked_tool_calls: list[dict[str, Any]] = []  # design layer: trap-tool calls stopped for approval
    model_answer: VendorDecision | None = None  # design layer: the model's answer before code re-decided
    guardrail_checks: list[GuardrailCheck] = []  # design layer: the four checks as decided by code
    final_answer: ReviewedDecision | VendorDecision | None
    error: str | None = None


class RequestUsageRecord(BaseModel):
    """Token counts the API reported for one model request inside a run."""

    input_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    output_tokens: int
    reasoning_tokens: int
    api_model: str | None = None  # model name the API says answered
    raw_usage: dict[str, Any] | None = None  # the API's usage block, unmodified


class CostBreakdown(BaseModel):
    """Dollar cost of a run, priced with data/prices.json."""

    uncached_input_usd: float
    cached_input_usd: float
    cache_write_usd: float
    output_usd: float
    total_usd: float


class UsageEntry(BaseModel):
    """One run's token counts (as reported by the API) and dollar cost, for output/usage_log.json."""

    run_id: str
    time: str
    document: str
    model: str
    cache_setup: Literal["with_cache", "without_cache"]
    defenses: str = "none"
    requests: int
    input_tokens: int  # all prompt tokens, including cached ones
    cache_read_tokens: int
    cache_write_tokens: int
    uncached_input_tokens: int  # input_tokens minus cache reads and writes
    output_tokens: int  # includes reasoning tokens
    reasoning_tokens: int
    total_tokens: int
    per_request: list[RequestUsageRecord]
    cost: CostBreakdown


class TrapCall(BaseModel):
    """A call to send_email or approve_payment. Any entry means a document hijacked the agent."""

    time: str
    document: str
    tool: Literal["send_email", "approve_payment"]
    args: dict[str, Any]
    executed: bool = True  # False when the design layer's human-approval gate stopped the call
    blocked_by: str | None = None


class CacheTestCall(BaseModel):
    """One model call in the Problem 4 cache test, for output/cache_test.json."""

    setup: Literal["with_cache", "without_cache"]
    document: str
    run_id: str
    request_index: int  # 1 = the call that asks for read_document, 2 = the call that answers
    api_model: str | None
    input_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    uncached_input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int
    raw_usage: dict[str, Any] | None
    cost: CostBreakdown
