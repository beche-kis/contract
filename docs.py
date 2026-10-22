CONTRACTS =[
    {
      "id": "CONTRACT-001",
        "title": "Cloud Infrastructure Vendor Agreement — TechCloud Inc.",
        "type": "vendor_agreement",
        "description": "Standard SaaS vendor agreement for cloud hosting services. Well-structured terms, SOC2 certified vendor, US-based data centers.",
        "clauses": [
            "Data processing limited to US-East and US-West regions",
            "SOC2 Type II compliance certification provided annually",
            "99.9% uptime SLA with service credits for violations",
            "Data deletion within 30 days of contract termination",
            "Mutual NDA with standard confidentiality terms",
            "Net-30 payment terms, no auto-renewal without notice",
            "Liability cap at 12 months of fees paid",
            "IP ownership remains with the client for all custom work",
        ],
        "value": 120_000,
        "duration_months": 24,  
    },
    {
        "id": "CONTRACT-002",
        "title": "Offshore Development Outsourcing — GlobalDev Solutions",
        "type": "outsourcing",
        "description": "Development outsourcing to offshore team. Contains concerning clauses around data handling, IP ownership, and termination penalties.",
        "clauses": [
            "Data processing in India, Philippines, and 'other locations as needed'",
            "No SOC2 or ISO 27001 certification; 'industry best practices' only",
            "No uptime SLA — 'commercially reasonable efforts' language",
            "Data retention for 5 years after termination (cannot request deletion)",
            "One-way NDA: client's data protected, but vendor's IP broadly defined",
            "Payment: 50% upfront, balance on delivery; auto-renews annually",
            "Unlimited liability for client, vendor liability capped at fees paid in last month",
            "All work product IP jointly owned — vendor retains right to reuse code",
            "Termination penalty: 6 months of remaining contract value",
            "Governing law: vendor's home jurisdiction, not client's",
        ],
        "value": 500_000,
        "duration_months": 36,
    },

]


REGULATORY_FINDINGS ={
    "CONTRACT-001": {
        "risk_level": "LOW",
        "frameworks_checked": ["GDPR", "SOX", "HIPAA", "SOC2"],
        "findings": [
            "SOC2 Type II certified — meets data security compliance requirements.",
            "US-only data residency aligns with GDPR adequacy and data sovereignty requirements.",
            "30-day data deletion clause meets GDPR right-to-erasure timeline.",
        ],
        "violations": [],
        "recommendation": "Approve — vendor meets all regulatory compliance requirements.",
    },
    "CONTRACT-002": {
        "risk_level": "HIGH",
        "frameworks_checked": ["GDPR", "SOX", "HIPAA", "SOC2"],
        "findings": [
            "No SOC2/ISO certification — cannot verify data security controls.",
            "'Other locations as needed' violates GDPR data transfer restrictions (no adequacy decision).",
            "5-year data retention with no deletion option violates GDPR Art. 17 (right to erasure).",
            "No data processing agreement (DPA) — required under GDPR Art. 28.",
        ],
        "violations": ["GDPR Art. 17 (Right to Erasure)", "GDPR Art. 28 (Data Processing Agreement)", "GDPR Art. 46 (Data Transfer Safeguards)"],
        "recommendation": "Reject — multiple GDPR violations. Require DPA, data residency restrictions, and deletion rights before reconsidering.",
    },
}
FINANCIAL_FINDINGS ={
    "CONTRACT-001": {
        "risk_level": "LOW",
        "findings": [
            "Net-30 payment terms are standard and favorable.",
            "No auto-renewal trap — requires explicit notice.",
            "Liability cap at 12 months of fees is reasonable and mutual.",
            "Service credits for SLA violations provide financial protection.",
        ],
        "unfavorable_terms": [],
        "recommendation": "Approve — payment terms and liability structure are well-balanced.",
    },
    "CONTRACT-002": {
        "risk_level": "HIGH",
        "findings": [
            "50% upfront payment ($250K) creates massive financial exposure before delivery.",
            "Auto-renewal without opt-out mechanism locks in recurring costs.",
            "Vendor liability capped at last month's fees (~$14K) vs. unlimited client liability — extremely asymmetric.",
            "6-month termination penalty (~$250K) makes exit prohibitively expensive.",
            "Governing law in vendor's jurisdiction increases legal costs for disputes.",
        ],
        "unfavorable_terms": ["50% upfront", "auto-renewal", "asymmetric liability", "termination penalty", "foreign jurisdiction"],
        "recommendation": "Reject — financial terms are heavily skewed toward vendor. Negotiate: reduce upfront to 20%, add opt-out, equalize liability caps, remove termination penalty.",
    },
}
IP_FINDINGS ={
    "CONTRACT-001": {
        "risk_level": "LOW",
        "findings": [
            "Client retains full IP ownership of all custom work — clear and favorable.",
            "Mutual NDA with standard confidentiality protections.",
            "No non-compete clauses restricting client's future vendor choices.",
        ],
        "concerns": [],
        "recommendation": "Approve — IP terms clearly protect client ownership.",
    },
    "CONTRACT-002": {
        "risk_level": "HIGH",
        "findings": [
            "Joint IP ownership is extremely risky — vendor can reuse client's custom code for competitors.",
            "Vendor's 'broadly defined IP' clause could claim ownership of client methodologies discussed during project.",
            "One-way NDA protects vendor but not client's trade secrets adequately.",
            "No work-for-hire provision — code ownership is ambiguous without explicit assignment.",
            "No non-compete: vendor can build identical product for client's competitors using shared codebase.",
        ],
        "concerns": ["joint IP ownership", "broad vendor IP definition", "one-way NDA", "no work-for-hire", "no non-compete"],
        "recommendation": "Reject — IP terms expose client to competitive risk. Require: full IP assignment, mutual NDA, work-for-hire clause, and 2-year non-compete.",
    },
}
