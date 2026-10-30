import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);
  return <header className="site-header"><div className="nav-wrap"><Link className="wordmark" to="/" onClick={close}><span>✳</span> mediassist</Link><button className="mobile-menu" onClick={() => setOpen(!open)} aria-label="Toggle navigation">{open ? <X/> : <Menu/>}</button><nav className={open ? "nav-links open" : "nav-links"}><NavLink to="/" onClick={close}>Home</NavLink><NavLink to="/upload" onClick={close}>Prescription reader</NavLink><NavLink to="/chat" onClick={close}>Ask MediAssist</NavLink><Link className="nav-cta" to="/upload" onClick={close}>Get started <span>↗</span></Link></nav></div></header>;
}
