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
      const result = MuseGuardClashes.preview(table);
      status.textContent = `${result.checked} declared inputs checked · ${result.conflicts} conflict${result.conflicts === 1 ? "" : "s"}`;
      status.dataset.clashes = result.groups.reduce((n,g) => n+g.affected_inputs,0);
      status.dataset.conflicts = result.conflicts;
      if (!result.groups.length) cards.append(node("p", "No conflicting actions among the enabled rules and declared inputs."));
      for (const group of result.groups) {
        const card = node("article"); card.className = "clash-example preview-group";
        card.append(node("h3", `1 conflict (${group.rules.join(" vs ")}), ${group.affected_inputs} input${group.affected_inputs === 1 ? "" : "s"} affected`));
        const preview = node("table"), head = node("thead"), labels = node("tr"), body = node("tbody");
        for (const label of ["Declared input", ...group.choices.map(c => `${c.winner} wins`)]) {
          const th = node("th", label); th.scope = "col"; labels.append(th);
        }
        head.append(labels);
        for (const row of group.rows) {
          const tr = node("tr"), th = node("th"); th.scope = "row";
          th.append(node("code", JSON.stringify(row.input))); tr.append(th);
          for (const action of row.actions) {const td=node("td");td.append(node("code",action));tr.append(td);}
          body.append(tr);
        }
        preview.append(head,body);card.append(preview,node("p","Other declared inputs have the same outcome under either choice."));cards.append(card);
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
