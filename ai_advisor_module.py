#!/usr/bin/env python3
"""
AI ADVISOR MODULE
Injects local AI chat into any app champion.
Uses llama-server on port 8080.
"""

# Domain-specific system prompts
DOMAIN_PROMPTS = {
    "law":           "You are an expert legal advisor. Help with case strategy, legal research, Missouri statutes, and procedures. Be precise and practical.",
    "healthcare":    "You are a medical office advisor. Help with patient care workflows, medical billing, HIPAA compliance, and clinical procedures. Always recommend consulting a physician for medical decisions.",
    "pharmacy":      "You are a pharmacy operations advisor. Help with prescription management, drug interactions, pharmacy law, and patient counseling. Always note when a pharmacist or physician should be consulted.",
    "restaurant":    "You are a restaurant operations expert. Help with menu planning, food costs, kitchen efficiency, health codes, and customer service.",
    "salon":         "You are a salon business advisor. Help with appointment management, pricing, retail products, client retention, and beauty industry trends.",
    "gym":           "You are a fitness business advisor. Help with member retention, workout programming, equipment, certifications, and gym operations.",
    "agriculture":   "You are an agricultural advisor specializing in Missouri farming. Help with crop management, soil health, market timing, equipment, and Missouri extension resources.",
    "smart_farm":    "You are an agricultural advisor specializing in Missouri farming. Help with crop management, soil health, market timing, equipment, and Missouri extension resources.",
    "nutrition_center": "You are a nutrition and community food service advisor. Help with meal planning, dietary restrictions, food safety, grant reporting, and elderly care best practices.",
    "dental":        "You are a dental practice advisor. Help with patient scheduling, dental procedures, billing codes, infection control, and practice management.",
    "mental-health": "You are a mental health practice advisor. Help with therapy approaches, practice management, billing, HIPAA, and patient care workflows.",
    "mental_wellness": "You are a wellness advisor. Help with mindfulness practices, wellness programs, client engagement, and holistic health approaches.",
    "realestate":    "You are a real estate advisor. Help with property valuation, contracts, Missouri real estate law, market analysis, and client management.",
    "construction":  "You are a construction business advisor. Help with project management, contractor licensing, safety codes, bidding, and materials.",
    "plumber":       "You are a plumbing business advisor. Help with job estimates, plumbing codes, scheduling, equipment, and customer service.",
    "autorepair":    "You are an auto repair shop advisor. Help with diagnostics, repair estimates, parts sourcing, shop management, and customer communication.",
    "accounting":    "You are an accounting and bookkeeping advisor. Help with financial statements, tax preparation, QuickBooks, small business accounting, and Missouri tax law.",
    "insurance":     "You are an insurance industry advisor. Help with policy management, claims processing, Missouri insurance regulations, and client service.",
    "nonprofit":     "You are a nonprofit management advisor. Help with grant writing, board governance, fundraising, program management, and Missouri nonprofit law.",
    "church":        "You are a church administration advisor. Help with congregation management, event planning, financial stewardship, and community outreach.",
    "school":        "You are an education administrator advisor. Help with student management, curriculum planning, Missouri education standards, and school operations.",
    "daycare":       "You are a childcare business advisor. Help with Missouri childcare licensing, curriculum, parent communication, staff management, and safety.",
    "tutoring":      "You are an education and tutoring advisor. Help with learning strategies, student assessment, curriculum design, and tutoring business management.",
    "petcare":       "You are a pet care business advisor. Help with animal care best practices, Missouri veterinary regulations, pet health, and business operations.",
    "inventory":     "You are an inventory and supply chain advisor. Help with stock management, ordering systems, warehouse organization, and cost reduction.",
    "supply_chain":  "You are a supply chain advisor. Help with logistics, vendor management, inventory optimization, and procurement strategies.",
    "freelancer":    "You are a freelance business advisor. Help with client management, project pricing, contracts, time management, and growing a freelance practice.",
    "jobboard":      "You are a recruitment and HR advisor. Help with job posting, candidate screening, hiring best practices, and employment law.",
    "esports":       "You are an esports and gaming business advisor. Help with team management, tournament organization, streaming, sponsorships, and gaming industry trends.",
    "music_studio":  "You are a music studio business advisor. Help with recording sessions, music production, licensing, artist management, and studio operations.",
    "photography":   "You are a photography business advisor. Help with client sessions, pricing, editing workflows, licensing, and growing a photography business.",
    "vr_studio":     "You are a VR and immersive media advisor. Help with VR development, content creation, hardware, and immersive experience design.",
    "game_engine":   "You are a game development advisor. Help with game design, programming, Unity/Unreal, publishing, and game industry best practices.",
    "game_mobile":   "You are a mobile game development advisor. Help with mobile game design, monetization, app store optimization, and player retention.",
    "game_rpg":      "You are a game design advisor specializing in RPGs. Help with story design, character systems, world building, and game mechanics.",
    "game_shooter":  "You are a game design advisor specializing in shooters. Help with game mechanics, level design, multiplayer systems, and player experience.",
    "game_strategy": "You are a game design advisor specializing in strategy games. Help with game balance, AI systems, UI design, and player progression.",
    "game_platformer":"You are a game design advisor specializing in platformers. Help with level design, character movement, game feel, and progression systems.",
    "game_puzzle":   "You are a game design advisor specializing in puzzle games. Help with puzzle design, difficulty curves, UI, and player engagement.",
    "game_racing":   "You are a game design advisor specializing in racing games. Help with vehicle physics, track design, multiplayer, and game feel.",
    "fitness":       "You are a fitness and wellness advisor. Help with workout programming, nutrition, client motivation, and fitness business operations.",
    "yoga":          "You are a yoga and mindfulness advisor. Help with class planning, yoga philosophy, student progression, and studio management.",
    "spa":           "You are a spa and wellness business advisor. Help with treatment menus, client experience, staff training, and spa operations.",
    "beauty":        "You are a beauty industry advisor. Help with beauty treatments, product knowledge, client retention, and beauty business management.",
    "cleaning":      "You are a cleaning business advisor. Help with scheduling, pricing, cleaning techniques, staff management, and client retention.",
    "catering":      "You are a catering business advisor. Help with menu planning, event logistics, food safety, pricing, and client management.",
    "bakery":        "You are a bakery business advisor. Help with recipes, production planning, pricing, food safety, and bakery operations.",
    "events":        "You are an event planning advisor. Help with event logistics, vendor management, budgeting, timelines, and client communication.",
    "ministry":      "You are a ministry and faith community advisor. Help with program planning, volunteer management, community outreach, and ministry growth.",
    "education":     "You are an education advisor. Help with curriculum design, teaching strategies, student assessment, and educational technology.",
    "telehealth":    "You are a telehealth and digital health advisor. Help with virtual care best practices, platform selection, patient engagement, and healthcare regulations.",
    "rental":        "You are a rental business advisor. Help with property or equipment management, tenant relations, Missouri landlord-tenant law, and rental pricing.",
    "fleet_management": "You are a fleet management advisor. Help with vehicle maintenance, routing, driver management, fuel costs, and fleet optimization.",
    "drone_delivery": "You are a drone operations advisor. Help with FAA regulations, flight planning, payload management, and drone delivery logistics.",
    "autonomous_vehicle": "You are an autonomous vehicle systems advisor. Help with AV technology, safety systems, route optimization, and fleet operations.",
    "rf_sensing":    "You are an RF and wireless systems advisor. Help with signal analysis, spectrum management, device identification, and wireless security.",
    "robotics":      "You are a robotics systems advisor. Help with robot programming, maintenance, safety protocols, and automation integration.",
    "crypto_exchange": "You are a cryptocurrency and blockchain advisor. Help with trading strategies, blockchain technology, DeFi, and crypto regulations.",
    "insurance":     "You are an insurance advisor. Help with policy types, coverage analysis, claims, and Missouri insurance regulations.",
    "dental":        "You are a dental practice advisor. Help with patient care, billing codes, infection control, and dental practice management.",
}

