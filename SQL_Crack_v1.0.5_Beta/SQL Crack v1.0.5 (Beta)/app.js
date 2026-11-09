"use strict";
const $ = id => document.getElementById(id);
const FEATURES = [
  "Tek tık CMD başlatıcısı", "Python 3 denetimi", "Otomatik port seçimi", "Tarayıcıyı otomatik açma", "Özel uygulama logosu",
  "Neon hacker arayüzü", "Mobil uyumlu tasarım", "Sabit v1.0.5 (Beta) etiketi", "4 demo hedefi", "6 simülasyon senaryosu",
  "Yerel metin analizi", "Canlı terminal akışı", "Toplam olay istatistiği", "Uyarı sayacı", "Sunucu bağlantı göstergesi",
  "Diske kaydedilen günlükler", "Günlüklerde anlık arama", "Seviye filtresi", "Tarih filtresi", "Günlük sayfalama",
  "JSON rapor indirme", "CSV rapor indirme", "Sahte SQL dump kaydı", "Dump indirme ve silme", "Günlük temizleme ve kısayollar", "İzinli HTTP kontrolü", "Rastgele zararsız HTTP parametreleri", "Kesin URL izin listesi", "Hız ve istek limiti",
  "Sunucu sağlık monitörü", "24 saatlik karşılaştırmalı raporlar", "Akıllı güvenlik ve kota uyarıları"
];
const state = { logs: [], dumps: [], page: 1, pageSize: 8, connected: false, busy: false, lastAction: null, autoRefresh: true };
let toastTimer;
let refreshEpoch = 0;

function toast(message, error = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast show" + (error ? " error" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = "toast"; }, 3200);
}

