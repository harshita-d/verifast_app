// Base URL for all chat-related backend endpoints
const BASE = "http://localhost:8000/chat";

/**
 * Sends a user message to the backend and yields streaming Gemini responses.
 * Uses a streaming fetch with a TextDecoder to handle incremental response.
 *
 * @param {string} sessionId - Unique session identifier
 * @param {string} text - User input message
 * @yields {string} - Incremental assistant response from Gemini
 */
export async function* sendMessage(sessionId, text) {
  const res = await fetch(`${BASE}/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message: text, top_k: 3 }),
  });

  if (!res.body) throw new Error("No body in response");

  // Set up a stream reader to decode the response body in real time
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();

  let full = "";
  for (;;) {
    const { value, done } = await reader.read(); // read next chunk
    if (done) break;
    full += value;

    // Try to parse once we think we have complete JSON
    if (full.startsWith("{") && full.endsWith("}")) {
      try {
        const { reply } = JSON.parse(full);
        yield reply; // yield the parsed reply to the UI
        full = "";   // reset buffer for next chunk
      } catch (e) {
        console.log("Error parsing JSON:", e);
      }
    } else {
      // Optional: log incomplete JSON chunks
      console.log("Partial JSON:", full);
    }
  }
}

/**
 * Fetches the full chat history for the given session.
 *
 * @param {string} sessionId - Unique session identifier
 * @returns {Promise<Array>} - An array of {role, content} messages
 */
export async function getHistory(sessionId) {
  const r = await fetch(`${BASE}/history?session_id=${sessionId}`);
  return r.json();
}

/**
 * Clears the chat session history from Redis cache (server-side).
 *
 * @param {string} sessionId - Unique session identifier
 */
export async function resetSession(sessionId) {
  await fetch(`${BASE}/reset?session_id=${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
}