DEFAULT_PROMPT = "You are a helpful business advisor. Help with operations, management, customer service, and business growth strategies. Be practical and concise."

AI_MODULE_TEMPLATE = '''
<!-- ═══════════════════════════════════════ -->
<!-- AI ADVISOR — Powered by Local LLM      -->
<!-- Runs on llama-server port 8080         -->
<!-- ═══════════════════════════════════════ -->
<style>
.ai-page { display:flex; flex-direction:column; height:calc(100vh - 160px); min-height:400px; }
.ai-messages { flex:1; overflow-y:auto; padding:4px 0 12px; display:flex; flex-direction:column; gap:10px; }
.ai-msg { max-width:90%; padding:11px 14px; border-radius:10px; font-size:13px; line-height:1.6; }
.ai-msg.user { background:AI_COLOR_LIGHT; border:1px solid AI_COLOR_BORDER; color:#1a1a1a; align-self:flex-end; border-radius:10px 10px 2px 10px; }
.ai-msg.bot { background:#f8f9fa; border:1px solid #e8e8e8; color:#1a1a1a; align-self:flex-start; border-radius:10px 10px 10px 2px; }
.ai-msg.bot strong { color:AI_PRIMARY; }
.ai-msg.error { background:#ffe0e0; border:1px solid #ffb3b3; color:#842029; align-self:flex-start; border-radius:10px; }
.ai-typing { display:flex; gap:4px; padding:10px 14px; align-self:flex-start; background:#f8f9fa; border-radius:10px; border:1px solid #e8e8e8; }
.ai-typing span { width:7px; height:7px; background:AI_PRIMARY; border-radius:50%; animation:aityp 1.2s infinite; opacity:0.4; }
.ai-typing span:nth-child(2){animation-delay:0.2s}
.ai-typing span:nth-child(3){animation-delay:0.4s}
@keyframes aityp{0%,100%{opacity:0.4;transform:scale(1)}50%{opacity:1;transform:scale(1.2)}}
.ai-input-row { display:flex; gap:8px; margin-top:10px; }
.ai-input-row input { flex:1; padding:11px 13px; border:1.5px solid #e8e8e8; border-radius:8px; font-size:13px; font-family:inherit; }
.ai-input-row input:focus { outline:none; border-color:AI_PRIMARY; }
.ai-send { border:none; background:AI_PRIMARY; color:#fff; padding:11px 16px; border-radius:8px; font-weight:700; cursor:pointer; font-size:13px; white-space:nowrap; }
.ai-send:disabled { opacity:0.5; cursor:not-allowed; }
.ai-chips { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px; }
.ai-chip { background:#f0f0f0; border:1px solid #e0e0e0; color:#333; padding:6px 12px; border-radius:20px; font-size:11px; cursor:pointer; font-family:inherit; }
.ai-chip:hover { background:AI_COLOR_LIGHT; border-color:AI_PRIMARY; color:AI_PRIMARY; }
.ai-status { font-size:11px; color:#888; text-align:center; padding:4px; }
</style>

<div id="AI_PAGE_ID" class="page">
  <div class="card ai-page">
    <h3>🤖 AI_TITLE</h3>
    <div class="ai-chips" id="ai-chips">AI_CHIPS</div>
    <div class="ai-messages" id="ai-messages">
      <div class="ai-msg bot"><strong>AI Advisor</strong><br>AI_GREETING</div>
    </div>
    <div class="ai-status" id="ai-status">● Local AI · Private · No internet needed</div>
    <div class="ai-input-row">
      <input type="text" id="ai-input" placeholder="Ask anything..." onkeydown="if(event.key==='Enter')sendAI()"/>
      <button class="ai-send" id="ai-btn" onclick="sendAI()">Ask ›</button>
    </div>
  </div>
</div>

<script>
const AI_SYSTEM_PROMPT = `AI_SYSTEM`;
const AI_LOCAL_URL = 'http://localhost:8080/v1/chat/completions';
let aiHistory = [];
let aiOnline = false;

// Check if local AI is available
fetch(AI_LOCAL_URL, {method:'POST',headers:{'Content-Type':'application/json'},
  body:JSON.stringify({messages:[{role:'user',content:'hi'}],max_tokens:5})
}).then(r=>{
  if(r.ok){aiOnline=true;document.getElementById('ai-status').textContent='● Local AI · Online · Private';}
}).catch(()=>{
  document.getElementById('ai-status').textContent='○ Local AI offline — start llama-server on port 8080';
});

function aiChip(q){document.getElementById('ai-input').value=q;sendAI();}

async function sendAI(){
  const inp = document.getElementById('ai-input');
  const msg = inp.value.trim();
  if(!msg) return;
  inp.value='';
  const msgs = document.getElementById('ai-messages');
  msgs.innerHTML += `<div class="ai-msg user">${msg}</div>`;
  const tid = 't'+Date.now();
  msgs.innerHTML += `<div class="ai-typing" id="${tid}"><span></span><span></span><span></span></div>`;
  msgs.scrollTop = msgs.scrollHeight;
  document.getElementById('ai-btn').disabled = true;
  aiHistory.push({role:'user',content:msg});
  try {
    const r = await fetch(AI_LOCAL_URL,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        messages:[{role:'system',content:AI_SYSTEM_PROMPT},...aiHistory],
        max_tokens:400,
        temperature:0.7
      })
    });
    const d = await r.json();
    const reply = d.choices?.[0]?.message?.content || 'No response received.';
    aiHistory.push({role:'assistant',content:reply});
    document.getElementById(tid)?.remove();
    const fmt = reply.replace(/\\n/g,'<br>').replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');
    msgs.innerHTML += `<div class="ai-msg bot"><strong>AI Advisor</strong><br>${fmt}</div>`;
  } catch(e) {
    document.getElementById(tid)?.remove();
    msgs.innerHTML += `<div class="ai-msg error">⚠️ AI offline. Run: llama-server -m [model] --port 8080</div>`;
  }
  document.getElementById('ai-btn').disabled = false;
  msgs.scrollTop = msgs.scrollHeight;
}
</script>
'''

