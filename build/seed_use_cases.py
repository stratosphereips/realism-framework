"""One-off: assemble data/use_cases.json from the transcribed methodology
use-case->dimension mapping (Critical/Useful/Not-needed) plus UC-A1's
element-level requirements copied verbatim from the source repo.

Profiles are transcribed from notes/src/realism_dimensions_methodology.md,
section "Use case to dimension mapping" (C=critical, U=useful, -=not needed),
in canonical dimension order D1..D11.
"""
import json
import sys

DIMS = [f"D{i}" for i in range(1, 12)]

NAMES = {
    "UC-A1": "Targeted data exfiltration",
    "UC-A2": "Ransomware deployment",
    "UC-A3": "Worm / self-propagation",
    "UC-A5": "Credential-based privilege escalation",
    "UC-A6": "Evasive red-team operation",
    "UC-D1": "Alert triage",
    "UC-D2": "Incident response",
    "UC-D3": "Threat hunting",
    "UC-S1": "Attacker-defender simulation",
    "UC-S2": "Security architecture evaluation",
}

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
    "UC-A1": "An attacker who already holds a foothold must locate specific high-value data somewhere in the network and move it out without being detected. This is the state-espionage pattern (APT29, Turla; SolarWinds, Operation Ghost): the aim is not to compromise as many hosts as possible but to reach a particular dataset, exfiltrate it over a channel that blends with normal traffic, and preserve access for future tasking. Success is judged by whether the target data leaves the network while the operation's footprint stays below the defender's detection threshold — which is why the objective depends on realistic monitoring, baselines, and benign traffic to hide within.",
    "UC-A2": "An attacker must escalate to domain-level control and deploy ransomware across business-critical systems within a short window, before incident response can react. This is the ransomware pattern (Wizard Spider, Scattered Spider): data is typically exfiltrated first for double extortion, then encryption is pushed as widely as possible across critical hosts over a hours-to-days campaign. The evaluation turns on encryption coverage and speed against the defender's containment, so it exercises privilege escalation, lateral movement, and destructive impact under time pressure.",
    "UC-A3": "This models the autonomous spread of worm-like malware through a network from an initial foothold, in the destructive NotPetya lineage (Sandworm; the Ukraine campaigns). Here — unusually — compromising as many hosts as possible is itself the real objective, and the outcome is governed mainly by network structure and patch state rather than by stealth or credential nuance. Because topology and reachability dominate, it is one of the few objectives an abstract simulator with a realistic network graph can support meaningfully.",
    "UC-A5": "Starting from an initial foothold, the attacker escalates to domain admin by stealing credentials and moving laterally through Active Directory trust relationships. This is the financial/ransomware-operator pattern: the realistic goal is to reach the target privilege level by the shortest and quietest path through the identity fabric — Kerberos and NTLM exchanges, session tokens, group memberships, and misconfigured ACLs. It is demanding on service, operating-system, identity, action, and observation fidelity, which is why real-software environments support it well while abstract simulators do not.",
    "UC-A6": "An attacker must accomplish an objective while actively evading a blue team, in the pre-positioning lineage (Volt Typhoon, KV Botnet). The defining constraint is operational security: the operator relies on living-off-the-land techniques, avoids deploying detectable malware, and blends with legitimate administrative activity. Because blending in is only meaningful when there is realistic activity to blend with and realistic detection to evade, this is the most demanding objective — it exercises nearly every realism dimension at once.",
    "UC-D1": "A defender processes a stream of alerts and must separate true positives from false positives under realistic base rates. This is the counterpart to every attacker archetype, and it depends squarely on benign activity: the analyst's task only exists when malicious events are embedded in a noisy baseline of normal logins, administration, and traffic. Performance is measured by true-positive rate within a service-level window, mean time to detect, and the management of analyst fatigue and false-positive cost — none of which is testable against a clean, attack-only signal.",
    "UC-D2": "A defender detects an active compromise and must contain it while preserving forensic evidence and business continuity. It is the counterpart to the time-critical ransomware and evidence-sensitive espionage patterns: the realistic goal is to confine the attacker to a bounded set of hosts, keep the artifacts needed for investigation, and minimize disruption, often coordinating across teams. This exercises defensive controls, telemetry, and a response action space with real propagation delays and side effects, rather than an instantaneous “contain” button.",
    "UC-D3": "A defender proactively searches for pre-positioned or espionage actors that have not raised an alert, in the Volt Typhoon / APT29 mold. The task is hypothesis-driven log analysis over a long horizon: find previously undetected presence and, critically, distinguish an attacker's living-off-the-land activity from legitimate administration. It is one of the most demanding defender objectives because it needs both realistic benign activity and temporal dynamics spanning days to weeks — the combination current IT-enterprise environments most lack.",
    "UC-S1": "A system-level objective in which attacker and defender agents operate simultaneously and adapt to each other, as in purple-teaming and real engagements where both sides learn. The question is whether the defender can detect and contain the attacker, and how strategies co-evolve over repeated interaction. It requires a credible two-sided environment — both a real attacker action space and a real defender action-and-observation space — which is why environments that model only one side cannot support it.",
    "UC-S2": "A system-level objective that asks whether a given network configuration is robust against automated attack, rather than how a particular agent performs. By running attacks across different topologies and policies and comparing the outcomes, one measures time-to-compromise under each configuration and identifies the weakest paths an attacker would take. Because the question is about the structure — segmentation, reachability, and policy — topology and observation are the dominant dimensions, and an abstract simulator with a faithful network model can produce valid comparisons here even without real-software fidelity. It is the system-level analogue of worm-spread analysis (UC-A3).",
}

