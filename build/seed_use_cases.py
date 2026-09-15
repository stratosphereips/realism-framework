"""Assemble data/use_cases.json from the source repo's use-case requirements.

Dimension-level profiles are NOT transcribed by hand. They are derived from the
sub-dimension requirements in the source repo's data/use_case_requirements.json,
by taking the strongest level required by any sub-dimension of that dimension
(C > U > -). This is the same aggregation rule the source analysis uses, so the
two repositories cannot drift apart in the way a hand-copied table can.

Only the site-specific prose (short description and long detail for the use-case
pages) is defined here, because it has no counterpart in the source data.

Usage:
    python build/seed_use_cases.py <path to use_case_requirements.json> data/use_cases.json
"""
import json
import sys
import os

DIMS = [f"D{i}" for i in range(1, 12)]
RANK = {"C": 2, "U": 1, "-": 0}
LEVEL = {2: "C", 1: "U", 0: "-"}

DESCRIPTIONS = {
    "UC-A1": "Locate sensitive data and move it out of the network covertly, against monitoring and baselines.",
    "UC-A2": "Deploy ransomware across hosts: propagation, encryption, and impact.",
    "UC-A3": "Self-propagating spread across a network from an initial foothold.",
    "UC-A5": "Escalate from a low-privilege account to higher privileges using credential and OS mechanics.",
    "UC-A6": "Conduct a stealthy, operationally-secure campaign that blends into realistic activity.",
    "UC-D1": "Triage security alerts, separating malicious activity from benign noise.",
    "UC-D2": "Respond to and contain an active incident.",
    "UC-D3": "Proactively hunt for threats across hosts and telemetry.",
    "UC-S1": "Simulate interacting attacker and defender agents.",
    "UC-S2": "Compare configurations and policies for time-to-compromise and weakest paths.",
}

# Longer descriptions for the use-case pages, grounded in the methodology's use-case
# definitions table (Description + Realistic goal + ATT&CK archetype).
DETAILS = {
    "UC-A1": "An attacker who already holds a foothold must locate specific high-value data somewhere in the network and move it out without being detected. This is the state-espionage pattern (APT29, Turla; SolarWinds, Operation Ghost): the aim is not to compromise as many hosts as possible but to reach a particular dataset, exfiltrate it over a channel that blends with normal traffic, and preserve access for future tasking. Success is judged by whether the target data leaves the network while the operation's footprint stays below the defender's detection threshold, which is why the objective depends on realistic monitoring, baselines, and benign traffic to hide within.",
    "UC-A2": "An attacker must escalate to domain-level control and deploy ransomware across business-critical systems within a short window, before incident response can react. This is the ransomware pattern (Wizard Spider, Scattered Spider): data is typically exfiltrated first for double extortion, then encryption is pushed as widely as possible across critical hosts over a hours-to-days campaign. The evaluation measures how widely and how quickly critical hosts are encrypted before the defender can contain the incident, so it exercises privilege escalation, lateral movement, and destructive impact under time pressure.",
    "UC-A3": "This models the autonomous spread of worm-like malware through a network from an initial foothold, in the destructive NotPetya lineage (Sandworm; the Ukraine campaigns). Here, unusually, compromising as many hosts as possible is itself the real objective, and the outcome is governed mainly by network structure and patch state rather than by stealth or credential nuance. Because topology and reachability dominate, it is one of the few objectives an abstract simulator with a realistic network graph can support meaningfully.",
    "UC-A5": "Starting from an initial foothold, the attacker escalates to domain admin by stealing credentials and moving laterally through Active Directory trust relationships. This is the financial/ransomware-operator pattern: the realistic goal is to reach the target privilege level by the shortest and quietest path through the identity layer: Kerberos and NTLM exchanges, session tokens, group memberships, and misconfigured ACLs. It is demanding on service, operating-system, identity, action, and observation fidelity, which is why real-software environments support it well while abstract simulators do not.",
    "UC-A6": "An attacker must accomplish an objective while actively evading a blue team. The archetype is pre-positioning (Volt Typhoon, KV Botnet), where an actor quietly establishes and holds long-term access ahead of a future operation rather than striking immediately. The defining constraint is operational security: the attacker relies on living-off-the-land techniques, avoids deploying detectable malware, and blends with legitimate administrative activity. Because blending in is only meaningful when there is realistic activity to blend with and realistic detection to evade, this is the most demanding objective; it exercises nearly every realism dimension at once.",
    "UC-D1": "A defender processes a stream of alerts and must separate true positives from false positives under realistic base rates. This is the counterpart to every attacker archetype, and it depends squarely on benign activity: there is nothing to triage unless malicious events sit within a noisy baseline of normal logins, administration, and traffic. Performance is measured by true-positive rate within a service-level window, mean time to detect, and the cost of examining alerts under sustained volume, none of which is testable against a clean, attack-only signal.",
    "UC-D2": "A defender detects an active compromise and must contain it while preserving forensic evidence and business continuity. It is the counterpart to the time-critical ransomware and evidence-sensitive espionage patterns: the realistic goal is to confine the attacker to a bounded set of hosts, keep the artifacts needed for investigation, and minimize disruption, often coordinating across teams. This exercises defensive controls, telemetry, and a response action space with real propagation delays and side effects, rather than an instantaneous “contain” button.",
    "UC-D3": "A defender proactively searches for pre-positioned or espionage actors that have not raised an alert, in the Volt Typhoon / APT29 mold. The task is hypothesis-driven log analysis over a long horizon: find previously undetected presence and, critically, distinguish an attacker's living-off-the-land activity from legitimate administration. It is one of the most demanding defender objectives because it needs both realistic benign activity and temporal dynamics spanning days to weeks; this is the combination current IT-enterprise environments most lack.",
    "UC-S1": "A system-level objective in which attacker and defender agents operate simultaneously and adapt to each other, as in purple-teaming and real engagements where both sides learn. The question is whether the defender can detect and contain the attacker, and how strategies co-evolve over repeated interaction. It requires a credible two-sided environment (both a real attacker action space and a real defender action-and-observation space), which is why environments that model only one side cannot support it.",
    "UC-S2": "A system-level objective that asks whether a given network configuration is robust against automated attack, rather than how a particular agent performs. By running attacks across different topologies and policies and comparing the outcomes, one measures time-to-compromise under each configuration and identifies the weakest paths an attacker would take. Because the question is about the structure (segmentation, reachability, and policy), topology and observation are the dominant dimensions, and an abstract simulator with a faithful network model can produce valid comparisons here even without real-software fidelity. It is the system-level analogue of worm-spread analysis (UC-A3).",
}