async function request(path, opts = {}) {
  // A stalled request should not leave buttons disabled forever.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 25000);
  try {
    const response = await fetch(path, { cache: "no-store", ...opts, signal: controller.signal });
    let body;
    try { body = await response.json(); }
    catch { throw Error("Sunucudan geçersiz yanıt geldi."); }
    if (!response.ok || !body.ok) throw Error(body.error || `HTTP ${response.status}`);
    return body;
  } catch (error) {
    if (error.name === "AbortError") throw Error("İstek zaman aşımına uğradı. Sunucuyu kontrol et.");
    if (error instanceof TypeError) throw Error("Sunucuya bağlanılamadı. Başlatıcıyı kontrol et.");
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function line(tag, msg, severity = "normal") {
  const container = $("terminal");
  const d = document.createElement("div");
  d.className = "term-line" + (severity === "warn" ? " warn" : "");
  const prefix = document.createElement("span");
  prefix.className = "term-stamp";
  prefix.textContent = `[${tag}]`;
  d.append(prefix, document.createTextNode(` ${msg}`));
  container.append(d);
  while (container.children.length > 120) container.firstElementChild.remove();
  container.scrollTop = container.scrollHeight;
}

function formatTime(value) {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString("tr-TR", {day:"2-digit",month:"2-digit",year:"numeric",hour:"2-digit",minute:"2-digit",second:"2-digit"});
}

function renderMetrics() {
  $("metricTotal").textContent = state.logs.length.toLocaleString("tr-TR");
  $("metricWarn").textContent = state.logs.filter(x => x.level === "WARNING").length.toLocaleString("tr-TR");
  $("metricDumps").textContent = String(state.dumps.length);
  $("metricStatus").textContent = state.connected ? "AKTİF" : "ÇEVRİMDIŞI";
  $("connectionText").textContent = state.connected ? "SİSTEM AKTİF" : "BAĞLANTI YOK";
  $("connDot").classList.toggle("online", state.connected);
}

function filteredLogs() {
  const q = $("searchLogs").value.trim().toLocaleLowerCase("tr-TR");
  const lvl = $("filterLevel").value;
  const date = $("filterDate").value;
  const now = Date.now();
  return state.logs.filter(log => {
    if (lvl !== "ALL" && log.level !== lvl) return false;
    if (date !== "all") {
      const ts = new Date(log.time).getTime();
      if (Number.isNaN(ts)) return false;
      if (date === "today" && new Date(log.time).toDateString() !== new Date().toDateString()) return false;
      if (date === "week" && (now - ts > 7 * 86400000 || ts > now)) return false;
    }
    if (q && ![log.target,log.scenario,log.level,log.result,log.id].join(" ").toLocaleLowerCase("tr-TR").includes(q)) return false;
    return true;
  }).reverse();
}

function renderLogs() {
  const logs = filteredLogs();
  const max = Math.max(1, Math.ceil(logs.length / state.pageSize));
  state.page = Math.max(1, Math.min(max, state.page));
  const selected = logs.slice((state.page - 1) * state.pageSize, state.page * state.pageSize);
  $("logBody").replaceChildren();
  $("visibleCount").textContent = String(logs.length);
  $("pageInfo").textContent = `${logs.length} kayıt (filtrelenmiş)`;
  $("pageNumber").textContent = `${state.page} / ${max}`;
  $("prevPage").disabled = state.page <= 1;
  $("nextPage").disabled = state.page >= max;
  if (!selected.length) {
    const row = document.createElement("tr"), td = document.createElement("td");
    td.colSpan = 5; td.className = "empty-row";
    td.textContent = "Henüz eşleşen kayıt yok. Bir simülasyon çalıştırabilirsin.";
    row.append(td); $("logBody").append(row);
  }
  for (const event of selected) {
    const row = document.createElement("tr");
    for (const val of [formatTime(event.time),event.target,event.scenario,event.level,event.result]) {
      const td = document.createElement("td");
      if (val === event.level) {
        const badge = document.createElement("span"); badge.className = `level ${event.level === "WARNING" ? "WARNING" : "INFO"}`;
        badge.textContent = val; td.append(badge);
      } else { td.textContent = String(val ?? ""); }
      row.append(td);
    }
    $("logBody").append(row);
  }
}

function renderDumps() {
  const list = $("dumpList"); list.replaceChildren();
  $("dumpCount").textContent = String(state.dumps.length);
  if (!state.dumps.length) {
    const empty = document.createElement("div");
    empty.className = "archive-empty";
    empty.textContent = "Henüz demo dump yok. Test Laboratuvarı'ndan sahte SQL dump senaryosunu seç.";
    list.append(empty); return;
  }
  for (const dump of state.dumps) {
    const item = document.createElement("div"); item.className = "dump-item";
    const icon = document.createElement("div"); icon.className = "dump-symbol"; icon.textContent = "▣";
    const meta = document.createElement("div"); meta.className = "dump-text";
    const title = document.createElement("strong"); title.textContent = dump.name;
    const small = document.createElement("small"); small.textContent = `${formatTime(dump.created)} · ${dump.bytes} byte · SAHTE EĞİTİM VERİSİ`;
    meta.append(title,small);
    const actions = document.createElement("div"); actions.className = "dump-actions";
    const download = document.createElement("a"); download.href = `/api/dump?name=${encodeURIComponent(dump.name)}`;
    download.textContent = "↓ İNDİR"; download.setAttribute("download",dump.name);
    const remove = document.createElement("button"); remove.textContent = "SİL"; remove.type = "button";
    remove.addEventListener("click", () => removeDump(dump.name));
    actions.append(download,remove); item.append(icon,meta,actions); list.append(item);
  }
}

function renderChart() {
  const end = new Date(); end.setHours(0,0,0,0);
  const daily = Array.from({length:7},(_,i) => {
    const day = new Date(end); day.setDate(day.getDate() - (6 - i));
    return {day, count:0};
  });
  state.logs.forEach(entry => {
    const eventDay = new Date(entry.time);
    if (Number.isNaN(eventDay.getTime())) return;
    eventDay.setHours(0,0,0,0);
    const match = daily.find(d => d.day.getTime() === eventDay.getTime());
    if (match) match.count++;
  });
  const max = Math.max(1,...daily.map(x=>x.count));
  $("chart").replaceChildren();
  daily.forEach(d => {
    const col = document.createElement("div"); col.className="chart-col";
    const num = document.createElement("span"); num.className="chart-num"; num.textContent=String(d.count);
    const bar = document.createElement("div"); bar.className="chart-bar";
    bar.style.height=`${Math.max(3, Math.round(d.count / max * 92))}px`;
    const day = document.createElement("span"); day.className="chart-day";
    day.textContent=d.day.toLocaleDateString("tr-TR",{weekday:"short"});
    col.append(num,bar,day); $("chart").append(col);
  });
}

function renderAll() { renderMetrics(); renderLogs(); renderDumps(); renderChart(); }


function formatUptime(seconds) {
  if (!Number.isFinite(seconds)) return "—";
  const h = Math.floor(seconds / 3600), m = Math.floor((seconds % 3600) / 60);
  return h ? `${h} sa ${m} dk` : `${m} dk ${Math.floor(seconds % 60)} sn`;
}

function renderMonitor(m) {
  $("monitorHealth").textContent = m.online ? "ÇALIŞIYOR" : "KAPALI";
  $("monitorUptime").textContent = formatUptime(m.uptime_seconds);
  $("monitorRequests").textContent = String(m.requests_total ?? "—");
  $("monitorLatency").textContent = m.average_local_ms === null ? "—" : `${m.average_local_ms} ms`;
  $("monitorErrors").textContent = String(m.recent_server_errors ?? "—");
}

function renderReports(r) {
  const c = r.current, p = r.previous;
  $("reportCurrent").textContent = String(c.events);
  $("reportPrevious").textContent = String(p.events);
  $("reportDelta").textContent = `${r.event_delta > 0 ? "+" : ""}${r.event_delta}`;
  $("reportCheckSuccess").textContent = c.success_percent === null ? "Veri yok" : `${c.success_percent}%`;
  $("reportDetail").textContent = `Son 24 saat: ${c.warnings} uyarı · ${c.checks} izinli GET kontrolü · Ortalama ${c.avg_probe_ms === null ? "veri yok" : c.avg_probe_ms + " ms"}`;
  const top = $("reportTop"); top.replaceChildren();
  if (!r.top_scenarios.length) { top.textContent = "Son 24 saatte test kaydı bulunmuyor."; return; }
  for (const item of r.top_scenarios) {
    const row = document.createElement("div"); row.className = "scenario-row";
    const label = document.createElement("span"); label.textContent = item.name;
    const count = document.createElement("strong"); count.textContent = `${item.events} olay`;
    row.append(label,count); top.append(row);
  }
}

function renderSafety(s) {
  $("safetyStatus").textContent = s.status;
  $("safetyStatus").classList.toggle("guard-warning",s.status !== "KORUNUYOR");
  $("safetyApproved").textContent = String(s.approved_urls);
  $("safetyBlocked").textContent = String(s.blocked_last_hour);
  $("safetyRemaining").textContent = `${s.rate_limit.remaining}/${s.rate_limit.limit_per_minute}`;
  $("safetyFailures").textContent = String(s.consecutive_failed_probes);
  const box = $("safetyAlerts"); box.replaceChildren();
  if (!s.alerts.length) { box.textContent = "✓ Kapsam ve istek sınırı kontrolleri etkin. Aktif uyarı yok."; return; }
  for (const alert of s.alerts) {
    const item = document.createElement("div"); item.className = "safety-warning";
    item.textContent = "⚠ " + alert; box.append(item);
  }
}

async function refreshInsights(epoch) {
  const results = await Promise.allSettled([
    request("/api/monitor"), request("/api/reports"), request("/api/safety")
  ]);
  if (epoch !== refreshEpoch) return;
  if (results[0].status === "fulfilled") renderMonitor(results[0].value.monitor);
  if (results[1].status === "fulfilled") renderReports(results[1].value.report);
  if (results[2].status === "fulfilled") renderSafety(results[2].value.safety);
  if (results.some(x => x.status === "rejected")) {
    line("WARN", "Analiz panellerinden biri güncellenemedi.", "warn");
  }
}

async function refresh() {
  const epoch = ++refreshEpoch;
  try {
    const data = await request("/api/state");
    if (epoch !== refreshEpoch) return;
    state.logs = Array.isArray(data.logs) ? data.logs : [];
    state.dumps = Array.isArray(data.dumps) ? data.dumps : [];
    state.connected = true;
    renderAll();
    await refreshInsights(epoch);
  } catch(e) {
    if (epoch !== refreshEpoch) return;
    const wasOnline = state.connected;
    state.connected = false;
    renderMetrics();
    if (wasOnline) { line("ERROR", "Sunucu bağlantısı kesildi.", "warn"); toast(e.message,true); }
  }
}

async function runSimulation(replay = false) {
  if (state.busy) return;
  if (!state.connected) return toast("Sunucu bağlantısı yok. BAT başlatıcısını kontrol et.",true);
  state.busy = true;
  $("runBtn").disabled = true;
  $("runText").textContent = "⏳ SİMÜLASYON ÇALIŞIYOR";
  try {
    const key = replay && state.lastAction ? state.lastAction.scenario : $("scenario").value;
    const target = replay && state.lastAction ? state.lastAction.target : $("target").value;
    const input = replay && state.lastAction ? state.lastAction.input : $("inputText").value;
    const data = await request("/api/run", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({scenario:key,target,input})
    });
    state.lastAction = {scenario:key,target,input};
    $("rerunBtn").disabled = false;
    $("replayHint").textContent = "Son senaryo tekrar çalıştırılabilir";
    const event = data.event;
    line("SIM", `${event.target} → ${event.scenario}`);
    line(event.level, event.result, event.level === "WARNING" ? "warn" : "normal");
    if (data.dump) line("DUMP", `Sentetik dosya diske kaydedildi: ${data.dump}`);
    line("SAFE", "Gerçek SQL çalıştırılmadı. Dış hedefe ağ isteği gönderilmedi.");
    $("lastRun").textContent = `SON TEST: ${new Date().toLocaleTimeString("tr-TR")}`;
    state.page = 1;
    await refresh();
    toast(data.dump ? "Sahte SQL dump data/dumps içine kaydedildi." : "Simülasyon tamamlandı, olay kaydedildi.");
  } catch(e) { line("ERROR", e.message,"warn"); toast(e.message,true); }
  finally { state.busy=false; $("runBtn").disabled=false; $("runText").textContent="▶ SİMÜLASYONU BAŞLAT"; }
}

async function removeDump(name) {
  if (!confirm(`Bu sahte örnek dosya silinsin mi?\n${name}`)) return;
  try { await request("/api/dumps/delete",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name})});await refresh();toast("Örnek dosya silindi."); }
  catch(e) { toast(e.message,true); }
}

