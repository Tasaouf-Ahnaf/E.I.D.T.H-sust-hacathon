async function analyzeTicket() {

    const complaint = document.getElementById("complaint").value;
    const language = document.getElementById("language").value;
    const transactionId = document.getElementById("transaction_id").value;
    const amount = Number(document.getElementById("amount").value);
    const status = document.getElementById("status").value;

    const payload = {
        ticket_id: "WEB001",
        complaint: complaint,
        language: language,
        channel: "web",
        user_type: "customer",
        campaign_context: "frontend_demo",
        transaction_history: [
            {
                transaction_id: transactionId,
                timestamp: new Date().toISOString(),
                type: "send_money",
                amount: amount,
                counterparty: "01711111111",
                status: status
            }
        ]
    };

    const resultDiv = document.getElementById("result");

    resultDiv.innerHTML = "Analyzing...";

    try {

        const response = await fetch(
            "https://e-i-d-t-h-sust-hacathon.onrender.com/analyze-ticket",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        resultDiv.innerHTML = `
<h2>Analysis Result</h2>

<b>Case Type:</b>
${data.case_type}

<b>Department:</b>
${data.department}

<b>Severity:</b>
${data.severity}

<b>Evidence Verdict:</b>
${data.evidence_verdict}

<b>Relevant Transaction:</b>
${data.relevant_transaction_id}

<b>Confidence:</b>
${data.confidence}

<b>Agent Summary:</b>
${data.agent_summary}

<b>Recommended Action:</b>
${data.recommended_next_action}

<b>Customer Reply:</b>
${data.customer_reply}
`;

    }
    catch (error) {

        resultDiv.innerHTML =
            "<h3 style='color:red;'>Cannot connect to FastAPI server.</h3>";

        console.error(error);
    }

}