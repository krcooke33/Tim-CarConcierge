---
name: GitHub authentication
description: Source-control connector health and actual Git authentication can disagree.
---
Do not treat a healthy source-control connection as proof that workspace Git can push.

**Why:** The platform reported an active, healthy GitHub source-control connection with repository write scope, while Git authentication timed out and the CLI reported no login. The connection prompt also rejected the existing source-control connection identifier.

**How to apply:** Verify actual push access with a non-mutating dry run. If authentication and connection prompts fail, ask the user to reconnect GitHub in account connected services rather than repeatedly retrying, requesting credentials in chat, or claiming a backup succeeded.
