"""CPE Fleet Ops Agent — ADK 2.0 Multi-Agent System for Chrome Enterprise.

Demonstrates ADK 2.0 patterns applied to enterprise IT fleet management:

  1. SequentialAgent  — Support Intake: Triage → Diagnose → Resolve
  2. LoopAgent        — Policy Automation: Draft ↔ Validate (loop) → Stage
  3. ParallelAgent    — Security Posture: DLP + Extension + Compliance (concurrent)
  4. Skills           — Domain knowledge: enrollment, policy reference, runbook creator
  5. LLM Delegation   — Root orchestrator routes to the right workflow

Architecture:
  ┌──────────────────────────────────────────────────────────────────┐
  │                 CPE Fleet Ops Orchestrator (LlmAgent)            │
  │   Routes requests to the appropriate fleet management workflow   │
  ├────────────┬────────────────┬───────────────┬───────────────────┤
  │            │                │               │                   │
  │  Sequential│   Loop         │   Parallel    │   Skills          │
  │  Support   │   Policy       │   Security    │   Toolset         │
  │  Intake    │   Automation   │   Posture     │                   │
  │            │                │               │                   │
  │  Triage    │  Drafter       │  DLP Check    │  enrollment       │
  │    ↓       │    ↓           │  Extension    │  chrome-policy    │
  │  Diagnose  │  Validator     │  Compliance   │  runbook-creator  │
  │    ↓       │    ↓ (loop)    │               │                   │
  │  Resolve   │  Stage         │               │                   │
  └────────────┴────────────────┴───────────────┴───────────────────┘

Grounding:
  - Option A: Vertex AI Search data store (for KB-grounded answers)
  - Option B: Skills with inline policy references (zero infra)
"""

import os
import pathlib

from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.skills import load_skill_from_dir, models
from google.adk.tools.skill_toolset import SkillToolset



# =============================================================================
# 1. SKILLS — Domain Knowledge for Chrome Enterprise Fleet Management
# =============================================================================

# ── Skill A: Inline — Chrome Policy Quick Reference ─────────────────────────
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
        "- **DeviceEnrollmentMode**: Controls auto-enrollment. Values: forced | optional | disabled\n"
        "- **ForceReenrollment**: Force device re-enrollment after wipe. Values: true | false\n"
        "- **DeviceBlockDevmode**: Block developer mode on enrolled devices. Values: true | false\n"
        "- **AutoEnrollmentProtocol**: Protocol for zero-touch enrollment. Values: FRE | initial\n\n"
        "## Security Policies\n"
        "- **PasswordManagerEnabled**: Enable/disable password manager. Values: true | false\n"
        "- **BrowserSignin**: Control browser sign-in. Values: 0 (disabled) | 1 (enabled) | 2 (forced)\n"
        "- **DeveloperToolsAvailability**: Control DevTools. Values: 0 (always) | 1 (extensions only) | 2 (disabled)\n"
        "- **IncognitoModeAvailability**: Control incognito. Values: 0 (available) | 1 (disabled) | 2 (forced)\n"
        "- **SafeBrowsingProtectionLevel**: Safe Browsing level. Values: 0 (off) | 1 (standard) | 2 (enhanced)\n\n"
        "## Extension Policies\n"
        "- **ExtensionInstallBlocklist**: Block specific extensions. Values: list of extension IDs or '*' for all\n"
        "- **ExtensionInstallAllowlist**: Allow specific extensions. Values: list of extension IDs\n"
        "- **ExtensionInstallForcelist**: Force-install extensions. Values: list of extension_id;update_url\n"
        "- **ExtensionSettings**: Granular per-extension settings (JSON). Controls install, permissions, pin\n\n"
        "## Data Loss Prevention\n"
        "- **PrintingEnabled**: Allow printing. Values: true | false\n"
        "- **ScreenCaptureAllowed**: Allow screen capture. Values: true | false\n"
        "- **ExternalStorageDisabled**: Disable USB/external storage. Values: true | false\n"
        "- **CloudPrintEnabled**: Allow cloud print. Values: true | false (deprecated — use CUPS)\n"
        "- **DataLeakPreventionRulesList**: DLP rules (JSON). Controls clipboard, screenshot, printing, files\n\n"
        "## Network Policies\n"
        "- **ProxyMode**: Proxy configuration. Values: direct | auto_detect | pac_script | fixed_servers\n"
        "- **WebRtcIPHandling**: WebRTC IP policy. Values: default | disable_non_proxied_udp\n"
        "- **DnsOverHttpsMode**: DoH mode. Values: off | automatic | secure\n\n"
        "## Policy Scope\n"
        "- **User-level**: Applied per user profile (follows the user across devices)\n"
        "- **Device-level**: Applied to the device (affects all users on that device)\n"
        "- **OU-scoped**: Inherited down the Organizational Unit tree unless overridden\n\n"
        "For each policy recommendation, specify: policy name, value, scope (user/device), "
        "OU path, and any dependencies or conflicts.\n"
    ),
)

