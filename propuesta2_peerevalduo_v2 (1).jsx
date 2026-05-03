import { useState } from "react";
//para visualizar en el navegador, ingresar el siguiente comando en la terminal:  
//npx serve -s . -l 3000
//y luego abrir localhost:3000 en el navegador
//asegurarse de estar ubicado en la carpeta donde se encuentra este archivo propuesta2_peerevalduo_v2.jsx para que el comando funcione correctamente
// ─── GOOGLE FONTS ────────────────────────────────────────────────────────────
const fontLink = document.createElement("link");
fontLink.rel = "stylesheet";
fontLink.href = "https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap";
document.head.appendChild(fontLink);

const styleTag = document.createElement("style");
styleTag.textContent = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  ::-webkit-scrollbar { width: 0; }
  input { outline: none; }
  button { font-family: 'Sora', sans-serif; }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
  }
  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.35; }
  }
  .anim-fade { animation: fadeUp 0.35s ease both; }
  .live-dot  { animation: pulse-dot 1.8s ease-in-out infinite; }

  .nav-pill:hover { opacity: 0.85; transform: translateY(-1px); }
  .card-hover:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(0,0,0,0.10); }
  .btn-hover:hover  { filter: brightness(1.06); transform: translateY(-1px); }
  .nav-pill, .card-hover, .btn-hover { transition: all 0.18s ease; }
