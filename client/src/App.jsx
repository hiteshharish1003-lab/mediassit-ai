import { Component } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import About from "./pages/About";
import Upload from "./pages/Upload";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";
import Chatbot from "./components/Chatbot";
import { DataProvider } from "./context/DataContext";

function ChatPage() { return <div className="page-shell chat-page"><div className="page-heading"><span className="eyebrow"><MessageMark/> YOUR CARE COMPANION</span><h1>Questions are<br/><em>a good place to start.</em></h1><p>Ask about your prescription or explore general health information.</p></div><Chatbot/></div>; }
function MessageMark() { return <span aria-hidden="true">✳</span>; }

class ChatErrorBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }
  componentDidCatch(error) { console.error("Chat page failed to render:", error); }
  render() {
    if (this.state.error) return <section className="page-shell chat-page"><div className="chat-load-error"><h2>Chat couldn’t open</h2><p>Refresh the page. If it happens again, share this browser error with the project developer:</p><code>{this.state.error.message}</code><Link to="/upload">Return to prescription reader</Link></div></section>;
    return this.props.children;
  }
}

export default function App() {
  return <BrowserRouter><DataProvider><div className="app-frame"><Navbar/><main className="app-main"><Routes><Route path="/" element={<Home/>}/><Route path="/about" element={<About/>}/><Route path="/upload" element={<Upload/>}/><Route path="/contact" element={<Contact/>}/><Route path="/dashboard" element={<Dashboard/>}/><Route path="/chat" element={<ChatErrorBoundary><ChatPage/></ChatErrorBoundary>}/></Routes></main><Footer/></div></DataProvider></BrowserRouter>;
}
