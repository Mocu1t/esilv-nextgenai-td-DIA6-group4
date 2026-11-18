#!/usr/bin/env python3
"""TD 2 and TD 3: read the decisions of a routing rule, then adapt it to your own.

Synthetic resources, no API call, no key.

Adapted by sub-group DIA6 - Group 4 (Pair C, TD 2) to its routing rule
(reports/td2/routing-rule.md), with coding assistance declared in prompts-en.md.
The output of the supplied version is kept in reports/td2/simulator-before.jsonl.

Resources are the five TD 1 models and the paid route of the same model as the
F2 champion. A model is eligible on a family only if it was correct on every
evaluated TD 1 cell of that family (model-question-comparison-en.csv); the
cells are quoted in every reason. Costs are USD excluding tax per request, for
the fixed envelope of modeles-autorises.json: 2000 input and 1024 output tokens.
Quota availability is supplied as a scenario, not measured from a provider.
"""
import argparse
import json

ENVELOPE_TOKENS = (2000, 1024)  # input, output: budget_entree_tokens_estime, sortie_max_tokens_raisonnement_compris


def per_request(input_usd_per_million, output_usd_per_million):
    tokens_in, tokens_out = ENVELOPE_TOKENS
    return round((tokens_in * input_usd_per_million + tokens_out * output_usd_per_million) / 1e6, 6)


FAMILIES = {
    "F1": "period",
    "F2": "age on a reference date",
    "F2b": "age at the time of the order",
    "F3": "product list",
    "F4": "combinations",
}
# Families where TD 1 errors were plausible wrong values shared by several models,
# and where quorums were wrong together (C02 under 3-of-5, C09 under 2-of-3).
AGE_FAMILIES = {"F2", "F2b", "F4"}

# families: TD 1 evidence of 100 % on the evaluated cells. paid_fallback_usd: price per request of the
# paid route of the same model (tie-break between free routes), None when no paid route is documented.
RESOURCES = [
    {"id": "groq:openai/gpt-oss-20b", "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "paid_fallback_usd": per_request(0.10, 0.50),
     "families": {"F1": "6/6 (C01, C04, C05, C06, C07, C20)", "F2b": "1/1 (C10)",
                  "F3": "4/4 (C03, C12, C13, C14)", "F4": "5/5 (C15, C16, C17, C18, C19)"}},
    {"id": "groq:openai/gpt-oss-120b", "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "paid_fallback_usd": per_request(0.15, 0.60),
     "families": {"F1": "6/6 (C01, C04, C05, C06, C07, C20)", "F2": "4/4 (C02, C08, C09, C11)",
                  "F2b": "1/1 (C10)", "F3": "4/4 (C03, C12, C13, C14)"}},
    {"id": "groq:qwen/qwen3.8-27b", "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
     "paid_fallback_usd": per_request(0.04, 1.35),
     "families": {"F1": "5/5 (C01, C04, C05, C06, C07; C20 not run, HTTP 429 twice)", "F2b": "1/1 (C10)",
                  "F3": "4/4 (C03, C12, C13, C14)"}},
    {"id": "openrouter:cohere/north-mini-code:free", "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "paid_fallback_usd": None,
     "families": {"F1": "6/6 (C01, C04, C05, C06, C07, C20)", "F3": "4/4 (C03, C12, C13, C14)"}},
    {"id": "openrouter:dots-studio/dots-3-note-preview:free", "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None, "paid_fallback_usd": None,
     "families": {"F2b": "1/1 (C10)", "F3": "4/4 (C03, C12, C13, C14)"}},
    # Same model as groq:openai/gpt-oss-120b, hence the same TD 1 evidence; billed per token.
    {"id": "openrouter:openai/gpt-oss-120b", "access": "tokens", "available": True,
     "cash": per_request(0.15, 0.60), "allocation": per_request(0.15, 0.60), "reset_minutes": None,
     "paid_fallback_usd": per_request(0.15, 0.60),
     "families": {"F1": "6/6 (C01, C04, C05, C06, C07, C20), same model on Groq",
                  "F2": "4/4 (C02, C08, C09, C11), same model on Groq",
                  "F2b": "1/1 (C10), same model on Groq", "F3": "4/4 (C03, C12, C13, C14), same model on Groq"}},
]


