import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = 'http://localhost:5000/api';
const getToken = () => localStorage.getItem('token');
const authH = () => ({ headers: { Authorization: 'Bearer ' + getToken() } });

// Domain config injected by Organism
const APP_NAME = 'App';
const APP_ICON = '🏢';
const ENTITY = 'Record';
const ENTITIES = 'Records';
const NAV = [];
const FIELDS = [];
const COLS = [];

function Toast({ msg, type, onDone }) {
  useEffect(() => { const t = setTimeout(onDone, 3200); return () => clearTimeout(t); }, []);
  const c = { success:'#059669', error:'#dc2626', info:'#2563eb', warning:'#d97706' };
  return (
    <div style={{ position:'fixed', bottom:24, right:24, background:c[type]||c.success,
      color:'white', padding:'12px 20px', borderRadius:10, fontSize:14, zIndex:9999,
      boxShadow:'0 4px 20px rgba(0,0,0,0.2)', display:'flex', gap:10, alignItems:'center' }}>
      <span>{type==='error'?'✕':type==='warning'?'⚠':'✓'}</span><span>{msg}</span>
    </div>
  );
}

function Av({ name, size=36 }) {
  const bg = ['#0d7377','#7c3aed','#059669','#d97706','#dc2626','#2563eb'];
  return (
    <div style={{ width:size, height:size, borderRadius:'50%',
      background:bg[(name||'?').charCodeAt(0)%bg.length],
      display:'flex', alignItems:'center', justifyContent:'center',
      color:'white', fontWeight:600, fontSize:size*0.38, flexShrink:0 }}>
      {(name||'?').charAt(0).toUpperCase()}
    </div>
  );
}

function Badge({ label, type='gray' }) {
  const s = { green:{background:'#ecfdf5',color:'#059669'}, red:{background:'#fef2f2',color:'#dc2626'},
    blue:{background:'#eff6ff',color:'#2563eb'}, yellow:{background:'#fffbeb',color:'#d97706'},
    gray:{background:'#f3f4f6',color:'#6b7280'} };
  return <span style={{...s[type]||s.gray, padding:'3px 10px', borderRadius:20, fontSize:12, fontWeight:500}}>{label}</span>;
}

function Btn({ children, variant='primary', size='md', fullWidth, loading, ...props }) {
  const v = { primary:{background:'#0d7377',color:'white'},
    secondary:{background:'white',color:'#374151',border:'1.5px solid #e5e2db'},
    danger:{background:'#fef2f2',color:'#dc2626',border:'1.5px solid #fecaca'} };
  return (
    <button {...props} style={{ ...v[variant]||v.primary, border:v[variant]?.border||'none',
      padding:size==='sm'?'6px 12px':'10px 20px', borderRadius:8, fontFamily:'inherit',
      fontSize:size==='sm'?13:14, fontWeight:500, cursor:'pointer',
      display:'inline-flex', alignItems:'center', gap:7, justifyContent:'center',
      width:fullWidth?'100%':undefined, opacity:loading?0.7:1, ...props.style }}>
      {loading?'⏳':children}
    </button>
  );
}

function Input({ label, error, ...props }) {
  return (
    <div style={{marginBottom:16}}>
      {label && <label style={{display:'block',fontSize:13,fontWeight:500,color:'#6b7280',marginBottom:6}}>{label}</label>}
      <input {...props} style={{width:'100%',padding:'9px 13px',
        border:'1.5px solid '+(error?'#dc2626':'#e5e2db'),
        borderRadius:8,fontSize:14,outline:'none',fontFamily:'inherit',boxSizing:'border-box'}} />
      {error && <div style={{color:'#dc2626',fontSize:12,marginTop:4}}>{error}</div>}
    </div>
  );
}

