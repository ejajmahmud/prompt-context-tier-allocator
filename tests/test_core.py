"""Tests for Prompt Context Tier Allocator."""
import unittest
from prompt_context_tier_allocator.core import ContextTierAllocator, ContextItem, BudgetExceededError


class TestContextTierAllocator(unittest.TestCase):
    def test_pins_mandatory_and_packs_highest_density(self):
        alloc = ContextTierAllocator(max_tokens=100, reserve_output=20)
        res = alloc.allocate([
            ContextItem("sys", "rules", tokens=30, priority=100, mandatory=True),
            ContextItem("a", "small high", tokens=20, priority=50),
            ContextItem("b", "big low", tokens=50, priority=40),
            ContextItem("c", "medium", tokens=25, priority=45),
        ])
        ids = [i.item_id for i in res["selected"]]
        self.assertEqual(ids, ["sys", "a", "c"])
        self.assertEqual(res["used_tokens"], 75)

    def test_mandatory_overflow_raises(self):
        alloc = ContextTierAllocator(max_tokens=50)
        with self.assertRaises(BudgetExceededError):
            alloc.allocate([ContextItem("sys", "huge", tokens=60, priority=100, mandatory=True)])
