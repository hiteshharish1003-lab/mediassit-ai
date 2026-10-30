import { useContext, useEffect, useRef, useState } from "react";
import { ArrowUp, Bot, MessageCircle, Sparkles, UserRound } from "lucide-react";
import { DataContext } from "../context/DataContext";
import { apiRequest } from "../utils/api";

const prompts = ["What medicines were prescribed?", "What is this medicine commonly used for?", "Help me understand the instructions"];

export default function Chatbot() {
  const { ocrData } = useContext(DataContext);
  const [messages, setMessages] = useState([{ role: "assistant", text: "Hi, I’m your MediAssist guide. I can help explain the details in your prescription or answer general health questions. What would you like to know?" }]);
  const [input, setInput] = useState(""); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text = input) => {
    const query = text.trim(); if (!query || loading) return;
    setInput(""); setError(""); setMessages((m) => [...m, { role: "user", text: query }]); setLoading(true);
    try {
      const context = ocrData ? JSON.stringify(ocrData) : "";
      const history = messages.filter((message) => message.role === "user" || message.role === "assistant").slice(1).map(({ role, text }) => ({ role, content: text }));
      const answer = await apiRequest("/chat/", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query, context, history }) });
      setMessages((m) => [...m, { role: "assistant", text: answer.response || "I couldn't answer that just now. Please try again." }]);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  return <div className="chat-shell">
    <div className="chat-header"><div className="assistant-avatar"><Bot size={20}/><span/></div><div><h2>MediAssist guide</h2><p><span className="online-dot"/> Here to help you understand</p></div><span className="chat-header-tag"><Sparkles size={13}/> AI ASSISTANT</span></div>
    <div className="chat-messages">
      {!ocrData && <div className="chat-context-note"><MessageCircle size={15}/> Upload a prescription to ask questions about its details.</div>}
      {messages.map((message, i) => <div className={`chat-message ${message.role}`} key={i}><span className="message-avatar">{message.role === "assistant" ? <Bot size={16}/> : <UserRound size={16}/>}</span><div className="message-content"><span className="message-name">{message.role === "assistant" ? "MEDIASSIST" : "YOU"}</span><p>{message.text}</p></div></div>)}
      {loading && <div className="chat-message assistant"><span className="message-avatar"><Bot size={16}/></span><div className="typing-indicator"><i/><i/><i/></div></div>}
      <div ref={endRef}/>
    </div>
    {messages.length < 3 && <div className="suggested-prompts">{prompts.map((prompt) => <button key={prompt} onClick={() => send(prompt)}>{prompt}<ArrowUp size={13}/></button>)}</div>}
    {error && <div className="chat-error">{error}</div>}
    <form className="chat-composer" onSubmit={(e) => { e.preventDefault(); send(); }}><input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask anything about your prescription…" aria-label="Your question"/><button type="submit" disabled={!input.trim() || loading} aria-label="Send message"><ArrowUp size={18}/></button></form>
    <p className="chat-footnote">For personal medical decisions, please speak with your doctor or pharmacist.</p>
  </div>;
}
