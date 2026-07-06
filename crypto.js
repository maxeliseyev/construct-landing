const p = 71;
const G = 2;
const encoder = new TextEncoder();
const decoder = new TextDecoder();
let toyChatState = [];
let toyDisplayMode = "hex";

// Функция для вычисления mod
function modPow(base, exp, mod) {
  if (exp === 0) return 1;
  let result = 1;
  base = base % mod;
  while (exp > 0) {
    if (exp % 2 === 1) {
      result = (result * base) % mod;
    }
    base = (base * base) % mod;
    exp = Math.floor(exp / 2);
  }
  return result;
}

function modInverse(value, mod) {
  let t = 0;
  let newT = 1;
  let r = mod;
  let newR = ((value % mod) + mod) % mod;

  while (newR !== 0) {
    const quotient = Math.floor(r / newR);
    [t, newT] = [newT, t - quotient * newT];
    [r, newR] = [newR, r - quotient * newR];
  }

  if (r !== 1) return null;
  if (t < 0) t += mod;
  return t;
}

function getSharedSecret() {
  return parseInt(document.getElementById("shared_secret").textContent, 10);
}

function encryptToyMessage(text, secret) {
  const bytes = Array.from(encoder.encode(text));
  const nibbles = [];
  const encrypted = [];

  bytes.forEach((byte) => {
    nibbles.push(byte >> 4, byte & 15);
  });

  nibbles.forEach((nibble) => {
    encrypted.push(((nibble + 1) * secret) % p);
  });

  return { bytes, nibbles, encrypted };
}

function decryptToyMessage(encrypted, secret) {
  const inverse = modInverse(secret, p);
  if (inverse === null) return null;

  const nibbles = encrypted.map((block) => {
    const decoded = (block * inverse) % p;
    return (decoded + p - 1) % p;
  });

  const bytes = [];
  for (let i = 0; i < nibbles.length; i += 2) {
    bytes.push((nibbles[i] << 4) | nibbles[i + 1]);
  }

  return {
    nibbles,
    bytes,
    text: decoder.decode(new Uint8Array(bytes)),
  };
}

function formatBytes(bytes, mode) {
  if (!bytes.length) return "—";
  if (mode === "decimal") {
    return bytes.join(" ");
  }
  return bytes.map((byte) => byte.toString(16).padStart(2, "0")).join(" ");
}

function formatNibbles(nibbles, mode) {
  if (!nibbles.length) return "—";
  if (mode === "decimal") {
    return nibbles.join(" ");
  }
  return nibbles.map((nibble) => nibble.toString(16)).join(" ");
}

function formatEncryptedBlocks(blocks, mode) {
  if (!blocks.length) return "—";
  if (mode === "decimal") {
    return blocks.join(" ");
  }
  return blocks.map((block) => block.toString(16).padStart(2, "0")).join(" ");
}

function formatCipherInline(entry) {
  if (toyDisplayMode === "decimal") {
    return `decimal: ${entry.encrypted.join(" ")}`;
  }
  return `hex: ${entry.cipherHex}`;
}

function updateDisplayToggle() {
  document
    .getElementById("view_hex")
    .classList.toggle("is-active", toyDisplayMode === "hex");
  document
    .getElementById("view_decimal")
    .classList.toggle("is-active", toyDisplayMode === "decimal");
}