`;
document.head.appendChild(styleTag);

// ─── DESIGN TOKENS ──────────────────────────────────────────────────────────
const TK = {                        // Teacher — Dark slate + gold
  bg:       "#0E1117",
  surface:  "#161B25",
  elevated: "#1E2535",
  border:   "#262E40",
  borderSoft:"#1C2333",
  text:     "#F0F2F8",
  textMid:  "#8892A4",
  textFaint:"#4A5568",
  gold:     "#C9A84C",
  goldLight:"#E3C26E",
  goldBg:   "#C9A84C18",
  success:  "#34D399",
  warning:  "#FBBF24",
  danger:   "#F87171",
  accent:   "#60A5FA",
};

const SK = {                        // Student — White + deep teal
  bg:       "#F8FAFB",
  surface:  "#FFFFFF",
  surfaceAlt:"#F1F5F4",
  border:   "#E4EBE9",
  borderMid:"#C9D9D5",
  text:     "#0D2B25",
  textMid:  "#3D6B5E",
  textFaint:"#94A3B8",
  primary:  "#0D6655",
  primaryMid:"#128A6F",
  primaryLight:"#E8F5F1",
  accent:   "#1A7F64",
  success:  "#059669",
  warning:  "#D97706",
  danger:   "#DC2626",
};

// ─── SHARED ──────────────────────────────────────────────────────────────────
const ff = "'Sora', sans-serif";
const mono = "'DM Mono', monospace";

// SVG icons — no emojis in UI
const Icon = {
  chevronLeft: (c="#fff", s=16) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6"/>
    </svg>
  ),
  chevronRight: (c="#fff", s=14) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6"/>
    </svg>
  ),
  check: (c="#fff", s=14) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
  lock: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </svg>
  ),
  users: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>
  ),
  plus: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.5" strokeLinecap="round">
      <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
    </svg>
  ),
  barChart: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  refresh: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
    </svg>
  ),
  clock: (c, s=14) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  home: (c, s=18) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  edit: (c, s=18) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
    </svg>
  ),
  star: (c, s=18) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill={c} stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
    </svg>
  ),
  profile: (c, s=18) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
    </svg>
  ),
  download: (c, s=15) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  ),
};

// ─── PHONE SHELL ─────────────────────────────────────────────────────────────
const Phone = ({ children, bg, shadow }) => (
  <div style={{
    width: 360, height: 720,
    background: bg,
    borderRadius: 44,
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    fontFamily: ff,
    flexShrink: 0,
    boxShadow: shadow,
    position: "relative",
  }}>
    {children}
  </div>
);

const StatusBar = ({ light }) => (
  <div style={{ height: 44, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 24px", flexShrink: 0 }}>
    <span style={{ fontSize: 13, fontWeight: 600, color: light ? "rgba(255,255,255,0.9)" : TK.textMid, letterSpacing: 0.2 }}>9:41</span>
    <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
      <div style={{ display: "flex", gap: 2, alignItems: "flex-end" }}>
        {[4,6,9,11].map((h,i) => <div key={i} style={{ width: 3, height: h, borderRadius: 1, background: light ? "rgba(255,255,255,0.75)" : TK.textFaint }} />)}
      </div>
      <div style={{ width: 16, height: 10, borderRadius: 2, border: `1.5px solid ${light ? "rgba(255,255,255,0.6)" : TK.textFaint}`, position: "relative" }}>
        <div style={{ position: "absolute", left: 2, top: 1.5, right: 2, bottom: 1.5, borderRadius: 1, background: light ? "rgba(255,255,255,0.7)" : TK.textFaint, width: "70%" }} />
      </div>
    </div>
  </div>
);

const scroll = { flex: 1, overflowY: "auto", scrollbarWidth: "none" };

// Score ring SVG
const ScoreRing = ({ value, max=5, size=64, stroke=5, color, bg, label }) => {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = (value - 2) / (max - 2);
  const dash = circ * pct;
  return (
    <div style={{ position: "relative", width: size, height: size, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
      <svg width={size} height={size} style={{ position: "absolute", top: 0, left: 0, transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={bg} strokeWidth={stroke} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      </svg>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 15, fontWeight: 800, color, lineHeight: 1, fontFamily: mono }}>{value}</div>
        {label && <div style={{ fontSize: 8, color: TK.textFaint, fontWeight: 500, marginTop: 1, letterSpacing: 0.5 }}>{label}</div>}
      </div>
    </div>
  );
};

// Thin progress bar
const ProgressBar = ({ pct, color, bg, h=4, radius=99 }) => (
  <div style={{ background: bg, borderRadius: radius, height: h, overflow: "hidden" }}>
    <div style={{ height: h, borderRadius: radius, background: color, width: `${pct}%`, transition: "width 0.6s ease" }} />
  </div>
);

// ═══════════════════════════════════════════════════════════════════
// TEACHER APP SCREENS
// ═══════════════════════════════════════════════════════════════════

const TLogin = ({ nav }) => (
  <Phone bg={TK.bg} shadow={`0 40px 100px rgba(201,168,76,0.2), 0 0 0 1px ${TK.border}`}>
    <StatusBar />
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "12px 28px 40px" }}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {/* Logo mark */}
        <div style={{ marginBottom: 36 }}>
          <div style={{ width: 52, height: 52, background: TK.goldBg, border: `1px solid ${TK.gold}40`, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
            <div style={{ width: 22, height: 22, borderRadius: 6, background: TK.gold }} />
          </div>
          <div style={{ fontSize: 26, fontWeight: 800, color: TK.text, letterSpacing: -0.8, lineHeight: 1.1 }}>PeerEval</div>
          <div style={{ fontSize: 12, fontWeight: 500, color: TK.textFaint, letterSpacing: 3, textTransform: "uppercase", marginTop: 4 }}>Teacher</div>
        </div>

        {/* Form */}
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: TK.textMid, marginBottom: 6, letterSpacing: 0.3 }}>USUARIO INSTITUCIONAL</div>
          <div style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 14, padding: "13px 16px", fontSize: 13, color: TK.text, fontFamily: mono, marginBottom: 14 }}>
            a.martinez@uninorte.edu.co
          </div>
          <div style={{ fontSize: 13, fontWeight: 600, color: TK.textMid, marginBottom: 6, letterSpacing: 0.3 }}>CONTRASEÑA</div>
          <div style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 14, padding: "13px 16px", display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
            <div style={{ flex: 1, display: "flex", gap: 5 }}>
              {[...Array(8)].map((_, i) => <div key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: TK.textFaint }} />)}
            </div>
            {Icon.lock(TK.textFaint)}
          </div>
          <button className="btn-hover" onClick={() => nav("tDash")} style={{ width: "100%", background: TK.gold, color: "#0E1117", border: "none", borderRadius: 14, padding: "15px 0", fontSize: 14, fontWeight: 700, cursor: "pointer", letterSpacing: 0.2 }}>
            Iniciar sesión
          </button>
          <div style={{ textAlign: "center", marginTop: 16, fontSize: 11, color: TK.textFaint, fontFamily: mono }}>Autenticado por Roble SSO</div>
        </div>
      </div>
    </div>
  </Phone>
);

const TDash = ({ nav }) => (
  <Phone bg={TK.bg} shadow={`0 40px 100px rgba(201,168,76,0.2), 0 0 0 1px ${TK.border}`}>
    <StatusBar />
    {/* Header */}
    <div style={{ padding: "4px 22px 20px", flexShrink: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 500, color: TK.textFaint, letterSpacing: 0.5, marginBottom: 4 }}>Panel docente</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: TK.text, letterSpacing: -0.5 }}>Prof. Martínez</div>
        </div>
        <div style={{ width: 40, height: 40, borderRadius: 13, background: `linear-gradient(135deg, ${TK.gold}, ${TK.goldLight})`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: "#0E1117", fontFamily: mono }}>AM</div>
        </div>
      </div>
      {/* Stat row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8, marginTop: 16 }}>
        {[["2", "Cursos"], ["1", "Activa"], ["20", "Grupos"]].map(([v,l]) => (
          <div key={l} style={{ background: TK.elevated, border: `1px solid ${TK.borderSoft}`, borderRadius: 12, padding: "12px 10px", textAlign: "center" }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: TK.text, fontFamily: mono }}>{v}</div>
            <div style={{ fontSize: 10, color: TK.textFaint, marginTop: 2, fontWeight: 500, letterSpacing: 0.4 }}>{l.toUpperCase()}</div>
          </div>
        ))}
      </div>
    </div>

    <div style={{ ...scroll, padding: "0 22px 16px" }}>
      {/* Active evaluation */}
      <div style={{ background: TK.goldBg, border: `1px solid ${TK.gold}35`, borderRadius: 16, padding: 16, marginBottom: 18, cursor: "pointer" }} onClick={() => nav("tResults")}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <div className="live-dot" style={{ width: 7, height: 7, borderRadius: "50%", background: TK.gold }} />
              <span style={{ fontSize: 10, fontWeight: 700, color: TK.gold, letterSpacing: 1.5 }}>EN CURSO</span>
            </div>
            <div style={{ fontSize: 14, fontWeight: 700, color: TK.text }}>Sprint 2 Review</div>
            <div style={{ fontSize: 11, color: TK.textMid, marginTop: 3 }}>DM2610 · cierra en 12h 30m</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: TK.gold, fontFamily: mono }}>56%</div>
            <div style={{ fontSize: 10, color: TK.textFaint }}>completado</div>
          </div>
        </div>
        <ProgressBar pct={56} color={TK.gold} bg={`${TK.gold}25`} h={3} />
      </div>

      <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>MIS CURSOS</div>
      {[
        { name: "Desarrollo Móvil 2026-10", code: "DM2610", g: 8, active: true },
        { name: "Arquitectura de Software", code: "AS2610", g: 12, active: false },
      ].map(c => (
        <div className="card-hover" key={c.code} style={{ background: TK.surface, border: `1px solid ${TK.border}`, borderRadius: 16, padding: 16, marginBottom: 10 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: TK.text }}>{c.name}</div>
              <div style={{ fontSize: 11, color: TK.textFaint, marginTop: 3, fontFamily: mono }}>{c.code} · {c.g} grupos</div>
            </div>
            {c.active && (
              <div style={{ background: `${TK.success}20`, borderRadius: 20, padding: "3px 10px" }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: TK.success, letterSpacing: 0.5 }}>ACTIVO</span>
              </div>
            )}
          </div>
          <div style={{ display: "flex", gap: 7 }}>
            <button className="btn-hover" onClick={() => nav("tImport")} style={{ flex: 1, background: TK.elevated, color: TK.textMid, border: `1px solid ${TK.border}`, borderRadius: 10, padding: "8px 0", fontSize: 11, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}>
              {Icon.refresh(TK.textMid, 12)} Grupos
            </button>
            <button className="btn-hover" onClick={() => nav("tNew")} style={{ flex: 1, background: TK.gold, color: "#0E1117", border: "none", borderRadius: 10, padding: "8px 0", fontSize: 11, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}>
              {Icon.plus("#0E1117", 12)} Nueva eval.
            </button>
            <button className="btn-hover" onClick={() => nav("tResults")} style={{ flex: 1, background: TK.elevated, color: TK.textMid, border: `1px solid ${TK.border}`, borderRadius: 10, padding: "8px 0", fontSize: 11, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}>
              {Icon.barChart(TK.textMid, 12)} Resultados
            </button>
          </div>
        </div>
      ))}
    </div>

    {/* Bottom nav */}
    <div style={{ display: "flex", background: TK.surface, borderTop: `1px solid ${TK.border}`, padding: "10px 0 20px", flexShrink: 0 }}>
      {[[Icon.home, "Inicio", true, null],[Icon.edit, "Evaluar", false, "tNew"],[Icon.barChart, "Datos", false, "tResults"],[Icon.profile, "Perfil", false, null]].map(([Ic,lb,act,sc],i) => (
        <button key={lb} onClick={() => sc && nav(sc)} style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", gap:3, background:"none", border:"none", cursor:"pointer", color: act ? TK.gold : TK.textFaint }}>
          {Ic(act ? TK.gold : TK.textFaint, 18)}
          <span style={{ fontSize: 9, fontWeight: act ? 700 : 500, letterSpacing: 0.3 }}>{lb.toUpperCase()}</span>
        </button>
      ))}
    </div>
  </Phone>
);

const TImport = ({ nav }) => {
  const [sel, setSel] = useState([0]);
  const cats = [
    { name: "Equipos Sprint 1", g: 8, m: 32, sync: "Ayer", ok: true },
    { name: "Equipos Proyecto Final", g: 10, m: 40, sync: "Nunca", ok: false },
    { name: "Grupos de Estudio", g: 4, m: 16, sync: "Hace 5 días", ok: true },
  ];
  return (
    <Phone bg={TK.bg} shadow={`0 40px 100px rgba(201,168,76,0.2), 0 0 0 1px ${TK.border}`}>
      <StatusBar />
      {/* Header */}
      <div style={{ padding: "4px 22px 20px", flexShrink: 0 }}>
        <button onClick={() => nav("tDash")} style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 16, color: TK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(TK.textMid, 14)} Volver
        </button>
        <div style={{ fontSize: 20, fontWeight: 800, color: TK.text, letterSpacing: -0.5 }}>Importar grupos</div>
        <div style={{ fontSize: 12, color: TK.textFaint, marginTop: 4, fontFamily: mono }}>Desde Brightspace · DM2610</div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 24px" }}>
        {/* Connected badge */}
        <div style={{ background: `${TK.success}15`, border: `1px solid ${TK.success}30`, borderRadius: 10, padding: "9px 14px", marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: TK.success, flexShrink: 0 }} />
          <span style={{ fontSize: 11, fontWeight: 600, color: TK.success }}>Conectado a Brightspace · 3 categorías disponibles</span>
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>CATEGORÍAS</div>

        {cats.map((c, i) => (
          <div key={i} onClick={() => setSel(prev => prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i])}
            style={{ background: sel.includes(i) ? `${TK.gold}12` : TK.surface, border: `1px solid ${sel.includes(i) ? TK.gold : TK.border}`, borderRadius: 14, padding: 14, marginBottom: 10, cursor: "pointer", transition: "all 0.18s" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 22, height: 22, borderRadius: 7, background: sel.includes(i) ? TK.gold : TK.elevated, border: `1px solid ${sel.includes(i) ? TK.gold : TK.border}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "all 0.18s" }}>
                {sel.includes(i) && Icon.check("#0E1117", 12)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: TK.text }}>{c.name}</div>
                <div style={{ fontSize: 11, color: TK.textFaint, marginTop: 2, fontFamily: mono }}>{c.g} grupos · {c.m} estudiantes</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 9, color: TK.textFaint, letterSpacing: 0.5, fontWeight: 500 }}>SYNC</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: c.ok ? TK.success : TK.danger, marginTop: 1 }}>{c.sync}</div>
              </div>
            </div>
          </div>
        ))}

        <div style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 12, padding: 12, marginBottom: 20 }}>
          <div style={{ fontSize: 11, color: TK.textFaint, lineHeight: 1.5 }}>Si hay una evaluación activa, los cambios de grupo se aplicarán al cerrarla.</div>
        </div>

        <button className="btn-hover" onClick={() => nav("tDash")} style={{ width: "100%", background: TK.gold, color: "#0E1117", border: "none", borderRadius: 14, padding: "14px 0", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
          Importar {sel.length} categoría{sel.length !== 1 ? "s" : ""}
        </button>
      </div>
    </Phone>
  );
};

