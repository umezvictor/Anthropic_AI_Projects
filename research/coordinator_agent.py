"""
Coordinator agent (Claude Agent SDK) for the COVID-19 well-being research tool.

Exercise objective: practice orchestrating subagents, managing explicit context
passing, implementing error propagation, and synthesizing results with
provenance tracking -- plus parallel subagent execution with latency
measurement, structured findings with source attribution, and simulated
timeout handling with partial-results coverage reporting.

Architecture
------------
Coordinator (this script)
  -> "web-research" subagent   (tool: WebFetch)  -> findings_web.md
  -> "document-analysis" subagent (tool: Read)   -> findings_doc.md
  -> synthesize() (coordinator itself, no further delegation)
       -> covid19_coordinator_report.html (styled, provenance-tagged,
          per-claim source attribution, coverage-gaps section)
       -> provenance.json (machine-readable audit trail incl. structured
          error context for any failed source)
       -> latency_report.json (sequential vs. parallel timing)
       -> attribution_check.json (automated check that the synthesis step
          actually preserved source attribution, not just a claim that it did)

Two ways to run the subagents (--mode):
  sequential  one query() call per subagent, awaited one after another.
  parallel    ONE query() call whose prompt instructs the coordinator model
              to emit both Agent tool calls together, in the same response,
              so they execute concurrently (the Messages API runs multiple
              tool_use blocks in one assistant turn concurrently and returns
              all their tool_results together).
  compare     (default) runs both and reports the latency difference; the
              parallel run's results are used for the final report.

--simulate-timeout AGENT_KEY forces that subagent's timeout down to
near-zero so you can exercise the error-propagation path deterministically,
without waiting on a real network/API timeout.

Design notes tied to the exercise requirements
-----------------------------------------------
1. The coordinator's `allowed_tools` includes "Agent" (the SDK's name for the
   Task/subagent-delegation tool; it shows as "Task" in the system:init tools
   list and in Claude Code's own UI, but is invoked as the "Agent" tool).
2. Each subagent call gets its *entire* task embedded directly in the prompt
   string passed to query() -- the URL to fetch, or the file path to read,
   plus exactly what to extract. A Claude Agent SDK subagent's context starts
   fresh on every call (unless resumed) and only ever receives its own
   system prompt + that prompt string -- never the coordinator's history.
3. Structured output: each subagent must respond with a JSON array of finding
   objects -- {claim, evidence_excerpt, source, publication_date} -- not
   free-form prose. This separates content (the claim/evidence) from
   metadata (source/date) so the synthesis step can cite per-claim, and so
   a downstream consumer doesn't have to re-parse markdown prose to recover
   who said what. `parse_findings()` validates the shape and rejects
   anything that doesn't match it (treated as a parse-error failure, not
   silently accepted as a plain-text blob).
4. Error propagation: every subagent call (sequential or parallel) is
   wrapped so a failure -- timeout, API error, transport error, malformed
   JSON, or an empty findings array -- becomes a structured ErrorContext
   (failure_type, attempted_query, partial_output, detail) attached to a
   SubagentResult with status="error", instead of crashing the pipeline or
   losing the detail behind a bare string. The synthesis step is told
   explicitly which sources failed, with that full error context, and is
   required to render a "Coverage Gaps" section rather than silently
   dropping or fabricating content for a failed source. The pipeline aborts
   only if every subagent fails; a single failure still produces a
   degraded-but-honest report built from partial results.
5. Provenance: every subagent result carries its source, tool used, status,
   findings/error, and UTC timestamps -- written to provenance.json
   independent of whatever the model says in the HTML. attribution_check.json
   is a second, independent check: it greps the generated HTML for each
   successful source's identity and claim text, so "the synthesis preserved
   attribution" is verified, not just asserted by the model that wrote it.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

PROJECT_DIR = Path(__file__).resolve().parent
PDF_PATH = PROJECT_DIR / "covid2.pdf"
ARTICLE_URL = (
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC10964844"
)
OUTPUT_HTML = PROJECT_DIR / "covid19_coordinator_report.html"
PROVENANCE_JSON = PROJECT_DIR / "provenance.json"
LATENCY_JSON = PROJECT_DIR / "latency_report.json"
ATTRIBUTION_JSON = PROJECT_DIR / "attribution_check.json"
WEB_FINDINGS_MD = PROJECT_DIR / "findings_web.md"
DOC_FINDINGS_MD = PROJECT_DIR / "findings_doc.md"

DEFAULT_TIMEOUT_SECONDS = 180.0
SIMULATED_TIMEOUT_SECONDS = 0.01  # effectively instant -- guarantees a real timeout


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ErrorContext:
    """Structured failure detail passed back to the coordinator, instead of
    a bare error string. This is what the exercise means by "the coordinator
    receives structured error context (failure type, attempted query,
    partial results)"."""

    failure_type: str  # "timeout" | "api_error" | "transport_error" | "parse_error" | "background_launch_ack" | "no_dispatch"
    attempted_query: str
    partial_output: str
    detail: str


