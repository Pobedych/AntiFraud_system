from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/ui", response_class=HTMLResponse)
def ui():
    return HTMLResponse(
        """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>AntiFraud UI (Tier0)</title>
  <style>
    body { font-family: system-ui, Arial; margin: 20px; background:#0b1020; color:#e7e9ee; }
    h1 { margin: 0 0 12px; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .card { background:#121a33; border:1px solid #22305c; border-radius:12px; padding:12px; }
    .row { display:flex; gap:8px; margin:8px 0; flex-wrap:wrap; }
    input, textarea, select {
      background:#0b1020; border:1px solid #2a3a72; color:#e7e9ee;
      border-radius:10px; padding:8px; outline:none;
    }
    textarea { width:100%; min-height:80px; }
    input { min-width: 180px; }
    button {
      background:#3b82f6; border:none; color:white; padding:9px 12px;
      border-radius:10px; cursor:pointer; font-weight:600;
    }
    button.secondary { background:#64748b; }
    button.danger { background:#ef4444; }
    .small { font-size: 12px; color:#b6bdd1; }
    pre {
      background:#0b1020; border:1px solid #22305c; border-radius:12px;
      padding:10px; overflow:auto; max-height: 320px;
    }
    .ok { color:#22c55e; }
    .bad { color:#ef4444; }
    .token { word-break: break-all; }
  </style>
</head>
<body>
  <h1>AntiFraud UI</h1>
  <div class="small">
    UI для ручного тестирования API. Tier0: правила не вычисляются (matched=false), но CRUD/структура/батч работают.
  </div>

  <div class="card" style="margin-top:12px">
    <div class="row">
      <b>API Base:</b>
      <input id="baseUrl" value="http://localhost:8000" style="min-width:320px" />
      <button class="secondary" onclick="ping()">Ping</button>
      <span id="pingStatus" class="small"></span>
    </div>
    <div class="row">
      <b>Token:</b>
      <span id="tokenLabel" class="small token">(нет)</span>
      <button class="secondary" onclick="clearToken()">Clear</button>
    </div>
  </div>

  <div class="grid" style="margin-top:14px">
    <div class="card">
      <h3>Login (ADMIN/USER)</h3>
      <div class="row">
        <input id="loginEmail" placeholder="email" value="admin@example.com" />
        <input id="loginPass" placeholder="password" value="Admin1234" />
        <button onclick="login()">Login</button>
      </div>
      <div class="small">Сохранит JWT в localStorage и будет использовать его для запросов.</div>
    </div>

    <div class="card">
      <h3>Register (USER)</h3>
      <div class="row">
        <input id="regEmail" placeholder="email" value="u2@example.com" />
        <input id="regPass" placeholder="password" value="User12345" />
        <input id="regName" placeholder="fullName" value="User Two" />
        <button onclick="register()">Register</button>
      </div>
    </div>

    <div class="card">
      <h3>Create Fraud Rule (ADMIN)</h3>
      <div class="row">
        <input id="ruleName" placeholder="name" value="Big amounts" />
        <input id="rulePrio" placeholder="priority" value="10" />
        <select id="ruleEnabled">
          <option value="true">enabled=true</option>
          <option value="false">enabled=false</option>
        </select>
      </div>
      <div class="row">
        <input id="ruleDesc" placeholder="description" value="Tier0 rule" style="min-width:360px" />
      </div>
      <div class="row">
        <input id="ruleDsl" placeholder="dslExpression" value="amount > 10000" style="min-width:360px" />
        <button onclick="createRule()">Create</button>
        <button class="secondary" onclick="listRules()">List</button>
      </div>
    </div>

    <div class="card">
      <h3>Create User (ADMIN)</h3>
      <div class="row">
        <input id="auEmail" placeholder="email" value="u1@example.com" />
        <input id="auPass" placeholder="password" value="User12345" />
        <input id="auName" placeholder="fullName" value="User One" />
      </div>
      <div class="row">
        <select id="auRole">
          <option value="USER">USER</option>
          <option value="ADMIN">ADMIN</option>
        </select>
        <input id="auAge" placeholder="age (optional)" value="20" />
        <input id="auRegion" placeholder="region (optional)" value="RU-MOW" />
      </div>
      <div class="row">
        <select id="auGender">
          <option value="">gender=null</option>
          <option value="MALE">MALE</option>
          <option value="FEMALE">FEMALE</option>
        </select>
        <select id="auMarital">
          <option value="">maritalStatus=null</option>
          <option value="SINGLE">SINGLE</option>
          <option value="MARRIED">MARRIED</option>
          <option value="DIVORCED">DIVORCED</option>
          <option value="WIDOWED">WIDOWED</option>
        </select>
        <button onclick="adminCreateUser()">Create</button>
        <button class="secondary" onclick="listUsers()">List</button>
      </div>
      <div class="small">ID созданного пользователя автоматически подставится в "Create Transaction".</div>
    </div>

    <div class="card">
      <h3>Create Transaction</h3>
      <div class="row">
        <input id="txUserId" placeholder="userId (ADMIN only)" style="min-width:320px" />
      </div>
      <div class="row">
        <input id="txAmount" placeholder="amount" value="15000" />
        <input id="txCurrency" placeholder="currency" value="RUB" />
        <input id="txTs" placeholder="timestamp ISO" value="" style="min-width:260px" />
        <button onclick="createTx()">Create</button>
      </div>
      <div class="row">
        <input id="txId" placeholder="transactionId" style="min-width:320px" />
        <button class="secondary" onclick="getTx()">Get</button>
        <button class="secondary" onclick="listTx()">List</button>
      </div>
      <div class="small">timestamp оставь пустым → подставим текущее UTC время автоматически.</div>
    </div>

    <div class="card">
      <h3>Batch Transactions</h3>
      <div class="small">Вставь JSON массива items (как в ТЗ). userId для USER игнорируется.</div>
      <textarea id="batchBody"></textarea>
      <div class="row">
        <button onclick="batchTx()">Send Batch</button>
        <button class="secondary" onclick="fillBatchExample()">Example</button>
      </div>
    </div>
  </div>

  <div class="card" style="margin-top:14px">
    <h3>Response</h3>
    <pre id="out">(пока пусто)</pre>
  </div>

<script>
  function base() {
    return document.getElementById("baseUrl").value.replace(/\\/$/, "");
  }

  function getToken() {
    return localStorage.getItem("af_token") || "";
  }
  function setToken(t) {
    localStorage.setItem("af_token", t);
    document.getElementById("tokenLabel").textContent = t ? t : "(нет)";
  }
  function clearToken() { setToken(""); }

  // init token label + default timestamp
  setToken(getToken());
  document.getElementById("txTs").value = "";

  function headers() {
    const t = getToken();
    const h = { "Content-Type": "application/json" };
    if (t) h["Authorization"] = "Bearer " + t;
    return h;
  }

  async function req(method, path, body) {
    const opts = { method, headers: headers() };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(base() + path, opts);
    const text = await res.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text; }
    return { status: res.status, data };
  }

  function print(res) {
    const ok = res.status >= 200 && res.status < 300;
    document.getElementById("out").textContent =
      "HTTP " + res.status + "\\n\\n" + JSON.stringify(res.data, null, 2);
    document.getElementById("out").className = ok ? "ok" : "bad";
  }

  async function ping() {
    const r = await req("GET", "/api/v1/ping");
    document.getElementById("pingStatus").textContent = "HTTP " + r.status;
    print(r);
  }

  async function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPass").value;
    const r = await req("POST", "/api/v1/auth/login", { email, password });
    if (r.status === 200) {
      setToken(r.data.accessToken);
    }
    print(r);
  }

  async function register() {
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPass").value;
    const fullName = document.getElementById("regName").value;
    const r = await req("POST", "/api/v1/auth/register", { email, password, fullName });
    if (r.status === 201) {
      setToken(r.data.accessToken);
    }
    print(r);
  }

  async function createRule() {
    const name = document.getElementById("ruleName").value;
    const description = document.getElementById("ruleDesc").value;
    const dslExpression = document.getElementById("ruleDsl").value;
    const enabled = document.getElementById("ruleEnabled").value === "true";
    const priority = parseInt(document.getElementById("rulePrio").value || "100", 10);
    const r = await req("POST", "/api/v1/fraud-rules", { name, description, dslExpression, enabled, priority });
    print(r);
  }

  async function listRules() {
    const r = await req("GET", "/api/v1/fraud-rules");
    print(r);
  }

  async function adminCreateUser() {
    const email = document.getElementById("auEmail").value;
    const password = document.getElementById("auPass").value;
    const fullName = document.getElementById("auName").value;
    const role = document.getElementById("auRole").value;

    const ageRaw = document.getElementById("auAge").value.trim();
    const regionRaw = document.getElementById("auRegion").value.trim();
    const genderRaw = document.getElementById("auGender").value;
    const maritalRaw = document.getElementById("auMarital").value;

    const body = {
      email, password, fullName, role,
      age: ageRaw ? parseInt(ageRaw, 10) : null,
      region: regionRaw ? regionRaw : null,
      gender: genderRaw ? genderRaw : null,
      maritalStatus: maritalRaw ? maritalRaw : null
    };

    const r = await req("POST", "/api/v1/users", body);
    if (r.status === 201) {
      document.getElementById("txUserId").value = r.data.id;
    }
    print(r);
  }

  async function listUsers() {
    const r = await req("GET", "/api/v1/users?page=0&size=20");
    print(r);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  async function createTx() {
    const userId = document.getElementById("txUserId").value.trim();
    const amount = parseFloat(document.getElementById("txAmount").value);
    const currency = document.getElementById("txCurrency").value.trim();
    let timestamp = document.getElementById("txTs").value.trim();
    if (!timestamp) timestamp = nowIso();

    const body = { userId: userId || null, amount, currency, timestamp };

    const r = await req("POST", "/api/v1/transactions", body);
    if (r.status === 201) {
      document.getElementById("txId").value = r.data.transaction.id;
    }
    print(r);
  }

  async function getTx() {
    const id = document.getElementById("txId").value.trim();
    if (!id) return alert("transactionId пустой");
    const r = await req("GET", "/api/v1/transactions/" + id);
    print(r);
  }

  async function listTx() {
    const r = await req("GET", "/api/v1/transactions?page=0&size=20");
    print(r);
  }

  function fillBatchExample() {
    const uid = document.getElementById("txUserId").value.trim();
    const items = [
      { userId: uid || null, amount: 1000, currency: "RUB", timestamp: nowIso() },
      { userId: uid || null, amount: 50000, currency: "RUB", timestamp: nowIso() }
    ];
    document.getElementById("batchBody").value = JSON.stringify({ items }, null, 2);
  }

  async function batchTx() {
    let body;
    try { body = JSON.parse(document.getElementById("batchBody").value); }
    catch { return alert("batchBody невалидный JSON"); }

    const r = await req("POST", "/api/v1/transactions/batch", body);
    print(r);
  }
</script>
</body>
</html>
        """
    )
