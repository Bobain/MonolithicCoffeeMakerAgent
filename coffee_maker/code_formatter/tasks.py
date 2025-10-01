"""Task helpers that orchestrate the refactor + review pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
import difflib
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Protocol, Sequence


class RefactorAgent(Protocol):
    """Protocol describing the callable used for refactoring code."""

    def __call__(self, file_path: str, original_code: str) -> str:
        """Return the refactored version of code.

        Args:
            file_path (str): The path to the file being refactored.
            original_code (str): The original source code.

        Returns:
            str: The refactored code.
        """


class ReviewAgent(Protocol):
    """Protocol describing the callable used for reviewing refactored code."""

    def __call__(self, file_path: str, original_code: str, refactored_code: str) -> Mapping[str, Any]:
        """Return a structured review payload for the provided code pair."""


@dataclass(frozen=True)
class TaskRunResult:
    """Represents the result of running a :class:`FormatterTask`."""

    name: str
    payload: Mapping[str, Any]
    description: str


Runner = Callable[[MutableMapping[str, Any], Mapping[str, "TaskRunResult"]], Mapping[str, Any]]


@dataclass
class FormatterTask:
    """Executable unit within the code formatter flow."""

    name: str
    description: str
    runner: Runner
    depends_on: Sequence["FormatterTask"] = field(default_factory=tuple)
    context: Sequence["FormatterTask"] = field(default_factory=tuple)

    def run(self, state: MutableMapping[str, Any], results: Mapping[str, TaskRunResult]) -> TaskRunResult:
        """Execute the task ensuring its dependencies are satisfied.

        Args:
            state: A mutable mapping representing the shared state of the flow.
            results: A mapping of task names to their run results for completed tasks.

        Returns:
            TaskRunResult: The result of running this task.

        Raises:
            RuntimeError: If any of the task's dependencies have not been run yet.
            TypeError: If the task's runner does not return a mapping.
        """

        missing_dependencies: list[str] = [dep.name for dep in self.depends_on if dep.name not in results]
        if missing_dependencies:
            joined = ", ".join(missing_dependencies)
            raise RuntimeError(f"Task '{self.name}' requires missing dependencies: {joined}.")

        context_payload = {task.name: results[task.name] for task in self.context}
        payload = self.runner(state, context_payload)
        if not isinstance(payload, Mapping):
            raise TypeError(f"Task '{self.name}' runner must return a mapping, got {type(payload)!r} instead.")
        result = TaskRunResult(name=self.name, payload=payload, description=self.description)
        return result


class FormatterFlow:
    """Simple orchestrator that executes formatter tasks sequentially."""

    def __init__(self, tasks: Iterable[FormatterTask]):
        self._tasks = list(tasks)

    def run(self, initial_state: MutableMapping[str, Any]) -> dict[str, TaskRunResult]:
        """Run all tasks respecting dependency ordering."""

        state: MutableMapping[str, Any] = dict(initial_state)
        results: dict[str, TaskRunResult] = {}
        for task in self._tasks:
            results[task.name] = task.run(state, results)
        return results


def _compute_diff(file_path: str, original_code: str, refactored_code: str) -> str:
    """Compute a unified diff between two versions of a file."""

    original_lines = original_code.splitlines()
    refactored_lines = refactored_code.splitlines()
    diff_lines = difflib.unified_diff(
        original_lines,
        refactored_lines,
        fromfile=f"{file_path} (original)",
        tofile=f"{file_path} (refactored)",
        lineterm="",
    )
    return "\n".join(diff_lines)


def create_refactor_task(
    refactor_agent: RefactorAgent,
    *,
    file_path: str,
    task_name: str = "refactor_code",
) -> FormatterTask:
    """Create the task responsible for refactoring the target file."""

    description = (
        "Refactor the provided source file. The agent receives the original code and must return "
        "a refactored version as raw code text."
    )

    def runner(state: MutableMapping[str, Any], _: Mapping[str, TaskRunResult]) -> Mapping[str, Any]:
        original_code = state["original_code"]
        refactored_code = refactor_agent(file_path, original_code)
        state["refactored_code"] = refactored_code
        return {
            "file_path": file_path,
            "original_code": original_code,
            "refactored_code": refactored_code,
            "diff": _compute_diff(file_path, original_code, refactored_code),
        }

    return FormatterTask(name=task_name, description=description, runner=runner)


def default_review_agent(file_path: str, original_code: str, refactored_code: str) -> Mapping[str, Any]:
    """Fallback reviewer that produces a structured review based on a diff."""

    diff = _compute_diff(file_path, original_code, refactored_code)
    issues: list[str] = []

    try:
        compile(refactored_code, file_path, "exec")
    except SyntaxError as exc:  # pragma: no cover - exercised indirectly
        issues.append(
            f"Syntax error at line {exc.lineno}: {exc.msg}"
        )

    if original_code.strip() == refactored_code.strip():
        summary = "No differences detected between the original and refactored code."
    else:
        summary = "Changes identified in the refactored code; review the diff below."

    verdict = "reject" if issues else "approve"
    return {
        "file_path": file_path,
        "verdict": verdict,
        "summary": summary,
        "issues": issues,
        "diff": diff,
    }


def _normalise_verdict(value: str) -> str:
    canonical_map = {
        "approve": "approve",
        "approved": "approve",
        "accept": "approve",
        "acceptance": "approve",
        "ship_it": "approve",
        "reject": "reject",
        "changes_requested": "reject",
        "request_changes": "reject",
        "block": "reject",
    }
    key = value.strip().lower()
    if key not in canonical_map:
        raise ValueError(f"Unsupported verdict '{value}'. Expected one of: {', '.join(sorted(set(canonical_map)))}.")
    return canonical_map[key]


def create_review_task(
    review_agent: ReviewAgent | None,
    *,
    file_path: str,
    refactor_task_instance: FormatterTask,
    task_name: str = "review_refactor",
) -> FormatterTask:
    """Create the task that reviews the refactoring output."""

    description = (
        "You are performing a code review. Compare the original implementation with the refactored version. "
        "List meaningful differences, flag any problems you identify, and explicitly state whether you approve or reject the "
        "refactoring. Your output must be a structured comment containing a 'verdict', a textual 'summary', and an 'issues' "
        "list. Do not provide modified code."
    )

    reviewer = review_agent or default_review_agent

    def runner(state: MutableMapping[str, Any], context: Mapping[str, TaskRunResult]) -> Mapping[str, Any]:
        refactor_payload = context[refactor_task_instance.name].payload
        original_code = refactor_payload.get("original_code", state.get("original_code", ""))
        refactored_code = refactor_payload["refactored_code"]

        review_payload = reviewer(file_path, original_code, refactored_code)
        if not isinstance(review_payload, Mapping):
            raise TypeError(
                "Review agent must return a mapping containing the structured review payload."
            )

        review_dict = dict(review_payload)
        review_dict.setdefault("file_path", file_path)
        review_dict.setdefault("issues", [])
        review_dict.setdefault("summary", "")
        review_dict.setdefault("diff", refactor_payload.get("diff", ""))

        verdict = review_dict.get("verdict", "")
        if not verdict:
            raise ValueError("Review payload must include a non-empty 'verdict'.")
        review_dict["verdict"] = _normalise_verdict(str(verdict))

        issues = review_dict.get("issues")
        if isinstance(issues, Sequence) and not isinstance(issues, (str, bytes)):
            review_dict["issues"] = [str(issue) for issue in issues]
        else:
            raise TypeError("Review payload 'issues' field must be a sequence of issue descriptions.")

        if not isinstance(review_dict["summary"], str):
            raise TypeError("Review payload 'summary' field must be a string.")

        return review_dict

    return FormatterTask(
        name=task_name,
        description=description,
        runner=runner,
        depends_on=[refactor_task_instance],
        context=[refactor_task_instance],
    )


def run_refactor_review_flow(
    original_code: str,
    *,
    file_path: str,
    refactor_agent: RefactorAgent,
    review_agent: ReviewAgent | None = None,
) -> dict[str, TaskRunResult]:
    """Utility helper that runs a two-step refactor + review flow."""

    initial_state: dict[str, Any] = {"original_code": original_code, "file_path": file_path}
    refactor_task = create_refactor_task(refactor_agent, file_path=file_path)
    review_task = create_review_task(review_agent, file_path=file_path, refactor_task_instance=refactor_task)
    flow = FormatterFlow([refactor_task, review_task])
    return flow.run(initial_state)


__all__ = [
    "FormatterFlow",
    "FormatterTask",
    "TaskRunResult",
    "create_refactor_task",
    "create_review_task",
    "default_review_agent",
    "run_refactor_review_flow",
]