async function clearLogs() {
  if (!confirm("Kaydedilmiş tüm olay günlükleri silinsin mi? Dump dosyaları korunur.")) return;
  try { await request("/api/clear",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});state.page=1;await refresh();line("SYSTEM","Günlükler temizlendi.");toast("Olay günlükleri temizlendi."); }
  catch(e) { toast(e.message,true); }
}

function exportTerminal() {
  const content = Array.from($("terminal").children).map(n=>n.textContent).join("\n");
  const blob = new Blob([`SQL Crack v1.0.5 (Beta) - Terminal Çıktısı\n\n${content}\n`], {type:"text/plain;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "sql-crack-terminal.txt";
  document.body.append(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),2000);
  toast("Terminal çıktısı indirildi.");
}

async function runSafeProbe() {
  if (state.busy) return;
  if (!state.connected) return toast("Sunucu bağlantısı yok. Başlatıcıyı kontrol et.",true);
  const button = $("probeBtn");
  const confirmed = $("probeConfirm").checked;
  if (!confirmed) {toast("Test iznini onaylamalısın.",true);return;}
  const url = $("probeUrl").value.trim();
  const count = Number($("probeCount").value);
  state.busy = true;
  button.disabled = true;
  const previous = button.textContent;
  button.textContent = "KONTROL SÜRÜYOR...";
  $("probeResults").textContent = "İzinli URL üzerinde sınırlı GET kontrolü yapılıyor...";
  try {
    const data = await request("/api/safe-probe", {
      method:"POST",headers:{"Content-Type":"application/json"},
      body: JSON.stringify({url,count,confirmed})
    });
    $("probeResults").replaceChildren();
    const note=document.createElement("p"); note.textContent=data.report.note;
    $("probeResults").append(note);
    for (const check of data.report.checks) {
      const resultLine=document.createElement("div");
      resultLine.textContent=`${check.param} → HTTP ${check.status ?? "YANIT YOK"} · ${check.ms} ms`;
      $("probeResults").append(resultLine);
      line("PROBE", check.param + " HTTP " + (check.status ?? "YANIT YOK"));
    }
    toast("Güvenli HTTP kontrolü tamamlandı.");
    await refresh();
  } catch(error) {
    $("probeResults").textContent=error.message;
    toast(error.message,true);
    await refreshInsights(refreshEpoch);
  } finally {state.busy=false;button.disabled=false;button.textContent=previous;}
}

function init() {
  $("featureGrid").replaceChildren();
  FEATURES.forEach((label,i)=>{const div=document.createElement("div");div.className="feature";
    const n=document.createElement("strong");n.textContent=String(i+1).padStart(2,"0");
    const t=document.createElement("span");t.textContent=label;div.append(n,t);$("featureGrid").append(div);});
  $("probeUrl").value = `${location.origin}/api/health`;
  $("probeBtn").addEventListener("click",runSafeProbe);
  $("runBtn").addEventListener("click",()=>runSimulation(false));
  $("rerunBtn").addEventListener("click",()=>runSimulation(true));
  $("exportTerminal").addEventListener("click",exportTerminal);
  $("autoRefresh").addEventListener("change",e=>{
    state.autoRefresh=e.target.checked;
    toast(state.autoRefresh ? "Otomatik yenileme etkin." : "Otomatik yenileme duraklatıldı.");
    if (state.autoRefresh) refresh();
  });
  $("clearConsole").addEventListener("click",()=>{$("terminal").replaceChildren();line("SYSTEM","Terminal görünümü temizlendi. Disk kayıtları korundu.");});
  $("clearLogs").addEventListener("click",clearLogs);
  $("exportJson").addEventListener("click",()=>{location.href="/api/export?format=json";});
  $("exportCsv").addEventListener("click",()=>{location.href="/api/export?format=csv";});
  for(const id of ["searchLogs","filterLevel","filterDate"]) {
    $(id).addEventListener(id==="searchLogs"?"input":"change",()=>{state.page=1;renderLogs();});
  }
  $("prevPage").addEventListener("click",()=>{state.page--;renderLogs();});
  $("nextPage").addEventListener("click",()=>{state.page++;renderLogs();});
  $("inputText").addEventListener("input",()=>{$("chars").textContent=String($("inputText").value.length);});
  document.addEventListener("keydown",e=>{
    if(e.ctrlKey && e.key==="Enter") { e.preventDefault();runSimulation(); }
    if(e.key==="/" && !["INPUT","TEXTAREA","SELECT"].includes(document.activeElement.tagName)) {e.preventDefault();$("searchLogs").focus();}
  });
  const tick=()=>{$("clock").textContent=new Date().toLocaleTimeString("tr-TR",{hour12:false});};
  tick();setInterval(tick,1000);
  renderAll();refresh();setInterval(()=>{if(state.autoRefresh)refresh();},12000);
}

document.addEventListener("DOMContentLoaded",init);
