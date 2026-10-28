/* Finite rule search: eq/gte conditions, one action per input. No network. */
(function (root) {
  "use strict";
  function inputs(table) {
    const fields = Object.keys(table.input_space);
    if (!fields.length || fields.length > 8) throw new Error("Declare 1–8 finite fields.");
    let values = [{}];
    for (const field of fields) {
      const domain = table.input_space[field];
      if (!Array.isArray(domain) || !domain.length || new Set(domain.map(JSON.stringify)).size !== domain.length ||
          domain.some(v => !["boolean", "number", "string"].includes(typeof v) || (typeof v === "number" && !Number.isFinite(v))))
        throw new Error("Invalid finite domain.");
      if (values.length * domain.length > 256) throw new Error("At most 256 declared inputs.");
      values = values.flatMap(value => domain.map(v => ({...value, [field]: v})));
    }
    return values;
  }
  function matches(rule, value) {
    return Object.entries(rule.when).every(([field, conditions]) =>
      Object.hasOwn(value, field) && Object.entries(conditions).every(([op, expected]) => {
        const actual = value[field];
        if (op === "eq") return typeof actual === typeof expected && actual === expected;
        if (op === "gte") return typeof actual === "number" && actual >= expected;
        throw new Error("Unsupported condition operator.");
      }));
  }
  function search(table) {
    if (table.priority?.length) throw new Error("This editor uses unprioritized v1 tables.");
    if (table.rules.some(r => typeof r.action !== "string" || !r.action.trim()))
      throw new Error("Give every rule an action before checking.");
    const space = inputs(table), clashes = [];
    for (const witness of space) {
      const active = table.rules.filter(r => r.enabled !== false && matches(r, witness));
      for (let i = 0; i < active.length; i++) {
        for (let j = i + 1; j < active.length; j++) {
          if (active[i].action !== active[j].action)
            clashes.push({witness, rules: [active[i].id, active[j].id], actions: [active[i].action, active[j].action]});
        }
      }
    }
    return {checked: space.length, clashes};
  }
  function preview(table) {
    const result = search(table), groups = [];
    const active = table.rules.filter(r => r.enabled !== false);
    const seen = new Set();
    for (const clash of result.clashes) {
      const key = JSON.stringify(clash.rules);
      if (seen.has(key)) continue;
      seen.add(key);
      const ids = clash.rules, rest = active.map(r => r.id).filter(id => !ids.includes(id));
      const choices = [{winner: ids[0], priority: [...ids, ...rest]},
                       {winner: ids[1], priority: [...ids].reverse().concat(rest)}];
      const rows = [];
      for (const value of inputs(table)) {
        const matching = active.filter(r => matches(r, value));
        const outcomes = choices.map(c => {
          const id = c.priority.find(id => matching.some(r => r.id === id));
          return id === undefined ? table.default : matching.find(r => r.id === id).action;
        });
        if (outcomes[0] !== outcomes[1]) rows.push({input: value, actions: outcomes});
      }
      groups.push({rules: ids, affected_inputs: rows.length, choices, rows});
    }
    return {checked: result.checked, conflicts: groups.length, groups};
  }
  root.MuseGuardClashes = {inputs, matches, search, preview};
})(globalThis);
