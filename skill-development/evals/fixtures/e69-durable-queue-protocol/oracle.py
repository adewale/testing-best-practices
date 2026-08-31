#!/usr/bin/env python3
"""E69 oracle: assess the end-to-end durability protocol and its fault tests."""
from __future__ import annotations

import re
import sys
from pathlib import Path


NEGATED = re.compile(
    r"(?:\b(?:do|does|did|should|must|need|can|could|will|would)\s+not\b"
    r"|\b(?:don.t|doesn.t|didn.t|shouldn.t|mustn.t|needn.t|can.t|cannot|"
    r"couldn.t|won.t|wouldn.t)\b|\bnot\b|\bnever\b|\bwithout\b|\bno\s+need\s+to\b)"
    r"(?:\W+\w+){0,6}\W*$",
    re.I,
)


def read_markdown(root: Path) -> str:
    return "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.md"))


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.S) is not None


def negated_before(text: str, start: int) -> bool:
    prefix = text[max(0, start - 140) : start]
    prefix = re.split(r"(?<=[.!?;])\s+", prefix)[-1]
    return NEGATED.search(prefix) is not None


def affirmed(pattern: str, text: str) -> bool:
    return any(
        not negated_before(text, match.start())
        for match in re.finditer(pattern, text, re.I | re.S)
    )


def affirmed_predicate_after(subject: str, predicate: str, text: str, distance: int = 180) -> bool:
    for subject_match in re.finditer(subject, text, re.I | re.S):
        tail = text[subject_match.end() : subject_match.end() + distance]
        for predicate_match in re.finditer(predicate, tail, re.I | re.S):
            start = subject_match.end() + predicate_match.start()
            if not negated_before(text, start):
                return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    low = read_markdown(root).lower()
    errors: list[str] = []
    if not low.strip():
        print("no markdown assessment found", file=sys.stderr)
        return 1

    dual_write = has(
        r"(dual.?write|two systems|db.{0,60}redis|database.{0,60}redis).{0,180}"
        r"(gap|atomic|fail|lost|loses?|unavailable|enqueue)"
        r"|(commit|insert).{0,120}(before|then).{0,80}(rpush|redis).{0,120}(fail|unavailable|lost)",
        low,
    )
    early_ack = has(
        r"lpop.{0,180}(remove|destructive|ack|lost|loss|crash|before)"
        r"|(remove|ack).{0,100}(before|prior).{0,100}(process|charge|work).{0,100}(lost|crash)",
        low,
    )
    if not dual_write:
        errors.append("misses the committed-database / failed-Redis dual-write window")
    if not early_ack:
        errors.append("misses that LPOP destructively acknowledges the job before work completes")

    persisted_intent = affirmed(
        r"\b(write|insert|persist|record|enqueue|create|add|use)\b.{0,200}"
        r"(transactional outbox|outbox row|database job|db job|publication intent|pending status)"
        r"|\b(poll|scan|reconcile)\b.{0,180}(accepted order|database|orders table)",
        low,
    ) and has(
        r"(same|one|order).{0,100}(database )?transaction"
        r"|(database )?transaction.{0,140}(outbox|job|publication intent|accepted order|pending)",
        low,
    )
    publication_recovery = affirmed(
        r"\b(retry|republish|publish|relay|poll|scan|reconcile|recover)\b.{0,180}"
        r"(unsent|unpublished|pending|accepted|publication|outbox|job)",
        low,
    )
    if not (persisted_intent and publication_recovery):
        errors.append(
            "does not make publication intent transactionally durable and recoverably publish pending work"
        )

    durable_claim = affirmed(
        r"\b(replace|use|adopt|move|claim)\b.{0,180}"
        r"(durable claim|claim/ack|claim.{0,50}ack|consumer group|pending.{0,50}ack|processing.{0,50}ack)"
        r"|\b(ack|complete)\b.{0,100}(only|after).{0,100}(durable|terminal|record|work)",
        low,
    )
    recovery = affirmed(
        r"\b(reclaim|redeliver|recover|requeue|xautoclaim|reap)\w*\b.{0,160}"
        r"(pending|claim|work|job|entry|lease|failure|worker)"
        r"|\b(reaper|pending-entry list)\b",
        low,
    )
    if not (durable_claim and recovery):
        errors.append("does not specify durable claim/ack semantics with pending-work recovery")

    chooses_lease = affirmed(r"\b(use|add|adopt|set|renew|expire)\b.{0,100}\blease\b", low)
    if chooses_lease:
        lease_safety = has(r"expir|reclaim|redeliver|reaper", low) and has(
            r"fenc|owner.?token|claim.?token|stale (owner|worker)", low
        )
        if not lease_safety:
            errors.append("chooses leases without expiry recovery and stale-owner fencing")

    ambiguity = affirmed(
        r"\b(use|pass|persist|add|deduplicate|dedupe)\b.{0,160}"
        r"(idempotency key|idempotent charge|payment dedup|deduplication)"
        r"|\b(idempotency key)\b.{0,100}(payment|charge|provider)",
        low,
    ) and has(
        r"(succeed|charged|effect).{0,120}(before|then).{0,100}(crash|ack|database|record)"
        r"|(death|die|dies|killed|crash).{0,120}(after).{0,60}(charge|payment).{0,120}(before).{0,80}(update|record|commit)"
        r"|(after).{0,60}(charge|payment).{0,120}(before).{0,80}(update|record|commit).{0,100}(death|die|killed|crash|retry|redeliver)"
        r"|(payment|provider).{0,80}(accept|commit|charge).{0,100}(worker ).{0,20}(die|dies|crash).{0,80}(before|during).{0,80}(update|record|commit)"
        r"|ambiguous.{0,100}(charge|external|effect)",
        low,
    )
    if not ambiguity:
        errors.append("does not handle charge-success/crash ambiguity with a stable idempotency key or dedupe")

    fault_tests = affirmed(
        r"\b(add|write|run|inject|test)\b.{0,180}(fault|kill|crash).{0,160}"
        r"(before|after|point|boundary|instruction|claim|charge|complete|ack|publish)"
        r"|\b(add|write|run|inject|test)\b.{0,180}"
        r"(before|after).{0,100}(claim|charge|complete|ack|publish|transaction)",
        low,
    ) and affirmed(
        r"\b(add|write|run|inject|test|assert|prove)\b.{0,180}"
        r"(concurr|two workers|redeliver|recover|reclaim|stale worker|expiry|lease)",
        low,
    )
    if not fault_tests:
        errors.append("does not add crash-window plus recovery/concurrent-worker fault tests")

    if affirmed(r"\b(guarantee|achieve|provide)\b.{0,50}exactly.?once", low):
        errors.append("promises exactly-once effects across independent systems")
    if affirmed_predicate_after(
        r"redis (multi|transaction)", r"\b(atomic|atomically|same transaction)\b", low
    ):
        errors.append("claims a Redis transaction can atomically cover the database")
    if affirmed_predicate_after(
        r"\b(retry|try/except|requeue)\b", r"\b(enough|sufficient|fully solve|guarantee)\w*\b", low
    ):
        errors.append("treats retry/requeue alone as a durability protocol")
    if affirmed_predicate_after(r"\blpop\b", r"\b(safe|fine|correct)\b", low):
        errors.append("accepts destructive early acknowledgement as safe")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
