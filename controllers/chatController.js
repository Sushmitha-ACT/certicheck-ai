const API_KEY = process.env.ANTHROPIC_API_KEY;

async function sendAnthropicResponse(message, history = []) {
  const system = `You are CertiCheck AI, a professional assistant that helps users verify certificates, understand risk scores, identify forgery markers, and explain why documents may be suspicious or fake.`;
  const messages = [
    { role: 'system', content: system },
    ...history,
    { role: 'user', content: message }
  ];

  const resp = await fetch('https://api.anthropic.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Api-Key': API_KEY
    },
    body: JSON.stringify({
      model: 'claude-3.5-sonic',
      messages,
      max_tokens: 400,
      temperature: 0.3
    })
  });
  if (!resp.ok) {
    const errBody = await resp.text().catch(() => '');
    throw new Error(`Anthropic API error ${resp.status}: ${errBody}`);
  }
  const data = await resp.json();
  const messageObj = data?.choices?.[0]?.message;
  return messageObj?.content || 'Sorry, I could not generate a response.';
}

function generateFallbackReply(message) {
  const text = message.toLowerCase();
  if (text.includes('wrong picture') || text.includes('not certificate') || text.includes('fake image') || text.includes('attach')) {
    return 'If the uploaded file is not a certificate image or PDF, the system will likely flag it as suspicious or fake because it cannot verify unknown document types. Upload a clear certificate file for the most accurate result.';
  }
  if (text.includes('verify') || text.includes('how do i verify') || text.includes('how to verify') || text.includes('check certificate') || text.includes('certificate verification')) {
    return 'To verify a certificate, open the Verify tab, upload a clear certificate image or PDF, and submit it. The system analyzes text, seals, layout, and authenticity markers, then shows a confidence score, risk level, and detailed reasons.';
  }
  if (text.includes('doubt') || text.includes('question') || text.includes('ask')) {
    return 'Tell me your doubt or question and I will explain the verification result, confidence score, suspicious indicators, or what makes a certificate look genuine or fake.';
  }
  if (text.includes('90%') || text.includes('confidence')) {
    return 'A 90% confidence score means the certificate appears likely authentic, but there can still be minor uncertainties. Review the flagged reasons to understand any remaining risk.';
  }
  if (text.includes('login')) {
    return 'You need to log in before uploading a document. Once signed in, use the Verify tab to upload your certificate and receive a full analysis report.';
  }
  if (text.includes('history')) {
    return 'History stores your previously verified certificates. You can revisit saved reports and review analysis details anytime.';
  }
  return 'I am CertiCheck AI. Ask me anything about certificate verification, suspicious files, confidence scoring, or verification steps. I will explain the results clearly.';
}

exports.chat = async (req, res) => {
  try {
    const { message, history } = req.body || {};
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message text is required.' });
    }

    if (API_KEY) {
      const reply = await sendAnthropicResponse(message, history || []);
      return res.json({ reply });
    }

    const reply = generateFallbackReply(message);
    return res.json({ reply, warning: 'No AI key configured. Using built-in fallback assistant.' });
  } catch (error) {
    console.error('chatController error', error);
    res.status(500).json({ error: error.message || 'Unable to generate chat response.' });
  }
};
