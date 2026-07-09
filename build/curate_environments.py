"""One-off: add curated summaries and primary sources to environments.json.
Summaries are qualitative (the scored tables and radars carry the F/P/A/U counts).
Justifications are left for the well-developed environments to fill over time.
Sources are added only where the primary reference URL is known with confidence.
"""
import json
import sys

SUMMARIES = {
    "yawning-titan": "DSTL's abstract graph-based autonomous-cyber-defence simulator: a scripted red agent spreads across a network graph while a learning blue agent isolates, restores, hardens, and places deceptive nodes under probabilistic detection. It abstracts services, OS, identity, benign activity, and telemetry.",
    "primaite": "The higher-fidelity DSTL/ARCD successor to Yawning-Titan: it models topology with routing and ACLs, protocol-aware services, a simulated filesystem and user accounts, green pattern-of-life, and packet-capture telemetry. The broadest-coverage environment here, yet full on no dimension because every subsystem is simulated rather than real software.",
    "cyberbattlesim": "Microsoft's abstract network-graph simulator for autonomous red-agent RL; models topology and the action/observation interface but abstracts services, OS, identity, and the defensive/telemetry context.",
    "nasim": "A lightweight abstract network attack simulator for RL pentesting; scenario-driven topology and actions with abstracted services and little defender context.",
    "cage-2": "The CAGE-2 autonomous-defence scenario (built on CybORG); an abstract host/service model with a single discovery-only 'green' agent providing minimal benign activity.",
    "farland": "A red-agent simulator emphasising large, procedurally-varied networks; abstracts service and OS fidelity and the defender/telemetry context.",
    "netsecgame": "A configurable network-security game for attacker RL with a built-in stochastic defender; abstract topology and actions.",
    "cybershield": "A defence-oriented simulation; several dimensions are undocumented and scored Unknown from the available sources.",
    "cye": "Attack-path / exposure analysis over a modelled enterprise identity and topology; broad partial coverage, with a few dimensions Unknown.",
    "nasimemu": "NASim's emulator counterpart: the same scenarios backed by real services, raising service and OS fidelity above the pure simulator.",
    "cygil": "A CyberGym-style RL environment; most dimensions are Unknown from the available documentation.",
    "cyberwheel": "A defender-training simulation with decoys and deception and a modelled benign/telemetry layer; broad partial coverage.",
    "pengym": "A Gym environment backed by real vulnerable services behind a NASim-compatible interface; strong service, OS, action, and observation fidelity.",
    "caldera": "MITRE CALDERA, an adversary-emulation platform executing real ATT&CK techniques on real hosts; strong real-software fidelity with partial context.",
    "goad": "Game of Active Directory, an emulated multi-domain AD lab on real Windows Server VMs; strong service, OS, identity, action, and observation fidelity, but absent temporal, defensive, benign, telemetry, and external context.",
    "scorpion": "A cyber-exercise / range platform; most dimensions are Unknown from the available sources.",
    "htb": "Hack The Box-style vulnerable-machine challenges on real hosts; strong real-software fidelity with little organizational or defender context.",
    "cage-4": "The CybORG CAGE-4 scenario: a larger multi-subnet enterprise with decentralised blue agents, richer green (benign) agents, mission phases, and variable action durations; among the most context-complete abstract simulators.",
}

# Proposed family classification (REVIEW THIS). Drives the "two families" framing.
FAMILY = {
    "yawning-titan": "Abstract simulator", "primaite": "Abstract simulator",
    "goad": "Real-software emulator", "pengym": "Real-software emulator",
    "htb": "Real-software emulator", "caldera": "Real-software emulator",
    "nasimemu": "Real-software emulator",
    "cyberbattlesim": "Abstract simulator", "nasim": "Abstract simulator",
    "cage-2": "Abstract simulator", "cage-4": "Abstract simulator",
    "netsecgame": "Abstract simulator", "farland": "Abstract simulator",
    "cyberwheel": "Abstract simulator", "cygil": "Abstract simulator",
    "cye": "Abstract simulator", "cybershield": "Abstract simulator",
    "scorpion": "Cyber range / other",
}

# Per-environment caveats rendered as a note on the environment page.
NOTES = {
    "yawning-titan": "Yawning-Titan was archived read-only in March 2025 and superseded by the higher-fidelity PrimAITE under DSTL's Autonomous Resilient Cyber Defence programme. The scores reflect the released version.",
    "primaite": "PrimAITE reaches partial on ten of the eleven dimensions but full on none: it models each subsystem in interface rather than as real software, illustrating breadth of coverage without the depth a real-software layer provides.",
    "caldera": "CALDERA's Observation dimension is scored Absent not because it lacks observation, but because it provides a single, complete report of all facts and outcomes (oracle-like visibility) rather than the partial, noisy, privilege-dependent perception this framework calls observation realism. That is why a tool with the catalogue's highest action realism still meets no objective's observation requirement.",
    "nasimemu": "NASimEmu is both a simulator and an emulator over the same scenarios. The scores here reflect its emulation mode, in which actions run against real services; this is what lifts its OS, action, and observation fidelity above the pure NASim simulator. Run in its simulation mode, it would score like the abstract-simulator family.",
}

SOURCES = {
    "yawning-titan": [{"label": "GitHub (archived)", "url": "https://github.com/dstl/YAWNING-TITAN"}],
    "primaite": [{"label": "GitHub", "url": "https://github.com/Autonomous-Resilient-Cyber-Defence/PrimAITE"}],
    "cyberbattlesim": [{"label": "GitHub", "url": "https://github.com/microsoft/CyberBattleSim"}],
    "nasim": [{"label": "GitHub", "url": "https://github.com/Jjschwartz/NetworkAttackSimulator"}],
    "cage-2": [{"label": "CAGE Challenge 2", "url": "https://github.com/cage-challenge/cage-challenge-2"}],
    "netsecgame": [{"label": "GitHub", "url": "https://github.com/stratosphereips/NetSecGame"}],
    "nasimemu": [{"label": "GitHub", "url": "https://github.com/jaromiru/NASimEmu"}],
    "caldera": [{"label": "GitHub", "url": "https://github.com/mitre/caldera"}],
    "goad": [{"label": "GitHub", "url": "https://github.com/Orange-Cyberdefense/GOAD"}],
    "cage-4": [{"label": "CAGE Challenge 4", "url": "https://github.com/cage-challenge/cage-challenge-4"}],
    "htb": [{"label": "Hack The Box", "url": "https://www.hackthebox.com/"}],
    "pengym": [{"label": "GitHub", "url": "https://github.com/cyb3rlab/PenGym"}],
    "cyberwheel": [{"label": "GitHub", "url": "https://github.com/ORNL/cyberwheel"}],
}


def main(path):
    data = json.load(open(path))
    envs = data["environments"]
    for slug, env in envs.items():
        if slug in SUMMARIES:
            env["summary"] = SUMMARIES[slug]
        if slug in SOURCES:
            env["sources"] = SOURCES[slug]
        if slug in FAMILY:
            env["family"] = FAMILY[slug]
        if slug in NOTES:
            env["note"] = NOTES[slug]
    json.dump(data, open(path, "w"), indent=2)
    missing = [s for s in envs if not envs[s]["summary"]]
    print(f"curated {len(envs)} envs; summaries set for {len(envs) - len(missing)}; "
          f"sources for {sum(1 for e in envs.values() if e['sources'])}")
    if missing:
        print("MISSING SUMMARY:", missing)


if __name__ == "__main__":
    main(sys.argv[1])
