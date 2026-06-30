/* ==========================================================================
   Aita-Lagun — Chat Application (Brutalist UI)
   
   Extracted from original index.html IIFE. Adapted for flat-entry DOM
   structure. All functions preserved: fetch, markdown, language detection.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     DOM References
     ------------------------------------------------------------------------ */
  var chatMessages = document.getElementById("chat-messages");
  var form = document.getElementById("chat-form");
  var input = document.getElementById("message-input");
  var sendBtn = document.getElementById("send-btn");
  var emptyState = document.getElementById("empty-state");
  var suggestions = document.getElementById("suggestions");
  /* Session language — detected once from the first user message
     and reused for all button rendering. This avoids language
     detection failing on short follow-up messages like "Every day"
     or "Gaur bakarrik" that lack enough keywords. */
  var _sessionLang = null;

  /* ------------------------------------------------------------------------
     Confirmation Detection — detect when agent asks to confirm an action
     Supports ES, EU, EN patterns. Falls back gracefully if not detected.
     ------------------------------------------------------------------------ */
  var CONFIRM_PATTERNS = [
    /\bconfirmar\b/i, /\bconfirma\b/i, /\bconfirmas\b/i,
    /\bquieres\b/i, /\bquiere\b/i, /\bdeseas\b/i, /\bdesea\b/i,
    /\best(?:á|a)s seguro\b/i,
    /\bprocedemos\b/i, /\bprocedo\b/i,
    /\bcreo (?:el |un )?(?:evento|recordatorio)\b/i,
    /\bcrear (?:el |un )?(?:evento|recordatorio)\b/i,
    /\bagendo\b/i, /\bprogramo\b/i,
    /shall i/i, /do you want/i, /do you wish/i, /should i/i,
    /\bproceed\b/i, /\bconfirm\b/i,
    /\baieztatu\b/i, /\bnahi\b/i, /\bgogorarazi\b/i, /\bgogorarazpen\b/i, /\bsortu/i,
    /\bkonfirm(?:atu|atzen|azio)\b/i,
    /\bberretsi\b/i, /\begokia\b/i, /\bzuzenak\b/i, /\bzuzena\b/i,
    /\bonartzen\b/i, /\bprest\b/i,
  ];

  /* Recurrence patterns — detect when agent asks about frequency.
     Checked BEFORE confirmation patterns to show the right buttons. */
  var RECURRENCE_PATTERNS = [
    /every day/i, /every (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i,
    /just for today/i, /single (?:reminder|time|event|one)/i, /recurring/i,
    /\bsolo hoy\b/i, /\btodos los días\b/i, /\bcada día\b/i,
    /\blos (?:lunes|martes|miércoles|jueves|viernes|sábado|domingos)\b/i,
    /\bentre semana\b/i, /\bdías laborables\b/i,
    /\bgaur bakarrik\b/i, /\begunero\b/i, /\bastelehenero\b/i,
    /\berrepikakor\b/i, /\bbakarra\b/i,
  ];

  function isRecurrenceText(text) {
    if (!text) return false;
    var hasQuestion = text.indexOf("?") !== -1 || text.indexOf("¿") !== -1;
    if (!hasQuestion) return false;
    for (var i = 0; i < RECURRENCE_PATTERNS.length; i++) {
      if (RECURRENCE_PATTERNS[i].test(text)) return true;
    }
    return false;
  }

  function isConfirmationText(text) {
    if (!text) return false;
    var hasQuestion = text.indexOf("?") !== -1 || text.indexOf("¿") !== -1;
    if (!hasQuestion) return false;
    for (var i = 0; i < CONFIRM_PATTERNS.length; i++) {
      if (CONFIRM_PATTERNS[i].test(text)) return true;
    }
    return false;
  }

  /* ------------------------------------------------------------------------
     Scroll to bottom (uses rAF for smooth layout flush)
     ------------------------------------------------------------------------ */
  function scrollToBottom() {
    requestAnimationFrame(function () {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });
  }

  /* ------------------------------------------------------------------------
     Current time — HH:MM format
     ------------------------------------------------------------------------ */
  function getCurrentTime() {
    var d = new Date();
    return (
      String(d.getHours()).padStart(2, "0") +
      ":" +
      String(d.getMinutes()).padStart(2, "0")
    );
  }

  /* ------------------------------------------------------------------------
     Escape HTML — prevent XSS in user-generated content
     ------------------------------------------------------------------------ */
  function escapeHtml(t) {
    var d = document.createElement("div");
    d.appendChild(document.createTextNode(t));
    return d.innerHTML;
  }

  /* ------------------------------------------------------------------------
     Simple Markdown Renderer
     Supports: **bold**, *italic*, `code`, [links](url), paragraph breaks
     ------------------------------------------------------------------------ */
  function renderMarkdown(text) {
    var html = escapeHtml(text);
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
    html = html.replace(/`(.+?)`/g, "<code>$1</code>");
    html = html.replace(
      /\[(.+?)\]\((.+?)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    );
    var parts = html.split(/\n\s*\n/);
    if (parts.length > 1) {
      return parts
        .map(function (p) {
          return p.trim() ? "<p>" + p + "</p>" : "";
        })
        .join("");
    }
    return html.replace(/\n/g, "<br>");
  }

  /* ------------------------------------------------------------------------
     Language Detection
     Returns 'EU' (Basque), 'ES' (Spanish), or 'EN' (English/other)
     ------------------------------------------------------------------------ */
  function detectLanguage(text) {
    var lower = text.toLowerCase();
    var eu = 0,
      es = 0,
      m;
    m = lower.match(
      /\b(eta|ez|bat|du|da|zen|dira|dute|zuen|bere|gure|zure|haien|batez|batek|gisa|moduan|eskatu|behar|nahi|izan|egon|osakidetza|sendagai|mediku|botika|errezeta|hitza|egin|eman|eskaera|baieztatu|sortu|gogoratu|pastilla|kaixo)\b/g
    );
    if (m) eu = m.length;
    m = lower.match(
      /\b(el|la|los|las|que|por|para|con|una|como|más|pero|este|esta|hola|gracias|puede|debe|usted|señor|señora|buenos|días|tardes|noches|salud|cita|médico|farmacia|pastillas|medicamento|receta|turno|horario|centro|atencion|paciente|recuerda|tomar)\b/g
    );
    if (m) es = m.length;
    if (eu > es && eu >= 2) return "EU";
    if (es > eu && es >= 2) return "ES";
    return "EN";
  }

  /* ------------------------------------------------------------------------
     Add Message to Chat — Terminal Log Style
     
     Creates a flat .entry for each message. No bubbles, no right-alignment.
     All entries left-aligned like a terminal log. User messages prefixed
     with ❯ (see CSS .entry.user::before). Entries separated by dashed
     horizontal rules (see .entry + .entry in styles.css).
     
     @param {string} text  — message body
     @param {string} type  — 'user' | 'assistant' | 'error'
     ------------------------------------------------------------------------ */
  function addMessage(text, type) {
    // Remove empty state on first message
    if (emptyState && emptyState.parentNode) {
      emptyState.remove();
    }

    var entry = document.createElement("div");
    entry.className = "entry " + type;

    if (type === "assistant") {
      // Render markdown for assistant responses
      entry.innerHTML = renderMarkdown(text);

      // Language badge
      var badge = document.createElement("span");
      badge.className = "lang-badge";
      badge.textContent = detectLanguage(text);
      entry.appendChild(badge);

      // Timestamp
      var time = document.createElement("span");
      time.className = "timestamp";
      time.textContent = getCurrentTime();
      entry.appendChild(time);
    } else if (type === "error") {
      // Error — flat text, no markdown
      entry.textContent = text;

      var timeErr = document.createElement("span");
      timeErr.className = "timestamp";
      timeErr.textContent = getCurrentTime();
      entry.appendChild(timeErr);
    } else {
      // User — plain text, ❯ prefix comes from CSS ::before
      entry.textContent = text;

      var timeUsr = document.createElement("span");
      timeUsr.className = "timestamp";
      timeUsr.textContent = getCurrentTime();
      entry.appendChild(timeUsr);
    }

    chatMessages.appendChild(entry);
    scrollToBottom();
  }

  /* ------------------------------------------------------------------------
     Loading Indicator — terminal-style text with blinking cursor
     ------------------------------------------------------------------------ */
  function toggleLoading(show) {
    var el = document.querySelector(".loading-indicator");
    if (show && !el) {
      el = document.createElement("div");
      el.className = "loading-indicator";
      el.setAttribute("aria-label", "Assistant is thinking");
      el.textContent = "_thinking";
      chatMessages.appendChild(el);
      scrollToBottom();
    } else if (!show && el) {
      el.remove();
    }
  }

  /* ------------------------------------------------------------------------
     Confirmation Buttons — language-aware labels
     
     Renders two inline buttons in the detected language.
     Clicking one sends the matching confirmation word back to the agent.
     
     Labels are set from CONF_LABELS by detected language.
     Falls back to English if the language code is unknown.
     ------------------------------------------------------------------------ */
  var CONF_LABELS = {
    EN: { yes: "Yes",  no: "No",  sendYes: "Yes", sendNo: "No" },
    ES: { yes: "Sí",   no: "No",  sendYes: "Sí",  sendNo: "No" },
    EU: { yes: "Bai",  no: "Ez",  sendYes: "Bai",  sendNo: "Ez" },
  };

  /* Recurrence button labels — language-aware.
     First button = single/just today, Second button = recurring/every day. */
  var RECUR_LABELS = {
    EN: { single: "Just today", recurring: "Every day", other: "Other...", sendSingle: "Just today", sendRecurring: "Every day", sendOther: "Other" },
    ES: { single: "Solo hoy",   recurring: "Todos los días", other: "Otro...",  sendSingle: "Solo hoy",   sendRecurring: "Todos los días", sendOther: "Otro" },
    EU: { single: "Gaur bakarrik", recurring: "Egunero",      other: "Bestelakoa...", sendSingle: "Gaur bakarrik", sendRecurring: "Egunero",      sendOther: "Bestelakoa" },
  };

  function addRecurrenceButtons(entry, lang) {
    if (entry.querySelector(".confirmation-buttons")) return;

    var l = RECUR_LABELS[lang] || RECUR_LABELS.EN;

    var btnGroup = document.createElement("div");
    btnGroup.className = "confirmation-buttons confirmation-buttons--three";

    var singleBtn = document.createElement("button");
    singleBtn.className = "confirm-no";
    singleBtn.textContent = l.single;
    singleBtn.setAttribute("aria-label", l.single);

    var recurringBtn = document.createElement("button");
    recurringBtn.className = "confirm-yes";
    recurringBtn.textContent = l.recurring;
    recurringBtn.setAttribute("aria-label", l.recurring);

    var otherBtn = document.createElement("button");
    otherBtn.className = "confirm-other";
    otherBtn.textContent = l.other;
    otherBtn.setAttribute("aria-label", l.other);

    singleBtn.addEventListener("click", function () {
      if (singleBtn.disabled) return;
      singleBtn.disabled = true;
      recurringBtn.disabled = true;
      otherBtn.disabled = true;
      input.value = l.sendSingle;
      form.requestSubmit();
    });

    recurringBtn.addEventListener("click", function () {
      if (recurringBtn.disabled) return;
      singleBtn.disabled = true;
      recurringBtn.disabled = true;
      otherBtn.disabled = true;
      input.value = l.sendRecurring;
      form.requestSubmit();
    });

    otherBtn.addEventListener("click", function () {
      if (otherBtn.disabled) return;
      singleBtn.disabled = true;
      recurringBtn.disabled = true;
      otherBtn.disabled = true;
      input.value = l.sendOther;
      form.requestSubmit();
    });

    btnGroup.appendChild(singleBtn);
    btnGroup.appendChild(recurringBtn);
    btnGroup.appendChild(otherBtn);
    entry.appendChild(btnGroup);
  }

  function addConfirmationButtons(entry, lang) {
    if (entry.querySelector(".confirmation-buttons")) return;

    var l = CONF_LABELS[lang] || CONF_LABELS.EN;

    var btnGroup = document.createElement("div");
    btnGroup.className = "confirmation-buttons";

    var yesBtn = document.createElement("button");
    yesBtn.className = "confirm-yes";
    yesBtn.textContent = l.yes;
    yesBtn.setAttribute("aria-label", "Confirm: " + l.yes);

    var noBtn = document.createElement("button");
    noBtn.className = "confirm-no";
    noBtn.textContent = l.no;
    noBtn.setAttribute("aria-label", "Cancel: " + l.no);

    yesBtn.addEventListener("click", function () {
      if (yesBtn.disabled) return;
      yesBtn.disabled = true;
      noBtn.disabled = true;
      input.value = l.sendYes;
      form.requestSubmit();
    });

    noBtn.addEventListener("click", function () {
      if (noBtn.disabled) return;
      yesBtn.disabled = true;
      noBtn.disabled = true;
      input.value = l.sendNo;
      form.requestSubmit();
    });

    btnGroup.appendChild(yesBtn);
    btnGroup.appendChild(noBtn);
    entry.appendChild(btnGroup);
  }

  /* ------------------------------------------------------------------------
     Textarea Auto-Resize
     ------------------------------------------------------------------------ */
  input.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 150) + "px";
  });

  /* ------------------------------------------------------------------------
     Keyboard: Enter to submit, Shift+Enter for newline
     ------------------------------------------------------------------------ */
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  /* ------------------------------------------------------------------------
     Suggestion Chips — click to populate and auto-submit
     ------------------------------------------------------------------------ */
  suggestions.addEventListener("click", function (e) {
    var btn = e.target.closest("button");
    if (!btn) return;
    input.value = btn.getAttribute("data-msg");
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 150) + "px";
    form.requestSubmit();
  });

  /* ------------------------------------------------------------------------
     Status Bar — update clock every 30s
     ------------------------------------------------------------------------ */
  var statusBar = document.getElementById("status-bar");
  if (statusBar) {
    var rightSpan = statusBar.querySelector(".footer-right");
    if (rightSpan) {
      var clockSpan = document.createElement("span");
      clockSpan.className = "status-clock";
      clockSpan.textContent = getCurrentTime();
      rightSpan.appendChild(clockSpan);
      setInterval(function () {
        clockSpan.textContent = getCurrentTime();
      }, 30000);
    }
  }

  /* ------------------------------------------------------------------------
     Form Submit — POST to /api/chat
     
     EXACT fetch logic preserved from original implementation.
     ------------------------------------------------------------------------ */
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";
    input.style.height = "auto";
    sendBtn.disabled = true;
    toggleLoading(true);

    try {
      var res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        var errData;
        try {
          errData = await res.json();
        } catch (_) {
          errData = {};
        }
        throw new Error(errData.detail || "Request failed (" + res.status + ")");
      }

      var data = await res.json();
      toggleLoading(false);
      addMessage(data.reply, "assistant");
      var entries = chatMessages.querySelectorAll(".entry.assistant");
      var lastEntry = entries[entries.length - 1];
      // Cache language from the FIRST user message of the session.
      // Re-detecting on every message fails for short follow-ups
      // like "Every day" or "Gaur bakarrik" that lack enough keywords.
      if (_sessionLang === null) {
        _sessionLang = detectLanguage(text);
      }
      // Check recurrence question FIRST, then confirmation.
      if (isRecurrenceText(data.reply)) {
        addRecurrenceButtons(lastEntry, _sessionLang);
      } else if (isConfirmationText(data.reply)) {
        addConfirmationButtons(lastEntry, _sessionLang);
      }
    } catch (err) {
      toggleLoading(false);
      addMessage("Something went wrong. Please try again.", "error");
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  });
})();