const TNew = ({ nav }) => {
  const [vis, setVis] = useState("private");
  const [hours, setHours] = useState("48");
  return (
    <Phone bg={TK.bg} shadow={`0 40px 100px rgba(201,168,76,0.2), 0 0 0 1px ${TK.border}`}>
      <StatusBar />
      <div style={{ padding: "4px 22px 16px", flexShrink: 0 }}>
        <button onClick={() => nav("tDash")} style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 16, color: TK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(TK.textMid, 14)} Volver
        </button>
        <div style={{ fontSize: 20, fontWeight: 800, color: TK.text, letterSpacing: -0.5 }}>Nueva evaluación</div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 24px" }}>
        {/* Nombre */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 8 }}>NOMBRE</div>
          <div style={{ background: TK.elevated, border: `1px solid ${TK.gold}50`, borderRadius: 13, padding: "13px 15px", fontSize: 14, fontWeight: 600, color: TK.text }}>Sprint 2 Review</div>
        </div>

        {/* Categoría */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 8 }}>CATEGORÍA DE GRUPOS</div>
          <div style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 13, padding: "13px 15px", fontSize: 13, color: TK.textMid, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Equipos Sprint 1</span>
            {Icon.chevronRight(TK.textFaint)}
          </div>
        </div>

        {/* Ventana */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 8 }}>VENTANA DE TIEMPO</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 6 }}>
            {["24", "48", "72", "168"].map(h => (
              <button key={h} onClick={() => setHours(h)} style={{ padding: "10px 0", borderRadius: 10, background: hours === h ? TK.gold : TK.elevated, color: hours === h ? "#0E1117" : TK.textMid, border: `1px solid ${hours === h ? TK.gold : TK.border}`, fontWeight: hours === h ? 700 : 500, fontSize: 12, cursor: "pointer", fontFamily: mono }}>
                {h}h
              </button>
            ))}
          </div>
        </div>

        {/* Visibilidad */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 8 }}>VISIBILIDAD DE RESULTADOS</div>
          {[
            { v: "public", icon: Icon.users, label: "Pública", desc: "Estudiantes ven sus promedios recibidos por criterio" },
            { v: "private", icon: Icon.lock, label: "Privada", desc: "Solo el docente accede a los resultados detallados" },
          ].map(opt => (
            <div key={opt.v} onClick={() => setVis(opt.v)} style={{ background: vis === opt.v ? `${TK.gold}12` : TK.elevated, border: `1px solid ${vis === opt.v ? TK.gold : TK.border}`, borderRadius: 13, padding: "13px 14px", display: "flex", alignItems: "center", gap: 12, marginBottom: 8, cursor: "pointer", transition: "all 0.18s" }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: vis === opt.v ? `${TK.gold}25` : TK.surface, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                {opt.icon(vis === opt.v ? TK.gold : TK.textFaint)}
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: vis === opt.v ? TK.gold : TK.text }}>{opt.label}</div>
                <div style={{ fontSize: 11, color: TK.textFaint, marginTop: 2 }}>{opt.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <button className="btn-hover" onClick={() => nav("tDash")} style={{ width: "100%", background: TK.gold, color: "#0E1117", border: "none", borderRadius: 14, padding: "15px 0", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
          Lanzar evaluación
        </button>
        <div style={{ fontSize: 11, color: TK.textFaint, textAlign: "center", marginTop: 10, fontFamily: mono }}>Se notificará a todos los estudiantes de Equipos Sprint 1</div>
      </div>
    </Phone>
  );
};

const TResults = ({ nav }) => {
  const [drill, setDrill] = useState(null);
  const groups = [
    { n: "Equipo Ágil 1", avg: 4.2, punct: 4.0, contrib: 4.5, commit: 4.1, attitude: 4.2 },
    { n: "Equipo Ágil 2", avg: 3.6, punct: 3.0, contrib: 3.8, commit: 3.7, attitude: 3.9 },
    { n: "Equipo Ágil 3", avg: 4.7, punct: 4.8, contrib: 4.6, commit: 4.6, attitude: 4.8 },
  ];
  const colors = ["#60A5FA", "#A78BFA", "#34D399", "#F9A8D4"];
  const g = drill !== null ? groups[drill] : null;
  return (
    <Phone bg={TK.bg} shadow={`0 40px 100px rgba(201,168,76,0.2), 0 0 0 1px ${TK.border}`}>
      <StatusBar />
      <div style={{ padding: "4px 22px 16px", flexShrink: 0 }}>
        <button onClick={() => drill !== null ? setDrill(null) : nav("tDash")} style={{ background: TK.elevated, border: `1px solid ${TK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 16, color: TK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(TK.textMid, 14)} {drill !== null ? "Grupos" : "Volver"}
        </button>
        <div style={{ fontSize: 20, fontWeight: 800, color: TK.text, letterSpacing: -0.5 }}>{g ? g.n : "Resultados"}</div>
        <div style={{ fontSize: 11, color: TK.textFaint, marginTop: 3, fontFamily: mono }}>Sprint 2 Review · {g ? "Desglose completo" : "Vista general"}</div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 20px" }}>
        {!g ? (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 20 }}>
              {[["4.1", "Promedio general", TK.gold], ["75%", "Completitud", TK.success]].map(([v,l,c]) => (
                <div key={l} style={{ background: TK.surface, border: `1px solid ${TK.border}`, borderRadius: 14, padding: "16px 14px" }}>
                  <div style={{ fontSize: 28, fontWeight: 800, color: c, fontFamily: mono }}>{v}</div>
                  <div style={{ fontSize: 10, color: TK.textFaint, marginTop: 4, fontWeight: 500, letterSpacing: 0.4 }}>{l.toUpperCase()}</div>
                </div>
              ))}
            </div>
            <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>GRUPOS — toca para detalle</div>
            {groups.map((gr, i) => (
              <div className="card-hover" key={i} onClick={() => setDrill(i)} style={{ background: TK.surface, border: `1px solid ${TK.border}`, borderRadius: 14, padding: "14px", marginBottom: 10, cursor: "pointer" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: TK.text }}>{gr.n}</div>
                  <div style={{ background: gr.avg >= 4 ? `${TK.success}20` : `${TK.warning}20`, color: gr.avg >= 4 ? TK.success : TK.warning, borderRadius: 8, padding: "4px 10px", fontSize: 15, fontWeight: 800, fontFamily: mono }}>{gr.avg}</div>
                </div>
                <ProgressBar pct={((gr.avg - 2) / 3) * 100} color={gr.avg >= 4 ? TK.success : TK.warning} bg={TK.elevated} h={3} />
              </div>
            ))}
          </>
        ) : (
          <>
            <div style={{ display: "flex", justifyContent: "center", gap: 14, marginBottom: 20, background: TK.surface, border: `1px solid ${TK.border}`, borderRadius: 16, padding: 18 }}>
              {[["Puntualidad", g.punct, colors[0]], ["Contrib.", g.contrib, colors[1]], ["Compromiso", g.commit, colors[2]], ["Actitud", g.attitude, colors[3]]].map(([l,v,c]) => (
                <ScoreRing key={l} value={v} color={c} bg={TK.elevated} size={60} stroke={4} label={l.substring(0,6).toUpperCase()} />
              ))}
            </div>
            <div style={{ fontSize: 11, fontWeight: 700, color: TK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>ESTUDIANTES</div>
            {[["M. García", 4.5, colors[0]], ["C. López", 3.8, colors[1]], ["J. Martínez", 4.2, colors[2]], ["A. Torres", 4.0, colors[3]]].map(([n,v,c]) => (
              <div key={n} style={{ background: TK.surface, border: `1px solid ${TK.border}`, borderRadius: 13, padding: "12px 14px", marginBottom: 8, display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 34, height: 34, borderRadius: 10, background: `${c}25`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 800, color: c }}>{n[0]}</div>
                <div style={{ flex: 1, fontSize: 13, fontWeight: 600, color: TK.text }}>{n}</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: v >= 4 ? TK.success : TK.warning, fontFamily: mono }}>{v}</div>
              </div>
            ))}
          </>
        )}
      </div>
    </Phone>
  );
};

// ═══════════════════════════════════════════════════════════════════
// STUDENT APP SCREENS
// ═══════════════════════════════════════════════════════════════════

const SLogin = ({ nav }) => (
  <Phone bg={SK.surface} shadow={`0 40px 100px rgba(13,102,85,0.18), 0 0 0 1px ${SK.border}`}>
    <StatusBar light={false} />
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "12px 28px 40px" }}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        <div style={{ marginBottom: 40 }}>
          <div style={{ width: 52, height: 52, background: SK.primaryLight, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
            <div style={{ width: 22, height: 22, borderRadius: "50%", background: SK.primary }} />
          </div>
          <div style={{ fontSize: 26, fontWeight: 800, color: SK.text, letterSpacing: -0.8, lineHeight: 1.1 }}>PeerEval</div>
          <div style={{ fontSize: 12, fontWeight: 500, color: SK.textFaint, letterSpacing: 3, textTransform: "uppercase", marginTop: 4 }}>Student</div>
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: SK.textMid, marginBottom: 6, letterSpacing: 0.3 }}>USUARIO INSTITUCIONAL</div>
          <div style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 14, padding: "13px 16px", fontSize: 13, color: SK.text, fontFamily: mono, marginBottom: 14 }}>
            m.garcia@uninorte.edu.co
          </div>
          <div style={{ fontSize: 13, fontWeight: 600, color: SK.textMid, marginBottom: 6, letterSpacing: 0.3 }}>CONTRASEÑA</div>
          <div style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 14, padding: "13px 16px", display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
            <div style={{ flex: 1, display: "flex", gap: 5 }}>
              {[...Array(8)].map((_, i) => <div key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: SK.borderMid }} />)}
            </div>
            {Icon.lock(SK.textFaint)}
          </div>
          <button className="btn-hover" onClick={() => nav("sCourses")} style={{ width: "100%", background: SK.primary, color: "#fff", border: "none", borderRadius: 14, padding: "15px 0", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
            Iniciar sesión
          </button>
          <div style={{ textAlign: "center", marginTop: 16, fontSize: 11, color: SK.textFaint, fontFamily: mono }}>Rol ESTUDIANTE · Roble SSO</div>
        </div>
      </div>
    </div>
  </Phone>
);

const SCourses = ({ nav }) => (
  <Phone bg={SK.surface} shadow={`0 40px 100px rgba(13,102,85,0.18), 0 0 0 1px ${SK.border}`}>
    <StatusBar light={false} />
    <div style={{ padding: "4px 22px 20px", flexShrink: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 500, color: SK.textFaint, letterSpacing: 0.4, marginBottom: 4 }}>Mis cursos</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: SK.text, letterSpacing: -0.5 }}>María García</div>
        </div>
        <div style={{ width: 40, height: 40, borderRadius: 13, background: SK.primaryLight, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontSize: 11, fontWeight: 800, color: SK.primary, fontFamily: mono }}>MG</div>
        </div>
      </div>
    </div>

    <div style={{ ...scroll, padding: "0 22px 16px" }}>
      {/* Active eval banner */}
      <div style={{ background: SK.primary, borderRadius: 18, padding: 18, marginBottom: 18, cursor: "pointer" }} onClick={() => nav("sEvalList")}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
              <div className="live-dot" style={{ width: 7, height: 7, borderRadius: "50%", background: "#fff" }} />
              <span style={{ fontSize: 10, fontWeight: 700, color: "rgba(255,255,255,0.75)", letterSpacing: 1.5 }}>EVALUACIÓN ACTIVA</span>
            </div>
            <div style={{ fontSize: 16, fontWeight: 800, color: "#fff", lineHeight: 1.2 }}>Sprint 2 Review</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.65)", marginTop: 4 }}>Desarrollo Móvil · Cierra en 12h</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginBottom: 2 }}>Progreso</div>
            <div style={{ fontSize: 22, fontWeight: 800, color: "#fff", fontFamily: mono }}>0/3</div>
          </div>
        </div>
        <ProgressBar pct={0} color="rgba(255,255,255,0.8)" bg="rgba(255,255,255,0.2)" h={3} />
        <div style={{ marginTop: 14, background: "rgba(255,255,255,0.15)", borderRadius: 10, padding: "9px 14px", textAlign: "center", fontSize: 12, fontWeight: 700, color: "#fff", cursor: "pointer" }}>
          Evaluar ahora
        </div>
      </div>

      <div style={{ fontSize: 11, fontWeight: 700, color: SK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>CURSOS ACTIVOS</div>
      {[
        { name: "Desarrollo Móvil 2026-10", group: "Equipo Ágil 3", members: 4 },
        { name: "Arquitectura de Software", group: "Grupo Backend", members: 3 },
      ].map(c => (
        <div className="card-hover" key={c.name} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 16, padding: 16, marginBottom: 10 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: SK.text }}>{c.name}</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 4, marginBottom: 12 }}>
            {Icon.users(SK.textFaint, 12)}
            <span style={{ fontSize: 11, color: SK.textFaint }}>{c.group} · {c.members} integrantes</span>
          </div>
          <button className="btn-hover" onClick={() => nav("sMyResults")} style={{ width: "100%", background: SK.surface, color: SK.primary, border: `1px solid ${SK.border}`, borderRadius: 10, padding: "9px 0", fontSize: 12, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
            {Icon.barChart(SK.primary, 13)} Ver mis resultados
          </button>
        </div>
      ))}
    </div>

    <div style={{ display: "flex", background: SK.surface, borderTop: `1px solid ${SK.border}`, padding: "10px 0 20px", flexShrink: 0 }}>
      {[[Icon.home,"Inicio",true,null],[Icon.edit,"Evaluar",false,"sEvalList"],[Icon.star,"Resultados",false,"sMyResults"],[Icon.profile,"Perfil",false,null]].map(([Ic,lb,act,sc]) => (
        <button key={lb} onClick={() => sc && nav(sc)} style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", gap:3, background:"none", border:"none", cursor:"pointer", color: act ? SK.primary : SK.textFaint }}>
          {Ic(act ? SK.primary : SK.textFaint, 18)}
          <span style={{ fontSize: 9, fontWeight: act ? 700 : 500, letterSpacing: 0.3 }}>{lb.toUpperCase()}</span>
        </button>
      ))}
    </div>
  </Phone>
);

const SEvalList = ({ nav }) => {
  const [done, setDone] = useState([]);
  const peers = [
    { name: "Carlos López", initials: "CL" },
    { name: "Juan Martínez", initials: "JM" },
    { name: "Ana Torres", initials: "AT" },
  ];
  return (
    <Phone bg={SK.surface} shadow={`0 40px 100px rgba(13,102,85,0.18), 0 0 0 1px ${SK.border}`}>
      <StatusBar light={false} />
      <div style={{ padding: "4px 22px 16px", flexShrink: 0 }}>
        <button onClick={() => nav("sCourses")} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 16, color: SK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(SK.textMid, 14)} Volver
        </button>
        <div style={{ fontSize: 20, fontWeight: 800, color: SK.text, letterSpacing: -0.5 }}>Sprint 2 Review</div>
        <div style={{ fontSize: 11, color: SK.textFaint, marginTop: 3, fontFamily: mono }}>Equipo Ágil 3 · {done.length}/{peers.length} evaluados</div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 24px" }}>
        {/* Timer card */}
        <div style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 14, padding: "14px 16px", marginBottom: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {Icon.clock(SK.textMid)}
              <span style={{ fontSize: 13, fontWeight: 700, color: SK.text }}>Cierra en 12h 30m</span>
            </div>
            <div style={{ fontSize: 22, fontWeight: 800, color: SK.primary, fontFamily: mono }}>{Math.round((done.length / peers.length) * 100)}%</div>
          </div>
          <ProgressBar pct={(done.length / peers.length) * 100} color={SK.primary} bg={SK.border} h={3} />
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, color: SK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>COMPAÑEROS A EVALUAR</div>

        {peers.map((p, i) => (
          <div className="card-hover" key={i} onClick={() => nav("sPeerScore")}
            style={{ background: done.includes(i) ? SK.primaryLight : SK.surface, border: `1px solid ${done.includes(i) ? SK.primaryMid : SK.border}`, borderRadius: 14, padding: 16, marginBottom: 10, cursor: "pointer" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 13 }}>
              <div style={{ width: 42, height: 42, borderRadius: 13, background: done.includes(i) ? SK.primary : SK.surfaceAlt, border: `1px solid ${done.includes(i) ? SK.primary : SK.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: done.includes(i) ? "#fff" : SK.textMid, fontFamily: mono, flexShrink: 0 }}>
                {done.includes(i) ? Icon.check("#fff", 16) : p.initials}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: SK.text }}>{p.name}</div>
                <div style={{ fontSize: 11, color: done.includes(i) ? SK.primary : SK.textFaint, marginTop: 2, fontWeight: done.includes(i) ? 600 : 400 }}>
                  {done.includes(i) ? "Evaluado" : "Pendiente"}
                </div>
              </div>
              {!done.includes(i) && Icon.chevronRight(SK.textFaint)}
            </div>
          </div>
        ))}

        {done.length === peers.length && (
          <button className="btn-hover" onClick={() => nav("sCourses")} style={{ width: "100%", background: SK.primary, color: "#fff", border: "none", borderRadius: 14, padding: "14px 0", fontSize: 14, fontWeight: 700, cursor: "pointer", marginTop: 8 }}>
            Enviar evaluación completa
          </button>
        )}
      </div>
    </Phone>
  );
};