function setToyDisplayMode(mode) {
  toyDisplayMode = mode;
  updateDisplayToggle();
  renderToyChat();
  if (toyChatState.length) {
    updatePipeline(toyChatState[toyChatState.length - 1]);
  } else {
    document.getElementById("pipeline_bytes_mode").textContent = mode;
    document.getElementById("pipeline_nibbles_mode").textContent =
      mode === "hex" ? "hex digits 0..f" : "values 0..15";
  }
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderToyChat() {
  const aliceLog = document.getElementById("alice_chat_log");
  const bobLog = document.getElementById("bob_chat_log");

  if (!toyChatState.length) {
    aliceLog.innerHTML =
      '<div class="chat-bubble chat-bubble--received"><div class="chat-bubble__label">Подсказка</div><p class="chat-bubble__text">Отправьте сообщение, и мы покажем открытый текст, hex и результат расшифровки.</p></div>';
    bobLog.innerHTML =
      '<div class="chat-bubble chat-bubble--received"><div class="chat-bubble__label">Подсказка</div><p class="chat-bubble__text">Общий секрет автоматически берётся из шага Diffie-Hellman выше.</p></div>';
    return;
  }

  aliceLog.innerHTML = toyChatState
    .map((entry) => {
      const isAliceSender = entry.from === "alice";
      const label = isAliceSender ? "Алиса → Боб" : "Боб → Алиса";
      return `
                            <div class="chat-bubble ${isAliceSender ? "chat-bubble--sent" : "chat-bubble--received"}">
                                <div class="chat-bubble__label">${label}</div>
                                <p class="chat-bubble__text">${escapeHtml(entry.plaintext)}</p>
                                <div class="chat-bubble__cipher">${formatCipherInline(entry)}</div>
                            </div>
                        `;
    })
    .join("");

  bobLog.innerHTML = toyChatState
    .map((entry) => {
      const isBobSender = entry.from === "bob";
      const label = isBobSender ? "Боб → Алиса" : "Алиса → Боб";
      return `
                            <div class="chat-bubble ${isBobSender ? "chat-bubble--sent" : "chat-bubble--received"}">
                                <div class="chat-bubble__label">${label}</div>
                                <p class="chat-bubble__text">${escapeHtml(entry.decryptedText)}</p>
                                <div class="chat-bubble__cipher">${formatCipherInline(entry)}</div>
                            </div>
                        `;
    })
    .join("");

  aliceLog.scrollTop = aliceLog.scrollHeight;
  bobLog.scrollTop = bobLog.scrollHeight;
}

function updatePipeline(entry) {
  if (!entry) return;

  document.getElementById("pipeline_summary").textContent =
    `${entry.fromLabel} отправляет сообщение, мы кодируем его в UTF-8, разбиваем на hex-цифры и шифруем общим секретом S = ${entry.secret}.`;
  document.getElementById("pipeline_from").textContent = entry.fromLabel;
  document.getElementById("pipeline_plaintext").textContent =
    entry.plaintext || "∅";
  document.getElementById("pipeline_bytes_mode").textContent = toyDisplayMode;
  document.getElementById("pipeline_bytes").textContent = formatBytes(
    entry.bytes,
    toyDisplayMode,
  );
  document.getElementById("pipeline_nibbles_mode").textContent =
    toyDisplayMode === "hex" ? "hex digits 0..f" : "values 0..15";
  document.getElementById("pipeline_nibbles").textContent = formatNibbles(
    entry.nibbles,
    toyDisplayMode,
  );
  document.getElementById("pipeline_formula").textContent =
    `c = (m + 1) × ${entry.secret} mod 71`;
  document.getElementById("pipeline_cipher").textContent =
    formatEncryptedBlocks(entry.encrypted, toyDisplayMode);
  document.getElementById("pipeline_decrypted").textContent =
    entry.decryptedText || "∅";
}

function sendToyMessage(sender) {
  const input = document.getElementById(
    sender === "alice" ? "alice_message" : "bob_message",
  );
  const text = input.value.trim();
  if (!text) return;

  const secret = getSharedSecret();
  const encryptedData = encryptToyMessage(text, secret);
  const decryptedData = decryptToyMessage(encryptedData.encrypted, secret);

  const entry = {
    from: sender,
    fromLabel: sender === "alice" ? "Алиса" : "Боб",
    plaintext: text,
    decryptedText: decryptedData ? decryptedData.text : "Ошибка",
    bytes: encryptedData.bytes,
    nibbles: encryptedData.nibbles,
    encrypted: encryptedData.encrypted,
    cipherHex: encryptedData.encrypted
      .map((block) => block.toString(16).padStart(2, "0"))
      .join(" "),
    secret,
  };

  toyChatState.push(entry);
  renderToyChat();
  updatePipeline(entry);
}

function rebuildToyChatForSecret(secret) {
  if (!toyChatState.length) return;

  toyChatState = toyChatState.map((entry) => {
    const encryptedData = encryptToyMessage(entry.plaintext, secret);
    const decryptedData = decryptToyMessage(encryptedData.encrypted, secret);

    return {
      ...entry,
      decryptedText: decryptedData ? decryptedData.text : "Ошибка",
      bytes: encryptedData.bytes,
      nibbles: encryptedData.nibbles,
      encrypted: encryptedData.encrypted,
      cipherHex: encryptedData.encrypted
        .map((block) => block.toString(16).padStart(2, "0"))
        .join(" "),
      secret,
    };
  });

  renderToyChat();
  updatePipeline(toyChatState[toyChatState.length - 1]);
}

function updateMITMToggleButton() {
  const mitmDemo = document.getElementById("mitm_demo");
  const mitmToggleButton = document.getElementById("mitm_toggle_button");
  const isOpen = !mitmDemo.classList.contains("is-hidden");

  mitmToggleButton.textContent = isOpen
    ? "Скрыть MITM атаку"
    : "Показать MITM атаку";
}

function toggleMITM() {
  const mitmDemo = document.getElementById("mitm_demo");
  const isOpen = !mitmDemo.classList.contains("is-hidden");

  if (isOpen) {
    resetDemo();
    return;
  }

  simulateMITM();
}

function clearToyChat() {
  toyChatState = [];
  renderToyChat();
  document.getElementById("pipeline_summary").textContent =
    "Нажмите «Отправить», и здесь появится раскладка по шагам.";
  document.getElementById("pipeline_from").textContent = "—";
  document.getElementById("pipeline_plaintext").textContent = "—";
  document.getElementById("pipeline_bytes_mode").textContent = toyDisplayMode;
  document.getElementById("pipeline_bytes").textContent = "—";
  document.getElementById("pipeline_nibbles_mode").textContent =
    toyDisplayMode === "hex" ? "hex digits 0..f" : "values 0..15";
  document.getElementById("pipeline_nibbles").textContent = "—";
  document.getElementById("pipeline_formula").textContent =
    "c = (m + 1) × S mod 71";
  document.getElementById("pipeline_cipher").textContent = "—";
  document.getElementById("pipeline_decrypted").textContent = "—";
}

// Функция для обновления всех значений
function updateAll() {
  const alice_priv = parseInt(document.getElementById("alice_priv").value);
  const bob_priv = parseInt(document.getElementById("bob_priv").value);

  // Публичные ключи
  const alice_pub = modPow(G, alice_priv, p);
  const bob_pub = modPow(G, bob_priv, p);

  document.getElementById("alice_pub").textContent = alice_pub;
  document.getElementById("bob_pub").textContent = bob_pub;

  // Обмен ключами
  document.getElementById("alice_to_bob").textContent = alice_pub;
  document.getElementById("bob_to_alice").textContent = bob_pub;

  // Общий секрет
  const alice_secret = modPow(bob_pub, alice_priv, p);
  const bob_secret = modPow(alice_pub, bob_priv, p);

  document.getElementById("alice_compute").innerHTML =
    `${bob_pub}^${alice_priv} mod 71`;
  document.getElementById("alice_secret").textContent = alice_secret;
  document.getElementById("bob_compute").innerHTML =
    `${alice_pub}^${bob_priv} mod 71`;
  document.getElementById("bob_secret").textContent = bob_secret;
  document.getElementById("shared_secret").textContent = alice_secret;
  document.getElementById("chat_shared_secret").textContent = alice_secret;
  document.getElementById("alice_chat_secret").textContent = alice_secret;
  document.getElementById("bob_chat_secret").textContent = alice_secret;
  rebuildToyChatForSecret(alice_secret);

  // X3DH демо
  document.getElementById("ik_alice").textContent = alice_pub;
  document.getElementById("ik_bob").textContent = bob_pub;

  // SPK (подписанные предварительные ключи)
  const spk_alice = modPow(G, 23, p); // 2^23 mod 71
  const spk_bob = modPow(G, 32, p); // 2^32 mod 71
  document.getElementById("spk_alice").textContent = spk_alice;
  document.getElementById("spk_bob").textContent = spk_bob;

  // OTPK (одноразовые)
  const otpk_alice = [
    modPow(G, 17, p),
    modPow(G, 23, p),
    modPow(G, 41, p),
    modPow(G, 53, p),
  ];
  const otpk_bob = [
    modPow(G, 19, p),
    modPow(G, 29, p),
    modPow(G, 37, p),
    modPow(G, 43, p),
  ];
  document.getElementById("otpk_alice").textContent =
    `[${otpk_alice.join(", ")}]`;
  document.getElementById("otpk_bob").textContent = `[${otpk_bob.join(", ")}]`;

  // Эфемерные ключи
  const eph_alice = modPow(G, 33, p);
  const eph_bob = modPow(G, 44, p);
  document.getElementById("eph_alice").textContent = eph_alice;
  document.getElementById("eph_bob").textContent = eph_bob;
}

// Функция для симуляции MITM
function simulateMITM() {
  const eve_priv1 = 33;
  const eve_priv2 = 44;

  const alice_priv = parseInt(document.getElementById("alice_priv").value);
  const bob_priv = parseInt(document.getElementById("bob_priv").value);

  const eve_pub1 = modPow(G, eve_priv1, p);
  const eve_pub2 = modPow(G, eve_priv2, p);

  document.getElementById("eve_to_bob").textContent = eve_pub1;
  document.getElementById("eve_to_alice").textContent = eve_pub2;

  const eve_alice_secret = modPow(eve_pub2, eve_priv1, p);
  const eve_bob_secret = modPow(eve_pub1, eve_priv2, p);

  document.getElementById("eve_alice_secret").textContent = eve_alice_secret;
  document.getElementById("eve_bob_secret").textContent = eve_bob_secret;

  const mitmDemo = document.getElementById("mitm_demo");
  mitmDemo.classList.remove("is-hidden");
  mitmDemo.setAttribute("aria-hidden", "false");
  updateMITMToggleButton();
}

// Функция для сброса
function resetDemo() {
  const mitmDemo = document.getElementById("mitm_demo");
  mitmDemo.classList.add("is-hidden");
  mitmDemo.setAttribute("aria-hidden", "true");
  updateMITMToggleButton();
  document.getElementById("receipt_demo").style.display = "none";
}

// Функции для уведомлений
function simulateDelivery() {
  document.getElementById("receipt_demo").style.display = "block";
  document.getElementById("receipt_text").innerHTML =
    'Боб отправил DeliveryReceipt: "Сообщение доставлено на устройство"';
}

function simulateRead() {
  document.getElementById("receipt_demo").style.display = "block";
  document.getElementById("receipt_text").innerHTML =
    'Боб отправил ReadReceipt: "Сообщение прочитано в 15:30"';
}

// Функции для калькулятора
function computePow() {
  const exp = parseInt(document.getElementById("pow_input").value);
  const result = modPow(G, exp, p);
  document.getElementById("pow_result").textContent = result;
}

function computeShared() {
  const exp = parseInt(document.getElementById("shared_input").value);
  const result = modPow(25, exp, p);
  document.getElementById("shared_result").textContent = result;
}

const LOG10_2 = Math.log10(2);
const LOG10_E = Math.log10(Math.E);

function formatMantissaExp(log10x) {
  if (!Number.isFinite(log10x)) return "—";
  const exp = Math.floor(log10x);
  const mantissa = Math.pow(10, log10x - exp);
  return `${mantissa.toFixed(2)}e${exp}`;
}

function formatOpsEstimate(model, bits) {
  const k = Number(bits);
  const log10Ops = model === "bruteforce" ? k * LOG10_2 : (k / 2) * LOG10_2;
  const pow2 = model === "bruteforce" ? `2^${k}` : `2^${k / 2}`;
  if (log10Ops < 6) {
    const ops = Math.round(Math.pow(10, log10Ops));
    return `~ ${pow2} ≈ ${ops.toLocaleString("ru-RU")} операций`;
  }
  return `~ ${pow2} ≈ ${formatMantissaExp(log10Ops)} операций`;
}

function humanizeLog10Seconds(log10Seconds) {
  if (!Number.isFinite(log10Seconds)) return "—";
  if (log10Seconds < 0) return "< 1 сек";

  const sec = Math.pow(10, Math.min(log10Seconds, 15)); // safe number for small ranges
  if (log10Seconds <= 5) {
    if (sec < 60) return `≈ ${Math.round(sec).toLocaleString("ru-RU")} сек`;
    if (sec < 3600) return `≈ ${(sec / 60).toFixed(1).replace(".", ",")} мин`;
    if (sec < 86400) return `≈ ${(sec / 3600).toFixed(1).replace(".", ",")} ч`;
    return `≈ ${(sec / 86400).toFixed(1).replace(".", ",")} дн`;
  }

  const log10Year = Math.log10(365.25 * 24 * 3600);
  const log10Years = log10Seconds - log10Year;
  if (log10Years < 6) {
    const years = Math.pow(10, log10Years);
    return `≈ ${years.toFixed(0).toLocaleString("ru-RU")} лет`;
  }
  return `≈ ${formatMantissaExp(log10Years)} лет`;
}

function updateBruteforce() {
  const model = document.getElementById("bf_model").value;
  const bits = parseInt(document.getElementById("bf_bits").value, 10);
  const rate = parseFloat(document.getElementById("bf_rate").value);

  document.getElementById("bf_bits_label").textContent = String(bits);

  const log10Ops =
    model === "bruteforce" ? bits * LOG10_2 : (bits / 2) * LOG10_2;
  const log10Rate = Math.log10(rate);

  // Средний случай: половина пространства поиска
  const log10AvgSeconds = log10Ops - log10Rate + Math.log10(0.5);
  const log10WorstSeconds = log10Ops - log10Rate;

  document.getElementById("bf_ops").textContent = formatOpsEstimate(
    model,
    bits,
  );
  document.getElementById("bf_time").textContent =
    humanizeLog10Seconds(log10AvgSeconds);
  document.getElementById("bf_time_worst").textContent =
    humanizeLog10Seconds(log10WorstSeconds);

  // В этой демке: приватный ключ в диапазоне 1..70 (примерно 70 вариантов)
  const demoSpace = 70;
  const demoAvgSeconds = demoSpace / 2 / rate;
  const demoWorstSeconds = demoSpace / rate;
  const demoText =
    `≈ ${demoAvgSeconds.toExponential(2)} сек (в среднем), ` +
    `≈ ${demoWorstSeconds.toExponential(2)} сек (худший случай)`;
  document.getElementById("bf_demo_time").textContent = demoText.replace(
    ".",
    ",",
  );
}

// Обновляем при загрузке
window.onload = function () {
  updateAll();
  updateBruteforce();
  updateDisplayToggle();
  updateMITMToggleButton();
  renderToyChat();
  sendToyMessage("alice");
};

// Обновляем при изменении полей
document.getElementById("alice_priv").addEventListener("input", updateAll);
document.getElementById("bob_priv").addEventListener("input", updateAll);

document
  .getElementById("bf_model")
  .addEventListener("change", updateBruteforce);
document.getElementById("bf_bits").addEventListener("input", updateBruteforce);
document.getElementById("bf_rate").addEventListener("change", updateBruteforce);
