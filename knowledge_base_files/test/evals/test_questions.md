# Evaluation Questions

Use these prompts to test the Contract Analyzer GPT after the files are added to the knowledge base.

## Retrieval and Current Policy Tests

1. According to the current contract review policy, what liability cap is preferred?
Expected answer: twelve months of fees paid or payable under the agreement. The GPT should prefer policy v2, not the legacy v1 policy.

2. Is net 75 acceptable under the current policy?
Expected answer: No. Payment terms longer than net 60 require escalation.

3. For auto-renewal, what notice period is acceptable?
Expected answer: At least 30 days before the end of the then-current term. A 120-day notice requirement is a red flag because renewal notice periods longer than 90 days are flagged.

## Contract Review Tests

4. Review the Sample SaaS Agreement - High Risk. What are the top five risks?
Expected answer should include net 75, 120-day renewal notice, AI training on customer data/personal data without consent, customer ownership of vendor improvements/platform-related work, unlimited liability, broad indemnity, and Ontario governing law.

5. Review the Sample Mutual NDA. Is it low, medium, or high risk?
Expected answer: Moderate or medium risk. Main issue is confidentiality obligations expire after two years and trade secrets are not separately protected. Governing law is acceptable.

6. Review the Sample Professional Services Agreement. Does the IP position align with the playbook?
Expected answer: Mostly yes. Customer owns paid final deliverables, consultant retains background technology and reusable components, and customer receives internal-use license.

## Vector Store Management Tests

7. Which file is outdated and should not be used as the primary source for current policy?
Expected answer: contract_review_policy_v1_legacy.md.

8. Which files should be retrieved for a question about whether AI training on customer data is allowed?
Expected answer: data_processing_guidelines.md and possibly sample_saas_agreement_high_risk.md if reviewing that contract.

9. Which files should be retrieved for a question about work product ownership?
Expected answer: ip_ownership_playbook.md and the relevant sample contract.