DOMAIN_CHIPS = {
    "law":        ["Attorney-client privilege", "Missouri statute of limitations", "Contract elements", "Discovery process", "Criminal defense basics"],
    "healthcare": ["HIPAA compliance", "Billing codes", "Patient intake", "Medicare basics", "Appointment no-shows"],
    "pharmacy":   ["Drug interactions", "Prescription transfers", "Missouri pharmacy law", "Controlled substances", "Patient counseling"],
    "restaurant": ["Food cost formula", "Health code basics", "Menu pricing", "Kitchen efficiency", "Handling bad reviews"],
    "salon":      ["Pricing services", "Client retention", "Booking tips", "Product retail", "Handling cancellations"],
    "gym":        ["Member retention", "PT pricing", "Class scheduling", "Liability waivers", "Equipment maintenance"],
    "agriculture":["Missouri planting calendar", "Soil testing", "Crop rotation", "Market timing", "USDA programs"],
    "smart_farm": ["Missouri planting calendar", "Soil testing", "Crop rotation", "Market timing", "USDA programs"],
    "dental":     ["Billing codes", "Infection control", "Patient communication", "Insurance processing", "New patient intake"],
    "accounting": ["QuickBooks basics", "Missouri sales tax", "Small biz deductions", "Cash flow tips", "Payroll basics"],
    "nonprofit":  ["Grant writing tips", "IRS Form 990", "Board governance", "Volunteer management", "Missouri nonprofit law"],
    "realestate": ["Missouri contract law", "Property valuation", "Buyer vs seller agent", "Closing process", "Market analysis"],
    "construction":["Contractor licensing MO", "Lien waivers", "Change orders", "OSHA basics", "Bid writing"],
    "cleaning":   ["Pricing jobs", "Cleaning products", "Client contracts", "Staff management", "Upselling services"],
    "bakery":     ["Food safety basics", "Cottage food law MO", "Pricing baked goods", "Scaling recipes", "Wholesale pricing"],
}