# ── Skill B: File-based — Chrome Policy Full Reference ──────────────────────
chrome_policy_reference = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "chrome-policy-reference"
)

# ── Skill C: File-based — Enrollment Playbook ───────────────────────────────
enrollment_playbook = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "enrollment-playbook"
)

# ── Skill D: Meta — Runbook Creator ─────────────────────────────────────────
runbook_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="runbook-creator",
        description=(
            "Generates new operational runbooks for CPE processes."
            " Creates structured, step-by-step runbooks for device management,"
            " policy rollouts, incident response, and fleet operations."
        ),
    ),
    instructions=(
        "When asked to create a new runbook, generate a complete operational document.\n\n"
        "## Runbook Template\n\n"
        "### Title\n"
        "Clear, descriptive title for the procedure.\n\n"
        "### Metadata\n"
        "- **Owner**: Team/person responsible\n"
        "- **Last Updated**: Date\n"
        "- **Frequency**: How often this runs (on-demand, weekly, etc.)\n"
        "- **Priority**: P1-P4\n"
        "- **Estimated Duration**: Time to complete\n\n"
        "### Prerequisites\n"
        "- Required access/permissions\n"
        "- Required tools\n"
        "- Required knowledge\n\n"
        "### Steps\n"
        "Numbered, detailed steps with:\n"
        "1. What to do (exact commands/clicks)\n"
        "2. Expected output/result\n"
        "3. What to do if it fails\n\n"
        "### Rollback\n"
        "How to undo changes if something goes wrong.\n\n"
        "### Validation\n"
        "How to verify the procedure completed successfully.\n\n"
        "### Escalation\n"
        "Who to contact if the runbook fails at any step.\n"
    ),
)

skill_toolset = SkillToolset(
    skills=[
        chrome_policy_quick_ref,
        chrome_policy_reference,
        enrollment_playbook,
        runbook_creator,
    ]
)




# =============================================================================
# 2. SEQUENTIAL AGENT — Support Intake Pipeline
# =============================================================================
# Triage → Diagnose → Resolve/Escalate in strict order.

triage_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="triage_agent",
    description="Classifies support requests and extracts device/issue context.",
    instruction=(
        "You are a CPE support triage specialist for Chrome Browser and ChromeOS fleet.\n\n"
        "Given a support request:\n\n"
        "1. **Classify** the issue into one category:\n"
        "   - ENROLLMENT: Device enrollment, re-enrollment, provisioning, OOBE\n"
        "   - POLICY: Chrome/ChromeOS policy configuration, conflicts, inheritance\n"
        "   - EXTENSION: Extension installation, permissions, blocklist/allowlist\n"
        "   - HARDWARE: Physical device issues, peripherals, display\n"
        "   - NETWORK: Connectivity, proxy, VPN, certificate issues\n"
        "   - ACCOUNT: User account, sign-in, profile, sync issues\n\n"
        "2. **Extract** key information:\n"
        "   - Device type: Chromebook / Chrome Browser on Windows/Mac/Linux\n"
        "   - OS/Browser version (if mentioned)\n"
        "   - Organizational Unit (OU) path (if mentioned)\n"
        "   - User email or device ID (if mentioned)\n"
        "   - Error messages or symptoms\n\n"
        "3. **Assess priority**:\n"
        "   - P1: Fleet-wide impact (>100 devices), security incident\n"
        "   - P2: Team-wide (10-100 devices), blocking critical workflow\n"
        "   - P3: Individual device, blocking user's work\n"
        "   - P4: Individual device, workaround available\n\n"
        "Store your triage result in state key 'triage_result'."
    ),
    output_key="triage_result",
)

