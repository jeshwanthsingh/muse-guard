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
  root.MuseGuardClashes = {inputs, matches, search};
})(globalThis);