DEFAULT_CHIPS = ["How do I get started?", "Best practices", "Common mistakes to avoid", "How to grow my business", "Tips for efficiency"]

def generate_ai_module(domain_id, primary_color):
    system_prompt = DOMAIN_PROMPTS.get(domain_id, DEFAULT_PROMPT)
    chips = DOMAIN_CHIPS.get(domain_id, DEFAULT_CHIPS)
    
    # Build chip HTML
    chips_html = "".join([f'<button class="ai-chip" onclick="aiChip(\'{c}\')">{c}</button>' for c in chips])
    
    # Domain title
    title_map = {
        "law":"Legal Advisor","healthcare":"Medical Advisor","pharmacy":"Pharmacy Advisor",
        "restaurant":"Restaurant Advisor","salon":"Salon Advisor","gym":"Fitness Advisor",
        "agriculture":"Farm Advisor","smart_farm":"Farm Advisor","dental":"Dental Advisor",
        "accounting":"Accounting Advisor","nonprofit":"Nonprofit Advisor","realestate":"Real Estate Advisor",
        "construction":"Construction Advisor","cleaning":"Cleaning Advisor","bakery":"Bakery Advisor",
    }
    title = title_map.get(domain_id, "AI Business Advisor")
    
    greeting = f"Ask me anything about {domain_id.replace('_',' ')} — operations, best practices, regulations, or strategy. I run locally on your device — completely private."
    
    # Color variants
    color_light = primary_color + "22"
    color_border = primary_color + "44"
    
    module = AI_MODULE_TEMPLATE
    module = module.replace("AI_PRIMARY", primary_color)
    module = module.replace("AI_COLOR_LIGHT", color_light)
    module = module.replace("AI_COLOR_BORDER", color_border)
    module = module.replace("AI_PAGE_ID", "ai-advisor")
    module = module.replace("AI_TITLE", title)
    module = module.replace("AI_CHIPS", chips_html)
    module = module.replace("AI_GREETING", greeting)
    module = module.replace("AI_SYSTEM", system_prompt)
    
    return module

if __name__ == "__main__":
    # Test
    module = generate_ai_module("law", "#1e3a5f")
    print(f"✅ AI module generated: {len(module)} chars")
    print(f"   Domain: law")
    print(f"   Color: #1e3a5f")
    print(f"   Chips: 5 quick questions")
