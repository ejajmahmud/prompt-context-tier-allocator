"""Core priority-aware token budget allocator for context engineering."""
from dataclasses import dataclass
from typing import Any, Dict, List


class BudgetExceededError(Exception):
    """Raised when mandatory context items alone exceed the available budget."""


@dataclass
class ContextItem:
    item_id: str
    content: str
    tokens: int
    priority: float
    mandatory: bool = False


class ContextTierAllocator:
    """Packs mandatory and optional context items under a hard token ceiling."""

    def __init__(self, max_tokens: int, reserve_output: int = 0):
        self.available_tokens = max_tokens - reserve_output
        if self.available_tokens <= 0:
            raise ValueError("Effective token budget must be positive")

    def allocate(self, items: List[ContextItem]) -> Dict[str, Any]:
        mandatory = [i for i in items if i.mandatory]
        optional = [i for i in items if not i.mandatory]

        used = sum(i.tokens for i in mandatory)
        if used > self.available_tokens:
            raise BudgetExceededError(f"Mandatory items need {used} tokens, budget is {self.available_tokens}")

        selected = list(mandatory)
        dropped: List[ContextItem] = []

        # Sort optional items by priority density (priority / tokens), tie-break by raw priority
        ranked = sorted(optional, key=lambda i: (i.priority / max(1, i.tokens), i.priority), reverse=True)
        for item in ranked:
            if used + item.tokens <= self.available_tokens:
                selected.append(item)
                used += item.tokens
            else:
                dropped.append(item)

        return {
            "selected": selected,
            "dropped": dropped,
            "used_tokens": used,
            "remaining_tokens": self.available_tokens - used,
        }
