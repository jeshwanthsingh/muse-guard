/* Presentation-only playground. Never changes recorded evidence or decisions. */
(function () {
  "use strict";
  const select = document.getElementById("demo-table");
  const tbody = document.getElementById("rule-rows");
  const status = document.getElementById("clash-status");
  const cards = document.getElementById("clash-cards");
  const fields = document.getElementById("declared-fields");
  let table;
  const node = (tag, value) => { const el = document.createElement(tag); if (value !== undefined) el.textContent = value; return el; };
  function renderResult() {
    cards.replaceChildren();
    try {
      const result = MuseGuardClashes.search(table);
      status.textContent = `${result.checked} declared inputs checked · ${result.clashes.length} clashes found`;
      status.dataset.clashes = result.clashes.length;
      if (!result.clashes.length) cards.append(node("p", "No conflicting actions among the enabled rules and declared inputs."));
      for (const clash of result.clashes) {
        const card = node("article"); card.className = "clash-example";
        card.append(node("h3", `Rule ${clash.rules[0]} vs Rule ${clash.rules[1]}`), node("code", JSON.stringify(clash.witness)),
          node("p", `${clash.rules[0]} → ${clash.actions[0]}   /   ${clash.rules[1]} → ${clash.actions[1]}`));
        cards.append(card);
      }
    } catch (error) { status.textContent = error.message; delete status.dataset.clashes; }
  }
  function load() {
    table = structuredClone(MuseGuardDemoTables[Number(select.value)]);
    fields.textContent = Object.entries(table.input_space).map(([key, values]) => `${key}: ${JSON.stringify(values)}`).join(" · ");
    tbody.replaceChildren();
    for (const rule of table.rules) {
      const tr = node("tr"), toggleCell = node("td"), condition = node("td"), action = node("td");
      const toggle = node("input"); toggle.type = "checkbox"; toggle.checked = true;
      toggle.setAttribute("aria-label", `Enable Rule ${rule.id}`);
      toggle.addEventListener("change", () => { rule.enabled = toggle.checked; tr.classList.toggle("disabled-rule", !toggle.checked); renderResult(); });
      toggleCell.append(toggle, node("span", ` ${rule.id}`));
      condition.append(node("span", rule.text), node("code", JSON.stringify(rule.when)));
      const edit = node("input"); edit.type = "text"; edit.value = rule.action; edit.maxLength = 80;
      edit.setAttribute("aria-label", `Rule ${rule.id} action`);
      edit.addEventListener("input", () => { rule.action = edit.value; renderResult(); });
      action.append(edit); tr.append(toggleCell, condition, action); tbody.append(tr);
    }
    renderResult();
  }
  MuseGuardDemoTables.forEach((t, i) => { const option = node("option", t.title); option.value = i; select.append(option); });
  select.addEventListener("change", load);
  document.getElementById("reset-rules").addEventListener("click", load);
  load();
})();