# Level lists in canonical dimension order D1..D11:
# Topological, Service, OS, Identity, Temporal, Defensive, Benign, Telemetry,
# Action, Observation, External.
PROFILES = {
    "UC-A1": ["C", "C", "U", "U", "C", "C", "C", "C", "U", "U", "C"],
    "UC-A2": ["C", "U", "C", "U", "U", "U", "-", "-", "C", "C", "-"],
    "UC-A3": ["C", "U", "U", "-", "C", "U", "-", "-", "U", "C", "-"],
    "UC-A5": ["U", "C", "C", "C", "U", "-", "-", "-", "C", "C", "-"],
    "UC-A6": ["C", "C", "C", "C", "C", "C", "C", "U", "C", "C", "U"],
    "UC-D1": ["U", "-", "-", "U", "C", "C", "C", "C", "-", "C", "-"],
    "UC-D2": ["C", "U", "U", "C", "C", "C", "C", "C", "-", "C", "-"],
    "UC-D3": ["U", "U", "U", "C", "C", "C", "C", "C", "-", "C", "U"],
    "UC-S1": ["C", "U", "U", "C", "C", "C", "C", "C", "U", "C", "-"],
    "UC-S2": ["C", "U", "U", "U", "U", "U", "-", "-", "U", "C", "-"],
}


def main(seed_reqs_path, out_path):
    src = json.load(open(seed_reqs_path))
    uc_a1_reqs = src["use_cases"]["UC-A1"]["requirements"]
    use_cases = {}
    for uc, levels in PROFILES.items():
        entry = {"name": NAMES[uc], "description": DESCRIPTIONS[uc],
                 "detail": DETAILS[uc], "profile": dict(zip(DIMS, levels))}
        if uc == "UC-A1":
            entry["requirements"] = uc_a1_reqs
        use_cases[uc] = entry
    out = {
        "meta": {"levels": ["C", "U", "-"], "dimensions": DIMS,
                 "source": "notes/src/realism_dimensions_methodology.md use-case->dimension mapping"},
        "use_cases": use_cases,
    }
    json.dump(out, open(out_path, "w"), indent=2)
    print(f"wrote {out_path}: {len(use_cases)} use cases; UC-A1 element reqs={len(uc_a1_reqs)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
