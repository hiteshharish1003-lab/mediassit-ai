import { ArrowRight, HeartPulse, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

export default function About() {
  return <section className="page-shell info-page"><span className="eyebrow"><HeartPulse size={14}/> ABOUT MEDIASSIST</span><h1>Healthcare language<br/><em>should feel human.</em></h1><p>MediAssist helps people get oriented when a prescription feels hard to read. It organizes legible details, explains common medicine uses, and makes room for follow-up questions.</p><div className="info-values"><article><ShieldCheck/><h2>Careful with details</h2><p>Unclear text should stay unclear. We encourage you to verify every medicine and direction with a pharmacist or prescriber.</p></article><article><Sparkles/><h2>Built for understanding</h2><p>Plain-language context can help you prepare better questions about your care.</p></article></div><p className="info-disclaimer">MediAssist is an educational tool. It does not diagnose conditions or replace professional medical advice.</p><Link className="button-primary" to="/upload">Try the prescription reader <ArrowRight size={16}/></Link></section>;
}