diagnostic_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="diagnostic_agent",
    description="Runs diagnostic checks based on the triage classification.",
    instruction=(
        "You are a CPE diagnostic engineer. Read the triage result from state['triage_result'].\n\n"
        "Based on the category, run the appropriate diagnostic checklist:\n\n"
        "### ENROLLMENT Diagnostics\n"
        "1. Is the enrollment token valid and not expired?\n"
        "2. Is ForceReenrollment enabled for the device's OU?\n"
        "3. Was the device previously enterprise-enrolled (check serial)?\n"
        "4. Is DeviceEnrollmentMode set to 'forced' at the correct OU level?\n"
        "5. Can the device reach accounts.google.com and m.google.com/devicemanagement?\n"
        "6. Is the Chrome Education/Enterprise Upgrade license assigned?\n\n"
        "### POLICY Diagnostics\n"
        "1. Which specific policy is affected? (check chrome://policy on device)\n"
        "2. What source is the policy coming from? (Platform, Cloud, AD, Extension)\n"
        "3. Are there conflicting policies at parent/child OU levels?\n"
        "4. Is the policy user-level or device-level? (scope mismatch?)\n"
        "5. When was the policy last pushed? (propagation delay?)\n\n"
        "### EXTENSION Diagnostics\n"
        "1. Is the extension in ExtensionInstallForcelist or ExtensionSettings?\n"
        "2. Is ExtensionInstallBlocklist set to '*' (blocking all by default)?\n"
        "3. Does the extension require permissions not granted by policy?\n"
        "4. Is there a CSP or network policy blocking the extension's update URL?\n"
        "5. Is the extension compatible with the current Chrome version?\n\n"
        "Provide a confidence score (0-100%) for your root cause hypothesis.\n"
        "Store your diagnosis in state key 'diagnosis'."
    ),
    output_key="diagnosis",
)

resolution_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="resolution_agent",
    description="Provides resolution steps or escalates with full context.",
    instruction=(
        "You are a CPE resolution specialist. Read state['triage_result'] and state['diagnosis'].\n\n"
        "### If diagnostic confidence ≥ 80%:\n"
        "Provide a step-by-step resolution:\n"
        "1. Clear, numbered steps the admin/user should take\n"
        "2. Include exact navigation paths (Admin Console > Devices > Chrome > Settings)\n"
        "3. Include verification steps (how to confirm the fix worked)\n"
        "4. Note any related policies that should be checked\n\n"
        "### If diagnostic confidence < 80%:\n"
        "Generate an escalation ticket:\n"
        "- **Summary**: One-line issue description\n"
        "- **Category**: From triage classification\n"
        "- **Priority**: From triage assessment\n"
        "- **Diagnostic Data**: All findings from diagnostic step\n"
        "- **Attempted Resolutions**: What was tried\n"
        "- **Recommended Team**: MDM / Network / Security / Hardware\n"
        "- **Impact**: Number of affected devices/users\n\n"
        "Store your resolution in state key 'resolution'."
    ),
    output_key="resolution",
)

support_intake = SequentialAgent(
    name="support_intake",
    description=(
        "End-to-end IT support workflow for Chrome/ChromeOS issues."
        " Runs Triage → Diagnose → Resolve/Escalate sequentially."
        " Use when a user reports a device, policy, or extension problem."
    ),
    sub_agents=[triage_agent, diagnostic_agent, resolution_agent],
)


# =============================================================================
# 3. LOOP AGENT — Policy Automation with Validation
# =============================================================================
# Draft ↔ Validate until all checks pass, then stage the rollout.

policy_drafter = LlmAgent(
    model="gemini-2.5-flash",
    name="policy_drafter",
    description="Drafts Chrome Enterprise policy configurations from requirements.",
    instruction=(
        "You are a Chrome Enterprise policy engineer.\n\n"
        "Given a policy change request:\n\n"
        "1. **Identify** the exact Chrome Enterprise policy names\n"
        "   (use the chrome-policy-quick-ref skill for reference)\n"
        "2. **Determine scope**: OU path, user-level vs device-level\n"
        "3. **Generate the configuration** in Admin Console format:\n"
        "   ```\n"
        "   Policy: <PolicyName>\n"
        "   Value: <value>\n"
        "   Scope: User | Device\n"
        "   OU Path: /Engineering/Developers\n"
        "   ```\n"
        "4. **Document**: What changes, why, who's affected, dependencies\n\n"
        "If critique exists in state['policy_critique']:\n"
        "  - Read ALL validation failures\n"
        "  - Fix EVERY issue identified\n"
        "  - Explain what you changed and why\n\n"
        "Store your policy draft in state key 'policy_draft'."
    ),
    output_key="policy_draft",
)

