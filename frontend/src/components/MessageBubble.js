import React from "react";

export default function MessageBubble({ role, children }) {
  const isUser = role === "user";

  return (
    <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
      <div className="message-role">
        {isUser ? "You" : "AI Assistant"}
      </div>
      <div className="message-text">
        {children}
      </div>
    </div>
  );
}