@dataclass
class SubagentResult:
    agent_name: str
    source: str
    tool_used: str
    status: str  # "success" | "error"
    findings: list[dict]  # [{claim, evidence_excerpt, source, publication_date}, ...]
    raw_output: str
    error: dict | None  # asdict(ErrorContext) when status == "error", else None
    started_at: str
    finished_at: str


@dataclass
class SubagentTask:
    """One unit of delegated work. The same task list drives both the
    sequential and parallel code paths, so timing comparisons are apples-
    to-apples."""

    agent_key: str
    coordinator_prompt: str
    source_label: str
    tool_used: str
    env: dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


# --- Subagent definitions -----------------------------------------------
# Each subagent is scoped to exactly the tool it needs. Omitting a tool
# means the subagent cannot use it at all -- not even a permission prompt,
# it's simply not in that subagent's session. Each must respond with ONLY a
# JSON array of finding objects -- structured content, separated from the
# source/date metadata that travels alongside each claim.

STRUCTURED_FINDINGS_MARKER = "STRUCTURED_FINDINGS_JSON"

FINDING_SCHEMA_INSTRUCTIONS = (
    "You may write whatever analysis, notes, or summary you find useful. "
    "But your response is read by a program, not a person, so it MUST end "
    f"with a line containing only the marker `{STRUCTURED_FINDINGS_MARKER}:` "
    "followed immediately by a ```json code fence containing a JSON array "
    "of finding objects. This block is mandatory and must be the very "
    "last thing in your response -- a program extracts everything after "
    f"the `{STRUCTURED_FINDINGS_MARKER}:` marker and parses it with "
    "json.loads(); if the marker or valid JSON is missing, your entire "
    "research effort is discarded. Example of the required ending:\n\n"
    f"{STRUCTURED_FINDINGS_MARKER}:\n"
    "```json\n"
    "[\n"
    '  {"claim": "...", "evidence_excerpt": "...", "source": "...", '
    '"publication_date": "YYYY-MM-DD or null"}\n'
    "]\n"
    "```\n\n"
    "Each object in the array must have exactly these keys:\n"
    '- "claim": a single factual statement (string)\n'
    '- "evidence_excerpt": a short direct quote or close paraphrase from '
    "the source that supports the claim (string)\n"
    '- "source": the exact URL or file path you were given (string) -- '
    "the same value on every finding you produce\n"
    '- "publication_date": the source\'s stated publication/update date '
    "in YYYY-MM-DD format if it states one, otherwise JSON null\n\n"
    "Aim for 8-15 findings covering the requested topics. Do not include "
    "any finding whose claim is not directly supported by the source. If "
    f"you cannot access the source at all, put `{STRUCTURED_FINDINGS_MARKER}:` "
    "followed by an empty JSON array `[]` in a code fence."
)

AGENT_DEFINITIONS: dict[str, AgentDefinition] = {
    "web-research": AgentDefinition(
        description=(
            "Fetches a specific web article and extracts structured, "
            "factual findings about COVID-19's societal/economic impact. "
            "Use only when given an explicit URL to fetch."
        ),
        prompt=(
            "You are a research analyst. You will be given a URL and a "
            "research focus. Use WebFetch to retrieve the page. Use ONLY "
            "what the page actually says -- no outside knowledge.\n\n"
            f"{FINDING_SCHEMA_INSTRUCTIONS}"
        ),
        tools=["WebFetch"],
        model="sonnet",
    ),
    "document-analysis": AgentDefinition(
        description=(
            "Reads and summarizes a local PDF document, extracting "
            "structured findings. Use only when given an explicit file path."
        ),
        prompt=(
            "You are a document analyst. You will be given a file path and "
            "a research focus. The underlying transport has a hard 1MB "
            "limit per tool result, so you MUST read the PDF in small "
            "batches: call Read with the `pages` parameter set to at most "
            "3 pages at a time (e.g. '1-3', then '4-6', ...), never the "
            "whole file in one call, until you've covered every page. Use "
            "ONLY what the document actually says -- no outside knowledge.\n\n"
            f"{FINDING_SCHEMA_INSTRUCTIONS}"
        ),
        tools=["Read"],
        model="sonnet",
    ),
}


def build_tasks() -> list[SubagentTask]:
    return [
        SubagentTask(
            agent_key="web-research",
            coordinator_prompt=(
                f"Fetch this URL: {ARTICLE_URL}\n\n"
                "Research focus: the main thesis; impacts on global poverty "
                "and inequality; effects on societies/vulnerable groups; "
                "effects on economies/businesses; key statistics and "
                "quotes; key takeaways."
            ),
            source_label=ARTICLE_URL,
            tool_used="WebFetch",
        ),
        SubagentTask(
            agent_key="document-analysis",
            coordinator_prompt=(
                f"Read this file: {PDF_PATH}\n\n"
                "Research focus: document overview; key findings on "
                "societal/business impact; well-being themes; "
                "business/economic impact themes; notable statistics; "
                "overall conclusion."
            ),
            source_label=str(PDF_PATH),
            tool_used="Read",
            env={"CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS": "6000"},
        ),
    ]


def _extract_block_text(content: str | list[dict] | None) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for item in content:
        if isinstance(item, dict):
            text = item.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts)


