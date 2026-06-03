"""Deploy CPE Fleet Ops agent to Vertex AI Agent Engine.

Agent Engine serializes agents via cloudpickle. File-based skills
(load_skill_from_dir) reference local paths that don't exist in the
Agent Engine runtime. This script builds the agent with ALL skills
inlined so the pickled artifact is self-contained.
"""

import vertexai
from vertexai import agent_engines

vertexai.init(
    project="mygenerativeai",
    location="us-central1",
    staging_bucket="gs://mygenerativeai-agent-staging",
)

# ── Build a self-contained agent (no file references) ────────────────────

from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset

# ── All skills inlined ──────────────────────────────────────────────────

chrome_policy_quick_ref = models.Skill(
    frontmatter=models.Frontmatter(
        name="chrome-policy-quick-ref",
        description=(
            "Quick reference for the most common Chrome Enterprise and ChromeOS"
            " policies. Covers enrollment, security, extension management,"
            " network, and user experience policies with values and scopes."
        ),
    ),
    instructions=(
        "When asked about Chrome Enterprise policies, reference this catalog:\n\n"
        "## Enrollment Policies\n"
        "- DeviceEnrollmentMode: forced | optional | disabled\n"
        "- ForceReenrollment: true | false\n"
        "- DeviceBlockDevmode: true | false\n"
        "- AutoEnrollmentProtocol: FRE | initial\n\n"
        "## Security Policies\n"
        "- PasswordManagerEnabled: true | false\n"
        "- BrowserSignin: 0 (disabled) | 1 (enabled) | 2 (forced)\n"
        "- DeveloperToolsAvailability: 0 (always) | 1 (extensions only) | 2 (disabled)\n"
        "- IncognitoModeAvailability: 0 (available) | 1 (disabled) | 2 (forced)\n"
        "- SafeBrowsingProtectionLevel: 0 (off) | 1 (standard) | 2 (enhanced)\n\n"
        "## Extension Policies\n"
        "- ExtensionInstallBlocklist: list of IDs or '*'\n"
        "- ExtensionInstallAllowlist: list of IDs\n"
        "- ExtensionInstallForcelist: list of extension_id;update_url\n"
        "- ExtensionSettings: JSON per-extension config\n\n"
        "## DLP\n"
        "- PrintingEnabled: true | false\n"
        "- ScreenCaptureAllowed: true | false\n"
        "- ExternalStorageDisabled: true | false\n"
        "- DataLeakPreventionRulesList: DLP rule JSON\n\n"
        "## Network\n"
        "- ProxyMode: direct | auto_detect | pac_script | fixed_servers\n"
        "- DnsOverHttpsMode: off | automatic | secure\n\n"
        "Scope: User-level (follows user) vs Device-level (affects all users).\n"
        "Policies at child OUs override parent OUs.\n"
    ),
)

chrome_policy_reference = models.Skill(
    frontmatter=models.Frontmatter(
        name="chrome-policy-reference",
        description=(
            "Comprehensive Chrome Enterprise policy reference with 50+ policies"
            " organized by category with values, scopes, and platform support."
        ),
    ),
    instructions=(
        "Full Chrome Enterprise policy catalog:\n\n"
        "## Enrollment: DeviceEnrollmentMode (enum), ForceReenrollment (bool), "
        "DeviceBlockDevmode (bool), ChromeDeviceAutoUpdatePolicy (enum), DeviceGuestModeEnabled (bool)\n\n"
        "## Security: BrowserSignin (int 0-2), SafeBrowsingProtectionLevel (int 0-2), "
        "PasswordManagerEnabled (bool), IncognitoModeAvailability (int 0-2), "
        "DeveloperToolsAvailability (int 0-2)\n\n"
        "## Extensions: ExtensionInstallBlocklist (list), ExtensionInstallAllowlist (list), "
        "ExtensionInstallForcelist (list), ExtensionSettings (JSON), BlockExternalExtensions (bool)\n\n"
        "## DLP: PrintingEnabled (bool), ScreenCaptureAllowed (bool), ExternalStorageDisabled (bool-device), "
        "DataLeakPreventionRulesList (JSON), DownloadRestrictions (int 0-4), SyncDisabled (bool)\n\n"
        "## Network: ProxyMode (enum), DnsOverHttpsMode (enum), WebRtcIPHandling (enum)\n\n"
        "## Reporting: CloudReportingEnabled (bool), ReportDeviceUsers (bool-device), "
        "ReportDeviceActivityTimes (bool-device)\n\n"
        "Provide configs as: Policy, Value, Scope (User|Device), OU Path, Platform (Chrome|ChromeOS|Both).\n"
    ),
)