const SPeerScore = ({ nav }) => {
  const [scores, setScores] = useState({});
  const criteria = [
    { k: "punct", label: "Puntualidad", color: "#0EA5E9" },
    { k: "contrib", label: "Contribuciones", color: "#8B5CF6" },
    { k: "commit", label: "Compromiso", color: SK.success },
    { k: "attitude", label: "Actitud", color: "#F59E0B" },
  ];
  const levels = ["Necesita Mejorar", "Adecuado", "Bueno", "Excelente"];
  const allDone = criteria.every(c => scores[c.k]);
  return (
    <Phone bg={SK.surface} shadow={`0 40px 100px rgba(13,102,85,0.18), 0 0 0 1px ${SK.border}`}>
      <StatusBar light={false} />
      <div style={{ padding: "4px 22px 14px", flexShrink: 0 }}>
        <button onClick={() => nav("sEvalList")} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 14, color: SK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(SK.textMid, 14)} Lista
        </button>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 42, height: 42, borderRadius: 13, background: SK.primaryLight, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13, fontWeight: 700, color: SK.primary, fontFamily: mono }}>CL</div>
          <div>
            <div style={{ fontSize: 17, fontWeight: 800, color: SK.text }}>Carlos López</div>
            <div style={{ fontSize: 11, color: SK.textFaint, fontFamily: mono }}>{Object.keys(scores).length}/4 criterios</div>
          </div>
        </div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 24px" }}>
        {criteria.map(c => (
          <div key={c.k} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 14, padding: 14, marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: SK.text }}>{c.label}</div>
              {scores[c.k] && (
                <div style={{ background: `${c.color}20`, borderRadius: 8, padding: "3px 9px" }}>
                  <span style={{ fontSize: 12, fontWeight: 800, color: c.color, fontFamily: mono }}>{scores[c.k]}.0</span>
                </div>
              )}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 5 }}>
              {[2,3,4,5].map((v,i) => (
                <button key={v} onClick={() => setScores(p => ({ ...p, [c.k]: v }))} style={{
                  padding: "9px 0", borderRadius: 9, cursor: "pointer",
                  background: scores[c.k] === v ? c.color : SK.surface,
                  color: scores[c.k] === v ? "#fff" : SK.textFaint,
                  border: `1px solid ${scores[c.k] === v ? c.color : SK.border}`,
                  fontWeight: 700, fontSize: 13, fontFamily: mono, transition: "all 0.15s",
                }}>{v}</button>
              ))}
            </div>
            <div style={{ fontSize: 10, color: SK.textFaint, marginTop: 6, textAlign: "center", fontFamily: mono, letterSpacing: 0.3 }}>
              {scores[c.k] ? levels[scores[c.k] - 2].toUpperCase() : "— SELECCIONA UN NIVEL —"}
            </div>
          </div>
        ))}
        <button className="btn-hover" onClick={() => { if (allDone) nav("sEvalList"); }} style={{ width: "100%", background: allDone ? SK.primary : SK.border, color: allDone ? "#fff" : SK.textFaint, border: "none", borderRadius: 14, padding: "14px 0", fontSize: 14, fontWeight: 700, cursor: allDone ? "pointer" : "default" }}>
          {allDone ? "Guardar y continuar" : "Completa los 4 criterios"}
        </button>
      </div>
    </Phone>
  );
};

