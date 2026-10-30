import { Mail, MessageCircle } from "lucide-react";

export default function Contact() {
  return <section className="page-shell info-page"><span className="eyebrow"><MessageCircle size={14}/> GET IN TOUCH</span><h1>We’re listening<br/><em>and learning.</em></h1><p>Have feedback about the experience or found something that could be clearer? Send the project team a note.</p><a className="contact-card" href="mailto:support@mediassist-ai.com"><span><Mail size={20}/></span><div><small>EMAIL THE TEAM</small><b>support@mediassist-ai.com</b></div><span className="contact-arrow">↗</span></a><p className="info-disclaimer">Please don’t send medical records or urgent health questions by email. For personal care guidance, contact your clinician or pharmacist.</p></section>;
}
