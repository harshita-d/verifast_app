import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import MessageBubble from "./components/MessageBubble"; // Reusable chat bubble component
import { sendMessage, getHistory, resetSession } from "./api"; // API utilities
import "./App.css"; // Custom styling

export default function App() {
  // Generate or retrieve a unique session ID stored in localStorage
  const [sessionId] = useState(() => {
    const saved = localStorage.getItem("sessId");
    if (saved) return saved;
    const id = uuidv4();
    localStorage.setItem("sessId", id);
    return id;
  });

  // State to store chat messages and user input
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Ref to auto-scroll to the latest message
  const bottom = useRef(null);

  // Fetch chat history on mount (or when sessionId changes)
  useEffect(() => {
    getHistory(sessionId).then(setMessages);
  }, [sessionId]);

  // Auto-scroll to bottom when new message is added
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle message submit (user → assistant)
  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user's message to the chat
    const userTurn = { role: "user", content: input };
    setMessages((m) => [...m, userTurn]);
    setInput("");

    // Stream assistant's response incrementally
    let assistantIndex = null;

    for await (const chunk of sendMessage(sessionId, input)) {
      setMessages((msgs) => {
        // If assistant response hasn't been added yet
        if (assistantIndex === null) {
          assistantIndex = msgs.length;
          return [...msgs, { role: "assistant", content: chunk }];
        }
    
        // Update the last assistant message
        const updated = [...msgs];
        updated[assistantIndex] = { ...updated[assistantIndex], content: chunk };
        return updated;
      });
    }
    
  }

  // Reset the chat session (clears messages from server & local state)
  async function handleReset() {
    await resetSession(sessionId);
    setMessages([]);
  }

  // Main render
  return (
    <div className="app-container">
      <header className="header">Verifast News Chat</header>

      <main className="chat-main">
        {messages.map((m, idx) => (
          <MessageBubble key={idx} role={m.role}>
            {m.content}
          </MessageBubble>
        ))}
        <div ref={bottom} />
      </main>

      {/* Chat input form */}
      <form onSubmit={handleSubmit} className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask something…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          type="submit"
          className="chat-button send"
          disabled={!input.trim()}
        >
          Send
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="chat-button reset"
        >
          Reset
        </button>
      </form>
    </div>
  );
}