const SMyResults = ({ nav }) => {
  const criteria = [
    { label: "Puntualidad", val: 4.5, color: "#0EA5E9" },
    { label: "Contribuciones", val: 3.8, color: "#8B5CF6" },
    { label: "Compromiso", val: 4.3, color: SK.success },
    { label: "Actitud", val: 4.7, color: "#F59E0B" },
  ];
  const avg = (criteria.reduce((s, c) => s + c.val, 0) / 4).toFixed(2);
  return (
    <Phone bg={SK.surface} shadow={`0 40px 100px rgba(13,102,85,0.18), 0 0 0 1px ${SK.border}`}>
      <StatusBar light={false} />
      <div style={{ padding: "4px 22px 14px", flexShrink: 0 }}>
        <button onClick={() => nav("sCourses")} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 10, padding: "7px 12px 7px 8px", display: "flex", alignItems: "center", gap: 6, cursor: "pointer", marginBottom: 14, color: SK.textMid, fontSize: 12, fontWeight: 600 }}>
          {Icon.chevronLeft(SK.textMid, 14)} Volver
        </button>
        <div style={{ fontSize: 20, fontWeight: 800, color: SK.text, letterSpacing: -0.5 }}>Mis resultados</div>
        <div style={{ fontSize: 11, color: SK.textFaint, marginTop: 3, fontFamily: mono }}>Sprint 2 Review · Visibilidad pública</div>
      </div>

      <div style={{ ...scroll, padding: "0 22px 24px" }}>
        {/* Hero */}
        <div style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 18, padding: "24px 20px", marginBottom: 20, textAlign: "center" }}>
          <div style={{ fontSize: 52, fontWeight: 800, color: SK.primary, fontFamily: mono, letterSpacing: -1 }}>{avg}</div>
          <div style={{ fontSize: 12, color: SK.textFaint, marginTop: 6, fontWeight: 500 }}>Promedio general recibido</div>
          <div style={{ marginTop: 14, background: `${SK.success}15`, border: `1px solid ${SK.success}30`, borderRadius: 10, padding: "8px 16px", display: "inline-block" }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: SK.success, letterSpacing: 0.3 }}>Excelente desempeño</span>
          </div>
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, color: SK.textFaint, letterSpacing: 1.5, marginBottom: 10 }}>DESGLOSE POR CRITERIO</div>
        {criteria.map(c => (
          <div key={c.label} style={{ background: SK.surfaceAlt, border: `1px solid ${SK.border}`, borderRadius: 14, padding: 14, marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
              <div style={{ width: 4, height: 28, borderRadius: 2, background: c.color, flexShrink: 0 }} />
              <div style={{ flex: 1, fontSize: 13, fontWeight: 700, color: SK.text }}>{c.label}</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: c.color, fontFamily: mono }}>{c.val}</div>
            </div>
            <ProgressBar pct={((c.val - 2) / 3) * 100} color={c.color} bg={SK.border} h={5} />
          </div>
        ))}
      </div>
    </Phone>
  );
};