def _is_background_launch_ack(text: str) -> bool:
    """A background Agent tool call returns an immediate 'launched' ack
    instead of the subagent's real output. We require run_in_background:
    false in the prompt, but this is a safety net: if the model ignores
    that and the result is just a launch acknowledgment, treat it as a
    failure rather than silently reporting the ack text as real findings."""
    lowered = text.lower()
    return "async agent launched" in lowered or "working in the background" in lowered


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
    return text


def parse_findings(raw_text: str) -> tuple[list[dict], str | None]:
    """Parse and validate a subagent's structured JSON output.

    Returns (findings, parse_error). On any shape mismatch, findings is []
    and parse_error explains why -- callers must treat that as a failure,
    not silently fall back to treating raw_text as free-form content.

    The prompt asks for free-form analysis followed by a mandatory
    `STRUCTURED_FINDINGS_JSON:` marker and a fenced JSON array -- models
    reliably keep this contract even when they ignore a "respond with
    ONLY JSON" instruction and write a prose report anyway. This extracts
    everything after the marker (case-insensitive) and parses that. If the
    marker is absent, it falls back to treating the whole response as the
    JSON array, and finally to a '[' ... ']' substring search, before
    giving up. None of these fallbacks relax the shape validation below.
    """
    text = raw_text.strip()

    marker_match = re.search(
        re.escape(STRUCTURED_FINDINGS_MARKER) + r"\s*:?", text, re.IGNORECASE
    )
    candidate = _strip_code_fence(text[marker_match.end() :]) if marker_match else text

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        start, end = candidate.find("["), candidate.rfind("]")
        if start == -1 or end == -1 or end <= start:
            detail = (
                f"JSONDecodeError after '{STRUCTURED_FINDINGS_MARKER}:' marker: {exc}"
                if marker_match
                else f"No '{STRUCTURED_FINDINGS_MARKER}:' marker found, and whole "
                f"response is not valid JSON: {exc}"
            )
            return [], detail
        try:
            data = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError as exc2:
            return [], f"JSONDecodeError: {exc2}"

    if not isinstance(data, list):
        return [], "Expected a JSON array of finding objects."

    required_keys = {"claim", "evidence_excerpt", "source", "publication_date"}
    cleaned: list[dict] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            return [], f"Finding #{i} is missing one of {sorted(required_keys)}."
        cleaned.append(
            {
                "claim": str(item["claim"]),
                "evidence_excerpt": str(item["evidence_excerpt"]),
                "source": str(item["source"]),
                "publication_date": item["publication_date"],
            }
        )

    if not cleaned:
        return [], "Findings array was empty (source may have been unreachable)."

    return cleaned, None


def _with_structured_output_reminder(task_text: str) -> str:
    """Appended to the literal task text (not just the subagent's system
    prompt) so the marker requirement is reinforced at the end of the
    user-turn the subagent actually reads -- a system prompt alone proved
    unreliable against the model's own instinct to write a prose report."""
    return (
        f"{task_text}\n\n"
        f"Reminder: your response is read by a program. It must end with a "
        f"line containing only `{STRUCTURED_FINDINGS_MARKER}:` followed by "
        "a ```json fenced array of finding objects (claim, evidence_excerpt, "
        "source, publication_date), as described in your instructions. "
        "This is mandatory, not optional."
    )


async def structure_findings(raw_prose: str, source_label: str) -> tuple[list[dict], str | None]:
    """Repair step: convert a subagent's free-form prose into the required
    findings schema via a dedicated, tool-free call.

    Empirically, asking a research subagent to BOTH use tools (WebFetch/
    Read) AND end with strict bare JSON is unreliable -- across several
    prompt-engineering attempts (system-prompt instruction, an explicit
    marker format, and a recency-reinforced reminder appended to the task
    text) the subagent kept writing a normal prose report instead. Rather
    than keep fighting that formatting instinct inside the research turn,
    this isolates the ONE job of reformatting into its own call that has
    no tools and nothing else to do, which is a far easier compliance
    target. parse_findings() is tried on the raw subagent output FIRST
    (fast path, no extra API call, used if a subagent does comply); this
    is only the fallback when that fails.
    """
    prompt = (
        "Convert the research notes below into a JSON array of finding "
        'objects. Each object must have exactly these keys: "claim" '
        "(a single factual statement, string), \"evidence_excerpt\" (a "
        'short quote or close paraphrase from the notes supporting the '
        f'claim, string), "source" (string, use exactly this value for '
        f'every object: {source_label}), and "publication_date" (the '
        "notes' stated publication/update date as a YYYY-MM-DD string if "
        "mentioned, otherwise JSON null). Produce one object per distinct "
        "factual claim in the notes.\n\n"
        "Respond with ONLY the JSON array -- the first character must be "
        "'[' and the last must be ']'. No prose, no markdown code fence, "
        "no commentary. Your entire response is passed directly to "
        "json.loads().\n\n"
        "RESEARCH NOTES:\n"
        f"{raw_prose}"
    )
    options = ClaudeAgentOptions(
        cwd=str(PROJECT_DIR),
        allowed_tools=[],
        permission_mode="bypassPermissions",
        max_turns=3,
    )
    text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text = block.text
        if isinstance(message, ResultMessage) and getattr(message, "result", None):
            text = message.result
    return parse_findings(text)