def derive_profile(requirements):
    """Dimension level = the strongest level required by any of its sub-dimensions."""
    profile = {}
    for d in DIMS:
        levels = [lvl for key, lvl in requirements.items() if key.split(".")[0] == d]
        if not levels:
            raise ValueError(f"no sub-dimensions found for {d}")
        profile[d] = LEVEL[max(RANK[lvl] for lvl in levels)]
    return profile


def main(seed_reqs_path, out_path):
    src = json.load(open(seed_reqs_path))
    src_ucs = src["use_cases"]

    missing = sorted(set(DESCRIPTIONS) - set(src_ucs))
    if missing:
        raise SystemExit(f"source data has no entry for: {', '.join(missing)}")

    previous = {}
    if os.path.exists(out_path):
        previous = json.load(open(out_path)).get("use_cases", {})

    use_cases = {}
    changes = []
    for uc in DESCRIPTIONS:
        reqs = src_ucs[uc]["requirements"]
        if len(reqs) != 115:
            raise SystemExit(f"{uc}: expected 115 sub-dimension keys, found {len(reqs)}")
        profile = derive_profile(reqs)

        old = previous.get(uc, {})
        if old.get("name") and old["name"] != src_ucs[uc]["name"]:
            changes.append(f"{uc} name: {old['name']!r} -> {src_ucs[uc]['name']!r}")
        for d in DIMS:
            if old.get("profile", {}).get(d, profile[d]) != profile[d]:
                changes.append(f"{uc} {d}: {old['profile'][d]} -> {profile[d]}")
        if old and not old.get("requirements"):
            changes.append(f"{uc}: sub-dimension requirements added ({len(reqs)} keys)")

        use_cases[uc] = {
            "name": src_ucs[uc]["name"],
            "description": DESCRIPTIONS[uc],
            "detail": DETAILS[uc],
            "profile": profile,
            "requirements": reqs,
        }

    out = {
        "meta": {
            "levels": ["C", "U", "-"],
            "dimensions": DIMS,
            "source": ("data/use_case_requirements.json in the source repo; dimension-level "
                       "profiles derived from the sub-dimension requirements by taking the "
                       "strongest level required in each dimension"),
        },
        "use_cases": use_cases,
    }
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)

    print(f"wrote {out_path}: {len(use_cases)} use cases, all with 115 sub-dimension requirements")
    if changes:
        print(f"\n{len(changes)} change(s) against the previous file:")
        for c in changes:
            print(f"  {c}")
    elif previous:
        print("no changes against the previous file")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
