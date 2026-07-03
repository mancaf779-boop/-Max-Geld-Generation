const test = require("node:test");
const assert = require("node:assert/strict");
const { routeLeads } = require("../src/lib/leads");

test("routes by deal size and region, round-robins owners within a team", () => {
  const { assignments, summary } = routeLeads([
    { id: "1", region: "US", dealSize: 75000 },
    { id: "2", region: "EU", dealSize: 1000 },
    { id: "3", region: "US", dealSize: 1000 },
    { id: "4", region: "US", dealSize: 1000 },
  ]);

  assert.equal(assignments[0].assignedTeam, "enterprise-sales");
  assert.equal(assignments[1].assignedTeam, "eu-sales");
  assert.equal(assignments[2].assignedTeam, "sdr-queue");
  assert.equal(assignments[3].assignedTeam, "sdr-queue");
  assert.notEqual(assignments[2].assignedOwner, assignments[3].assignedOwner);
  assert.equal(summary.byTeam["sdr-queue"], 2);
});