# --- Sequential path ------------------------------------------------------


async def run_subagent(
    agent_key: str,
    coordinator_prompt: str,
    source_label: str,
    tool_used: str,
    env: dict[str, str] | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> SubagentResult:
    """Run exactly one subagent in isolation (its own query() call) and
    capture its result.

    The subagent receives no conversation history -- only its own
    AgentDefinition.prompt plus `coordinator_prompt`, which must contain
    everything it needs (the URL or file path, and the extraction task).
    Wrapped in asyncio.wait_for so a hung subagent produces a structured
    timeout error (with whatever partial text had streamed in so far)
    instead of blocking the whole pipeline forever.
    """
    started_at = utc_now()
    options = ClaudeAgentOptions(
        cwd=str(PROJECT_DIR),
        allowed_tools=["Agent", tool_used],
        agents={agent_key: AGENT_DEFINITIONS[agent_key]},
        permission_mode="bypassPermissions",
        max_turns=20,
        env=env or {},
    )

    delegation_prompt = (
        f"Use the {agent_key} agent for this task. Do not do the work "
        "yourself; delegate it. When you invoke the Agent tool, pass the "
        "text below verbatim as the subagent's prompt -- do not shorten, "
        "paraphrase, or drop the final reminder line:\n\n"
        f"{_with_structured_output_reminder(coordinator_prompt)}"
    )

    # IMPORTANT: the coordinator's own final chat reply (captured via
    # AssistantMessage/ResultMessage.result) is the TOP-LEVEL model's own
    # paraphrase of what the subagent did -- it is NOT the subagent's raw
    # output and must never be parsed as the structured findings JSON. The
    # actual subagent output is the Agent tool's ToolResultBlock, which
    # arrives in a UserMessage. `coordinator_text` is kept only as a last-
    # resort fallback for partial_output if no tool_result ever arrives.
    coordinator_text = ""
    tool_result_text: str | None = None
    error_ctx: ErrorContext | None = None

    async def consume() -> None:
        nonlocal coordinator_text, tool_result_text, error_ctx
        async for message in query(prompt=delegation_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        coordinator_text = block.text
            if isinstance(message, UserMessage):
                blocks = message.content if isinstance(message.content, list) else []
                for block in blocks:
                    if isinstance(block, ToolResultBlock):
                        text = _extract_block_text(block.content).strip()
                        if block.is_error:
                            error_ctx = ErrorContext(
                                failure_type="api_error",
                                attempted_query=coordinator_prompt,
                                partial_output=text or coordinator_text,
                                detail=text or "Agent tool call returned an error.",
                            )
                        else:
                            tool_result_text = text
            if isinstance(message, ResultMessage):
                if getattr(message, "is_error", False) and error_ctx is None:
                    error_ctx = ErrorContext(
                        failure_type="api_error",
                        attempted_query=coordinator_prompt,
                        partial_output=tool_result_text or coordinator_text,
                        detail=str(
                            getattr(message, "result", None)
                            or getattr(message, "subtype", "unknown error")
                        ),
                    )

    try:
        await asyncio.wait_for(consume(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        error_ctx = ErrorContext(
            failure_type="timeout",
            attempted_query=coordinator_prompt,
            partial_output=tool_result_text or coordinator_text,
            detail=f"Subagent did not complete within {timeout_seconds}s.",
        )
    except Exception as exc:  # noqa: BLE001 - propagate as data, not a crash
        error_ctx = ErrorContext(
            failure_type="transport_error",
            attempted_query=coordinator_prompt,
            partial_output=tool_result_text or coordinator_text,
            detail=f"{type(exc).__name__}: {exc}",
        )

    finished_at = utc_now()

    final_text = tool_result_text or ""

    if error_ctx is None and not final_text:
        error_ctx = ErrorContext(
            failure_type="transport_error",
            attempted_query=coordinator_prompt,
            partial_output=coordinator_text,
            detail="The Agent tool call never returned a tool_result for this subagent.",
        )

    if error_ctx is None and _is_background_launch_ack(final_text):
        error_ctx = ErrorContext(
            failure_type="background_launch_ack",
            attempted_query=coordinator_prompt,
            partial_output=final_text,
            detail="Subagent ran in the background instead of returning its final result synchronously.",
        )

    if error_ctx is not None:
        return SubagentResult(
            agent_name=agent_key,
            source=source_label,
            tool_used=tool_used,
            status="error",
            findings=[],
            raw_output=final_text,
            error=asdict(error_ctx),
            started_at=started_at,
            finished_at=finished_at,
        )

    findings, parse_error = parse_findings(final_text)
    if parse_error:
        # The subagent didn't comply with the structured-output format
        # itself -- fall back to a dedicated, tool-free structuring pass
        # over its raw prose rather than discarding a perfectly good
        # research result just because of a formatting miss.
        findings, repair_error = await structure_findings(final_text, source_label)
        if repair_error:
            return SubagentResult(
                agent_name=agent_key,
                source=source_label,
                tool_used=tool_used,
                status="error",
                findings=[],
                raw_output=final_text,
                error=asdict(
                    ErrorContext(
                        failure_type="parse_error",
                        attempted_query=coordinator_prompt,
                        partial_output=final_text,
                        detail=(
                            f"Subagent output didn't match the required "
                            f"format ({parse_error}); structuring repair "
                            f"pass also failed ({repair_error})."
                        ),
                    )
                ),
                started_at=started_at,
                finished_at=finished_at,
            )

    return SubagentResult(
        agent_name=agent_key,
        source=source_label,
        tool_used=tool_used,
        status="success",
        findings=findings,
        raw_output=final_text,
        error=None,
        started_at=started_at,
        finished_at=finished_at,
    )


async def run_subagents_sequential(tasks: list[SubagentTask]) -> list[SubagentResult]:
    """Baseline: one query() call per subagent, awaited one after another."""
    results = []
    for t in tasks:
        result = await run_subagent(
            agent_key=t.agent_key,
            coordinator_prompt=t.coordinator_prompt,
            source_label=t.source_label,
            tool_used=t.tool_used,
            env=t.env,
            timeout_seconds=t.timeout_seconds,
        )
        results.append(result)
    return results


# --- Parallel path ----------------------------------------------------------


async def run_subagents_parallel(tasks: list[SubagentTask]) -> list[SubagentResult]:
    """Run every task from a SINGLE coordinator response.

    The prompt instructs the coordinator model to delegate to every
    subagent together, in one turn. Per the Messages API's parallel tool
    use behavior, an assistant message may contain multiple tool_use
    blocks, which are executed concurrently with all of their tool_results
    returned together -- so the two Agent tool calls here genuinely run as
    one coordinator response emitting multiple Task/Agent tool calls, with
    the subagents executing in parallel rather than one after another.

    Each subagent still only ever sees its own AgentDefinition.prompt plus
    the per-task text embedded in this combined prompt -- no automatic
    context inheritance, exactly as in the sequential path.

    The whole call is wrapped in asyncio.wait_for using the strictest
    per-task timeout, since this is one shared query(): a timeout here
    marks every still-pending subagent with a structured "timeout" error
    (partial per-subagent text isn't separable across concurrent subagents
    in this mode, so partial_output is left empty and the limitation is
    recorded in `detail`).
    """
    task_by_key = {t.agent_key: t for t in tasks}
    task_sections = "\n\n".join(
        f'{i + 1}. Delegate to the "{t.agent_key}" agent with this exact task '
        "(pass it verbatim as that Agent call's prompt, including the final "
        f"reminder line):\n{_with_structured_output_reminder(t.coordinator_prompt)}"
        for i, t in enumerate(tasks)
    )
    combined_prompt = (
        "You are the coordinator agent. Delegate ALL of the following tasks "
        "to their named subagents RIGHT NOW, in this single response, by "
        "emitting every Agent tool call together so they run in parallel. "
        "Do not call one agent, wait for its result, and then call the "
        "next -- emit all the tool calls in the same turn.\n\n"
        "IMPORTANT: set run_in_background to false on every one of these "
        "Agent tool calls. You must receive and then report back each "
        "subagent's complete, final output yourself -- not just an 'agent "
        "launched in the background' acknowledgment. Running them without "
        "run_in_background: false is the wrong behavior here, even though "
        "they must still execute concurrently with each other. Do not do "
        f"any of this work yourself.\n\n{task_sections}"
    )

    merged_env: dict[str, str] = {}
    for t in tasks:
        merged_env.update(t.env)

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_DIR),
        allowed_tools=["Agent"] + sorted({t.tool_used for t in tasks}),
        agents={t.agent_key: AGENT_DEFINITIONS[t.agent_key] for t in tasks},
        permission_mode="bypassPermissions",
        max_turns=25,
        env=merged_env,
    )

    pending: dict[str, dict[str, str]] = {}  # tool_use_id -> {agent_key, started_at}
    collected: dict[str, SubagentResult] = {}

    def _record_error_for_pending(failure_type: str, detail: str) -> None:
        now = utc_now()
        for meta in pending.values():
            t = task_by_key[meta["agent_key"]]
            collected[meta["agent_key"]] = SubagentResult(
                agent_name=meta["agent_key"],
                source=t.source_label,
                tool_used=t.tool_used,
                status="error",
                findings=[],
                raw_output="",
                error=asdict(
                    ErrorContext(
                        failure_type=failure_type,
                        attempted_query=t.coordinator_prompt,
                        partial_output="",
                        detail=detail,
                    )
                ),
                started_at=meta["started_at"],
                finished_at=now,
            )
        pending.clear()

    async def consume() -> None:
        async for message in query(prompt=combined_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name in ("Agent", "Task"):
                        agent_key = block.input.get("subagent_type")
                        if agent_key in task_by_key and agent_key not in collected:
                            pending[block.id] = {
                                "agent_key": agent_key,
                                "started_at": utc_now(),
                            }
            if isinstance(message, UserMessage):
                blocks = message.content if isinstance(message.content, list) else []
                for block in blocks:
                    if isinstance(block, ToolResultBlock) and block.tool_use_id in pending:
                        meta = pending.pop(block.tool_use_id)
                        t = task_by_key[meta["agent_key"]]
                        text = _extract_block_text(block.content).strip()
                        api_error = bool(block.is_error)
                        bg_ack = _is_background_launch_ack(text)

                        if api_error or bg_ack or not text:
                            failure_type = (
                                "background_launch_ack"
                                if bg_ack
                                else "api_error"
                                if api_error
                                else "parse_error"
                            )
                            detail = (
                                "Subagent ran in the background instead of "
                                "returning its final result synchronously."
                                if bg_ack
                                else (text or "Subagent returned no content.")
                            )
                            collected[meta["agent_key"]] = SubagentResult(
                                agent_name=meta["agent_key"],
                                source=t.source_label,
                                tool_used=t.tool_used,
                                status="error",
                                findings=[],
                                raw_output=text,
                                error=asdict(
                                    ErrorContext(
                                        failure_type=failure_type,
                                        attempted_query=t.coordinator_prompt,
                                        partial_output=text,
                                        detail=detail,
                                    )
                                ),
                                started_at=meta["started_at"],
                                finished_at=utc_now(),
                            )
                            continue

                        findings, parse_error = parse_findings(text)
                        if parse_error:
                            # Same repair fallback as the sequential path:
                            # reformat the subagent's raw prose via a
                            # dedicated, tool-free structuring call before
                            # giving up on an otherwise-good result.
                            findings, repair_error = await structure_findings(
                                text, t.source_label
                            )
                            parse_error = repair_error
                        if parse_error:
                            collected[meta["agent_key"]] = SubagentResult(
                                agent_name=meta["agent_key"],
                                source=t.source_label,
                                tool_used=t.tool_used,
                                status="error",
                                findings=[],
                                raw_output=text,
                                error=asdict(
                                    ErrorContext(
                                        failure_type="parse_error",
                                        attempted_query=t.coordinator_prompt,
                                        partial_output=text,
                                        detail=parse_error,
                                    )
                                ),
                                started_at=meta["started_at"],
                                finished_at=utc_now(),
                            )
                        else:
                            collected[meta["agent_key"]] = SubagentResult(
                                agent_name=meta["agent_key"],
                                source=t.source_label,
                                tool_used=t.tool_used,
                                status="success",
                                findings=findings,
                                raw_output=text,
                                error=None,
                                started_at=meta["started_at"],
                                finished_at=utc_now(),
                            )
            if isinstance(message, ResultMessage) and getattr(message, "is_error", False):
                err = getattr(message, "result", None) or "Coordinator turn ended in error."
                _record_error_for_pending("api_error", str(err))

    batch_timeout = min((t.timeout_seconds for t in tasks), default=DEFAULT_TIMEOUT_SECONDS)
    try:
        await asyncio.wait_for(consume(), timeout=batch_timeout)
    except asyncio.TimeoutError:
        _record_error_for_pending(
            "timeout",
            f"Parallel batch did not complete within {batch_timeout}s. "
            "(Per-subagent partial output isn't separable in parallel mode; "
            "this subagent was still pending when the batch timed out.)",
        )
    except Exception as exc:  # noqa: BLE001 - propagate as data, not a crash
        _record_error_for_pending("transport_error", f"{type(exc).__name__}: {exc}")

    # A task the coordinator never even dispatched (ignored the instruction,
    # or stopped before reaching it) is still reported, not silently dropped.
    now = utc_now()
    for t in tasks:
        if t.agent_key not in collected:
            collected[t.agent_key] = SubagentResult(
                agent_name=t.agent_key,
                source=t.source_label,
                tool_used=t.tool_used,
                status="error",
                findings=[],
                raw_output="",
                error=asdict(
                    ErrorContext(
                        failure_type="no_dispatch",
                        attempted_query=t.coordinator_prompt,
                        partial_output="",
                        detail="Coordinator never dispatched this subagent in the parallel turn.",
                    )
                ),
                started_at=now,
                finished_at=now,
            )

    return [collected[t.agent_key] for t in tasks]


async def timed(label: str, coro) -> tuple[list[SubagentResult], float]:
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    print(f"[coordinator] {label} wall-clock time: {elapsed:.2f}s", file=sys.stderr)
    return result, elapsed


def write_latency_report(mode: str, timing: dict[str, float]) -> None:
    report: dict[str, object] = {
        "mode": mode,
        "measured_at": utc_now(),
        **{k: round(v, 3) for k, v in timing.items()},
    }
    if "sequential_seconds" in timing and "parallel_seconds" in timing and timing["parallel_seconds"]:
        report["speedup_x"] = round(timing["sequential_seconds"] / timing["parallel_seconds"], 3)
        report["seconds_saved"] = round(
            timing["sequential_seconds"] - timing["parallel_seconds"], 3
        )
    LATENCY_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_findings_markdown(path: Path, result: SubagentResult) -> None:
    lines = [f"# Findings: {result.agent_name}", f"Status: {result.status}", ""]
    if result.status == "error":
        err = result.error or {}
        lines += [
            f"- failure_type: {err.get('failure_type')}",
            f"- attempted_query: {err.get('attempted_query')}",
            f"- detail: {err.get('detail')}",
            "",
            "## Partial output captured before failure",
            "```",
            err.get("partial_output") or "(none captured)",
            "```",
        ]
    else:
        lines += ["```json", json.dumps(result.findings, indent=2), "```"]
    path.write_text("\n".join(lines), encoding="utf-8")


# --- Synthesis (coordinator's own step, no further delegation) ------------


def render_findings_block(result: SubagentResult) -> str:
    """Render one subagent's result for the synthesis prompt, with its
    provenance -- and, on failure, its full structured error context --
    made explicit and unmissable."""
    header = (
        f"### Findings from `{result.agent_name}` "
        f"(source: {result.source}, status: {result.status})\n"
        f"- tool_used: {result.tool_used}\n"
        f"- started_at: {result.started_at}\n"
        f"- finished_at: {result.finished_at}\n"
    )
    if result.status == "error":
        err = result.error or {}
        partial = err.get("partial_output") or "(none captured)"
        return (
            header
            + f"- failure_type: {err.get('failure_type', 'unknown')}\n"
            + f"- attempted_query: {err.get('attempted_query', '')}\n"
            + f"- detail: {err.get('detail', '')}\n"
            + f"- partial_output_captured: {partial[:800]}\n\n"
            + "_This source produced no usable findings -- it is a coverage "
            "gap, not a finding. Do not invent content for it._\n"
        )
    return header + "\n```json\n" + json.dumps(result.findings, indent=2) + "\n```\n"


async def synthesize(results: list[SubagentResult]) -> None:
    """Coordinator's own synthesis step: no further delegation, just the
    explicit findings (with provenance/error context) embedded in the
    prompt."""
    findings_blocks = "\n\n---\n\n".join(render_findings_block(r) for r in results)
    succeeded = [r.source for r in results if r.status == "success"]
    failed = [r.source for r in results if r.status == "error"]

    synthesis_prompt = f"""You are the coordinator agent. The subagents already ran and \
returned the structured findings (or error context) below. Do NOT re-fetch \
or re-read any source yourself -- synthesize only from what is given here.

{findings_blocks}

---

Sources that succeeded: {succeeded or "none"}
Sources that failed: {failed or "none"}

Write a single self-contained HTML file to exactly this path using the \
Write tool: {OUTPUT_HTML}

Requirements for the HTML:
1. Title: "COVID-19's Impact on Society and Business -- Coordinator Report".
2. Apply CSS styling inline in a <style> tag (clean, readable, card-based \
   layout, no external stylesheets).
3. One section per successful source. Each finding has a claim, an \
   evidence_excerpt, a source, and a publication_date. PRESERVE SOURCE \
   ATTRIBUTION: every claim you present must be visibly tied to its own \
   source and publication date (e.g. inline "(Source: <source>, <date>)" \
   next to the claim, or a numbered citation with a reference list). Do \
   NOT merge claims from different sources into one unattributed sentence, \
   and do not drop the source/date metadata when you reword a claim.
4. A "Coordinator Synthesis" section comparing/cross-referencing the \
   successful sources' claims -- still citing each claim's source/date \
   when you reference it here too.
5. A "Coverage Gaps" section listing, for every FAILED source: its agent \
   name, failure_type, the attempted_query, and the detail given above \
   verbatim. State plainly that this source's findings are missing from \
   the report above -- never fabricate findings for a failed source to \
   fill the gap.
6. A "Provenance" footer listing, for every source (succeeded or failed): \
   agent name, status, tool used, and start/finish timestamps (use the \
   values given above verbatim -- do not invent timestamps).
Do not print the HTML in your response -- write it directly to the file.
"""

    options = ClaudeAgentOptions(
        cwd=str(PROJECT_DIR),
        allowed_tools=["Write"],
        permission_mode="bypassPermissions",
        max_turns=10,
    )

    async for message in query(prompt=synthesis_prompt, options=options):
        if isinstance(message, ResultMessage) and getattr(message, "is_error", False):
            raise RuntimeError(
                f"Synthesis step failed: {getattr(message, 'result', 'unknown error')}"
            )


def verify_attribution(results: list[SubagentResult]) -> dict:
    """Independent, non-LLM check that the synthesis step actually
    preserved source attribution, rather than trusting the model's own
    claim that it did. Greps the generated HTML for each successful
    source's identity and a snippet of each claim's text."""
    html_text = OUTPUT_HTML.read_text(encoding="utf-8") if OUTPUT_HTML.exists() else ""
    report: dict[str, object] = {"checked_at": utc_now(), "sources": []}

    for r in results:
        if r.status != "success":
            continue
        source_mentioned = r.source in html_text or Path(r.source).name in html_text
        claims_with_snippet_present = 0
        for f in r.findings:
            snippet = str(f.get("claim", ""))[:40].strip()
            if snippet and snippet in html_text:
                claims_with_snippet_present += 1
        total = len(r.findings)
        report["sources"].append(
            {
                "agent_name": r.agent_name,
                "source": r.source,
                "source_identifier_found_in_html": source_mentioned,
                "total_findings": total,
                "claims_with_recognizable_text_in_html": claims_with_snippet_present,
                "claim_coverage_ratio": round(claims_with_snippet_present / total, 3)
                if total
                else None,
            }
        )

    any_missing_source = any(
        not s["source_identifier_found_in_html"] for s in report["sources"]
    )
    report["all_successful_sources_attributed"] = not any_missing_source and bool(
        report["sources"]
    )
    ATTRIBUTION_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def write_provenance_manifest(results: list[SubagentResult]) -> None:
    """Deterministic, model-independent provenance record -- not generated
    by the LLM, so it can be trusted as an audit trail even if the HTML
    synthesis step misrepresents something."""
    manifest = {
        "generated_at": utc_now(),
        "sources": [asdict(r) for r in results],
    }
    PROVENANCE_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


async def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        print(
            "ERROR: No Anthropic credentials found. Set ANTHROPIC_API_KEY "
            "(or ANTHROPIC_AUTH_TOKEN) before running this script.",
            file=sys.stderr,
        )
        return 1

    parser = argparse.ArgumentParser(description="Coordinator agent for the COVID-19 research tool.")
    parser.add_argument(
        "--mode",
        choices=["sequential", "parallel", "compare"],
        default="compare",
        help=(
            "sequential: one query() call per subagent, awaited one after "
            "another. parallel: one query() call where the coordinator "
            "emits both Agent tool calls in a single response. compare "
            "(default): run both and report the latency difference -- the "
            "parallel run's results are used for the final report."
        ),
    )
    parser.add_argument(
        "--simulate-timeout",
        choices=list(AGENT_DEFINITIONS.keys()),
        default=None,
        help=(
            "Force this subagent's timeout to ~0s to deterministically "
            "exercise the error-propagation / partial-results path, "
            "without waiting on a real network timeout."
        ),
    )
    args = parser.parse_args()

    tasks = build_tasks()
    if args.simulate_timeout:
        for t in tasks:
            if t.agent_key == args.simulate_timeout:
                t.timeout_seconds = SIMULATED_TIMEOUT_SECONDS
                print(
                    f"[coordinator] SIMULATING a timeout on '{t.agent_key}' "
                    f"(timeout={SIMULATED_TIMEOUT_SECONDS}s)",
                    file=sys.stderr,
                )

    timing: dict[str, float] = {}
    results: list[SubagentResult] = []

    if args.mode in ("sequential", "compare"):
        print("[coordinator] running SEQUENTIAL subagent calls...", file=sys.stderr)
        seq_results, seq_elapsed = await timed("sequential", run_subagents_sequential(tasks))
        timing["sequential_seconds"] = seq_elapsed
        results = seq_results

    if args.mode in ("parallel", "compare"):
        print(
            "[coordinator] running PARALLEL subagent calls (single coordinator response)...",
            file=sys.stderr,
        )
        par_results, par_elapsed = await timed("parallel", run_subagents_parallel(tasks))
        timing["parallel_seconds"] = par_elapsed
        results = par_results  # prefer the parallel run's results when both ran

    if args.mode == "compare" and timing.get("parallel_seconds"):
        speedup = timing["sequential_seconds"] / timing["parallel_seconds"]
        saved = timing["sequential_seconds"] - timing["parallel_seconds"]
        print(
            f"[coordinator] LATENCY COMPARISON: sequential={timing['sequential_seconds']:.2f}s  "
            f"parallel={timing['parallel_seconds']:.2f}s  "
            f"speedup={speedup:.2f}x  saved={saved:.2f}s",
            file=sys.stderr,
        )

    write_latency_report(args.mode, timing)

    for r in results:
        target = WEB_FINDINGS_MD if r.agent_name == "web-research" else DOC_FINDINGS_MD
        write_findings_markdown(target, r)
        detail = f" ({r.error.get('failure_type')})" if r.status == "error" and r.error else ""
        print(f"[coordinator] {r.agent_name} status: {r.status}{detail}", file=sys.stderr)

    write_provenance_manifest(results)

    succeeded = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "error"]

    if not succeeded:
        print(
            "[coordinator] all subagents failed; aborting synthesis.",
            file=sys.stderr,
        )
        return 1

    if failed:
        print(
            f"[coordinator] proceeding with PARTIAL results: "
            f"{len(succeeded)} succeeded, {len(failed)} failed "
            f"({', '.join(r.agent_name for r in failed)}). "
            "The report will include a Coverage Gaps section.",
            file=sys.stderr,
        )

    print("[coordinator] synthesizing final report...", file=sys.stderr)
    try:
        await synthesize(results)
    except Exception as exc:  # noqa: BLE001
        print(f"[coordinator] synthesis failed: {exc}", file=sys.stderr)
        return 1

    attribution = verify_attribution(results)
    if attribution["sources"] and not attribution["all_successful_sources_attributed"]:
        print(
            "[coordinator] WARNING: attribution check failed -- at least one "
            "successful source's identity was not found in the generated "
            f"HTML. See {ATTRIBUTION_JSON}",
            file=sys.stderr,
        )
    else:
        print("[coordinator] attribution check passed.", file=sys.stderr)

    print(f"[coordinator] done. Report written to {OUTPUT_HTML}", file=sys.stderr)
    print(f"[coordinator] provenance manifest written to {PROVENANCE_JSON}", file=sys.stderr)
    print(f"[coordinator] latency report written to {LATENCY_JSON}", file=sys.stderr)
    print(f"[coordinator] attribution check written to {ATTRIBUTION_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
