import { useContext, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, ArrowRight, Check, FileImage, FileText, LoaderCircle, ShieldCheck, Sparkles, UploadCloud, X } from "lucide-react";
import { DataContext } from "../context/DataContext";
import { apiRequest } from "../utils/api";

const value = (v) => v && String(v).trim() ? v : "Not found";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const { ocrData, setOcrData } = useContext(DataContext);
  const navigate = useNavigate();

  const selectFile = (picked) => {
    if (!picked) return;
    if (!picked.type.startsWith("image/")) { setError("Choose an image file such as JPG, PNG or WEBP."); return; }
    if (picked.size > 12 * 1024 * 1024) { setError("This image is larger than 12 MB."); return; }
    setError(""); setFile(picked); setPreview(URL.createObjectURL(picked)); setOcrData(null);
  };

  const analyze = async () => {
    if (!file) return;
    setBusy(true); setError("");
    const form = new FormData(); form.append("file", file);
    try { setOcrData(await apiRequest("/upload/", { method: "POST", body: form })); }
    catch (e) { setError(e.message); }
    finally { setBusy(false); }
  };

  return <div className="page-shell upload-page">
    <div className="page-heading"><span className="eyebrow"><Sparkles size={14}/> PRESCRIPTION READER</span><h1>Clarity for your<br/><em>care plan.</em></h1><p>Upload a prescription to get a clear, organized explanation of what’s written.</p></div>
    <div className="analysis-layout">
      <section className="panel upload-panel">
        <div className="panel-top"><div><span className="step-label">01 / UPLOAD</span><h2>Your prescription</h2></div><ShieldCheck size={20} className="muted-icon"/></div>
        {!file ? <button className="dropzone" onClick={() => inputRef.current?.click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); selectFile(e.dataTransfer.files?.[0]); }}>
          <span className="drop-icon"><UploadCloud size={25}/></span><strong>Drop your image here</strong><span>or <b>browse files</b></span><small>JPG, PNG or WEBP · up to 12 MB</small>
        </button> : <div className="selected-file"><img src={preview} alt="Prescription preview"/><div className="file-detail"><span className="file-icon"><FileImage size={18}/></span><div><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(2)} MB · Ready to analyze</small></div></div><button className="icon-button" aria-label="Remove image" onClick={() => { setFile(null); setPreview(""); setOcrData(null); }}><X size={17}/></button></div>}
        <input ref={inputRef} type="file" accept="image/*" hidden onChange={(e) => selectFile(e.target.files?.[0])}/>
        <div className="privacy-note"><ShieldCheck size={16}/><span>Your image is sent to the configured AI provider for analysis. Avoid uploading sensitive information or another person’s prescription without permission.</span></div>
        {error && <div className="error-note"><AlertCircle size={17}/>{error}</div>}
        <button className="button-primary analyze-button" onClick={analyze} disabled={!file || busy}>{busy ? <><LoaderCircle className="spin" size={18}/> Reading your prescription…</> : <><Sparkles size={17}/> Analyze prescription <ArrowRight size={17}/></>}</button>
        {busy && <div className="processing-hint">Reading text and organizing the details. This can take a few moments.</div>}
      </section>
      <aside className="side-note"><span className="eyebrow">A CLEARER PICTURE</span><h3>From handwritten notes to helpful context.</h3><div className="benefit"><span>01</span><div><b>Key details</b><p>See the prescriber, date and instructions that could be read.</p></div></div><div className="benefit"><span>02</span><div><b>Medicine guide</b><p>Understand common uses, with a reminder to verify with your pharmacist.</p></div></div><div className="benefit"><span>03</span><div><b>Ask follow-ups</b><p>Continue with questions grounded in your uploaded prescription.</p></div></div></aside>
    </div>
    {ocrData && <section className="results-section" id="results">
      <div className="result-heading"><div><span className="eyebrow"><Check size={14}/> ANALYSIS READY</span><h2>Your prescription, <em>made clearer.</em></h2></div><button className="button-secondary" onClick={() => navigate("/chat")}>Ask a question <ArrowRight size={16}/></button></div>
      <div className="summary-card"><div className="summary-symbol"><FileText size={20}/></div><div><span className="eyebrow">PLAIN-LANGUAGE SUMMARY</span><p>{ocrData.summary || "We organized the details we could read from your prescription."}</p></div></div>
      <div className="detail-grid"><div className="panel detail-card"><span className="eyebrow">PRESCRIPTION DETAILS</span><div className="detail-list"><div><small>Prescriber</small><b>{value(ocrData.doctor_name)}</b></div><div><small>Patient</small><b>{value(ocrData.patient_name)}</b></div><div><small>Date</small><b>{value(ocrData.date_issued)}</b></div><div><small>Clinic</small><b>{value(ocrData.clinic)}</b></div></div></div>
        <div className="panel detail-card medicines-card"><span className="eyebrow">MEDICINES FOUND · {ocrData.medications?.length || 0}</span>{ocrData.medications?.length ? ocrData.medications.map((med, i) => <article className="medicine-row" key={`${med.medicine_name}-${i}`}><span className="medicine-dot">{String(i+1).padStart(2,"0")}</span><div><h3>{med.medicine_name?.trim() || (med.written_as ? `Unclear: ${med.written_as}` : "Medicine name unclear")}</h3><span className={`confidence-badge confidence-${med.confidence || "low"}`}>AI confidence: {med.confidence || "low"} · verify with a pharmacist</span><p>{[med.dosage, med.frequency, med.duration].filter(Boolean).join(" · ") || "Instructions not clearly identified"}</p>{med.common_use && <p className="medicine-use">Common use: {med.common_use}</p>}<small>Common uses are general information, not the reason it was prescribed to you.</small></div></article>) : <p className="empty-copy">No handwritten medicine lines were identified. Try a closer, well-lit photo with the prescription filling most of the frame. Always verify handwritten directions with a pharmacist.</p>}</div></div>
      <div className="medical-disclaimer"><ShieldCheck size={18}/><p><b>Please verify before acting.</b> {ocrData.disclaimer || "Handwriting and OCR can be inaccurate. Confirm every medicine and instruction with your prescriber or pharmacist. This summary is informational and does not replace medical advice."}</p></div>
    </section>}
  </div>;
}