def checks_for(request):
    """The check depends on the risk of a silent wrong value and on the use, not on the bare rate."""
    family, use = request["family"], request["use"]
    if use == "payout":
        return "deterministic check (script#script: validated reference SQL, 20/20 vs answer key) + human review"
    if family in AGE_FAMILIES:
        return ("deterministic check (script#script): age errors are plausible shared values that quorums "
                "accepted in TD 1 (C02 wrong under 3-of-5, C09 wrong under 2-of-3)")
    if use == "customer":
        return "2-of-3 quorum of distinct families"
    return ("none: first model 100 % on the family; the only TD 1 error on F1/F3 (E/C07) is invalid SQL, "
            "rejected by the sandbox, never a silent value")


def route_reason(resource, family, why):
    return f"{why}: {resource['id']} {resource['families'][family]} on {family} {FAMILIES[family]}"


def choose(request, resources):
    """A deterministic routing policy, with a reason the user can inspect.

    Same priority order as the supplied policy: already paid (or free) capacity
    before new spending; a nonurgent request can wait for it. Eligibility is no
    longer a capability level but the TD 1 evidence per family. At wake-up,
    availability must be measured again: reaching a reset time does not prove
    that capacity is available.
    """
    family = request["family"]
    checks = checks_for(request) if family in FAMILIES else "none possible"
    if family not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
                "reason": f"no TD 1 evidence for family {family!r}: no model is known to be correct on it"}
    eligible = [r for r in resources if family in r["families"]]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        # Tie-break between free routes: the cheapest paid route of the same model; undocumented price last.
        chosen = min(included, key=lambda r: (r["allocation"], r["paid_fallback_usd"] is None,
                                              r["paid_fallback_usd"] or 0, r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": route_reason(chosen, family, "cheapest eligible free route")}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": route_reason(chosen, family, "free route exhausted, refill before the deadline; "
                                       "recheck availability at wake-up"),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": route_reason(chosen, family, "no eligible free route in time; paid route within budget")}
    proven = "; ".join(f"{r['id']} {r['families'][family]}" for r in eligible) or "none"
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no route with 100 % on {family} {FAMILIES[family]} within deadline and budget "
                      f"(eligible: {proven}); no fallback to a model that erred on this family"}


def unavailable(resources, resource_id, reset_minutes):
    return [dict(r, available=False, reset_minutes=reset_minutes) if r["id"] == resource_id else dict(r)
            for r in resources]


def scenarios():
    base = {"family": "F1", "use": "dashboard", "can_wait": True, "deadline_minutes": 120, "budget": 0.30}
    # TD 1, operator D: Groq answered HTTP 429 per model and per minute; the refill is modelled at one minute.
    f2_exhausted = unavailable(RESOURCES, "groq:openai/gpt-oss-120b", 1)
    f1_down = unavailable(RESOURCES, "groq:openai/gpt-oss-20b", None)
    return [
        ("simple", base, RESOURCES),
        ("provider unavailable", {**base, "can_wait": False}, f1_down),
        ("complex", {**base, "family": "F4", "use": "customer"}, RESOURCES),
        ("deferrable", {**base, "family": "F2"}, f2_exhausted),
        ("urgent", {**base, "family": "F2", "can_wait": False, "deadline_minutes": 0}, f2_exhausted),
        ("budget exhausted", {**base, "family": "F2", "can_wait": False, "deadline_minutes": 0, "budget": 0},
         f2_exhausted),
        ("high impact", {**base, "family": "F3", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F5 revenue per customer segment"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