policy_validator = LlmAgent(
    model="gemini-2.5-flash",
    name="policy_validator",
    description="Validates policy configurations for correctness and safety.",
    instruction=(
        "You are a Chrome Enterprise policy security reviewer.\n"
        "Read the policy draft from state['policy_draft'].\n\n"
        "Run these validation checks:\n\n"
        "### 1. SCHEMA VALIDITY\n"
        "- Are all policy names valid Chrome Enterprise policies?\n"
        "- Are values within allowed ranges/types?\n"
        "- Score: PASS / FAIL\n\n"
        "### 2. SCOPE CORRECTNESS\n"
        "- Is user-level vs device-level appropriate for this policy?\n"
        "- Is the OU path valid and at the right level of specificity?\n"
        "- Could this conflict with policies at parent/child OUs?\n"
        "- Score: PASS / WARN / FAIL\n\n"
        "### 3. SECURITY IMPACT\n"
        "- Does this weaken any existing security controls?\n"
        "- Does this create data exfiltration vectors?\n"
        "- Does this affect DLP, Safe Browsing, or managed browser settings?\n"
        "- Score: PASS / WARN / FAIL\n\n"
        "### 4. BLAST RADIUS\n"
        "- How many devices/users are likely affected?\n"
        "- Is this easily reversible?\n"
        "- Should this be staged or deployed all at once?\n"
        "- Score: LOW / MEDIUM / HIGH / CRITICAL\n\n"
        "### 5. DEPENDENCY CHECK\n"
        "- Are there prerequisite policies that must be set first?\n"
        "- Are there related policies that should be updated together?\n"
        "- Score: PASS / WARN / FAIL\n\n"
        "### Verdict\n"
        "If ALL checks PASS (warnings OK with justification):\n"
        "  → Respond with 'APPROVED' on the first line\n"
        "  → Summarize what's safe and why\n\n"
        "If ANY check FAILS:\n"
        "  → List each failure with specific fix instructions\n"
        "  → Explain what's wrong and how to correct it\n\n"
        "Store validation results in state key 'policy_critique'."
    ),
    output_key="policy_critique",
)

policy_validation_loop = LoopAgent(
    name="policy_validation_loop",
    description=(
        "Iterative policy drafting with automated validation."
        " Drafter creates the policy config, Validator checks 5 dimensions."
        " Loop continues until all checks pass or 3 iterations reached."
        " Use when configuring, modifying, or rolling out Chrome/ChromeOS policies."
    ),
    sub_agents=[policy_drafter, policy_validator],
    max_iterations=3,
)


# =============================================================================
# 4. PARALLEL AGENT — Security Posture Audit
# =============================================================================
# Run DLP, Extension, and Compliance checks concurrently.

dlp_posture_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="dlp_posture_check",
    description="Audits Data Loss Prevention configuration and policies.",
    instruction=(
        "You are a DLP security auditor for Chrome Enterprise.\n\n"
        "Audit the DLP posture based on the user's described configuration:\n\n"
        "### DLP Checklist\n"
        "1. **Clipboard control**: Is DataLeakPreventionRulesList configured for clipboard?\n"
        "2. **Screenshot/recording**: Is ScreenCaptureAllowed set to false for sensitive OUs?\n"
        "3. **Printing**: Is PrintingEnabled restricted where needed?\n"
        "4. **External storage**: Is ExternalStorageDisabled for managed devices?\n"
        "5. **Download restrictions**: Are DownloadRestrictions configured?\n"
        "6. **Cloud services**: Are file sharing/upload policies in place?\n"
        "7. **Sync**: Is Chrome Sync appropriately restricted (SyncDisabled, SyncTypesListDisabled)?\n\n"
        "For each item, report: CONFIGURED ✅ | NOT CONFIGURED ❌ | PARTIALLY ⚠️\n"
        "Provide an overall DLP score (0-100%).\n\n"
        "Store audit in state key 'dlp_audit'."
    ),
    output_key="dlp_audit",
)

extension_audit_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="extension_audit",
    description="Audits browser extension posture and permissions.",
    instruction=(
        "You are a Chrome extension security auditor.\n\n"
        "Audit the extension management posture:\n\n"
        "### Extension Security Checklist\n"
        "1. **Default posture**: Is ExtensionInstallBlocklist set to '*' (block all by default)?\n"
        "2. **Allowlist**: Are only approved extensions in ExtensionInstallAllowlist?\n"
        "3. **Force-install**: Review ExtensionInstallForcelist for business-critical extensions\n"
        "4. **Permissions**: Are ExtensionSettings configured to restrict dangerous permissions?\n"
        "   - <all_urls> access?\n"
        "   - Web request interception?\n"
        "   - Cookie access?\n"
        "   - Native messaging?\n"
        "5. **Update sources**: Are extensions only allowed from Chrome Web Store?\n"
        "6. **Runtime permissions**: Are host permissions appropriately scoped?\n\n"
        "Flag any HIGH-RISK extensions (broad permissions + not force-installed).\n\n"
        "Store audit in state key 'extension_audit'."
    ),
    output_key="extension_audit",
)