function Login({ onLogin }) {
  const [email,setEmail] = useState('demo@app.com');
  const [pass,setPass] = useState('demo1234');
  const [err,setErr] = useState('');
  const [loading,setLoading] = useState(false);
  const submit = async () => {
    setErr(''); setLoading(true);
    try {
      const r = await axios.post(API+'/auth/login', {username:email, password:pass});
      localStorage.setItem('token', r.data.token);
      localStorage.setItem('user', JSON.stringify(r.data.user));
      onLogin(r.data.user);
    } catch(e) { setErr(e.response?.data?.error||'Login failed'); }
    finally { setLoading(false); }
  };
  return (
    <div style={{minHeight:'100vh',display:'flex',background:'#141318'}}>
      <div style={{flex:1,display:'flex',alignItems:'center',justifyContent:'center',padding:48}}>
        <div style={{maxWidth:380}}>
          <div style={{width:52,height:52,background:'#0d7377',borderRadius:14,display:'flex',
            alignItems:'center',justifyContent:'center',fontSize:24,marginBottom:24}}>{APP_ICON}</div>
          <h1 style={{fontFamily:'Georgia,serif',fontSize:36,color:'white',marginBottom:12,fontWeight:500}}>{APP_NAME}</h1>
          <p style={{color:'rgba(255,255,255,0.45)',fontSize:16}}>Professional {ENTITIES.toLowerCase()} management</p>
        </div>
      </div>
      <div style={{width:420,background:'white',display:'flex',alignItems:'center',
        justifyContent:'center',padding:48,boxShadow:'-20px 0 60px rgba(0,0,0,0.3)'}}>
        <div style={{width:'100%'}}>
          <h2 style={{fontSize:24,fontWeight:700,marginBottom:6}}>Welcome back</h2>
          <p style={{color:'#6b7280',fontSize:14,marginBottom:24}}>Sign in to continue</p>
          <div style={{background:'#f0fdf4',border:'1px solid #bbf7d0',borderRadius:8,
            padding:'10px 14px',fontSize:13,color:'#166534',marginBottom:20}}>
            🔑 Demo: <strong>demo@app.com</strong> / <strong>demo1234</strong>
          </div>
          <Input label="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} />
          <Input label="Password" type="password" value={pass}
            onChange={e=>setPass(e.target.value)} onKeyDown={e=>e.key==='Enter'&&submit()} />
          {err && <div style={{color:'#dc2626',fontSize:13,marginBottom:12}}>{err}</div>}
          <Btn fullWidth loading={loading} onClick={submit}>Sign in →</Btn>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [user,setUser] = useState(()=>{try{return JSON.parse(localStorage.getItem('user'));}catch{return null;}});
  const [page,setPage] = useState('dashboard');
  const [toast,setToast] = useState(null);
  const [records,setRecords] = useState([]);
  const [search,setSearch] = useState('');
  const [modal,setModal] = useState(null);
  const [form,setForm] = useState({});
  const [loading,setLoading] = useState(false);

  const showToast = (msg,type='success') => setToast({msg,type});
  const logout = () => { localStorage.clear(); setUser(null); };

  const fetchRecords = useCallback(async () => {
    try {
      const r = await axios.get(API+'/records', authH());
      setRecords(r.data);
    } catch {}
  }, []);

  useEffect(() => { if(user) fetchRecords(); }, [user,page]);

  if (!user) return <Login onLogin={u=>setUser(u)} />;

  const fullNav = [
    ...NAV,
    ['settings','⚙️','Settings']
  ].filter((v,i,a) => a.findIndex(x=>x[0]===v[0])===i);

  const exportCSV = () => {
    if (!records.length) { showToast('No data','warning'); return; }
    const h = Object.keys(records[0]);
    const rows = [h.join(','),...records.map(r=>h.map(k=>String(r[k]??'')).join(','))].join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([rows],{type:'text/csv'}));
    a.download = ENTITIES.toLowerCase()+'-export.csv';
    a.click(); showToast('Exported');
  };

  const saveRecord = async () => {
    const required = FIELDS[0];
    if (required && !form[required[0]]) { showToast('Fill required fields','error'); return; }
    setLoading(true);
    try {
      if (form.id) {
        await axios.put(API+'/records/'+form.id, form, authH());
        showToast(ENTITY+' updated');
      } else {
        await axios.post(API+'/records', form, authH());
        showToast(ENTITY+' saved');
      }
      setModal(null); setForm({}); fetchRecords();
    } catch(e) { showToast(e.response?.data?.error||'Failed','error'); }
    finally { setLoading(false); }
  };

  const deleteRecord = async (id) => {
    if (!window.confirm('Delete this '+ENTITY+'?')) return;
    try {
      await axios.delete(API+'/records/'+id, authH());
      showToast('Deleted'); fetchRecords();
    } catch(e) { showToast(e.response?.data?.error||'Failed','error'); }
  };

  const filtered = records.filter(r => !search ||
    Object.values(r).some(v => String(v).toLowerCase().includes(search.toLowerCase())));

  return (
    <>
      <style>{`
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:system-ui,-apple-system,sans-serif;background:#f8f7f4}
        table{width:100%;border-collapse:collapse;font-size:14px}
        th{padding:11px 18px;text-align:left;font-size:11px;font-weight:600;text-transform:uppercase;
           letter-spacing:.8px;color:#9ca3af;border-bottom:1px solid #f0ede8;background:#fafaf9}
        td{padding:13px 18px;border-bottom:1px solid #f0ede8;vertical-align:middle}
        tbody tr:hover td{background:#fafaf9}
      `}</style>

      {toast && <Toast msg={toast.msg} type={toast.type} onDone={()=>setToast(null)} />}

      <div style={{display:'flex',minHeight:'100vh'}}>
        <aside style={{width:240,background:'#141318',display:'flex',flexDirection:'column',
          position:'fixed',top:0,left:0,bottom:0,zIndex:200}}>
          <div style={{padding:'18px 16px',borderBottom:'1px solid rgba(255,255,255,0.07)',
            display:'flex',alignItems:'center',gap:10}}>
            <div style={{width:32,height:32,background:'#0d7377',borderRadius:8,display:'flex',
              alignItems:'center',justifyContent:'center',fontSize:15}}>{APP_ICON}</div>
            <span style={{fontFamily:'Georgia,serif',fontSize:17,color:'white'}}>{APP_NAME}</span>
          </div>
          <nav style={{flex:1,padding:'12px 8px'}}>
            {fullNav.map(([id,icon,label]) => (
              <div key={id} onClick={()=>setPage(id)} style={{
                display:'flex',alignItems:'center',gap:10,padding:'9px 10px',
                borderRadius:8,cursor:'pointer',marginBottom:2,fontSize:14,
                background:page===id?'#0d7377':'transparent',
                color:page===id?'white':'rgba(255,255,255,0.5)',
                fontWeight:page===id?500:400,transition:'all 0.15s'}}>
                <span style={{fontSize:15,width:18,textAlign:'center'}}>{icon}</span>{label}
              </div>
            ))}
          </nav>
          <div style={{padding:'12px 8px',borderTop:'1px solid rgba(255,255,255,0.07)'}}>
            <div style={{display:'flex',alignItems:'center',gap:10,padding:'8px 10px'}}>
              <Av name={user?.username||user?.email} size={32} />
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:13,fontWeight:500,color:'rgba(255,255,255,0.85)',
                  overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                  {user?.username||user?.email}</div>
                <div style={{fontSize:11,color:'rgba(255,255,255,0.35)'}}>{user?.role||'staff'}</div>
              </div>
              <span onClick={logout} style={{color:'rgba(255,255,255,0.3)',cursor:'pointer',fontSize:14}}>⬅</span>
            </div>
          </div>
        </aside>

        <div style={{marginLeft:240,flex:1,display:'flex',flexDirection:'column'}}>
          <div style={{height:60,background:'white',borderBottom:'1px solid #f0ede8',
            display:'flex',alignItems:'center',padding:'0 28px',gap:16,
            position:'sticky',top:0,zIndex:100,boxShadow:'0 1px 2px rgba(0,0,0,0.04)'}}>
            <div style={{fontFamily:'Georgia,serif',fontSize:20,fontWeight:500,flex:1}}>
              {fullNav.find(([id])=>id===page)?.[2]||'Dashboard'}
            </div>
            <input value={search} onChange={e=>setSearch(e.target.value)}
              placeholder={'Search '+ENTITIES.toLowerCase()+'...'}
              style={{border:'1.5px solid #e5e2db',borderRadius:8,padding:'7px 13px',
                fontSize:13,outline:'none',width:200}} />
            <Btn size="sm" onClick={()=>{setForm({});setModal('form');}}>+ Add {ENTITY}</Btn>
            <Btn variant="secondary" size="sm" onClick={exportCSV}>↓ Export</Btn>
          </div>

          <div style={{padding:28,flex:1}}>
            {page==='dashboard' && (
              <div>
                <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))',
                  gap:16,marginBottom:24}}>
                  {[
                    {icon:APP_ICON,label:'Total '+ENTITIES,value:records.length},
                    {icon:'📅',label:'This Month',value:records.filter(r=>r.created_at?.startsWith(new Date().toISOString().slice(0,7))).length},
                    {icon:'🟢',label:'System',value:'Online'},
                    {icon:'👤',label:'Users',value:'Active'}
                  ].map(s=>(
                    <div key={s.label} style={{background:'white',borderRadius:12,
                      padding:'20px 22px',border:'1px solid #f0ede8',
                      boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
                      <div style={{fontSize:22,marginBottom:10}}>{s.icon}</div>
                      <div style={{fontSize:11,fontWeight:600,textTransform:'uppercase',
                        letterSpacing:'.7px',color:'#9ca3af',marginBottom:6}}>{s.label}</div>
                      <div style={{fontSize:32,fontWeight:700,color:'#1c1917',lineHeight:1}}>{s.value}</div>
                    </div>
                  ))}
                </div>
                <div style={{background:'white',borderRadius:12,border:'1px solid #f0ede8',
                  boxShadow:'0 1px 3px rgba(0,0,0,0.06)',overflow:'hidden'}}>
                  <div style={{padding:'18px 22px',borderBottom:'1px solid #f0ede8',
                    display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                    <span style={{fontWeight:600,fontSize:15}}>Recent {ENTITIES}</span>
                    <Btn variant="secondary" size="sm" onClick={()=>setPage(fullNav[1]?.[0]||'records')}>View all</Btn>
                  </div>
                  <table>
                    <thead><tr>{COLS.map(([k,l])=><th key={k}>{l}</th>)}<th>Added</th></tr></thead>
                    <tbody>
                      {records.slice(0,5).map(r=>(
                        <tr key={r.id}>
                          {COLS.map(([k],i)=>(
                            <td key={k} style={i===0?{fontWeight:500}:{color:'#6b7280'}}>
                              {i===0
                                ? <div style={{display:'flex',alignItems:'center',gap:10}}>
                                    <Av name={String(r[k]||'?')} size={30}/>
                                    <span>{r[k]||'—'}</span>
                                  </div>
                                : r[k]||'—'}
                            </td>
                          ))}
                          <td style={{color:'#9ca3af',fontSize:13}}>
                            {r.created_at?.split('T')[0]||'—'}
                          </td>
                        </tr>
                      ))}
                      {!records.length && (
                        <tr><td colSpan={COLS.length+1}
                          style={{padding:40,textAlign:'center',color:'#9ca3af'}}>
                          No {ENTITIES.toLowerCase()} yet
                        </td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {page!=='dashboard' && page!=='settings' && (
              <div style={{background:'white',borderRadius:12,border:'1px solid #f0ede8',
                boxShadow:'0 1px 3px rgba(0,0,0,0.06)',overflow:'hidden'}}>
                <div style={{padding:'18px 22px',borderBottom:'1px solid #f0ede8',
                  display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                  <span style={{fontWeight:600,fontSize:15}}>All {ENTITIES}</span>
                  <div style={{display:'flex',gap:8}}>
                    <Btn variant="secondary" size="sm" onClick={exportCSV}>↓ CSV</Btn>
                    <Btn size="sm" onClick={()=>{setForm({});setModal('form');}}>+ Add {ENTITY}</Btn>
                  </div>
                </div>
                <table>
                  <thead><tr>
                    {COLS.map(([k,l])=><th key={k}>{l}</th>)}
                    <th>Added</th><th></th>
                  </tr></thead>
                  <tbody>
                    {filtered.map(r=>(
                      <tr key={r.id}>
                        {COLS.map(([k],i)=>(
                          <td key={k} style={i===0?{fontWeight:500}:{color:'#6b7280'}}>
                            {i===0
                              ? <div style={{display:'flex',alignItems:'center',gap:10}}>
                                  <Av name={String(r[k]||'?')} size={30}/>
                                  <span>{r[k]||'—'}</span>
                                </div>
                              : r[k]||'—'}
                          </td>
                        ))}
                        <td style={{color:'#9ca3af',fontSize:13}}>{r.created_at?.split('T')[0]||'—'}</td>
                        <td>
                          <div style={{display:'flex',gap:6}}>
                            <Btn variant="secondary" size="sm"
                              onClick={()=>{setForm({...r});setModal('form');}}>Edit</Btn>
                            <Btn variant="danger" size="sm" onClick={()=>deleteRecord(r.id)}>Del</Btn>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {!filtered.length && (
                      <tr><td colSpan={COLS.length+2}>
                        <div style={{textAlign:'center',padding:48,color:'#9ca3af'}}>
                          <div style={{fontSize:36,marginBottom:12}}>{APP_ICON}</div>
                          <div style={{fontWeight:500,color:'#374151',marginBottom:6}}>No {ENTITIES.toLowerCase()} yet</div>
                          <Btn onClick={()=>{setForm({});setModal('form');}}>Add your first {ENTITY.toLowerCase()}</Btn>
                        </div>
                      </td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {page==='settings' && (
              <div style={{maxWidth:480}}>
                <div style={{background:'white',borderRadius:12,border:'1px solid #f0ede8',
                  boxShadow:'0 1px 3px rgba(0,0,0,0.06)',padding:28}}>
                  <h3 style={{fontSize:17,fontWeight:600,marginBottom:20}}>Account Settings</h3>
                  <div style={{display:'flex',alignItems:'center',gap:16,marginBottom:20,
                    padding:'16px 0',borderBottom:'1px solid #f0ede8'}}>
                    <Av name={user?.username||user?.email} size={52} />
                    <div>
                      <div style={{fontWeight:600,fontSize:16}}>{user?.username||user?.email}</div>
                      <div style={{color:'#6b7280',fontSize:14}}>{user?.email}</div>
                      <Badge label={user?.role||'staff'} type="blue" />
                    </div>
                  </div>
                  <p style={{color:'#6b7280',fontSize:14}}>
                    Contact your administrator to update account details.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {modal==='form' && (
        <div onClick={e=>e.target===e.currentTarget&&setModal(null)}
          style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.45)',display:'flex',
            alignItems:'center',justifyContent:'center',zIndex:1000,padding:20}}>
          <div style={{background:'white',borderRadius:16,width:'100%',maxWidth:480,
            boxShadow:'0 20px 60px rgba(0,0,0,0.2)',maxHeight:'90vh',overflowY:'auto'}}>
            <div style={{padding:'22px 26px 18px',borderBottom:'1px solid #f0ede8',
              display:'flex',justifyContent:'space-between',alignItems:'center',
              position:'sticky',top:0,background:'white'}}>
              <span style={{fontSize:20,fontWeight:700}}>{form.id?'Edit':'Add'} {ENTITY}</span>
              <button onClick={()=>setModal(null)}
                style={{border:'none',background:'none',fontSize:20,cursor:'pointer',color:'#9ca3af'}}>✕</button>
            </div>
            <div style={{padding:'22px 26px'}}>
              {FIELDS.map(([key,label,type])=>(
                <Input key={key} label={label} type={type||'text'} value={form[key]||''}
                  onChange={e=>setForm(f=>({...f,[key]:e.target.value}))}
                  placeholder={'Enter '+label.toLowerCase()} />
              ))}
            </div>
            <div style={{padding:'16px 26px',borderTop:'1px solid #f0ede8',
              display:'flex',gap:10,justifyContent:'flex-end',
              position:'sticky',bottom:0,background:'white'}}>
              <Btn variant="secondary" onClick={()=>setModal(null)}>Cancel</Btn>
              <Btn loading={loading} onClick={saveRecord}>{form.id?'Update':'Save'} {ENTITY}</Btn>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