enrollment_playbook = models.Skill(
    frontmatter=models.Frontmatter(
        name="enrollment-playbook",
        description=(
            "Step-by-step enrollment procedures for Chrome Browser and ChromeOS."
            " Covers manual, forced re-enrollment, zero-touch, and CBCM."
        ),
    ),
    instructions=(
        "## Enrollment Methods\n\n"
        "### Manual (ChromeOS)\n"
        "1. Power on → OOBE → WiFi → sign in with managed account → auto-enrolls\n\n"
        "### Forced Re-enrollment\n"
        "Admin Console → Devices → Chrome → Settings → set ForceReenrollment=true at OU\n"
        "After powerwash, device re-enrolls without user bypass.\n\n"
        "### Zero-Touch\n"
        "Reseller registers serials → appear in Admin Console → assign OU → auto-enroll on first boot\n\n"
        "### CBCM (Windows/Mac/Linux)\n"
        "Admin Console → Managed Browsers → generate enrollment token\n"
        "Deploy: Windows=Registry CloudManagementEnrollmentToken, macOS=plist, Linux=/etc/opt/chrome/policies/\n\n"
        "## Troubleshooting\n"
        "- 'Unable to find account': Check Account settings > Device enrollment is ON + license assigned\n"
        "- Stuck at enrollment: Check network access to m.google.com, accounts.google.com\n"
        "- Policy not applying: Wait 30min or chrome://policy → Reload. Check OU assignment.\n"
    ),
)

runbook_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="runbook-creator",
        description="Generates operational runbooks for CPE fleet management processes.",
    ),
    instructions=(
        "Generate runbooks with: Title, Metadata (owner, frequency, priority, duration), "
        "Prerequisites, numbered Steps (with expected output + failure handling), "
        "Rollback procedure, Validation checks, Escalation contacts.\n"
    ),
)

skill_toolset = SkillToolset(
    skills=[chrome_policy_quick_ref, chrome_policy_reference, enrollment_playbook, runbook_creator]
)

# ── Import sub-agents from the main agent.py (they don't use file paths) ─

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from agent import (
    triage_agent, diagnostic_agent, resolution_agent,
    policy_drafter, policy_validator,
    dlp_posture_agent, extension_audit_agent, compliance_agent,
)

support_intake = SequentialAgent(
    name="support_intake",
    description="End-to-end IT support: Triage → Diagnose → Resolve/Escalate",
    sub_agents=[triage_agent, diagnostic_agent, resolution_agent],
)

policy_validation_loop = LoopAgent(
    name="policy_validation_loop",
    description="Iterative policy Draft ↔ Validate loop (max 3 iterations)",
    sub_agents=[policy_drafter, policy_validator],
    max_iterations=3,
)

security_posture = ParallelAgent(
    name="security_posture_check",
    description="Concurrent DLP + Extension + Compliance audits",
    sub_agents=[dlp_posture_agent, extension_audit_agent, compliance_agent],
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="cpe_fleet_ops",
    description="Chrome Enterprise fleet operations agent.",
    instruction=(
        "You are the CPE Fleet Ops assistant for Chrome Browser and ChromeOS fleet management.\n\n"
        "## Workflows\n"
        "1. support_intake: Problem/error/broken → Triage → Diagnose → Resolve\n"
        "2. policy_validation_loop: Configure/enable/disable → Draft ↔ Validate\n"
        "3. security_posture_check: Audit/security/compliance → DLP + Extension + Compliance\n"
        "4. Skills: How-to/reference → use skills directly\n"
    ),
    tools=[skill_toolset],
    sub_agents=[support_intake, policy_validation_loop, security_posture],
)

# ── Deploy ───────────────────────────────────────────────────────────────

print("🚀 Deploying CPE Fleet Ops to Agent Engine...")
print(f"   Agent: {root_agent.name}")

remote_agent = agent_engines.create(
    agent_engine=root_agent,
    requirements=["google-adk==2.1.0"],
    display_name="CPE Fleet Ops Agent",
    description="Chrome Enterprise fleet ops — multi-agent system for enrollment, policy automation, and security audits.",
)

print(f"\n✅ Deployed!")
print(f"   Resource: {remote_agent.resource_name}")
rid = remote_agent.resource_name.split('/')[-1]
print(f"   Playground: https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/us-central1/agent-engines/{rid}/playground?project=mygenerativeai")