compliance_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="compliance_scan",
    description="Checks Chrome/ChromeOS configuration against security baselines.",
    instruction=(
        "You are an IT compliance auditor for Chrome Enterprise.\n\n"
        "Verify the configuration against common security frameworks:\n\n"
        "### CIS Chrome Benchmark (Key Controls)\n"
        "1. Safe Browsing enabled (SafeBrowsingProtectionLevel ≥ 1)\n"
        "2. Password manager controlled (PasswordManagerEnabled)\n"
        "3. Incognito mode restricted where needed\n"
        "4. Developer tools restricted for non-dev OUs\n"
        "5. Third-party cookie handling configured\n"
        "6. Auto-update enabled (do not block Chrome updates)\n\n"
        "### Enterprise Security Baseline\n"
        "1. Managed browser enrollment active\n"
        "2. Browser sign-in enforced (BrowserSignin = 2)\n"
        "3. Cloud reporting enabled (CloudReportingEnabled)\n"
        "4. Endpoint verification deployed\n"
        "5. OS auto-update policy configured\n\n"
        "For each control: COMPLIANT ✅ | NON-COMPLIANT ❌ | NEEDS REVIEW ⚠️\n"
        "Provide an overall compliance score (0-100%).\n\n"
        "Store report in state key 'compliance_report'."
    ),
    output_key="compliance_report",
)

security_posture = ParallelAgent(
    name="security_posture_check",
    description=(
        "Comprehensive security audit running DLP, extension, and compliance"
        " checks concurrently. Use when an admin requests a security review,"
        " posture assessment, or compliance audit of their Chrome/ChromeOS fleet."
    ),
    sub_agents=[dlp_posture_agent, extension_audit_agent, compliance_agent],
)


# =============================================================================
# 5. ROOT ORCHESTRATOR — Intelligent Routing
# =============================================================================

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="cpe_fleet_ops",
    description="Chrome Enterprise fleet operations agent with multi-agent workflows.",
    instruction=(
        "You are the CPE Fleet Ops assistant for Chrome Browser and ChromeOS fleet"
        " management. You help IT administrators with device enrollment, policy"
        " configuration, extension management, and security posture.\n\n"
        "## Available Workflows\n\n"
        "### 1. Support Intake (Sequential)\n"
        "Use `support_intake` when the user reports a PROBLEM or ISSUE:\n"
        "- Device won't enroll\n"
        "- Policy not applying\n"
        "- Extension not installing\n"
        "- Error messages\n"
        "This runs: Triage → Diagnose → Resolve/Escalate.\n"
        "Example: 'Chromebook won't enroll after powerwash'\n\n"
        "### 2. Policy Automation (Loop)\n"
        "Use `policy_validation_loop` when the user wants to CREATE or CHANGE policies:\n"
        "- Enable/disable a feature\n"
        "- Configure a security control\n"
        "- Roll out a new policy\n"
        "This runs: Draft ↔ Validate (loop until approved).\n"
        "Example: 'Block personal Google accounts on managed devices'\n\n"
        "### 3. Security Posture (Parallel)\n"
        "Use `security_posture_check` when the user wants an AUDIT or REVIEW:\n"
        "- DLP assessment\n"
        "- Extension security review\n"
        "- Compliance check\n"
        "This runs: DLP + Extension + Compliance checks concurrently.\n"
        "Example: 'Run a security audit on our Chrome fleet configuration'\n\n"
        "### 4. Knowledge (Skills)\n"
        "Use skills directly for REFERENCE or HOW-TO questions:\n"
        "- `chrome-policy-quick-ref`: Policy names, values, scopes\n"
        "- `chrome-policy-reference`: Detailed policy documentation\n"
        "- `enrollment-playbook`: Step-by-step enrollment procedures\n"
        "- `runbook-creator`: Generate new operational runbooks\n\n"
        "## Routing Rules\n"
        "1. Problem/error/broken/not working → support_intake\n"
        "2. Configure/enable/disable/block/allow → policy_validation_loop\n"
        "3. Audit/security/compliance/review/DLP → security_posture_check\n"
        "4. How-to/reference/procedure/what is → use skills directly\n"
        "5. Simple questions about capabilities → respond directly\n\n"
        "Always explain which workflow you're using and why."
    ),
    tools=[skill_toolset],
    sub_agents=[support_intake, policy_validation_loop, security_posture],
)