// ─── REGISTRIES ──────────────────────────────────────────────────────────────
const TEACHER = { tLogin: TLogin, tDash: TDash, tImport: TImport, tNew: TNew, tResults: TResults };
const STUDENT  = { sLogin: SLogin, sCourses: SCourses, sEvalList: SEvalList, sPeerScore: SPeerScore, sMyResults: SMyResults };

// ─── MAIN ────────────────────────────────────────────────────────────────────
export default function PeerEvalDuo() {
  const [tS, setTS] = useState("tLogin");
  const [sS, setSS] = useState("sLogin");

  const TS = TEACHER[tS] || TLogin;
  const SS = STUDENT[sS]  || SLogin;

  const tNav = [["Login","tLogin"],["Dashboard","tDash"],["Grupos","tImport"],["Evaluación","tNew"],["Resultados","tResults"]];
  const sNav = [["Login","sLogin"],["Cursos","sCourses"],["Evaluar","sEvalList"],["Criterios","sPeerScore"],["Resultados","sMyResults"]];

  const NavBar = ({ items, active, onNav, accent }) => (
    <div style={{ display: "flex", gap: 5, justifyContent: "center", flexWrap: "wrap" }}>
      {items.map(([lb, sc]) => (
        <button key={sc} onClick={() => onNav(sc)} className="nav-pill" style={{
          background: active === sc ? accent : "rgba(255,255,255,0.07)",
          color: active === sc ? "#0E1117" : "rgba(255,255,255,0.55)",
          border: `1px solid ${active === sc ? accent : "rgba(255,255,255,0.12)"}`,
          borderRadius: 20, padding: "5px 13px", fontSize: 11, fontWeight: active === sc ? 700 : 500,
          cursor: "pointer", fontFamily: ff, letterSpacing: 0.2,
        }}>{lb}</button>
      ))}
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(150deg, #080C14 0%, #0E1520 50%, #090D18 100%)", display: "flex", flexDirection: "column", alignItems: "center", padding: "44px 24px 56px", fontFamily: ff }}>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 44 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center", marginBottom: 10 }}>
          <div style={{ width: 2, height: 28, background: `linear-gradient(${TK.gold}, transparent)`, borderRadius: 1 }} />
          <div style={{ fontSize: 26, fontWeight: 800, color: "#fff", letterSpacing: -0.8 }}>PeerEval Dúo</div>
          <div style={{ width: 2, height: 28, background: `linear-gradient(${SK.primary}, transparent)`, borderRadius: 1 }} />
        </div>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.3)", fontWeight: 400, letterSpacing: 0.3 }}>Propuesta 2 · Dos apps independientes · Dominio compartido via peereval_core</div>
      </div>

      {/* Nav rows */}
      <div style={{ display: "flex", gap: 80, marginBottom: 32, flexWrap: "wrap", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: TK.gold, letterSpacing: 2.5, marginBottom: 10 }}>PEEREVAL TEACHER</div>
          <NavBar items={tNav} active={tS} onNav={setTS} accent={TK.gold} />
        </div>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: SK.primaryMid, letterSpacing: 2.5, marginBottom: 10 }}>PEEREVAL STUDENT</div>
          <NavBar items={sNav} active={sS} onNav={setSS} accent={"#5EEAD4"} />
        </div>
      </div>

      {/* Phones */}
      <div style={{ display: "flex", gap: 52, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "center" }}>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
          <TS nav={setTS} />
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: TK.gold, letterSpacing: 1.5, marginBottom: 3 }}>TEACHER</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)" }}>Slate oscuro · Acento dorado</div>
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
          <SS nav={setSS} />
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: "#5EEAD4", letterSpacing: 1.5, marginBottom: 3 }}>STUDENT</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)" }}>Fondo blanco · Acento verde</div>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 48, fontSize: 11, color: "rgba(255,255,255,0.15)", textAlign: "center", maxWidth: 500, lineHeight: 1.6 }}>
        Navega cada app de forma independiente usando los controles superiores o tocando los elementos de cada pantalla
      </div>
    </div>
  );
}
