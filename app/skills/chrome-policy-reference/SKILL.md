---
name: chrome-policy-reference
description: >
  Comprehensive Chrome Enterprise and ChromeOS policy reference.
  Covers 50+ critical policies organized by category with values,
  scopes, platform support, and configuration best practices.
---

# Chrome Enterprise Policy Reference

Use `load_skill_resource` to read `references/policy-catalog.md` for the full catalog.

## Quick Lookup

When an administrator asks about a specific policy:
1. Look up the policy in the reference catalog
2. Provide: policy name, description, allowed values, scope (user/device), platforms
3. Note any dependencies or common conflicts
4. Suggest the recommended value for enterprise environments

## Configuration Format

Always provide policy configurations in this format:
```
Policy: <PolicyName>
Value: <value>
Scope: User-level | Device-level
OU Path: <suggested OU path>
Platform: Chrome Browser | ChromeOS | Both
Dependencies: <list any prerequisite policies>
Conflicts: <list any policies that may conflict>
```

## Important Notes
- Device-level policies only apply to ChromeOS (managed devices)
- User-level policies follow the user across devices
- Policies set at child OUs override parent OU policies
- Some policies require Chrome Enterprise Premium license
