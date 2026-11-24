# HansiZappo Daily Publishing and Monetization Cycle

## Target
One genuinely new, researched, original Roman Urdu movie-explainer per day, with scene-specific original visuals, narration, thumbnail, metadata, copyright checks, upload, and a daily performance/eligibility review.

## Required production gates
1. Select a different film/topic and verify factual details.
2. Write a distinct script with original commentary, analysis, and ending interpretation; do not reuse a template with only names swapped.
3. Generate scene-matched original visuals and Urdu narration.
4. Render, inspect audio/video, and run copyright/policy checks.
5. Create title, description, chapters, thumbnail, and disclosure where applicable.
6. Upload through the YouTube Data API only after channel OAuth is configured.
7. Record video ID, publish date, views, watch time, subscribers gained, claims/strikes, and audience retention.
8. Update YPP progress and flag any policy or rights issues.

## Current technical state
- GitHub repository: chohanaqib049-tech/hansizappo-automation
- Existing workflow renders a single checked-in episode JSON to an MP4 artifact.
- It does not yet generate new researched episodes, authenticate to YouTube, upload, schedule public publishing, or read YouTube Analytics.
- Do not schedule the existing Episode 001 JSON to upload repeatedly. The daily scheduler must only process a new, unique, approved episode from a queue.
- GitHub Actions runners are temporary and subject to free-tier usage limits; this is not an always-on server.

## YouTube publishing prerequisites
The repository currently has no YouTube OAuth refresh token/client credentials configured, and this GitHub connection cannot create repository Actions secrets. Before unattended upload can run, the channel owner must create/authorize the YouTube API OAuth application and add the required credentials as GitHub Actions secrets. Never put tokens in repository files or logs. Use least-privilege YouTube upload scopes and revoke access if no longer needed.

## Monetization tracker
Track the official YPP requirements in YouTube Studio. Standard ad-revenue eligibility currently requires 1,000 subscribers and either 4,000 valid public watch hours in the previous 12 months or 10 million valid public Shorts views in the previous 90 days, plus policy compliance, supported country/region, 2-step verification, advanced features, and an AdSense for YouTube account. Expanded YPP thresholds/features are country-dependent and must not be assumed available.

## Policy guardrails
- Movie explainers must add substantial original commentary and analysis.
- Do not upload repeated, mass-produced, or minimally varied videos.
- Do not use copyrighted film footage/posters/music without rights or a defensible legal basis; original visuals and licensed/creator-owned audio are preferred.
- Never buy views, subscribers, comments, or watch time.
- Monetization approval is decided by YouTube after channel review; no workflow can guarantee it.
- Country, identity, tax, and payment details must be accurate and consistent with the user's real circumstances. Never use a VPN, false address, or fabricated residency to bypass regional eligibility.
