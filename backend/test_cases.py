import time
import requests

BASE_URL = "http://127.0.0.1:8000/analyze-ticket"

VALID_EVIDENCE = {
    "consistent",
    "inconsistent",
    "insufficient_data",
}

FORBIDDEN_WORDS = [
    "PIN",
    "OTP",
    "password",
    "refund confirmed",
]


def run_test(name, payload):

    print("=" * 80)
    print("TEST:", name)

    start = time.time()

    response = requests.post(
        BASE_URL,
        json=payload,
        timeout=30,
    )

    elapsed = time.time() - start

    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {elapsed:.2f} sec")

    assert response.status_code == 200, response.text

    data = response.json()

    print(data)

    # ----------------------------
    # Assertions
    # ----------------------------

    assert (
        data["evidence_verdict"] in VALID_EVIDENCE
    ), "Invalid evidence_verdict"

    reply = data["customer_reply"].lower()

    for word in FORBIDDEN_WORDS:
        assert word.lower() not in reply, (
            f"Forbidden phrase detected: {word}"
        )

    assert elapsed < 30, "Response exceeded 30 seconds"

    print("✅ Test Passed")


# =====================================================
# Test Cases
# =====================================================

tests = [

    # -------------------------------------------------
    # 1 Wrong Transfer (English)
    # -------------------------------------------------

    (
        "English Wrong Transfer",

        {
            "ticket_id": "T001",

            "complaint":
                "I accidentally sent 5000 BDT to the wrong person.",

            "language": "en",

            "channel": "app",

            "user_type": "customer",

            "campaign_context": "none",

            "transaction_history": [

                {
                    "transaction_id": "TX1001",

                    "timestamp": "2026-06-26T10:00:00Z",

                    "type": "send_money",

                    "amount": 5000,

                    "counterparty": "01711111111",

                    "status": "success",
                }

            ],
        },
    ),

    # -------------------------------------------------
    # 2 Bangla
    # -------------------------------------------------

    (
        "Bangla Complaint",

        {
            "ticket_id": "T002",

            "complaint":
                "আমি ৫০০০ টাকা ভুল নম্বরে পাঠিয়েছি",

            "language": "bn",

            "channel": "app",

            "user_type": "customer",

            "campaign_context": "none",

            "transaction_history": [

                {
                    "transaction_id": "TX1002",

                    "timestamp": "2026-06-26T10:00:00Z",

                    "type": "send_money",

                    "amount": 5000,

                    "counterparty": "01811111111",

                    "status": "success",
                }

            ],
        },
    ),

    # -------------------------------------------------
    # 3 Banglish
    # -------------------------------------------------

    (
        "Banglish Failed Payment",

        {
            "ticket_id": "T003",

            "complaint":
                "Ami 500 taka send korsi but eta show korche failed",

            "language": "banglish",

            "channel": "app",

            "user_type": "customer",

            "campaign_context": "none",

            "transaction_history": [

                {
                    "transaction_id": "TX1003",

                    "timestamp": "2026-06-26T10:00:00Z",

                    "type": "send_money",

                    "amount": 500,

                    "counterparty": "01911111111",

                    "status": "failed",
                }

            ],
        },
    ),

    # -------------------------------------------------
    # 4 Inconsistent
    # -------------------------------------------------

    (
        "Inconsistent Claim",

        {
            "ticket_id": "T004",

            "complaint":
                "I lost 10000 BDT.",

            "language": "en",

            "channel": "app",

            "user_type": "customer",

            "campaign_context": "none",

            "transaction_history": [

                {
                    "transaction_id": "TX1004",

                    "timestamp": "2026-06-26T10:00:00Z",

                    "type": "send_money",

                    "amount": 500,

                    "counterparty": "01611111111",

                    "status": "success",
                }

            ],
        },
    ),

    # -------------------------------------------------
    # 5 Empty Transaction History
    # -------------------------------------------------

    (
        "Refund Request Without History",

        {
            "ticket_id": "T005",

            "complaint":
                "I want a refund for my failed payment.",

            "language": "en",

            "channel": "app",

            "user_type": "customer",

            "campaign_context": "none",

            "transaction_history": [],
        },
    ),
]


# =====================================================
# Run Tests
# =====================================================

if __name__ == "__main__":

    print("\nStarting Integration Tests...\n")

    for name, payload in tests:

        run_test(name, payload)

    print("\n🎉 ALL TESTS PASSED\n")